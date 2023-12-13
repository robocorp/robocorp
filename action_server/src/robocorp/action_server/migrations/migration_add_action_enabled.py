from robocorp.action_server._database import Database
from robocorp.action_server.migrations import Migration


def migrate(db: Database) -> None:
    from robocorp.action_server.migrations import MIGRATION_ID_TO_NAME

    db.execute(
        """
ALTER TABLE action 
ADD COLUMN enabled INTEGER CHECK(enabled IN (0, 1)) NOT NULL DEFAULT 1;
"""
    )

    db.insert(Migration(id=2, name=MIGRATION_ID_TO_NAME[2]))
