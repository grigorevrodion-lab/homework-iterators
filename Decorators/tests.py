import os
import types
from logger import logger, logger_with_path
from iterators import (
    FlatIteratorOneLevel,
    flat_generator_one_level,
    FlatIteratorAnyLevel,
    flat_generator_any_level
)


def test_logger_simple():
    path = 'main.log'
    if os.path.exists(path):
        os.remove(path)

    @logger
    def hello_world():
        return 'Hello World'

    @logger
    def summator(a, b=0):
        return a + b

    assert hello_world() == 'Hello World'
    assert summator(2, 2) == 4

    summator(4.3, b=2.2)

    with open(path) as f:
        content = f.read()

    assert 'summator' in content
    for item in (4.3, 2.2, 6.5):
        assert str(item) in content


def test_logger_with_path():
    path = 'custom.log'
    if os.path.exists(path):
        os.remove(path)

    @logger_with_path(path)
    def summator(a, b):
        return a + b

    summator(1, 2)

    assert os.path.exists(path)


def test_iterators_and_generators():
    list_of_lists_1 = [
        ['a', 'b', 'c'],
        ['d', 'e', 'f', 'h', False],
        [1, 2, None]
    ]

    assert list(FlatIteratorOneLevel(list_of_lists_1)) == [
        'a', 'b', 'c', 'd', 'e', 'f', 'h', False, 1, 2, None
    ]

    assert list(flat_generator_one_level(list_of_lists_1)) == [
        'a', 'b', 'c', 'd', 'e', 'f', 'h', False, 1, 2, None
    ]
    assert isinstance(flat_generator_one_level(list_of_lists_1), types.GeneratorType)

    list_of_lists_2 = [
        [['a'], ['b', 'c']],
        ['d', 'e', [['f'], 'h'], False],
        [1, 2, None, [[[[['!']]]]], []]
    ]

    assert list(FlatIteratorAnyLevel(list_of_lists_2)) == [
        'a', 'b', 'c', 'd', 'e', 'f', 'h', False, 1, 2, None, '!'
    ]

    assert list(flat_generator_any_level(list_of_lists_2)) == [
        'a', 'b', 'c', 'd', 'e', 'f', 'h', False, 1, 2, None, '!'
    ]


if __name__ == '__main__':
    test_logger_simple()
    test_logger_with_path()
    test_iterators_and_generators()
