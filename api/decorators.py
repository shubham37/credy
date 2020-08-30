import time


def retry(func):
    """
    Retry Decorator for Api Call
    """
    response = ''

    def decorator(*args, **kwargs):
        try:
            response = func(*args, **kwargs)
            if not response:
                raise
        except Exception as e:
            time.sleep(1)
            response = func(*args, **kwargs)
        return response
    return decorator
