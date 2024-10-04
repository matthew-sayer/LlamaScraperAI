import logging
from functools import wraps

def handleErrors(default_return_value=None):
    def decorator(func):
        @wraps(func)
        def wrapper (*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                logging.error(f'Error in {func.__name__}: {e}')
                return default_return_value
        return wrapper
    return decorator