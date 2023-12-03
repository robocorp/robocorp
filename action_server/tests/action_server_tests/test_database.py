import datetime
from pathlib import Path
from typing import Optional

import pytest
from pydantic.dataclasses import dataclass

from robocorp.action_server._database import Database, datetime_to_str


@dataclass
class SomeActionPackage:
    id: int
    name: str
    condayaml: str


@dataclass
class SomeAction:
    id: int
    some_action_package_id: int
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
    start_time: str  # datetime iso format
    end_time: Optional[str]


def test_database_schema_evolution(str_regression) -> None:
    from robocorp.action_server._models import get_all_model_classes

    db = Database(":memory:")
    all_model_classes = get_all_model_classes()
    db.register_classes(all_model_classes)
    s = ["IMPORTANT: If this file changes a new migration must be put in place!"]
    for cls in all_model_classes:
        s.append(db.create_table_sql(cls))

    str_regression.check("\n\n".join(s))


def test_migrate(database_v0: Path) -> None:
    from robocorp.action_server.migrations import (
        MIGRATION_ID_TO_NAME,
        Migration,
        db_migration_pending,
        migrate_db,
    )

    db_path = database_v0
    assert db_migration_pending(db_path)
    assert migrate_db(db_path, 1)
    assert not db_migration_pending(db_path)
    db = Database(db_path)
    with db.connect():
        assert sorted(db.list_table_names()) == sorted(
            ["action", "action_package", "run", "migration"]
        )
        assert db.all(Migration) == [
            Migration(*x) for x in MIGRATION_ID_TO_NAME.items()
        ]


def test_database_create_table(str_regression) -> None:
    db = Database(":memory:")
    # path = tmpdir / "test.db"
    # print(path)
    # db = Database(path)

    db.register_classes([SomeActionPackage, SomeAction, SomeRun])

    sql = db.create_table_sql(SomeAction)
    str_regression.check(sql, basename="some_action")

    sql = db.create_table_sql(SomeRun)
    str_regression.check(sql, basename="some_run")

    with db.connect():
        # Note: in-memory, as soon as we close the connection, it's gone.
        db.initialize([SomeActionPackage, SomeAction, SomeRun])

        assert set(db.list_table_names()) == set(
            ["some_action_package", "some_action", "some_run"]
        )


def test_database_insert():
    db = Database(":memory:")
    with db.connect():
        # Note: in-memory, as soon as we close the connection, it's gone.
        db.initialize([SomeActionPackage, SomeAction, SomeRun])

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
        date = datetime.datetime(
            2023, 11, 22, 13, 50, 37, 457881, tzinfo=datetime.timezone.utc
        )

        insert = [
            SomeActionPackage(1, "my_name", "conda contents"),
            SomeAction(1, 1, "action", "docs", "file", 22, "{}", "{}"),
            SomeRun(1, 1, 1, datetime_to_str(date), None),
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
