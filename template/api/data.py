from redis import Redis
redis = Redis()

def set_redis(db=None, host=None, port=None, password=None, socket_timeout=None):
    redis.select(db, host, port, password, socket_timeout)
