from re import compile as re_compile
from sre_constants import error as re_error


def valid_re_or_none(re_str):
    try:
        regex = re_compile(re_str)
    except re_error:
        return None
    return regex


def str2bool(v, missing=False):
    """
    Original code from:
     https://stackoverflow.com/questions/15008758/parsing-boolean-values-with-argparse/43357954#43357954
    """
    if v.lower() in {'yes', 'true', 't', 'y', '1'}:
        return True
    elif v.lower() in {'no', 'false', 'f', 'n', '0'}:
        return False
    else:
        return missing


def checked_or_empty(val, input_field_present, default):
    """Unchecked checkboxes do not appear by default in GET request"""
    # If checkbox does present and is checked -> checked
    # If checkbox does present and is empty -> unchecked
    # If checkbox does not present and the corresponding input field also does not present -> default value
    # If checkbox does not present and the corresponding input field does present -> unchecked
    if (val is not None and len(val) > 0) or (val is None and not input_field_present and len(default) > 0):
        return 'checked'
    return ''
