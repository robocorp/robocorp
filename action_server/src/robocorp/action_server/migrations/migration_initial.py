from robocorp.action_server._database import Database


def migrate(db: Database) -> None:
    raise RuntimeError(
        f"""Error: 
It seems that this version of the database ({db.db_path}) is too old.
Please erase it and recreate it from scratch."""
    )
