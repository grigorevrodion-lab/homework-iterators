import types


# =====================================================
# ЗАДАНИЕ 1. Итератор (1 уровень вложенности)
# =====================================================

class FlatIteratorOneLevel:
    def __init__(self, list_of_lists):
        self.list_of_lists = list_of_lists
        self.outer_index = 0
        self.inner_index = 0

    def __iter__(self):
        return self

    def __next__(self):
        while self.outer_index < len(self.list_of_lists):
            current_list = self.list_of_lists[self.outer_index]

            if self.inner_index < len(current_list):
                item = current_list[self.inner_index]
                self.inner_index += 1
                return item
            else:
                self.outer_index += 1
                self.inner_index = 0

        raise StopIteration


def test_1():
    list_of_lists_1 = [
        ['a', 'b', 'c'],
        ['d', 'e', 'f', 'h', False],
        [1, 2, None]
    ]

    result = list(FlatIteratorOneLevel(list_of_lists_1))
    assert result == ['a', 'b', 'c', 'd', 'e', 'f', 'h', False, 1, 2, None]


# =====================================================
# ЗАДАНИЕ 2. Генератор (1 уровень вложенности)
# =====================================================

def flat_generator_one_level(list_of_lists):
    for inner_list in list_of_lists:
        for item in inner_list:
            yield item


def test_2():
    list_of_lists_1 = [
        ['a', 'b', 'c'],
        ['d', 'e', 'f', 'h', False],
        [1, 2, None]
    ]

    result = list(flat_generator_one_level(list_of_lists_1))
    assert result == ['a', 'b', 'c', 'd', 'e', 'f', 'h', False, 1, 2, None]
    assert isinstance(flat_generator_one_level(list_of_lists_1), types.GeneratorType)


# =====================================================
# ЗАДАНИЕ 3*. Итератор (любой уровень вложенности)
# =====================================================

class FlatIteratorAnyLevel:
    def __init__(self, list_of_lists):
        self.stack = [iter(list_of_lists)]

    def __iter__(self):
        return self

    def __next__(self):
        while self.stack:
            try:
                item = next(self.stack[-1])
            except StopIteration:
                self.stack.pop()
                continue

            if isinstance(item, list):
                self.stack.append(iter(item))
            else:
                return item

        raise StopIteration


def test_3():
    list_of_lists_2 = [
        [['a'], ['b', 'c']],
        ['d', 'e', [['f'], 'h'], False],
        [1, 2, None, [[[[['!']]]]], []]
    ]

    result = list(FlatIteratorAnyLevel(list_of_lists_2))
    assert result == ['a', 'b', 'c', 'd', 'e', 'f', 'h', False, 1, 2, None, '!']


# =====================================================
# ЗАДАНИЕ 4*. Генератор (любой уровень вложенности)
# =====================================================

def flat_generator_any_level(list_of_lists):
    for item in list_of_lists:
        if isinstance(item, list):
            yield from flat_generator_any_level(item)
        else:
            yield item


def test_4():
    list_of_lists_2 = [
        [['a'], ['b', 'c']],
        ['d', 'e', [['f'], 'h'], False],
        [1, 2, None, [[[[['!']]]]], []]
    ]

    result = list(flat_generator_any_level(list_of_lists_2))
    assert result == ['a', 'b', 'c', 'd', 'e', 'f', 'h', False, 1, 2, None, '!']
    assert isinstance(flat_generator_any_level(list_of_lists_2), types.GeneratorType)


# =====================================================
# ЗАПУСК ВСЕХ ТЕСТОВ
# =====================================================

if __name__ == '__main__':
    test_1()
    test_2()
    test_3()
    test_4()
    print("Все тесты пройдены успешно")
