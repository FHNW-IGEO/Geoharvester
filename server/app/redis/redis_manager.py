import os
import sys

import redis
from app.constants import REDIS_HOST, REDIS_PORT
from dotenv import load_dotenv

# Requires a redis.env file in /redis folder, containing a passwort, matching the one in a redis.conf file in the same folder
env_location = sys.path[0]+"/app/redis/redis.env"
load_dotenv(dotenv_path=env_location) 

REDIS_HOST_PASSWORD = os.getenv("REDIS_HOST_PASSWORD") 


class RedisManager(object):
    def __init__(self, *args):
        self.redis = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, password=REDIS_HOST_PASSWORD, socket_timeout=60)


r = RedisManager().redis


