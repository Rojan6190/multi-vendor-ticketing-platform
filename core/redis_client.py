import redis 
from django.conf import settings

# One shared connection pool for the whole process - dont open a new 
# connection per request/lock check.

_pool = redis.ConnectionPool.from_url(settings.REDIS_URL)

def get_redis():
    return redis.Redis(connection_pool = _pool)