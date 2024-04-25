import functools
import inspect
import warnings

import pandas as pd

_string_types = (type(b""), type(""))

from .constants import DATAPATH


def sort_dict_by_values(d: dict, reverse=False) -> dict:
    """Return an instance of the given dictionary sorted by its values

    Parameters
    ----------
    d : dict
        The dictionary to sort by values

    Returns
    -------
    dict
        The sorted dictionary
    """
    return dict(sorted(d.items(), key=lambda x: x[1], reverse=reverse))


def read_event_desc(event_name: str) -> str:
    fpath = DATAPATH.joinpath(f"sport_descriptions/{event_name}.md")
    if not fpath.exists():
        print("File not found:", fpath)
        return "NO DESCRIPTION FOUND"
    with fpath.open("r", encoding="utf-8") as f:
        return f.read()


def all_equal(lst: list) -> bool:
    """Check whether all objects in a list are equal."""
    return all(x == lst[0] for x in lst)


def turn_series_list_to_dataframe(series_list: list[pd.Series]) -> pd.DataFrame:
    """Turns a given list of series objects to a pandas dataframe,
    assuming they all have the same structure.
    """
    if len(series_list) == 0:
        return pd.DataFrame()
    return pd.concat(series_list, axis=1).T


# Taken from https://stackoverflow.com/questions/2536307/decorators-in-the-python-standard-lib-deprecated-specifically
def deprecated(reason):
    """
    This is a decorator which can be used to mark functions
    as deprecated. It will result in a warning being emitted
    when the function is used.
    """

    if isinstance(reason, _string_types):

        # The @deprecated is used with a 'reason'.
        #
        # .. code-block:: python
        #
        #    @deprecated("please, use another function")
        #    def old_function(x, y):
        #      pass

        def decorator(func1):

            if inspect.isclass(func1):
                fmt1 = "Call to deprecated class {name} ({reason})."
            else:
                fmt1 = "Call to deprecated function {name} ({reason})."

            @functools.wraps(func1)
            def new_func1(*args, **kwargs):
                warnings.simplefilter("always", DeprecationWarning)
                warnings.warn(
                    fmt1.format(name=func1.__name__, reason=reason),
                    category=DeprecationWarning,
                    stacklevel=2,
                )
                warnings.simplefilter("default", DeprecationWarning)
                return func1(*args, **kwargs)

            return new_func1

        return decorator

    elif inspect.isclass(reason) or inspect.isfunction(reason):

        # The @deprecated is used without any 'reason'.
        #
        # .. code-block:: python
        #
        #    @deprecated
        #    def old_function(x, y):
        #      pass

        func2 = reason

        if inspect.isclass(func2):
            fmt2 = "Call to deprecated class {name}."
        else:
            fmt2 = "Call to deprecated function {name}."

        @functools.wraps(func2)
        def new_func2(*args, **kwargs):
            warnings.simplefilter("always", DeprecationWarning)
            warnings.warn(
                fmt2.format(name=func2.__name__),
                category=DeprecationWarning,
                stacklevel=2,
            )
            warnings.simplefilter("default", DeprecationWarning)
            return func2(*args, **kwargs)

        return new_func2

    else:
        raise TypeError(repr(type(reason)))
