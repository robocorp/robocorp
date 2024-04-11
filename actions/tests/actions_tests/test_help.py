# Disable this test for now: the output is different from Python 3.9
# to Python 3.10
#
# import pytest
#
#
# @pytest.mark.parametrize("args", [["-h"], ["run", "-h"], ["list", "-h"]])
# def test_help(args, str_regression):
#     from devutils.fixtures import robocorp_actions_run
#
#     str_regression.check(
#         robocorp_actions_run(args, returncode=0).stdout.decode("utf-8")
#     )
