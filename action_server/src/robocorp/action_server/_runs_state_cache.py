"""
Note: this is easy while we're in a single process!

If we ever change the design to support multiple processes we'd need to have a
way to synchronize state across multiple processes.
"""
import threading
import typing
from contextlib import contextmanager
from dataclasses import asdict, dataclass
from typing import Any, Dict, Literal, Optional

if typing.TYPE_CHECKING:
    from ._database import Database
    from ._models import Run


@dataclass(slots=True)
class RunChangeEvent:
    ev: Literal["added", "changed"]
    run: "Run"
    changes: Optional[dict[str, Any]] = None


class RunsState:
    def __init__(self, db: "Database"):
        from ._models import Run

        # Clients that want to register/unregister must use this semaphore
        # to avoid racing conditions.
        #
        # This is done because the expected scenario is the following:
        # 1. The client acquires this semaphore
        # 2. then notifies about existing
        # 3. then registers so that it knows about new runs in the structure
        #
        # In this case, if the client doesn't hold the semaphore himself we
        # could have a racing condition.
        #
        # We could make it an RLock, but then we'd need a wrapper to do the
        # verification on whether it's acquired, so, we use a Semaphore to
        # use the `_value` to do the needed asserts.
        self.semaphore = threading.Semaphore(1)

        # Use dict keys for uniqueness and ordering.
        self._run_listeners: Dict[Any, int] = {}

        # This is an in-memory view of the runs available to be seen by clients.
        # Older runs are in the db, but we don't provide them for the time being.

        # Note: we limit to the latest 200 Runs for now...
        # could be tweaked in the future.
        run_id_to_run = {}
        # order by is important so that we get the latest ones.
        for run in db.all(Run, offset=0, limit=200, order_by="numbered_id DESC"):
            run_id_to_run[run.id] = run

        self._run_id_to_run = run_id_to_run

    def get_current_run_state(self) -> list["Run"]:
        assert (
            self.semaphore._value == 0
        ), "Clients getting the current run state must acquire the semaphore."
        return list(self._run_id_to_run.values())

    def get_run_from_id(self, run_id) -> "Run":
        assert (
            self.semaphore._value == 0
        ), "Clients getting the current run state must acquire the semaphore."
        return self._run_id_to_run[run_id]

    def register(self, listener):
        assert (
            self.semaphore._value == 0
        ), "Clients registering must acquire the semaphore."
        self._run_listeners[listener] = 1

    def unregister(self, listener):
        assert (
            self.semaphore._value == 0
        ), "Clients unregistering must acquire the semaphore."
        self._run_listeners.pop(listener, None)

    def on_run_inserted(self, run: "Run"):
        # Semaphore is acquired internally in this case.
        from ._models import Run

        run_copy = Run(**asdict(run))
        with self.semaphore:
            self._run_id_to_run[run_copy.id] = run_copy
            for listener in self._run_listeners.keys():
                listener(RunChangeEvent("added", run_copy))

    def on_run_changed(self, run: "Run", changes: Dict[str, Any]):
        # Semaphore is acquired internally in this case.
        from ._models import Run

        run_copy = Run(**asdict(run))

        with self.semaphore:
            self._run_id_to_run[run_copy.id] = run_copy
            for listener in self._run_listeners.keys():
                listener(RunChangeEvent("changed", run_copy, changes))


_runs_state: Optional[RunsState] = None


@contextmanager
def use_runs_state_ctx(db: "Database"):
    global _runs_state
    _runs_state = RunsState(db)
    try:
        yield _runs_state
    finally:
        pass
    _runs_state = None


def get_global_runs_state() -> RunsState:
    assert _runs_state
    return _runs_state
