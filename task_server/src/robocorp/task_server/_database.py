# Keep SQL statements formatting as-is
# fmt: off
import datetime
import logging
import sqlite3
from contextlib import closing, contextmanager
from functools import cache
from pathlib import Path
from typing import Generator

from ._models import Run, Task
from ._settings import get_settings

LOGGER = logging.getLogger(__name__)


def _convert_datetime(val):
    return datetime.datetime.fromisoformat(val.decode())


@cache
def get_path() -> Path:
    settings = get_settings()
    path = settings.metadata / "server.db"
    path.parent.mkdir(exist_ok=True, parents=True)
    return path


@contextmanager
def connection() -> Generator[sqlite3.Connection, None, None]:
    path = get_path()
    sqlite3.register_converter("datetime", _convert_datetime)

    with closing(sqlite3.connect(path)) as conn:
        with conn:
            yield conn


@contextmanager
def cursor() -> Generator[tuple[sqlite3.Connection, sqlite3.Cursor], None, None]:
    with connection() as conn:
        with closing(conn.cursor()) as cur:
            yield conn, cur


def ensure_tables() -> None:
    LOGGER.info("Initializing database [path='%s']", get_path())

    with connection() as conn:
        conn.execute("PRAGMA foreign_keys = ON")

    with cursor() as (_, cur):
        cur.execute("""
        CREATE TABLE IF NOT EXISTS tasks (
            task_id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            docs TEXT NOT NULL,
            file TEXT NOT NULL,
            lineno INTEGER NOT NULL,
            input_schema TEXT NOT NULL,
            output_schema TEXT NOT NULL,
            enabled INTEGER CHECK(enabled IN (0, 1)))
        """)

        cur.execute("""
        CREATE TABLE IF NOT EXISTS runs (
            run_id TEXT PRIMARY KEY,
            task_id TEXT NOT NULL,
            state TEXT NOT NULL,
            start_time DATETIME NOT NULL,
            end_time DATETIME,
            FOREIGN KEY (task_id) REFERENCES tasks(task_id))
        """)


def list_tasks() -> list[Task]:
    with cursor() as (_, cur):
        cur.execute("""SELECT * FROM tasks""")
        rows = cur.fetchall()

    return [Task.from_row(row) for row in rows]


def update_tasks(tasks: list[Task]) -> None:
    LOGGER.info(
        "Updating tasks entries [names=%s]",
        ", ".join(f"'{task.name}'" for task in tasks)
    )

    with cursor() as (conn, cur):
        cur.execute("""
        UPDATE tasks
        SET enabled = 0
        """)

        # TODO: Should the tasks table be all parsed instances of tasks,
        #  so that we also store the schema history, etc. for a given task,
        #  with some value indicating which is the current
        cur.executemany("""
        INSERT INTO tasks
            (task_id, name, docs, file, lineno, input_schema, output_schema, enabled)
        VALUES
            (?, ?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(task_id) DO UPDATE
        SET
            name = excluded.name,
            docs = excluded.docs,
            file = excluded.file,
            lineno = excluded.lineno,
            input_schema = excluded.input_schema,
            output_schema = excluded.output_schema,
            enabled = excluded.enabled
        """, [task.to_row() for task in tasks])

        conn.commit()


def list_runs() -> list[Run]:
    with cursor() as (_, cur):
        cur.execute("""SELECT * FROM runs""")
        rows = cur.fetchall()

    return [Run.from_row(row) for row in rows]


def start_run(run: Run) -> None:
    with cursor() as (conn, cur):
        cur.execute("""
        INSERT INTO runs
            (run_id, task_id, state, start_time, end_time)
        VALUES
            (?, ?, ?, ?, ?)
        """, run.to_row())
        conn.commit()


def end_run(run: Run) -> None:
    with cursor() as (conn, cur):
        cur.execute("""
        UPDATE runs
        SET
            state = ?,
            end_time = ?
        WHERE
            run_id = ?
        """, (run.state, run.end_time, run.run_id))
        conn.commit()
