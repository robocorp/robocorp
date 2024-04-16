"""
The way that migrations work is the following:

We have a table with the id and name of each migration applied.

When starting up we connect to the db and see the current version.
Then, we apply each pending migration since the last version.
"""

import logging
import os.path
import typing
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Optional, Union

log = logging.getLogger(__name__)

if typing.TYPE_CHECKING:
    from robocorp.action_server._database import Database

MIGRATION_ID_TO_NAME: Dict[int, str] = {
    # we'll look for a 'migration_initial' module based on this.
    1: "initial",
    # we'll look for a 'migration_add_action_enabled' module based on this.
    2: "add_action_enabled",
    # we'll look for a 'migration_add_is_consequential' module based on this.
    3: "add_is_consequential",
    # we'll look for a 'migration_add_action_managed_params' module based on this.
    4: "add_action_managed_params",
}

CURRENT_VERSION: int = max(MIGRATION_ID_TO_NAME.keys())


@dataclass
class Migration:
    id: int  # Migration id
    name: str  # Migration name


def _migrate_to(db: "Database", db_migration_version: int) -> None:
    from importlib import import_module

    name = MIGRATION_ID_TO_NAME[db_migration_version]
    mod = import_module(f"robocorp.action_server.migrations.migration_{name}")
    mod.migrate(db)


def migrate_db(
    db_path: Union[Path, str],
    to_version=CURRENT_VERSION,
    database: Optional["Database"] = None,
) -> bool:
    """
    Returns true if the migration worked properly or if the migration was not needed
    and false if the migration could not be done for some reason.

    :param database: Expected to be passed when dealing with an in-memory database.
    """
    assert os.path.exists(db_path), f"Unable to do migration. {db_path} does not exist."

    if not db_migration_pending(db_path):
        return True  # It's already correct

    import shutil
    import time

    path = Path(db_path)
    # Ok, we need to do a migration. The first thing is creating a backup,
    # just in case something goes bad.
    parent_dir = path.parent
    name = path.name
    log.info("Preparing to migrate database at: %s", db_path)
    backup_file = parent_dir / f"{name}-pre-migration-{to_version}-{time.time()}.bak"
    log.info("Creating backup at: %s", backup_file)

    shutil.copyfile(path, backup_file)

    from robocorp.action_server._database import Database
    from robocorp.action_server._models import get_all_model_classes

    db = Database(db_path)
    with db.connect():
        with db.transaction():
            db.initialize(get_all_model_classes())
            if "migration" not in db.list_table_names():
                raise RuntimeError(
                    f"""Error: 
It seems that this version of the database ({db.db_path}) is too old.
Please erase it and recreate it from scratch."""
                )
            else:
                migrations = db.all(Migration)
                if not migrations:
                    raise RuntimeError(
                        f"""Error: 
It seems that this version of the database ({db.db_path}) is too old.
Please erase it and recreate it from scratch."""
                    )

                else:
                    db_migration_version = max(x.id for x in migrations)

            while db_migration_version < to_version:
                db_migration_version += 1
                log.info(
                    "Will migrate to version: %s (%s)",
                    db_migration_version,
                    MIGRATION_ID_TO_NAME[db_migration_version],
                )
                _migrate_to(db, db_migration_version)

    return True


def _db_migration_pending(db: "Database") -> bool:
    if "migration" not in db.list_table_names():
        return True

    db.initialize([Migration])
    migrations = db.all(Migration)
    if not migrations:
        # No migrations applied, do it now.
        return True

    latest_migration_applied = max(x.id for x in migrations)

    if latest_migration_applied == CURRENT_VERSION:
        return False

    return True


def db_migration_pending(db_path: Union[Path, str]) -> bool:
    from robocorp.action_server._database import Database

    if db_path == ":memory:":
        raise RuntimeError("Migration support not available for in-memory database.")

    path = Path(db_path)
    if not path.exists():
        raise RuntimeError(
            f"Unable to check if migration is pending because file: {db_path} does not exist."
        )

    # Ok, it already exists. Check if it's pending a migration.
    db = Database(db_path)
    with db.connect():
        return _db_migration_pending(db)
