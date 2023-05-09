from invoke import task
import sys


def build_common_tasks(root, package_name):
    SRC = root / "src"
    DIST = root / "dist"

    def poetry(ctx, *parts):
        args = " ".join(str(part) for part in parts)
        ctx.run(f"poetry {args}", pty=sys.platform != "win32", echo=True)

    @task
    def install(ctx):
        """Install dependencies"""
        poetry(ctx, "install")

    @task
    def lint(ctx):
        """Run static analysis and formatting checks"""
        poetry(ctx, f"run ruff {SRC}")
        poetry(ctx, f"run black --check {SRC}")
        poetry(ctx, f"run isort --check {SRC}")

    @task
    def typecheck(ctx):
        """Type check code"""
        poetry(ctx, f"run mypy {SRC}")

    @task
    def pretty(ctx):
        """Auto-format code and sort imports"""
        poetry(ctx, f"run black {SRC}")
        poetry(ctx, f"run isort {SRC}")

    @task
    def test(ctx):
        """Run unittests"""
        poetry(ctx, f"run pytest")

    @task
    def build(ctx):
        """Build distributable .tar.gz and .wheel files"""
        poetry(ctx, "build")

    @task
    def publish(ctx):
        """Publish package to PyPI"""
        for file in DIST.glob("*"):
            print(f"Removing: {file}")
            file.unlink()

        poetry(ctx, "publish", "--build")

    @task
    def docs(ctx):
        """Build API documentation"""
        poetry(
            ctx,
            "run lazydocs",
            "--overview-file README.md",
            "--remove-package-prefix",
            package_name,
        )

    return locals()
