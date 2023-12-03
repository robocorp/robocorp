from robocorp.action_server._database import Database


def migrate(db: Database):
    # For the first migration we don't really do anything, we just add the
    # migration column.
    # Tables were already created automatically when we initialized and
    # no table changes are needed.
    from robocorp.action_server.migrations import MIGRATION_ID_TO_NAME, Migration

    name = MIGRATION_ID_TO_NAME[1]
    db.insert(Migration(1, name))
