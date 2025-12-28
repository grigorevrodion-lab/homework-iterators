import types
from logger import logger_with_path


@logger_with_path('app.log')
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


@logger_with_path('app.log')
def flat_generator_one_level(list_of_lists):
    for inner_list in list_of_lists:
        for item in inner_list:
            yield item


@logger_with_path('app.log')
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


@logger_with_path('app.log')
def flat_generator_any_level(list_of_lists):
    for item in list_of_lists:
        if isinstance(item, list):
            yield from flat_generator_any_level(item)
        else:
            yield item
