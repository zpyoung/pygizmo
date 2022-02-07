from typing import IO, Any, Callable, Dict, Optional, Union

from orjson import orjson

# Options from orjson
from pygizmo.containers.function_return import Return


class DumpOptions:
    """
    Class Attributes:
        APPEND_NEWLINE: Append \n to the output.
        INDENT_2: Pretty-print output with an indent of two spaces. This is equivalent to `indent=2` in the standard library.
        NAIVE_UTC: Serialize `datetime.datetime` objects without a `tzinfo` as UTC. This has no effect on `datetime.datetime` objects that have `tzinfo` set.
        NON_STR_KEYS: Serialize dict keys of type other than `str`. This allows dict keys to be one of `str`, `int`, `float`, `bool`, `None`, `datetime.datetime`, `datetime.date`, `datetime.time`, `enum.Enum`, and `uuid.UUID`.
        OMIT_MICROSECONDS: Do not serialize the `microsecond` field on `datetime.datetime` and `datetime.time` instances.
        PASSTHROUGH_DATACLASS: Passthrough `dataclasses.dataclass` instances to default. This allows customizing their output but is much slower.
        PASSTHROUGH_DATETIME: Passthrough `datetime.datetime`, `datetime.date`, and `datetime.time` instances to `default`. This allows serializing datetimes to a custom format, e.g., HTTP dates. This does not affect datetimes in `dict` keys if using NON_STR_KEYS.
        PASSTHROUGH_SUBCLASS: Passthrough subclasses of builtin types to `default`. This does not affect datetimes in `dict` keys if using NON_STR_KEYS.
        SERIALIZE_NUMPY: Serialize `numpy.ndarray` instances.
        SORT_KEYS: Serialize `dict` keys in sorted order. The default is to serialize in an unspecified order. This is equivalent to `sort_keys=True` in the standard library.
        STRICT_INTEGER: Enforce 53-bit limit on integers. The limit is otherwise 64 bits, the same as the Python standard library.
        UTC_Z: Serialize a UTC timezone on `datetime.datetime` instances as `Z` instead of `+00:00`
    """

    APPEND_NEWLINE = 1024
    INDENT_2 = 1
    NAIVE_UTC = 2
    NON_STR_KEYS = 4
    OMIT_MICROSECONDS = 8
    PASSTHROUGH_DATACLASS = 2048
    PASSTHROUGH_DATETIME = 512
    PASSTHROUGH_SUBCLASS = 256
    SERIALIZE_NUMPY = 16
    SORT_KEYS = 32
    STRICT_INTEGER = 64
    UTC_Z = 128


def _gizmo_default(obj):
    if hasattr(obj, "__json_encode__"):
        return obj.__json_encode__()
    elif hasattr(obj, "json"):
        return obj.json()
    raise TypeError


def dumps(
    __obj: Any, *, default: Optional[Callable[[Any], Any]] = None, option: Optional[int] = None, encoding: str = "utf-8"
) -> str:
    def _default(obj: Any) -> Any:
        result = Return(_gizmo_default, obj).if_valid(default)
        result.raise_for_value()
        return result.value

    return orjson.dumps(__obj, default=_default, option=option).decode(encoding)


def dump(
    __obj: Any,
    fp: IO,
    *,
    default: Optional[Callable[[Any], Any]] = None,
    option: Optional[int] = None,
    encoding: str = "utf-8",
):
    result = dumps(__obj, default=default, option=option, encoding=encoding)
    fp.write(result)


def loads(__obj: Union[bytes, bytearray, memoryview, str]) -> Dict:
    return orjson.loads(__obj)


def load(
    fp: IO,
) -> Dict:
    obj = fp.read()
    return loads(obj)
