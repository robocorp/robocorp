from pathlib import Path

import yaml

CURDIR = Path(__file__).absolute().parent


class BaseTests:
    require_node = False
    require_log_built = False
    require_build_frontend = False
    before_run_custom_additional_steps = ()
    after_run_custom_additional_steps = ()

    matrix = {
        "name": [
            "ubuntu-py310-devmode",
            "windows-py310-devmode",
            "macos-py310-devmode",
        ],
        "include": [
            {
                "name": "ubuntu-py310-devmode",
                "python": "3.10",
                "os": "ubuntu-latest",
            },
            {
                "name": "windows-py310-devmode",
                "python": "3.10",
                "os": "windows-latest",
            },
            {
                "name": "macos-py310-devmode",
                "os": "macos-latest",
                "python": "3.10",
            },
        ],
    }

    run_tests = {
        "name": "Test",
        "env": {
            "GITHUB_ACTIONS_MATRIX_NAME": "${{ matrix.name }}",
            "CI_CREDENTIALS": "${{ secrets.CI_CREDENTIALS }}",
            "CI_ENDPOINT": "${{ secrets.CI_ENDPOINT }}",
        },
        "run": "python -m invoke test",
    }

    def __init__(self):
        project_dir = CURDIR.parent.parent / self.project_name
        assert project_dir.exists(), f"{project_dir} does not exist"

        self.target_file = CURDIR / f"{self.target}"
        self.name_part = {"name": self.name}
        paths = [
            f"{self.project_name}/**",
            f".github/workflows/{self.target}",
            f"devutils/**",
        ]
        if self.require_log_built:
            paths.append("log/**")

        self.on_part = {
            "on": {
                "push": {
                    "branches": ["master", "wip"],
                    "paths": paths[:],
                },
                "pull_request": {
                    "branches": ["master"],
                    "paths": paths[:],
                },
            }
        }
        self.defaults_part = {
            "defaults": {"run": {"working-directory": f"./{self.project_name}"}}
        }
        self.jobs_build_in_jobs = {
            "runs-on": "${{ matrix.os }}",
            "strategy": {
                "fail-fast": False,
                "matrix": self.matrix,
            },
        }

        steps = self.build_steps()
        self.jobs_steps_in_jobs = {"steps": steps}

        build = {}
        build.update(self.jobs_build_in_jobs)
        build.update(self.jobs_steps_in_jobs)

        self.jobs = {"jobs": {"build": build}}

        self.full = {}
        self.full.update(self.name_part)
        self.full.update(self.on_part)
        self.full.update(self.defaults_part)
        self.full.update(self.jobs)

    def build_steps(self):
        devinstall = {
            "name": "Install project (dev)",
            "if": "contains(matrix.name, '-devmode')",
            "run": "python -m invoke devinstall",
        }
        install = {
            "name": "Install project (not dev)",
            "if": "contains(matrix.name, '-devmode') == false",
            "run": "python -m invoke install",
        }
        setup_node = {
            "name": "Setup node",
            "uses": "actions/setup-node@v3",
            "with": {
                "node-version": "20.x",
                "registry-url": "https://npm.pkg.github.com",
                "scope": "@robocorp",
            },
        }

        build_log_react_view_steps = [
            {
                "name": "npm ci",
                "working-directory": "./log/output-react/",
                "if": "contains(matrix.name, '-devmode')",
                "run": "npm ci",
                "env": {
                    "CI": True,
                    "NODE_AUTH_TOKEN": "${{ secrets.CI_GITHUB_TOKEN }}",
                },
            },
            {
                "name": "Print robocorp-log info and build the output view.",
                "if": "contains(matrix.name, '-devmode')",
                "run": r"""
poetry run python -c "import sys;print('\n'.join(str(x) for x in sys.path))"
poetry run python -c "from robocorp import log;print(log.__file__)"
cd ../log
python -m invoke build-output-view-react
""",
                "env": {
                    "CI": True,
                    "NODE_AUTH_TOKEN": "${{ secrets.CI_GITHUB_TOKEN }}",
                },
            },
        ]

        build_frontend = {
            "name": "Build frontend",
            "run": "python -m invoke build-frontend",
            "env": {
                "CI": True,
                "NODE_AUTH_TOKEN": "${{ secrets.CI_GITHUB_TOKEN }}",
            },
        }

        install_poetry = {
            "name": "Install poetry",
            "run": "pipx install poetry",
        }
        checkout_repo = {
            "name": "Checkout repository and submodules",
            "uses": "actions/checkout@v3",
        }

        setup_python = {
            "name": "Set up Python ${{ matrix.python }}",
            "uses": "actions/setup-python@v4",
            "with": {
                "python-version": "${{ matrix.python }}",
                "cache": "poetry",
            },
        }
        install_tomlkit = {
            "name": "Install invoke/tomlkit",
            "run": "pip install invoke tomlkit",
        }
        run_lint = {
            "name": "`inv lint`/`inv typecheck`, potentially fixed with `inv pretty`",
            "if": "always()",
            "run": """
python -m invoke lint
python -m invoke typecheck
""",
        }

        steps = [
            checkout_repo,
            install_poetry,
            setup_python,
            install_tomlkit,
        ]
        if self.require_node or self.require_log_built:
            steps.append(setup_node)

        steps.extend(
            [
                install,
                devinstall,
            ]
        )

        if self.require_log_built:
            steps.extend(build_log_react_view_steps)

        if self.require_build_frontend:
            steps.append(build_frontend)

        steps.extend(self.before_run_custom_additional_steps)

        steps.extend(
            [
                self.run_tests,
                run_lint,
            ]
        )
        steps.extend(self.after_run_custom_additional_steps)
        return steps

    def generate(self):
        contents = yaml.safe_dump(self.full, sort_keys=False)
        path = CURDIR / self.target
        print("Writing to ", path)
        path.write_text(
            f"""# Note: auto-generated by `_gen_workflows.py`
{contents}""",
            "utf-8",
        )


class ActionServerTests(BaseTests):
    name = "Action Server Tests"
    target = "action_server_tests.yml"
    project_name = "action_server"
    require_node = True
    require_log_built = True
    require_build_frontend = True


class ActionsTests(BaseTests):
    name = "Actions Tests"
    target = "actions_tests.yml"
    project_name = "actions"
    require_node = True
    require_log_built = True


class BrowserTests(BaseTests):
    name = "Browser Tests"
    target = "browser_tests.yml"
    project_name = "browser"
    require_node = True
    require_log_built = True


class ExcelTests(BaseTests):
    name = "Excel Tests"
    target = "excel_tests.yml"
    project_name = "excel"


class IntegrationTests(BaseTests):
    name = "Integration Tests"
    target = "integration_tests.yml"
    project_name = "integration_tests"
    require_node = True
    require_log_built = True


class LogPyTestTests(BaseTests):
    name = "Log PyTest Tests"
    target = "log_pytest_tests.yml"
    project_name = "log_pytest"
    require_node = True
    require_log_built = True

    run_tests = {
        "name": "Test",
        "env": {
            "GITHUB_ACTIONS_MATRIX_NAME": "${{ matrix.name }}",
            "CI_CREDENTIALS": "${{ secrets.CI_CREDENTIALS }}",
            "CI_ENDPOINT": "${{ secrets.CI_ENDPOINT }}",
            # Must be customized to include the PYTHONPATH for the log tests.
            "PYTHONPATH": "../log/tests",
        },
        "run": "python -m invoke test",
    }


class LogTests(BaseTests):
    name = "Log Tests"
    target = "log_tests.yml"
    project_name = "log"
    require_node = True
    require_log_built = True

    matrix = {
        "name": [
            "ubuntu-py310-devmode-outviewintegrationtests",
            "windows-py310-devmode",
            "macos-py310-devmode",
        ],
        "include": [
            {
                "name": "ubuntu-py310-devmode-outviewintegrationtests",
                "python": "3.10",
                "os": "ubuntu-latest",
            },
            {
                "name": "windows-py310-devmode",
                "python": "3.10",
                "os": "windows-latest",
            },
            {
                "name": "macos-py310-devmode",
                "os": "macos-latest",
                "python": "3.10",
            },
        ],
    }

    before_run_custom_additional_steps = [
        {"name": "Install prettier", "run": "npm install -g prettier@2.4.1\n"},
        {
            "name": "Test React log",
            "working-directory": "./log/output-react/",
            "run": "npm ci\nnpm run test:prettier\nnpm run test:types\n",
            "env": {"CI": True, "NODE_AUTH_TOKEN": "${{ secrets.CI_GITHUB_TOKEN }}"},
        },
    ]

    after_run_custom_additional_steps = [
        {
            "uses": "actions/upload-artifact@v3",
            "if": "always() && contains(matrix.name, '-outviewintegrationtests')",
            "with": {
                "name": "robo_log_react.${{ matrix.name }}.html",
                "path": "log/output-react/tests_robo/output/log.html",
            },
        },
    ]


class StorageTests(BaseTests):
    name = "Asset Storage Tests"
    target = "storage_tests.yml"
    project_name = "storage"


class TasksTests(BaseTests):
    name = "Tasks Tests"
    target = "tasks_tests.yml"
    project_name = "tasks"
    require_node = True
    require_log_built = True


class VaultTests(BaseTests):
    name = "Vault Tests"
    target = "vault_tests.yml"
    project_name = "vault"


class WindowsTests(BaseTests):
    name = "Windows Tests"
    target = "windows_tests.yml"
    project_name = "windows"

    matrix = {
        "name": [
            "windows-py310-devmode",
        ],
        "include": [
            {
                "name": "windows-py310-devmode",
                "python": "3.10",
                "os": "windows-latest",
            },
        ],
    }

    before_run_custom_additional_steps = [
        {
            "name": "Set up chrome for tests",
            "run": "choco install googlechrome --ignore-checksums",
        }
    ]

    after_run_custom_additional_steps = [
        {
            "uses": "actions/upload-artifact@v1",
            "if": "always()",
            "with": {
                "name": "log.${{ matrix.name }}.html",
                "path": "windows/output/log.html",
            },
        },
        {
            "uses": "actions/upload-artifact@v1",
            "if": "always()",
            "with": {
                "name": "log.${{ matrix.name }}.robolog",
                "path": "windows/output/output.robolog",
            },
        },
    ]


class WorkItemsTests(BaseTests):
    name = "Work Items Tests"
    target = "workitems_tests.yml"
    project_name = "workitems"


TEST_TARGETS = [
    ActionServerTests(),
    ActionsTests(),
    BrowserTests(),
    ExcelTests(),
    IntegrationTests(),
    LogPyTestTests(),
    LogTests(),
    StorageTests(),
    TasksTests(),
    VaultTests(),
    WindowsTests(),
    WorkItemsTests(),
]


def main():
    for t in TEST_TARGETS:
        t.generate()


def load_curr():
    ON_PART = yaml.safe_load(
        r"""
    - name: Set up chrome for tests
      run: choco install googlechrome --ignore-checksums

"""
    )
    print(ON_PART)


if __name__ == "__main__":
    # load_curr()
    main()
