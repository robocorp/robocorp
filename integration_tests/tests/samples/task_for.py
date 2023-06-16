# ruff: noqa: F841
from robocorp.tasks import task


@task
def check_case_for():
    rows = 10
    cols = 10

    matrix = []
    for x in range(rows):
        row = []
        for y in range(cols):
            row.append(0)
        matrix.append(row)

    final_matrix = matrix
