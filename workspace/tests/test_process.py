import pytest

from robocorp.workspace import process


@pytest.mark.xfail(reason="not ready for CI yet (Control Room injected env vars)")
class ProcessApi:
    """Tests the Process API library wrapper."""

    def test_list_processes(self):
        print(process.list_processes())
