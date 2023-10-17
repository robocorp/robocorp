# Experiment with various OpenAPI generators

Objective: Finding the best tool with which we can generate maintainable code aligning
as close as possible to our idioms.

A few points to tick when assessing the tool:
- Generate usable running code ready for packaging which really works when calling the
  API with minimum intervention.
- Python 3.10 compatible, installable in both Robo and RPA Framework.
- Type-hinted, docstrings, documentation, testing coverage. (in this order)
- Preferably using `requests` for network traffic. (benefit from our own handler)

## OpenAPI generator CLI

- URL: https://www.npmjs.com/package/@openapitools/openapi-generator-cli
- Command: `openapi-generator-cli generate -g python -i https://robocorp.com/api/openapi.json --skip-validate-spec -o ./npm-js-openapi-generator-cli`
