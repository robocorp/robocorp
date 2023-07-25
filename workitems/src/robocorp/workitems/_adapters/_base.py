from abc import ABC, abstractmethod
from typing import Optional

from robocorp.workitems._types import State
from robocorp.workitems._utils import JSONType


class BaseAdapter(ABC):
    """Abstract base class for work item adapters.

    lazydocs: ignore
    """

    @abstractmethod
    def reserve_input(self) -> str:
        """Get next work item ID from the input queue and reserve it."""
        raise NotImplementedError

    @abstractmethod
    def release_input(
        self, item_id: str, state: State, exception: Optional[dict] = None
    ):
        """Release the lastly retrieved input work item and set state."""
        raise NotImplementedError

    @abstractmethod
    def create_output(self, parent_id: str, payload: Optional[JSONType] = None) -> str:
        """Create new output for work item, and return created ID."""
        raise NotImplementedError

    @abstractmethod
    def load_payload(self, item_id: str) -> JSONType:
        """Load JSON payload from work item."""
        raise NotImplementedError

    @abstractmethod
    def save_payload(self, item_id: str, payload: JSONType):
        """Save JSON payload to work item."""
        raise NotImplementedError

    @abstractmethod
    def list_files(self, item_id: str) -> list[str]:
        """List attached files in work item."""
        raise NotImplementedError

    @abstractmethod
    def get_file(self, item_id: str, name: str) -> bytes:
        """Read file's contents from work item."""
        raise NotImplementedError

    @abstractmethod
    def add_file(self, item_id: str, name: str, content: bytes):
        """Attach file to work item."""
        raise NotImplementedError

    @abstractmethod
    def remove_file(self, item_id: str, name: str):
        """Remove attached file from work item."""
        raise NotImplementedError
