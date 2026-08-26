import pytest

from robocorp.workspace import process


# @pytest.mark.xfail(reason="not ready for CI yet (Control Room injected env vars)")
class TestProcessAPI:
    """Tests the Process API library wrapper."""

    def test_list_processes(self):
        # FIXME(cmin764, 30 Oct 2023): Expose `configure` in `workspace`.
        from robocorp.workspace._client import configure
        import os
        configure(api_key=os.getenv("RC_API_KEY"))
        print(process.list_processes())
