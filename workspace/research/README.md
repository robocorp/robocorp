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

## OpenAPI generator

- URL: https://www.npmjs.com/package/@openapitools/openapi-generator-cli
  (https://openapi-generator.tech)
- Command: `openapi-generator-cli generate -g python -i https://robocorp.com/api/openapi.json --skip-validate-spec -o ./npm-js-openapi-generator-cli`
- Observations:
  - See `openapi-generator-cli config-help -g python` for package template
    customization. (e.g.: `generateSourceCodeOnly` so we generate what we need only)
  - Generate with `--dry-run` (to see diffs only), `--minimal-update` (changes only).
  - [Customization](https://github.com/OpenAPITools/openapi-generator/blob/master/docs/customization.md)
  - [Templates](https://github.com/OpenAPITools/openapi-generator/tree/master/modules/openapi-generator/src/main/resources/python)

## Swagger Codegen

- URL: https://github.com/swagger-api/swagger-codegen
  (https://swagger.io/tools/swagger-codegen/)
- Command: `swagger-codegen generate -i https://robocorp.com/api/openapi.json -l python -o ./swagger-codegen`
- Observations: Looks like the proprietary precursor of
  [OpenAPI generator](#openapi-generator). (fork
  [reasons](https://github.com/OpenAPITools/openapi-generator/blob/master/docs/qna.md))  

## OpenAPI Python client

- URL: https://github.com/openapi-generators/openapi-python-client
- Command: `openapi-python-client generate --url https://robocorp.com/api/openapi.json`
- Observations: It fails due to schema validation [errors](./openapi-errors.txt).
  ([comment](https://github.com/openapi-generators/openapi-python-client/issues/107#issuecomment-1766614815))
