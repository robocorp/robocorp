import datetime
import threading
import typing
from concurrent import futures
from pathlib import Path
from typing import Optional

import pytest
from pydantic.dataclasses import dataclass

from robocorp.action_server._database import Database, DBRules, datetime_to_str

_db_rules = DBRules()


@dataclass
class SomeActionPackage:
    id: int
    name: str
    condayaml: str


@dataclass
class SomeAction:
    id: int

    some_action_package_id: int
    _db_rules.indexes.add("SomeAction.some_action_package_id")
    _db_rules.foreign_keys.add("SomeAction.some_action_package_id")

    name: str
    docs: str
    file: str
    lineno: int
    input_schema: str
    output_schema: str


@dataclass
class SomeRun:
    id: int
    status: int

    some_action_id: int
    _db_rules.indexes.add("SomeRun.some_action_id")
    _db_rules.foreign_keys.add("SomeRun.some_action_id")

    start_time: str  # datetime iso format
    end_time: Optional[str]

    numbered_id: int
    _db_rules.unique_indexes.add("SomeRun.numbered_id")


def test_foreign_keys_validation(tmpdir) -> None:
    from robocorp.action_server._database import DBError

    db = Database(tmpdir / "test_foreign_keys_validation.db")
    with db.connect():
        db.initialize([SomeActionPackage, SomeAction])
        with db.transaction():
            db.create_tables(_db_rules)

        with db.transaction():
            with pytest.raises(DBError):
                db.insert(
                    SomeAction(1, 1, "action", "docs", "file", 22, "{}", "{}"),
                )

        with db.transaction():
            db.insert(SomeActionPackage(1, "action", ""))
            db.insert(
                SomeAction(1, 1, "action", "docs", "file", 22, "{}", "{}"),
            )


def test_database_schema_evolution(str_regression) -> None:
    from robocorp.action_server._models import get_all_model_classes, get_model_db_rules

    db = Database(":memory:")
    all_model_classes = get_all_model_classes()
    model_db_rules = get_model_db_rules()
    db.register_classes(all_model_classes)
    s = []
    for cls in all_model_classes:
        s.append(f"'''\n{db.create_table_sql(cls, model_db_rules).strip()}\n''',")
        s.extend(
            f"'''\n{x.strip()}\n''',"
            for x in db.create_indexes_sql(cls, model_db_rules)
        )

    new_lines = "\n\n\n"
    str_regression.check(
        f"IMPORTANT: If this file changes a new migration must be put in place!\n\n"
        f"[\n{new_lines.join(s)}\n]"
    )


def test_counters(tmpdir) -> None:
    from robocorp.action_server._database import DBError

    @dataclass
    class Counter:
        id: str
        value: int

    def _update_counter(db):
        with db.cursor() as cursor:
            db.execute_update_returning(
                cursor,
                "UPDATE counter SET value=value+1 WHERE id=? RETURNING value",
                ["foobar"],
            )
            return cursor.fetchall()[0][0]

    f = Path(str(tmpdir)) / "test_counters.db"

    def in_thread(
        ev: threading.Event,
        future1: futures.Future[int],
        future2: futures.Future[typing.Any],
    ):
        try:
            db = Database(f)
            with db.connect():
                with db.transaction():
                    future1.set_result(_update_counter(db))
                    ev.wait()
        except Exception as e:
            future2.set_exception(e)
        else:
            future2.set_result("worked")

    db = Database(f)
    with db.connect():
        db.initialize([Counter])

        with db.transaction():
            db.create_tables()
            db.insert(Counter("foobar", 1))

        with pytest.raises(RuntimeError):
            with db.transaction():
                assert _update_counter(db) == 2
                assert _update_counter(db) == 3
                raise RuntimeError("break")

        with pytest.raises(DBError):
            with db.transaction():
                # Rolled back, would start over...

                try:
                    ev = threading.Event()
                    future1: futures.Future[int] = futures.Future()
                    future2: futures.Future[typing.Any] = futures.Future()

                    # This will start a thread which will create a new connection
                    # which will create the transaction, update the counter and
                    # wait for the event to be released.
                    threading.Thread(
                        target=in_thread, args=(ev, future1, future2)
                    ).start()
                    assert future1.result() == 2

                    # This will not work because it can only work when
                    # the other transaction finishes (which won't because
                    # the transaction won't be closed until we release the
                    # event, so, we'll get a DBError here).
                    _update_counter(db)
                finally:
                    ev.set()

        assert future2.result() == "worked"
        assert db.first(Counter).value == 2


def test_migrate(database_v0: Path, tmpdir) -> None:
    from robocorp.action_server._models import create_db
    from robocorp.action_server.migrations import (
        MIGRATION_ID_TO_NAME,
        Migration,
        db_migration_pending,
        migrate_db,
    )

    base_path = tmpdir / "check.db"
    with create_db(base_path) as base_db:
        with base_db.connect():
            base_table_and_columns = base_db.list_table_and_columns()
            base_indexes = base_db.list_indexes()

    db_path = database_v0
    if db_migration_pending(db_path):
        assert migrate_db(db_path, 1)

    assert not db_migration_pending(db_path)
    db = Database(db_path)
    with db.connect():
        assert sorted(db.list_table_names()) == sorted(
            ["action", "action_package", "run", "migration", "counter"]
        )
        assert db.all(Migration) == [
            Migration(*x) for x in MIGRATION_ID_TO_NAME.items()
        ]

        assert base_table_and_columns == db.list_table_and_columns()
        assert base_indexes == db.list_indexes()


def test_database_create_table(str_regression) -> None:
    db = Database(":memory:")
    # path = tmpdir / "test.db"
    # print(path)
    # db = Database(path)

    db.register_classes([SomeActionPackage, SomeAction, SomeRun])

    sql = db.create_table_sql(SomeAction, _db_rules)
    str_regression.check(sql, basename="some_action")

    sql = db.create_table_sql(SomeRun, _db_rules)
    str_regression.check(sql, basename="some_run")

    with db.connect():
        # Note: in-memory, as soon as we close the connection, it's gone.
        db.initialize([SomeActionPackage, SomeAction, SomeRun])
        db.create_tables(_db_rules)

        assert set(db.list_table_names()) == set(
            ["some_action_package", "some_action", "some_run"]
        )


def test_database_insert():
    db = Database(":memory:")
    with db.connect():
        # Note: in-memory, as soon as we close the connection, it's gone.
        db.initialize([SomeActionPackage, SomeAction, SomeRun])
        db.create_tables(_db_rules)

        insert = [
            SomeActionPackage(1, "my_name", "conda contents"),
            SomeActionPackage(2, "my_name2", "conda contents2"),
        ]
        with db.transaction():
            for i in insert:
                db.insert(i)

        found = "\n".join(str(x) for x in db.all(SomeActionPackage))
        assert found == "\n".join(str(x) for x in insert)

        assert str(db.first(SomeActionPackage)) == str(insert[0])
        assert str(
            db.first(
                SomeActionPackage,
                "SELECT * FROM some_action_package WHERE name=?",
                [insert[0].name],
            )
        ) == str(insert[0])


def test_database_update():
    db = Database(":memory:")
    with db.connect():
        # Note: in-memory, as soon as we close the connection, it's gone.
        db.initialize([SomeActionPackage])
        db.create_tables(_db_rules)

        instance = SomeActionPackage(1, "my_name", "conda contents")
        with db.transaction():
            db.insert(instance)

        assert str(db.first(SomeActionPackage)) == str(instance)

        instance.name = "new_name"
        with db.transaction():
            db.update(instance, "name")
        assert db.first(SomeActionPackage).name == "new_name"


def test_database_datetime(str_regression):
    db = Database(":memory:")
    with db.connect():
        # Note: in-memory, as soon as we close the connection, it's gone.
        db.initialize([SomeActionPackage, SomeAction, SomeRun])
        db.create_tables(_db_rules)

        date = datetime.datetime(
            2023, 11, 22, 13, 50, 37, 457881, tzinfo=datetime.timezone.utc
        )

        insert = [
            SomeActionPackage(1, "my_name", "conda contents"),
            SomeAction(1, 1, "action", "docs", "file", 22, "{}", "{}"),
            SomeRun(1, 1, 1, datetime_to_str(date), None, 2),
        ]
        with db.transaction():
            for i in insert:
                db.insert(i)

        import json

        str_regression.check(json.dumps(db.list_whole_db(), indent=4))


def test_database_transactions():
    db = Database(":memory:")
    with db.connect():
        db.initialize([SomeActionPackage, SomeAction, SomeRun])
        db.create_tables(_db_rules)

        assert len(db.all(SomeActionPackage)) == 0

        with pytest.raises(Exception):
            with db.transaction():
                db.insert(SomeActionPackage(1, "foo", "foo"))
                raise Exception("err here, should not commit")

        assert len(db.all(SomeActionPackage)) == 0
        with db.transaction():
            db.insert(SomeActionPackage(1, "foo", "foo"))
        assert len(db.all(SomeActionPackage)) == 1


@dataclass
class SomeObject:
    id: int


def test_database_limit_offset():
    db = Database(":memory:")
    with db.connect():
        db.initialize([SomeObject])
        db.create_tables(_db_rules)

        with db.transaction():
            for i in range(5):
                db.insert(SomeObject(id=i))

        assert len(db.all(SomeObject)) == 5
        assert [x.id for x in db.all(SomeObject, limit=3)] == list(range(3))
        assert [x.id for x in db.all(SomeObject, limit=3, offset=2)] == list(
            range(2, 5)
        )


def test_database_transactions_nested():
    db = Database(":memory:")
    with db.connect():
        db.initialize([SomeActionPackage, SomeAction, SomeRun])
        db.create_tables(_db_rules)

        assert len(db.all(SomeActionPackage)) == 0

        with db.transaction():
            try:
                with db.transaction():
                    db.insert(SomeActionPackage(1, "foo", "foo"))
                    raise Exception("err here, should not commit")
            except Exception:
                pass
            db.insert(SomeActionPackage(2, "bar", "bar"))

        assert str(db.all(SomeActionPackage)) == str(
            [SomeActionPackage(2, "bar", "bar")]
        )
