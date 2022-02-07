from typing import Any, Callable

from pygizmo.types.null_type import create_null_type

_NoResult = create_null_type("_NoResult")


class Return:
    def __init__(self, func: Callable, *args: Any, **kwargs: Any):
        self.func = func
        self.args = args
        self.kwargs = kwargs
        try:
            self.value = self.func(*self.args, **self.kwargs)
        except Exception as exc:
            self.value = exc

    @property
    def is_exception(self) -> bool:
        return isinstance(self.value, Exception)

    def raise_for_value(self):
        if self.is_exception:
            raise self.value

    def if_valid(self, func: Callable, *args: Any, **kwargs: Any) -> "Return":
        if not self.is_exception:
            self.value = func(*args, **kwargs)
        return self
