# Note: besides the types supported here, pydantic is also supported
# by checking duck-typing for the APIs below:
#
# `cls.model_validate(dict)`
# `cls.model_json_schema()`
# `obj.model_dump_json()`
SUPPORTED_TYPES_IN_SCHEMA = (str, int, float, bool)

DEFAULT_TASK_SEARCH_GLOB = "*task*.py"

MODULE_ENTRY_POINT = "robocorp.tasks"
