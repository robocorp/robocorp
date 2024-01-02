from robocorp.action_server._database import Database
from robocorp.action_server.migrations import Migration


def migrate(db: Database) -> None:
    from robocorp.action_server.migrations import MIGRATION_ID_TO_NAME

    db.execute(
        """
ALTER TABLE action
ADD COLUMN is_consequential INTEGER;
"""
    )

    db.insert(Migration(id=3, name=MIGRATION_ID_TO_NAME[3]))
