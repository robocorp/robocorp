---
name: robocorp-automation
description: Bootstrap from an empty folder or build, debug, locally run, and validate Python automations built with Robocorp or Sema4.ai tooling, robocorp.tasks, rcc, robocorp-browser, and RPA Framework. Use when starting or changing a Robocorp automation, task package, browser workflow, work-item process, or local run configuration. Not for Sema4.ai Action Server action packages (`@action`, `package.yaml`).
---

# Robocorp automation development

Help implement reliable Python task automations, including when starting from an empty directory. Prefer repository evidence and current official docs over remembered APIs; the ecosystem has both Python task automations and Robot Framework projects, which are not interchangeable. Sema4.ai action packages (`@action` from `sema4ai.actions`, configured by `package.yaml` and run by Action Server) are a different project type; this skill does not cover them.

For the core `robocorp` library APIs (tasks, browser, work items, vault, storage, log), see [references/api.md](references/api.md).

## Bootstrap from an empty directory

1. Inspect the current directory and available tools before creating anything. Confirm whether it is truly empty, whether it is already a Git repository, and whether `rcc` or the Sema4.ai VS Code extension is available. Do not overwrite existing files or initialize/modify Git history without the user's approval.
2. Establish the first useful scope from the user's request: what the automation should accomplish, its inputs and outputs, the systems it touches, and whether it needs credentials or a visible browser/UI. Ask a focused clarifying question when a missing decision materially changes the design; otherwise state reasonable assumptions and proceed.
3. Default to the current Python task framework (`robocorp.tasks`) unless the user requests Robot Framework or an existing template/docs indicate otherwise. Explain the distinction if the choice is unclear; do not generate a `.robot` suite and Python task package together by default.
4. Scaffold from an official starter template with `rcc`. List the templates bundled with the installed `rcc`, pick the closest match, and initialize it:

   ```sh
   rcc robot initialize --list
   rcc robot initialize -t 02-python-browser -d my-robot
   ```

   Typical templates are `01-python` (minimal), `02-python-browser` (robocorp-browser/Playwright) and `03-python-workitems` (producer/consumer with local work-item test data); use the names `--list` actually prints. `rcc robot initialize` refuses to write into a non-empty directory; initialize into a new subdirectory instead, and never pass `--force` without the user's approval. Keep the dependency versions the template pins in `conda.yaml` rather than replacing them with remembered ones. For use cases the bundled templates don't cover, look at the [template portal](https://robocorp.com/portal/tag/template) or [automation quickstart](https://sema4.ai/docs/automation/quickstart-guide). `rcc task run` runs tasks; it is not a scaffolding command.
5. Only if no template can be used, create the minimal package structure supported by current official docs and the chosen framework. At minimum, provide the task entry point, `robot.yaml`, dependency/environment configuration, and concise run instructions. Add tests and other files only when the automation needs them. Do not invent dependency versions, obsolete configuration fields, or platform freeze files.
6. Make the first task small and runnable, with clear task inputs/outputs and explicit failures. Keep credentials out of files and examples. If the requested automation requires a real service or account, create a safe local/test path where feasible and describe any remaining setup needed from the user.
7. If a required tool such as `rcc` is missing, use the [RCC release notes](https://sema4.ai/docs/automation/release-notes/product/rcc) as the source of truth for the latest version and its download link. Follow the official link for the user's OS/architecture and its installation instructions; do not reuse a remembered version or download from an unofficial mirror. Check for published integrity information and verify it when available. Ask before using administrator privileges, changing shell startup files, installing system-wide, or making other machine-wide changes; prefer a documented user-local installation when supported. Distinguish installing project dependencies through the declared environment from installing developer tooling.
8. Run the task locally using the resulting `robot.yaml`, then inspect the exit status, final task status, and artifacts. Do not claim the starter works until it has actually run, and report any missing tool installation, account, credential, browser, or external service requirement. If installation is blocked by permissions, network access, or user choice, give the exact official next step rather than silently switching to an unrelated setup.

## Start by identifying the project shape

1. Read `robot.yaml`, the environment file it selects (commonly `conda.yaml`), task modules, README, and ignore rules before editing.
2. Determine the configured task names and the shell command for each task. In a Python task project, task functions are commonly decorated with `@robocorp.tasks.task`; a `.robot` file instead uses Robot Framework syntax.
3. Keep dependency changes in the project's environment configuration. Preserve its pinned versions and platform-specific lock/freeze files unless the requested change requires updating them.
4. Locate the existing local-run workflow (VS Code task/extension or `rcc`) and artifacts directory. Do not assume a developer's global Python environment matches the robot environment.

## Implement the smallest complete change

- Follow the project's existing task, library, logging, and error-handling patterns.
- Prefer Robocorp libraries already present in the environment. For browser automation, first check whether the project uses `robocorp-browser` (Playwright) or an RPA Framework browser library; do not mix their APIs.
- Use stable, user-visible locators and explicit waits for browser actions. Avoid brittle positional selectors and fixed sleeps when a condition can be awaited.
- Make network and file operations fail visibly: check HTTP status, use bounded timeouts, validate expected data, and write outputs under the configured artifacts directory.
- Add or update focused tests for deterministic logic. Keep end-to-end tests for actual integrations and make their external side effects clear.
- Never put API keys, passwords, or customer data in source, examples, logs, prompts, or this skill. Obtain secrets through the project's configured secret mechanism or environment variables; do not deploy, publish, or start Control Room runs unless explicitly asked.

## Run and validate locally

Use the project's configured environment and exact task key from `robot.yaml`:

```sh
rcc task run --robot robot.yaml --task "TASK NAME"
```

Replace `TASK NAME` with a key under `tasks:` exactly as written. If the project uses the Sema4.ai/Robocorp VS Code extension, its Run Task command is also a valid local path and provisions the configured environment. Do not copy extension-generated `--controller`, workspace, account, or bundled flags into generic instructions; those are extension context, not needed for the normal local command.

When debugging an environment or task:

1. Run only the relevant configured task first; don't deploy it to Control Room as a substitute for local verification.
2. Confirm the task runner's final result is `PASS`/success, not merely that the process emitted a log line. A `finally` block may print a completion message even when the task failed.
3. Inspect the configured artifacts directory (often `output/`) for the run log, screenshots, and expected files. Check stderr and the runner's exit status if the result is not successful.
4. Run focused unit tests for pure transformations and validations inside the robot environment, then the configured end-to-end task when its external services are available. `rcc task script` runs any command in the environment that `robot.yaml` defines (add `pytest` to `conda.yaml` if the project doesn't declare it):

   ```sh
   rcc task script --robot robot.yaml -- python -m pytest tests
   ```
5. Report exactly what was run, its result, and any dependency on browser/UI access, network, credentials, or other external services.

For a project whose `robot.yaml` declares (excerpt; real files also set `environmentConfigs`, `artifactsDir`, `PATH` and `PYTHONPATH`):

```yaml
tasks:
  Automation Challenge:
    shell: python -m robocorp.tasks run tasks.py
```

the local command is:

```sh
rcc task run --robot robot.yaml --task "Automation Challenge"
```

Run `rcc task run --help` for supported local options. If `rcc` is unavailable, use the project's documented VS Code extension workflow or install/configure the supported Robocorp tooling; don't silently fall back to an unrelated system Python.

## Local work items and secrets

Control Room normally supplies work items and Vault secrets. Locally, provide them through a development environment file passed with `-e` (the VS Code extension uses the same `devdata/` convention):

```sh
rcc task run --robot robot.yaml --task "Consumer" -e devdata/env.json
```

`devdata/env.json` is a flat JSON object of environment variables:

```json
{
  "RC_WORKITEM_ADAPTER": "FileAdapter",
  "RC_WORKITEM_INPUT_PATH": "devdata/work-items-in/test-input/work-items.json",
  "RC_WORKITEM_OUTPUT_PATH": "devdata/work-items-out/last-run/work-items.json",
  "RC_VAULT_SECRET_MANAGER": "FileSecrets",
  "RC_VAULT_SECRETS_FILE": "devdata/secrets.json"
}
```

- The input `work-items.json` is a list of items, each `{"payload": {...}, "files": {"name.xlsx": "name.xlsx"}}` with file paths relative to that JSON file. The `03-python-workitems` template contains working examples for a producer and a consumer.
- The secrets file maps secret names to key/value pairs, for example `{"swaglabs": {"username": "...", "password": "..."}}`. Use only dummy or test credentials in it, keep real secrets out of the repository, and make sure the file is gitignored if it holds anything sensitive.
- When a task fails because a work item or secret is missing, add or fix the local test data; never hardcode the value in task code.
- For local runs of a producer/consumer chain, point the consumer's `RC_WORKITEM_INPUT_PATH` at the producer's output file.

## Control Room and API boundaries

- Treat building/testing locally and publishing/orchestrating in Control Room as separate workflows. For uploading or updating an automation package, prefer `rcc cloud` (for example, inspect `rcc cloud push --help` or `rcc cloud upload --help`) over calling package-upload APIs directly. Use the documented `rcc` workflow for authentication, workspace/robot selection, and upload; do not assume exact flags or target IDs without checking the installed `rcc` help and project/user context.
- If `rcc` is unavailable, not authenticated, or does not support the requested Control Room operation, explain that limitation and follow its official setup/docs. Use a direct Control Room API call only when the operation is not supported by `rcc` or the user explicitly requests it (for example, creating a process if no `rcc` command covers that operation). For direct API use, consult current endpoint-specific documentation for authentication, request shape, and consequences. Never infer that an API key belongs in a URL or embed credentials in commands, source, examples, or logs.
- Ask for explicit confirmation before uploading/publishing a package, triggering a process, creating or modifying Control Room resources, or changing the selected workspace/robot. Before upload, summarize the exact local package directory and target workspace/robot. Use existing approved `rcc` authentication where possible; do not ask the user to paste secrets into chat or expose credentials or authorization tokens in command output.

## Documentation

- [Sema4.ai automation quickstart](https://sema4.ai/docs/automation/quickstart-guide)
- [RPA Framework libraries](https://rpaframework.org/)
- [Robocorp API documentation](https://robocorp.com/api)
- [rcc recipes and configuration](https://github.com/robocorp/rcc/blob/master/docs/recipes.md)
- [RCC release notes and latest downloads](https://sema4.ai/docs/automation/release-notes/product/rcc)
