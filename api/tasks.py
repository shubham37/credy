from celery.decorators import task
from .redis import redis_obj


@task
def increase_counter():
    if redis_obj.exists('counter'):
        redis_obj.incr('counter')
    else:
        redis_obj.set('counter', 1)
