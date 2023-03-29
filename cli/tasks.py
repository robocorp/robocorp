from invoke import task


def poetry(ctx, *parts):
    args = " ".join(str(part) for part in parts)
    ctx.run(f"poetry run {args}", pty=True, echo=True)


@task
def lint(ctx):
    """Run static analysis and formatting checks"""
    poetry(ctx, "ruff robo_cli")
    poetry(ctx, "black --check robo_cli")
    poetry(ctx, "isort --check robo_cli")


@task
def test(ctx):
    """Run unittests"""
    poetry(ctx, "pytest")


@task
def pretty(ctx):
    """Automatically format code"""
    poetry(ctx, "black robo_cli tests")
    poetry(ctx, "isort robo_cli tests")


@task
def build(ctx):
    """Build executable"""
    poetry(ctx, "pyinstaller robo_cli.spec")
