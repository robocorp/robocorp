# Changelog

## Unreleased

### Added

- Community adapters (opt-in) for self-hosted and on-premise deployments:
  - `SQLiteAdapter` – lightweight database storage for single-machine development and testing (no external dependencies)
  - `RedisAdapter` – high-throughput distributed queues backed by Redis (`pip install "robocorp-workitems[redis]"`)
  - `DocumentDBAdapter` – MongoDB/DocumentDB storage (`pip install "robocorp-workitems[docdb]"`)
- Adapter aliases for `RC_WORKITEM_ADAPTER`: `sqlite`, `redis`, and `docdb`
- Optional extras to install dependencies:
  - `pip install "robocorp-workitems[redis]"`
  - `pip install "robocorp-workitems[docdb]"`
  - `pip install "robocorp-workitems[all]"`
- `seed_input()` helper method on adapters for testing and development workflows
- Integration tests with Docker-based Redis and MongoDB services (`@pytest.mark.redis`, `@pytest.mark.docdb`)
- Documentation updates:
  - Community adapters section in the main README with installation guidance
  - Adapter Configuration Guide (`docs/guides/07-adapter-configuration.md`)
  - API entries for each adapter

### Features by adapter

#### SQLiteAdapter

- FIFO queue ordering with automatic schema migrations
- Thread-safe connection pooling
- Orphaned work item recovery
- Inline file storage
- No external dependencies

#### RedisAdapter

- Atomic `RPOPLPUSH`-based work item reservations
- Connection pooling for high concurrency
- Hybrid file storage (inline for small files, filesystem for large files)
- Namespace isolation for multiple queues
- TTL-based cleanup

#### DocumentDBAdapter

- GridFS integration for large file attachments (>1 MB)
- AWS DocumentDB TLS/SSL support
- Replica-set compatible queries
- TTL indexes for automatic cleanup
- Atomic `find_one_and_update` operations

### Non-breaking changes

- Existing `FileAdapter` and `RobocorpAdapter` behaviour is unchanged
- New adapters are opt-in via extras installation
- No impact on Control Room integration or production workflows
- Adapter selection logic remains backwards compatible

### Testing

- More than 100 new integration tests covering adapter operations
- Docker Compose setup for local integration testing
- GitHub Actions workflow with Redis and MongoDB service containers
- Pytest markers to skip tests when services are unavailable

### Use cases

Community adapters enable:

- Self-hosted or on-premise automation infrastructure
- Air-gapped environments without cloud connectivity
- Cost-sensitive high-volume processing
- Development and testing without Control Room access
- Integration with existing Redis or MongoDB infrastructure

Control Room remains the recommended option for hosted orchestration, monitoring, and production-grade error handling.

## 1.4.7 - 2025-04-22

- Bump to accept robocorp-tasks < 5.

## 1.4.6 - 2024-09-25

- bump certifi to 2024.8.30

## 1.4.5 - 2024-04-08

- Update package's main README.

## 1.4.4 - 2024-03-19

- Enables compatibility with Action Server `0.1.0` by accepting **robocorp-tasks**
  `3.x.x`.
- Outputs creation supports Path-like objects for the file parameters.

## 1.4.3 - 2024-02-07

- Support for retrieving the error through the `exception` property of a failed input
  work item.

## 1.4.2 - 2024-01-14

- Fix main README and update docs.

## 1.4.1 - 2023-11-09

- Upgrades `dataclasses-json` dependency to at least **0.6.1**.
- Prevent invalid operations on released work items with `FileAdapter`.

## 1.4.0 - 2023-09-07

- Add support for `RC_DISABLE_SSL`.

## 1.3.2 - 2023-08-24

- Handle exceptions derived from `BusinessException` or `ApplicationException`.

## 1.3.1 - 2023-08-22

- Create missing parent folders when testing in VSCode.

## 1.3.0 - 2023-07-31

- Improve development workflow with better error messages and more lenient defaults.
- Allow mutating input work items.

## 1.2.1 - 2023-06-28

- Updated dependency on `robocorp-tasks` to `>=1,<3`.
