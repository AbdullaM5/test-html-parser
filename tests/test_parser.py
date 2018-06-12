from os.path import dirname, abspath, join

import pytest

from parser import Parser


@pytest.mark.parametrize('filename, expected', [
    ('hands_ru_about.html', ['+74997099352', '+74951377767']),
    ('nix_ru_contacts.html', ['+74959743333', '+74956167001', '+74956169020', '+74956166906'])
])
def test_parser(filename, expected):
    path_to_html = join(dirname(abspath(__file__)), 'html', filename)
    parser = Parser()
    with open(path_to_html, 'r') as f:
        html = f.read()
    result = parser(html)
    assert set(result) == set(expected)
