from ticktick.helpers.hex_color import generate_hex_color, check_hex_color


def test_generate_hex_color():
    """Tests proper formatting of the color code"""
    color = generate_hex_color()
    assert '#' == color[0]
    assert len(color) == 7


def test_check_hex_color_good():
    """Tests that a valid code works"""
    color = '#4b98a9'
    assert check_hex_color(color)


def test_check_hex_color_bad():
    """Tests that a valid code does not work"""
    color = 'This color is not an actual color'
    assert not check_hex_color(color)


def test_generate_hex_color_and_check():
    """Tests a proper code is generated each time"""
    for _ in range(1000):
        color = generate_hex_color()
        assert check_hex_color(color)
