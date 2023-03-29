from typing import (
    Any,
    NotRequired,
    Type,
    TypeGuard,
    TypeVar,
    Union,
    get_args,
    get_origin,
    is_typeddict,
)

T = TypeVar("T")
MISSING = object()


def validate_schema(obj: dict[str, Any], schema: Type[T]) -> TypeGuard[T]:
    if not is_typeddict(schema):
        raise RuntimeError("Schema should be of TypedDict type")

    for key, value_type in schema.__annotations__.items():
        _validate_value(key=key, value=obj.get(key, MISSING), tp=value_type)

    return True


def _validate_value(key: str, value: Any, tp: Any):
    def invalid():
        raise ValueError(
            f"Key '{key}' has value '{value}', expected '{tp.__name__}' type"
        )

    origin = get_origin(tp)
    is_optional = origin == NotRequired
    is_missing = value is MISSING

    if is_optional and is_missing:
        return
    elif not is_optional and is_missing:
        raise KeyError(key)
    elif is_optional and not is_missing:
        tp = get_args(tp)[0]
        _validate_value(key, value, tp)
    elif origin == Union:
        options = get_args(tp)
        _ensure_type(key=key, value=value, options=options)
    elif origin == list:
        if not isinstance(value, list):
            invalid()
        options = get_args(tp)
        for v in value:
            _ensure_type(key=key, value=v, options=options)
    elif origin == dict:
        if not isinstance(value, dict):
            invalid()
        arg_key, arg_value = get_args(tp)
        for k, v in value.items():
            _ensure_type(key=key, value=k, options=(arg_key,))
            _ensure_type(key=key, value=v, options=(arg_value,))
    elif is_typeddict(tp):
        validate_schema(value, tp)
    elif type(value) != tp:
        invalid()


def _ensure_type(key: str, value: Any, options: tuple[Type, ...]):
    if Any in options:
        return
    if type(value) in options:
        return

    for arg in options:
        try:
            _validate_value(key=key, value=value, tp=arg)
            return
        except ValueError:
            pass

    if len(options) > 1:
        types = ", ".join(f"'{option.__name__}'" for option in options)
        msg = f"expected any of {types} types"
    else:
        msg = f"expected '{options[0].__name__}' type"
    raise ValueError(f"Key '{key}' has value '{value}', {msg}")
