
import redis


import redis

redis_client = redis.Redis(
    host="localhost",
    port=6379,
    db=0,
    decode_responses=True,
    socket_connect_timeout=5,
    socket_timeout=None,
    health_check_interval=30
)


def get_redis():
    return redis_client


def check_redis():
    try:
        return redis_client.ping()
    except redis.RedisError:
        return False