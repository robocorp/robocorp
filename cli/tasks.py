from invoke import task


def poetry(ctx, *parts):
    args = " ".join(str(part) for part in parts)
    ctx.run(f"poetry run {args}", pty=True, echo=True)


@task
def lint(ctx):
    poetry(ctx, "ruff robo_cli")
    poetry(ctx, "black --check robo_cli")
    poetry(ctx, "isort --check robo_cli")


@task
def pretty(ctx):
    poetry(ctx, "black robo_cli tests")
    poetry(ctx, "isort robo_cli tests")
