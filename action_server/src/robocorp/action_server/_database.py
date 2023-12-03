import datetime
import itertools
import logging
import re
import sqlite3
import threading
from contextlib import closing, contextmanager
from pathlib import Path
from types import NoneType
from typing import Any, Dict, Iterator, List, Optional, Tuple, Type, TypeVar, Union

log = logging.getLogger(__name__)

_RE_FIRST_CAP = re.compile("(.)([A-Z][a-z]+)")
_RE_ALL_CAP = re.compile("([a-z0-9])([A-Z])")


T = TypeVar("T")


def _make_table_name(cls_name):
    s1 = _RE_FIRST_CAP.sub(r"\1_\2", cls_name)
    return _RE_ALL_CAP.sub(r"\1_\2", s1).lower()


# Helper functions since we must store the datetime as str.
# (no need to autoconvert all the time).


def datetime_to_str(val: datetime.datetime) -> str:
    return val.isoformat()


def str_to_datetime(val: str) -> datetime.datetime:
    return datetime.datetime.fromisoformat(val)


class DBError(Exception):
    pass


class Database:
    """
    Some notes:

        Connections must be per-thread.

        No 2 connections should be writing at the same time (ideally, use a
        single thread for writing).

        This class makes it so that there's only one connection per thread.
    """

    def __init__(self, db_path: Optional[Union[Path, str]] = None):
        self._cls_to_type_hint: Dict[type, dict] = {}
        if not db_path:
            from ._settings import get_settings

            self._db_path = db_path or get_settings().datadir / "server.db"
        else:
            self._db_path = db_path

        self._table_name_to_cls: Dict[str, type] = {}
        self._tlocal = threading.local()
        self._counter = itertools.count(0)
        self._write_lock = threading.RLock()

    def _get_type_hints(self, cls) -> dict:
        try:
            return self._cls_to_type_hint[cls]
        except KeyError:
            from typing import get_type_hints

            ret = get_type_hints(cls)
            self._cls_to_type_hint[cls] = ret
            return ret

    def _iter_name_and_name_cls_fields(self, cls) -> Iterator[Tuple[str, type]]:
        yield from self._get_type_hints(cls).items()

    def _iter_name_fields(self, cls) -> Iterator[str]:
        yield from self._get_type_hints(cls).keys()

    @contextmanager
    def connect(self) -> Iterator[None]:
        try:
            conn = self._tlocal.conn
        except AttributeError:
            conn = None

        if conn is not None:
            yield
            return

        with closing(sqlite3.connect(self._db_path, isolation_level=None)) as conn:
            self._tlocal.conn = conn
            try:
                yield
            finally:
                self._tlocal.conn = None

    def _next_savepoint_name(self):
        return f"savepoint_{next(self._counter)}"

    @contextmanager
    def cursor(self) -> Iterator[sqlite3.Cursor]:
        """
        A cursor should be requested to do queries.
        """
        try:
            conn = self._tlocal.conn
        except AttributeError:
            conn = None
        if conn is None:
            raise RuntimeError(
                "Error. Cannot create a cursor without a connection in place."
            )

        with closing(conn.cursor()) as cur:
            yield cur

    def in_transaction(self) -> bool:
        """
        Returns:
            True if we're currently in a transaction and False otherwise.
        """
        try:
            in_transaction = self._tlocal.in_transaction
        except AttributeError:
            in_transaction = self._tlocal.in_transaction = 0

        return in_transaction > 0

    @contextmanager
    def transaction(self) -> Iterator[None]:
        """
        A transaction should be created when contents are about to be written.

        SQLite can't deal with multiple writers, so, we use a lock in Python
        which will prevent other threads from writing at the same time.
        """

        try:
            conn = self._tlocal.conn
        except AttributeError:
            conn = None
        if conn is None:
            raise DBError(
                "Unable to create a transaction because no connection is in place."
            )

        try:
            in_transaction = self._tlocal.in_transaction
        except AttributeError:
            in_transaction = self._tlocal.in_transaction = 0

        if in_transaction:
            # Nested transactions are not supported, so, don't start a new one
            # here, but we can still use savepoints.
            self._tlocal.in_transaction += 1
            savepoint_name = self._next_savepoint_name()
            self.execute(f"savepoint {savepoint_name};")
            try:
                yield
            except BaseException:
                self.execute(f"rollback to savepoint {savepoint_name};")
                raise
            finally:
                self._tlocal.in_transaction -= 1
            return

        assert (
            self._tlocal.in_transaction == 0
        ), "Error transaction nesting logic not correct!"

        self._tlocal.in_transaction += 1
        try:
            self.execute("BEGIN")
            yield
        except BaseException:
            log.exception("Error. Rolling back database")
            conn.rollback()
            raise
        else:
            conn.commit()
        finally:
            self._tlocal.in_transaction -= 1
            assert (
                self._tlocal.in_transaction == 0
            ), "Error transaction nesting logic not correct!"

    def update(self, instance, *fields):
        """
        Updates database values from some instance given its id.
        """
        table_name = _make_table_name(instance.__class__.__name__)
        set_fields = []
        values = []
        for field in fields:
            set_fields.append(f"{field}=?")
            values.append(getattr(instance, field))

        values.append(instance.id)
        sql = f"UPDATE {table_name} SET {', '.join(set_fields)} WHERE id=?"
        self.execute(sql, values)

    def insert(
        self,
        instance,
    ) -> None:
        table_name = _make_table_name(instance.__class__.__name__)

        field_names = []
        values = []
        placeholders = []
        for name in self._iter_name_fields(instance.__class__):
            field_names.append(name)
            values.append(getattr(instance, name))
            placeholders.append("?")

        fields_str = ", ".join(field_names)
        placeholders_str = ", ".join(placeholders)

        self.execute(
            f"""
INSERT INTO {table_name}
    ({fields_str})
VALUES
    ({placeholders_str})
""",
            values,
        )

    def all(
        self, cls: Type[T], offset: Optional[int] = None, limit: Optional[int] = None
    ) -> List[T]:
        table_name = _make_table_name(cls.__name__)
        if limit is not None:
            assert isinstance(limit, int)
        if offset is not None:
            assert isinstance(offset, int)

        sql = f"SELECT * FROM {table_name}"

        if limit:
            sql += f" LIMIT {limit}"

        if offset:
            sql += f" OFFSET {offset}"

        with self.cursor() as cursor:
            self.execute_query(cursor, sql)
            return [cls(*x) for x in cursor.fetchall()]

    def first(
        self,
        cls: Type[T],
        query: Optional[str] = None,
        values: Optional[List[Any]] = None,
    ) -> T:
        """
        Note: we want to use plain sql, not a bunch of ORM to query.

        Maybe we can use the same structure as:
        https://github.com/kruxia/sqly

        to build the SQL though (but right now the query is just
        the actual SQL with placeholders and the values should be
        passed separately).

        Example:

        db.first(
                ActionPackage,
                "SELECT * FROM action_package WHERE id = ?",
                [action.action_package_id],
            )

        Raises:
            KeyError if no entries were returned in the query.
        """
        if not query:
            table_name = _make_table_name(cls.__name__)
            query = f"SELECT * FROM {table_name}"

        with self.cursor() as cursor:
            self.execute_query(cursor, query, values=values)
            one = cursor.fetchone()
            if one is None:
                raise KeyError("Query returned no entries.")
            return cls(*one)

    def list_table_names(self) -> List[str]:
        with self.cursor() as cursor:
            self.execute_query(
                cursor,
                """
SELECT
    name
FROM
    sqlite_schema
WHERE
    type ='table' AND
    name NOT LIKE 'sqlite_%';
""",
            )
            return [x[0] for x in cursor.fetchall()]

    def list_whole_db(self) -> Dict[str, List[Dict[str, Any]]]:
        table_to_contents: Dict[str, List[Dict[str, Any]]] = {}
        for table, cls in self._table_name_to_cls.items():
            with self.cursor() as cursor:
                self.execute_query(cursor, f"SELECT * FROM {table}")

                cls = self._table_name_to_cls[table]
                field_names = list(self._iter_name_fields(cls))
                rows = []
                for row in cursor.fetchall():
                    rows.append(dict(itertools.zip_longest(field_names, row)))

                table_to_contents[table] = rows
        return table_to_contents

    def load_whole_db(self, contents: Dict[str, List[Dict[str, Any]]]) -> None:
        with self.transaction():
            for table, table_rows in contents.items():
                cls = self._table_name_to_cls[table]
                for row in table_rows:
                    instance = cls(**row)
                    self.insert(instance)

    def execute_query(
        self, cursor: sqlite3.Cursor, sql: str, values: Optional[list] = None
    ):
        """
        Executes a query which will NOT change the database (and should return values).

        No write-lock needed.
        """
        try:
            if values:
                cursor.execute(sql, values)
            else:
                cursor.execute(sql)
        except Exception:
            raise DBError(f"Error running sql query: {sql!r} with values: {values!r}")

    def execute(self, sql: str, values: Optional[list] = None) -> None:
        """
        Executes a query which will change the database.

        Requires the write-lock to be acquired since SQLite can't deal with
        writes in multiple threads concurrently.
        """

        try:
            if not self.in_transaction():
                raise DBError(
                    "When running an sql that changes the DB, it's expected that "
                    "a transaction is in place."
                )
            conn = self._tlocal.conn
            assert conn is not None
            with self._write_lock:
                if values:
                    conn.execute(sql, values)
                else:
                    conn.execute(sql)
        except Exception:
            raise DBError(f"Error running sql: {sql!r} with values: {values!r}")

    def register_classes(self, classes: List[Type]) -> None:
        if self._table_name_to_cls:
            values = set(self._table_name_to_cls.values())
            if values != set(classes):
                raise RuntimeError(
                    "The classes were already registered "
                    "(and do not match the new values)."
                )
            # i.e.: they were already registered.
            return

        for cls in classes:
            self._table_name_to_cls[_make_table_name(cls.__name__)] = cls

    def initialize(self, classes: List[Type]) -> None:
        """
        Initializes the tables as needed.
        """
        self.register_classes(classes)

        sqls = []
        for cls in classes:
            sql = self.create_table_sql(cls)
            sqls.append(sql)

        with self.connect():
            with self.transaction():
                self.execute("PRAGMA foreign_keys = ON")

            with self.transaction():
                for sql in sqls:
                    try:
                        self.execute(sql)
                    except sqlite3.OperationalError:
                        raise RuntimeError(f"Error with sql:\n{sql}")

    def create_table_sql(self, cls: Type) -> str:
        table_name = _make_table_name(cls.__name__)

        fields = []
        foreign_keys = []
        for name, name_cls in self._iter_name_and_name_cls_fields(cls):
            fields.append(self._get_field_create_sql(name, name_cls))

            if name.endswith("_id"):
                foreign_table = name[:-3]
                if foreign_table not in self._table_name_to_cls:
                    raise RuntimeError(
                        f"Error: unexpected foreign reference: {foreign_table} "
                        f"(for field: {name})"
                    )
                foreign_keys.append(
                    f"FOREIGN KEY ({name}) " f"REFERENCES {foreign_table}(id)"
                )

        fields.extend(foreign_keys)
        fields_str = ",\n    ".join(fields)
        sql = f"""
CREATE TABLE IF NOT EXISTS {table_name}(
    {fields_str}  
)
        """
        return sql

    def _get_field_create_sql(
        self,
        name: str,
        cls: Type,
        primary_key: Optional[bool] = None,
    ) -> str:
        if primary_key is None:
            primary_key = name == "id"

        if cls.__name__ == "Optional":
            not_none = [x for x in cls.__args__ if x != NoneType]
            assert len(not_none) == 1, f"Expected one not none in: {cls.__args__}"
            cls = not_none[0]
            not_null = False
        else:
            not_null = True

        if cls == int:
            use = "INTEGER"

        elif cls == str:
            use = "TEXT"

        elif cls == bool:
            use = f"INTEGER CHECK({name} IN (0, 1)))"

        elif cls == datetime.datetime:
            raise RuntimeError(
                f"Datetime not supported (field: {name}). Please "
                "use str and use utility functions to convert back and forth."
            )

        elif cls == float:
            use = "REAL"

        else:
            raise RuntimeError(f"Unsupported type: {cls}")

        use = f"{name} {use}"

        if not_null:
            use = f"{use} NOT NULL"

        if primary_key:
            use = f"{use} PRIMARY KEY"

        return f"{use}"
