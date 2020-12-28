import random
import re

VALID_HEX_VALUES = "^#([A-Fa-f0-9]{6}|[A-Fa-f0-9]{3})$"


def generate_hex_color() -> str:
    """
    Generates a random hexadecimal number to used for rgb color schemes
    :return: '#' followed by 6 hexadecimal digits in string format
    """
    num = random.randint(1118481, 16777215)
    hex_num = format(num, 'x')
    return '#' + hex_num


def check_hex_color(color: str) -> bool:
    """
    Verifies if the passed in color string is a valid hexadecimal color string
    :param color: Hex color code as a string
    :return: Boolean true or false
    """
    check_color = re.search(VALID_HEX_VALUES, color)
    if not check_color:
        return False
    else:
        return True
