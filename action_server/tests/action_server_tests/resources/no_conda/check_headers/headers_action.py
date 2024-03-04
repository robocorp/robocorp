# import os
# from pathlib import Path
#
# from robocorp.actions import Request, action
#
#
# @action
# def check_headers(request: Request, name: str, title="Mr.") -> str:
#     """
#     Gets something from the headers.
#
#     Args:
#         name: The name of the person to greet.
#         title: The title for the persor (Mr., Mrs., ...).
#
#     Returns:
#         The greeting for the person.
#     """
#     artifacts = Path(os.environ["ROBOT_ARTIFACTS"])
#     subdir = artifacts / "subdir"
#     subdir.mkdir(parents=True, exist_ok=True)
#     txt = subdir / "myfile.txt"
#     txt.write_text("Some text in myfile.txt")
#     return f"Hello {title} {name}."
