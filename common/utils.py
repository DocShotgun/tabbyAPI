"""Common utility functions"""

from types import NoneType
from typing import Dict, Optional, Type, Union, get_args, get_origin, TypeVar

T = TypeVar("T")


def unwrap(wrapped: Optional[T], default: T = None) -> T:
    """Unwrap function for Optionals."""
    if wrapped is None:
        return default

    return wrapped


def coalesce(*args):
    """Coalesce function for multiple unwraps."""
    return next((arg for arg in args if arg is not None), None)


def filter_none_values(collection: Union[dict, list]) -> Union[dict, list]:
    """Remove None values from a collection."""

    if isinstance(collection, dict):
        return {
            k: filter_none_values(v) for k, v in collection.items() if v is not None
        }
    elif isinstance(collection, list):
        return [filter_none_values(i) for i in collection if i is not None]
    else:
        return collection


def deep_merge_dict(dict1: Dict, dict2: Dict, copy: bool = False) -> Dict:
    """
    Merge 2 dictionaries. If copy is true, the original dictionary isn't modified.
    """

    if copy:
        dict1 = dict1.copy()

    for key, value in dict2.items():
        if isinstance(value, dict) and key in dict1 and isinstance(dict1[key], dict):
            deep_merge_dict(dict1[key], value, copy=False)
        else:
            dict1[key] = value

    return dict1


def deep_merge_dicts(*dicts: Dict) -> Dict:
    """
    Merge an arbitrary amount of dictionaries.
    We wanna do in-place modification for each level, so do not copy.
    """

    result = {}
    for dictionary in dicts:
        result = deep_merge_dict(result, dictionary)

    return result


def flat_map(input_list):
    """Flattens a list of lists into a single list."""

    return [item for sublist in input_list for item in sublist]


def is_list_type(type_hint) -> bool:
    """Checks if a type contains a list."""

    if get_origin(type_hint) is list:
        return True

    # Recursively check for lists inside type arguments
    type_args = get_args(type_hint)
    if type_args:
        return any(is_list_type(arg) for arg in type_args)

    return False


def unwrap_optional_type(type_hint) -> Type:
    """
    Unwrap Optional[type] annotations.
    This is not the same as unwrap.
    """

    if get_origin(type_hint) is Union:
        args = get_args(type_hint)
        if NoneType in args:
            for arg in args:
                if arg is not NoneType:
                    return arg

    return type_hint


def calculate_rope_alpha(base_seq_len: int, target_seq_len: int):
    """
    Converts a given max sequence length to a rope alpha value.

    Args:
        base_seq_len: The model's configured sequence length.
        target_seq_len: The user-specified max sequence length.
    """

    # Get the ratio of the model's max sequence length to the target
    ratio = target_seq_len / base_seq_len

    # Default to a 1 alpha if the sequence length is ever less
    # than or equal to 1
    if ratio <= 1.0:
        alpha = 1
    else:
        alpha = -0.13436 + 0.80541 * ratio + 0.28833 * ratio**2
    return alpha
