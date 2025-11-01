# Adapter configuration

Robocorp Work Items supports multiple adapters that determine how queues are
implemented when Control Room is not available. This guide explains how to
select an adapter, install its optional dependencies, and configure the
required environment variables.

> **Tip:** When running inside Control Room you normally do **not** need to
> set a custom adapter. The default `RobocorpAdapter` is selected
> automatically.

## Selecting an adapter

Adapters are selected with the `RC_WORKITEM_ADAPTER` environment variable. The
value can be a fully qualified class name or one of the built-in aliases listed
below.

| Alias | Adapter class | Description |
|-------|---------------|-------------|
| `file` (default) | `robocorp.workitems._adapters._file.FileAdapter` | Stores work items as JSON files on disk. Useful for quick local experiments. |
| `sqlite` | `robocorp.workitems._adapters._sqlite.SQLiteAdapter` | Uses SQLite for durable storage on a single machine. |
| `redis` | `robocorp.workitems._adapters._redis.RedisAdapter` | Backed by Redis, suitable for lightweight distributed workers. |
| `docdb` | `robocorp.workitems._adapters._docdb.DocumentDBAdapter` | Uses MongoDB/DocumentDB for document-oriented storage. |

```bash
# Example: pick the SQLite adapter
export RC_WORKITEM_ADAPTER=sqlite
```

You can still point to the full class path if necessary:

```bash
export RC_WORKITEM_ADAPTER="robocorp.workitems._adapters._sqlite.SQLiteAdapter"
```

## Common configuration

All adapters understand the following environment variables:

| Variable | Purpose | Default |
|----------|---------|---------|
| `RC_WORKITEM_QUEUE_NAME` | Name of the queue to read from / write to. | `default` |
| `RC_WORKITEM_FILES_DIR` | Directory used for persistent file attachments (when applicable). | `devdata/work_item_files` |

## File adapter

The file adapter remains available for backwards compatibility. It mirrors the
queue using two JSON files:

```bash
export RC_WORKITEM_ADAPTER=file
export RC_WORKITEM_INPUT_PATH=/path/to/input.json
export RC_WORKITEM_OUTPUT_PATH=/path/to/output.json
```

## SQLite adapter

The SQLite adapter requires no extra dependencies beyond Python's standard
library.

```bash
export RC_WORKITEM_ADAPTER=sqlite
export RC_WORKITEM_DB_PATH=/var/tmp/workitems.db
export RC_WORKITEM_QUEUE_NAME=invoices
```

### Features

- FIFO ordering backed by SQL queries.
- Automatic schema migrations and connection pooling.
- Inline storage for small file attachments.
- Helper method `seed_input()` for testing.

## Redis adapter

Install the optional dependency and then configure the connection string. The
adapter understands the same environment variables as the Control Room client
(`REDIS_HOST`, `REDIS_PORT`, etc.).

```bash
pip install "robocorp-workitems[redis]"

export RC_WORKITEM_ADAPTER=redis
export RC_REDIS_URL=redis://localhost:6379/0
export RC_WORKITEM_QUEUE_NAME=test_queue
```

### Features

- Atomic reservations using Redis primitives.
- Payload and metadata stored in Redis hashes.
- Optional TTL-based cleanup for orphaned work items.

## DocumentDB / MongoDB adapter

Install the extras and point to your MongoDB or AWS DocumentDB instance.

```bash
pip install "robocorp-workitems[docdb]"

export RC_WORKITEM_ADAPTER=docdb
export DOCDB_URI=mongodb://user:pass@host:27017
export DOCDB_DATABASE=automation
export RC_WORKITEM_QUEUE_NAME=documents
```

### Features

- Uses MongoDB's `findOneAndUpdate` for atomic reservations.
- Stores large attachments in GridFS; small files are persisted inline.
- Includes orphan recovery logic for long-running reservations.

## Local testing

Integration tests that exercise Redis and MongoDB are tagged with the
`redis`, `docdb`, and `integration` pytest markers. They are skipped
automatically when the required services are unavailable. To run them locally
start Redis and MongoDB (Docker Compose works well), then execute:

```bash
inv test -t tests/workitems_tests/test_adapters.py -m "redis or docdb"
```

For GitHub Actions the workflow spins up service containers automatically.
When running locally with [`act`](https://github.com/nektos/act), ensure that
your Docker daemon can pull the `redis:alpine` and `mongo:7` images.
