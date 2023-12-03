"""
The way that migrations work is the following:

We have a table with the id and name of each migration applied.

When starting up we connect to the db and see the current version.
Then, we apply each pending migration since the last version.
"""

import logging
import typing
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Union

log = logging.getLogger(__name__)

if typing.TYPE_CHECKING:
    from robocorp.action_server._database import Database

MIGRATION_ID_TO_NAME: Dict[int, str] = {
    1: "initial"  # we'll look for a 'migration_initial' module based on this.
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


def migrate_db(db_path: Union[Path, str], to_version=CURRENT_VERSION) -> bool:
    """
    Returns true if the migration worked properly or if the migration was not needed
    and false if the migration could not be done for some reason.
    """

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
            db.initialize([Migration] + get_all_model_classes())
            migrations = db.all(Migration)
            if not migrations:
                # Ok, we just initialized (or this was a *REALLY* old version before
                # migrations were in place).
                db_migration_version = 0

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
    db.initialize([Migration])
    migrations = db.all(Migration)
    if not migrations:
        # Ok, we just initialized (or this was a *REALLY* old version before
        # migrations were in place).
        return True

    latest_migration_applied = max(x.id for x in migrations)

    if latest_migration_applied == CURRENT_VERSION:
        return False

    return True


def create_db(db_path: Union[Path, str]) -> None:
    from robocorp.action_server._database import Database
    from robocorp.action_server._models import get_all_model_classes

    db = Database(db_path)
    with db.connect():
        db.initialize([Migration] + get_all_model_classes())
        current_migration = MIGRATION_ID_TO_NAME[CURRENT_VERSION]
        with db.transaction():
            db.insert(Migration(CURRENT_VERSION, current_migration))


def db_migration_pending(db_path: Union[Path, str]) -> bool:
    from robocorp.action_server._database import Database

    path = Path(db_path)
    if not path.exists():
        return False

    # Ok, it already exists. Check if it's pending a migration.
    db = Database(db_path)
    with db.connect():
        return _db_migration_pending(db)
