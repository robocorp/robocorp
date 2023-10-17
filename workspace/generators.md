# Experiment with various OpenAPI generators

Objective: Finding the best tool with which we can generate maintainable code aligning
as close as possible to our idioms.

A few points to tick when assessing the tool:
- Generate usable running code ready for packaging which really works when calling the
  API, requiring minimum intervention.
- Python 3.10 compatible, installable in both Robo and RPA Framework.
- Type-hinted, docstrings, documentation, testing coverage. (in this order)
- Preferably using `requests` for network traffic. (benefit from our own handler)
- Easy to extend for e.g. providing request info from env vars injected by CR.

## OpenAPI generator CLI

- URL: https://www.npmjs.com/package/@openapitools/openapi-generator-cli
- Command: `openapi-generator-cli generate -g python -i https://robocorp.com/api/openapi.json --skip-validate-spec -o ./npm-js-openapi-generator-cli`
- Traits:
  - See `openapi-generator-cli config-help -g python` for package template
    customization. (e.g.: `generateSourceCodeOnly` so we generate what we need only)
  - Generate with `--dry-run` (to see diffs only), `--minimal-update` (changes only).
