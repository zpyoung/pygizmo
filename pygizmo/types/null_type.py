from typing import Any


def create_null_type(name: str) -> Any:
    """
    Creates a singleton instance of a custom nullable-type. This nullable-type acts much in the
    same way `None` does. It is a "Falsey" value, returns `None` when called, raises `StopIteration`
    when iterated, returns `False` when checking for attributes, and is the only possible instance
    of its type.

    Use this to create a unique None-like constant where the standard `None` will not work.
    Args:
        name: The name to give the class of the returned nullable-type object.

    Returns:
        A nullable-type object.
    """

    def stop_iter(*args):
        raise StopIteration

    return type(
        name,
        (object,),
        {
            "__str__": lambda s: name,
            "__repr__": lambda s: name,
            "__bool__": lambda s: False,
            "__nonzero__": lambda s: False,
            "__contains__": lambda s: False,
            "__len__": lambda s: False,
            "__call__": lambda s: None,
            "__iter__": lambda s: s,
            "next": stop_iter,
        },
    )()


Null = create_null_type("Null")
