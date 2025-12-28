import datetime


def logger(old_function):
    def new_function(*args, **kwargs):
        result = old_function(*args, **kwargs)

        with open('main.log', 'a', encoding='utf-8') as f:
            f.write(
                f'{datetime.datetime.now()} | '
                f'{old_function.__name__} | '
                f'args={args}, kwargs={kwargs} | '
                f'result={result}\n'
            )

        return result

    return new_function


def logger_with_path(path):
    def __logger(old_function):
        def new_function(*args, **kwargs):
            result = old_function(*args, **kwargs)

            with open(path, 'a', encoding='utf-8') as f:
                f.write(
                    f'{datetime.datetime.now()} | '
                    f'{old_function.__name__} | '
                    f'args={args}, kwargs={kwargs} | '
                    f'result={result}\n'
                )

            return result

        return new_function

    return __logger