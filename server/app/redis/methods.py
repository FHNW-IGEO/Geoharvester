
import uuid

import redis
from app.constants import REDIS_HOST, REDIS_PORT
from redis.commands.search.indexDefinition import IndexDefinition, IndexType

r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT)


def check_if_index_exists(index_key):
    """Helper method as Redis does not allow for checking if an index exists, except for .info(). This however throws an exception instead of a boolean."""

    try:
         r.ft(index_key).info()
    except:
        # Return boolean instead of exception
        return False
    else:
        # Return boolean instead of info object
        return True


def create_index(PREFIX, INDEX_KEY, schema):
    index_def = IndexDefinition(
        index_type=IndexType.JSON,
        prefix = [PREFIX],
    )

    if(check_if_index_exists(INDEX_KEY)):
        # Drop index in case it is cached by Docker
        r.ft(INDEX_KEY).dropindex()
    r.ft(INDEX_KEY).create_index(schema, definition = index_def)
    return


def drop_redis_db(PREFIX):
    "Drop redis records with given prefix. Return database size"

    for key in r.keys('{}*'.format(PREFIX)):
        r.delete(key)

    remaining_records = r.dbsize()
    print("--- Redis dropped with {} records remaining".format(remaining_records))

    return remaining_records


def ingest_data(json, SERVICE_KEY):
    "Ingest data from a json array and assign uuid. Return database size"

    pipeline = r.pipeline(transaction=False)

    redis_size_before_ingest = r.dbsize()

    try:
        for element in json:
            key = SERVICE_KEY.format(uuid.uuid4()) # Keys need to be unique
            pipeline.json().set(key, "$", element)
        pipeline.execute()

    except:
        raise Exception("ERROR: Ingestion failed")

    finally:    
        redis_size_after_ingest = r.dbsize()
        print("--- Redis received {} additional records".format(redis_size_after_ingest - redis_size_before_ingest))
    
    return redis_size_after_ingest
