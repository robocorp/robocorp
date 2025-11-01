# robocorp-workitems

Work items are used in Robocorp Control Room for managing data that go through multiple steps and tasks inside a process. Each step of a process receives input work items from the previous step, and creates output work items for the next step.

## Getting started

The library exposes two objects, `inputs` and `outputs`, which are the main way to interact with work item queues. The former deals with the reading input work items, and the latter with creating output work items.

A run inside Control Room will always have at least one work item available to it. The simplest Robot which reads the current work item and creates an output can be done in the following manner:

```python
from robocorp import workitems
from robocorp.tasks import task

@task
def handle_item():
    item = workitems.inputs.current
    print("Received payload:", item.payload)
    workitems.outputs.create(payload={"key": "value"})
```

Iterating over all available input items in the queue is also easy:

```python
from robocorp import workitems
from robocorp.tasks import task

@task
def handle_all_items():
    for item in workitems.inputs:
        print("Received payload:", item.payload)
        workitems.outputs.create(payload={"key": "value"})
```

### Work item structure

A work item's data payload is JSON and allows storing anything that is JSON serializable. By default, the payload is a mapping of key-value pairs.

In addition to the payload section, a work item can also contain files, which are stored within Robocorp Control Room. Adding and using files with work items requires no additional setup from the user.

## Adapters

The library ships with multiple adapters that implement the Control Room work
item interface:

- `FileAdapter` – handles file-based work item data, mirroring queue
    operations with local JSON files when Control Room services are absent.
- `RobocorpAdapter` – integrates directly with Robocorp Control Room APIs for
    production runs inside the SaaS environment.

### Community adapters (opt-in)

For self-hosted, on-premise, or air-gapped deployments the library provides
optional community-maintained adapters. Control Room remains the recommended
hosted solution, but these adapters enable work item processing when Control
Room access is not available.

#### Adapters

- `SQLiteAdapter` – single-machine development and testing. Built-in with no
    extra dependencies.
- `RedisAdapter` – high-throughput queues that span multiple workers. Install
    with `pip install "robocorp-workitems[redis]"`.
- `DocumentDBAdapter` – MongoDB/DocumentDB clusters for document-oriented
    storage. Install with `pip install "robocorp-workitems[docdb]"`.

Install all adapters at once with `pip install "robocorp-workitems[all]"`.

#### Configuration

Select adapters via the `RC_WORKITEM_ADAPTER` environment variable. Aliases
such as `sqlite`, `redis`, and `docdb` are recognised in addition to the fully
qualified class names.

```bash
# SQLite (no extra dependencies required)
export RC_WORKITEM_ADAPTER=sqlite
export RC_WORKITEM_DB_PATH=/path/to/workitems.db

# Redis
export RC_WORKITEM_ADAPTER=redis
export REDIS_HOST=localhost
export REDIS_PORT=6379

# DocumentDB/MongoDB
export RC_WORKITEM_ADAPTER=docdb
export DOCDB_URI=mongodb://localhost:27017
export DOCDB_DATABASE=workitems
```

#### Examples

##### SQLite adapter (local development)

```python
import os
from robocorp import workitems
from robocorp.tasks import task

os.environ["RC_WORKITEM_ADAPTER"] = "sqlite"
os.environ["RC_WORKITEM_DB_PATH"] = "./workitems.db"
os.environ["RC_WORKITEM_QUEUE_NAME"] = "invoices"

@task
def process_invoices():
    for item in workitems.inputs:
        invoice_data = item.payload
        # Process invoice...
        workitems.outputs.create(payload={"status": "processed"})
        item.done()
```

##### Redis adapter (distributed processing)

```python
import os
from robocorp import workitems
from robocorp.tasks import task

os.environ["RC_WORKITEM_ADAPTER"] = "redis"
os.environ["REDIS_HOST"] = "redis.example.com"
os.environ["REDIS_PORT"] = "6379"
os.environ["RC_WORKITEM_QUEUE_NAME"] = "orders"

@task
def process_orders():
    for item in workitems.inputs:
        order = item.payload
        # Process order across multiple workers...
        workitems.outputs.create(payload={"order_id": order["id"]})
        item.done()
```

##### DocumentDB adapter (MongoDB clusters)

```python
import os
from robocorp import workitems
from robocorp.tasks import task

os.environ["RC_WORKITEM_ADAPTER"] = "docdb"
os.environ["DOCDB_URI"] = "mongodb://user:pass@docdb.example.com:27017"
os.environ["DOCDB_DATABASE"] = "automation"
os.environ["RC_WORKITEM_QUEUE_NAME"] = "documents"

@task
def process_documents():
    for item in workitems.inputs:
        doc = item.payload
        # Process document...
        workitems.outputs.create(payload={"doc_id": doc["id"]})
        item.done()
```

#### When to use community adapters

- Self-hosted or on-premise automation infrastructure
- Air-gapped environments without cloud access
- Development and testing without Control Room
- Cost-sensitive high-volume processing
- Integration with existing Redis or MongoDB infrastructure

#### Production considerations

- Control Room provides managed orchestration, monitoring, and error handling
- Community adapters require self-managed infrastructure and monitoring
- Test thoroughly with your specific deployment configuration
- See [Adapter Configuration Guide](https://github.com/robocorp/robocorp/blob/master/workitems/docs/guides/07-adapter-configuration.md) for detailed setup

## Guides

- [Reserving and releasing input items](https://github.com/robocorp/robocorp/blob/master/workitems/docs/guides/00-reserving-inputs.md)
- [Creating outputs](https://github.com/robocorp/robocorp/blob/master/workitems/docs/guides/01-creating-outputs.md)
- [Local development](https://github.com/robocorp/robocorp/blob/master/workitems/docs/guides/02-local-development.md)
- [Email triggering](https://github.com/robocorp/robocorp/blob/master/workitems/docs/guides/03-email-triggering.md)
- [Collecting all inputs](https://github.com/robocorp/robocorp/blob/master/workitems/docs/guides/04-collecting-inputs.md)
- [Flow control with exceptions](https://github.com/robocorp/robocorp/blob/master/workitems/docs/guides/05-input-exceptions.md)
- [Modifying inputs](https://github.com/robocorp/robocorp/blob/master/workitems/docs/guides/06-modifying-inputs.md)

Further user guides and tutorials can be found in [Robocorp Docs](https://robocorp.com/docs).

## API Reference

Explore our [API](https://github.com/robocorp/robocorp/blob/master/workitems/docs/api/README.md) for extensive documentation.

## Changelog

A list of releases and corresponding changes can be found in the [changelog](https://github.com/robocorp/robocorp/blob/master/workitems/docs/CHANGELOG.md).
