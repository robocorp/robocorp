<!-- markdownlint-disable -->

# API Overview

## Modules

- [`robocorp.action_server`](./robocorp.action_server.md#module-robocorpaction_server)
- [`robocorp.action_server.cli`](./robocorp.action_server.cli.md#module-robocorpaction_servercli)
- [`robocorp.action_server.migrations`](./robocorp.action_server.migrations.md#module-robocorpaction_servermigrations): The way that migrations work is the following:
- [`robocorp.action_server.migrations.migration_add_action_enabled`](./robocorp.action_server.migrations.migration_add_action_enabled.md#module-robocorpaction_servermigrationsmigration_add_action_enabled)
- [`robocorp.action_server.migrations.migration_add_is_consequential`](./robocorp.action_server.migrations.migration_add_is_consequential.md#module-robocorpaction_servermigrationsmigration_add_is_consequential)
- [`robocorp.action_server.migrations.migration_initial`](./robocorp.action_server.migrations.migration_initial.md#module-robocorpaction_servermigrationsmigration_initial)

## Classes

- [`migrations.Migration`](./robocorp.action_server.migrations.md#class-migration): Migration(id: int, name: str)

## Functions

- [`cli.main`](./robocorp.action_server.cli.md#function-main)
- [`cli.str2bool`](./robocorp.action_server.cli.md#function-str2bool)
- [`migrations.db_migration_pending`](./robocorp.action_server.migrations.md#function-db_migration_pending)
- [`migrations.migrate_db`](./robocorp.action_server.migrations.md#function-migrate_db): Returns true if the migration worked properly or if the migration was not needed
- [`migration_add_action_enabled.migrate`](./robocorp.action_server.migrations.migration_add_action_enabled.md#function-migrate)
- [`migration_add_is_consequential.migrate`](./robocorp.action_server.migrations.migration_add_is_consequential.md#function-migrate)
- [`migration_initial.migrate`](./robocorp.action_server.migrations.migration_initial.md#function-migrate)
