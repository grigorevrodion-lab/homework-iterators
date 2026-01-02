import pytest
from src.functions import sum_two, is_even, reverse_string


@pytest.mark.parametrize(
    "a, b, expected",
    [(1, 2, 3), (-1, 1, 0), (0, 0, 0)]
)
def test_sum_two(a, b, expected):
    assert sum_two(a, b) == expected


@pytest.mark.parametrize(
    "number, expected",
    [(2, True), (3, False), (0, True), (-4, True)]
)
def test_is_even(number, expected):
    assert is_even(number) == expected


@pytest.mark.parametrize(
    "value, expected",
    [("hello", "olleh"), ("123", "321"), ("", "")]
)
def test_reverse_string(value, expected):
    assert reverse_string(value) == expected
