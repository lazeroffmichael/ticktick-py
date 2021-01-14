"""
Provides some methods for dealing with hex color code strings.
"""

import random
import re

VALID_HEX_VALUES = "^#([A-Fa-f0-9]{6}|[A-Fa-f0-9]{3})$"


def generate_hex_color() -> str:
    """
    Generates a random hexadecimal color string to be used for rgb color schemes.

    Returns:
        '#' followed by 6 hexadecimal digits.

    ??? info "Import Help"
        ```python
        from ticktick.helpers.hex_color import generate_hex_color
        ```
    """
    num = random.randint(1118481, 16777215)
    hex_num = format(num, 'x')
    return '#' + hex_num


def check_hex_color(color: str) -> bool:
    """
    Verifies if the passed in color string is a valid hexadecimal color string

    Arguments:
        color: String to check.

    Returns:
        True if the string is a valid hex code, else False.

    ??? info "Import Help"
        ```python
        from ticktick.helpers.hex_color import check_hex_color
        ```
    """
    check_color = re.search(VALID_HEX_VALUES, color)
    if not check_color:
        return False
    else:
        return True
