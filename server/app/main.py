
import json
import logging
from typing import Union

import pandas as pd
import redis
from app.constants import REDIS_HOST, REDIS_PORT, url_geoservices_CH_csv
from app.processing.methods import (import_csv_into_dataframe,
                                    search_by_terms_dataframe,
                                    split_search_string)
from app.redis.methods import (create_index, drop_redis_db, ingest_data,
                               transform_wordlist_to_query)
from app.redis.schemas import (SVC_INDEX_ID, SVC_KEY, SVC_PREFIX,
                               geoservices_schema)
from fastapi import FastAPI
from fastapi.logger import logger as fastapi_logger
from fastapi.middleware.cors import CORSMiddleware
from redis import StrictRedis
from redis.commands.search.query import Query

app = FastAPI(debug=True)

dataframe=None
datajson=None
csv_row_limit= 5000
r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT)

origins = [
    # Adjust to your frontend localhost port if not default
    "http://localhost:3000"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

gunicorn_logger = logging.getLogger('gunicorn.error')
fastapi_logger.handlers = gunicorn_logger.handlers
if __name__ != "main":
    fastapi_logger.setLevel("DEBUG")
else:
    fastapi_logger.setLevel(logging.DEBUG)

@app.on_event("startup")
async def startup_event():
    """Startup Event: Load csv into data frame"""
    global dataframe

    # To reduce traffic we load the file from ./tmp instead from Github. Remove this and the next line for prod / demo use:
    url_geoservices_CH_csv = "app/tmp/geoservices_CH.csv"
    dataframe =  import_csv_into_dataframe(url_geoservices_CH_csv)
    
    global datajson
    datajson = json.loads(dataframe.to_json(orient='records'))

    try:
        # Flush DB on startup
        drop_redis_db(SVC_PREFIX)

        create_index(SVC_PREFIX, SVC_INDEX_ID, geoservices_schema)

        ingest_data(datajson, SVC_KEY)

    except:
            raise Exception("ERROR: Redis data import failed")
    finally:
        # Index Debugging:
        # print(r.ft(INDEX_KEY).info())

        # Verify database is up and running:
        total_keys = r.dbsize()
        fastapi_logger.info("Redis initialized with {} records".format(total_keys))



@app.get("/")
async def root():
    '''Root endpoint'''

    return {"message": "running1"}

@app.get("/getServerStatus")
async def get_server_status():
    '''Helper method for client'''
    return {"message": "running"}

@app.get("/getDataFromPandas")
async def get_data_from_pandas(query: Union[str, None] = None):
    """Route for the get_data request (search by terms) targeted at pandas dataframe"""

    if (query == None):
        return {"data": ""}

    word_list = split_search_string(query)

    dataframe_some_cols = import_csv_into_dataframe(url_geoservices_CH_csv, csv_row_limit)
    search_result = search_by_terms_dataframe(word_list, dataframe_some_cols)
    fastapi_logger.info(search_result)
    payload = search_result

    return {"data": payload}


@app.get("/getDataFromRedis")
async def get_data_from_redis(query: Union[str, None] = None, lang: str = "german", limit: int = 100):
    """Route for the get_data request (search by terms) targeted at redis
        query: The query string used for searching
        lang: Language parameter to optimize search
        limit: Redis returns 10 results by default, allow more results to be returned
    """
    search_result = {
        "total": 0,
        "docs": None,
        "fields": [],
        "duration": 0,
    }

    if (query == None):
        return {"data": search_result}

    word_list = split_search_string(query)
    print(transform_wordlist_to_query(word_list))

    redis_data = r.ft(SVC_INDEX_ID).search(Query('@TITLE|ABSTRACT:({})'.format(query))                     
        .language(lang)                                   
        .paging(0, limit) # offset, limit
        .return_field('NAME')
        .return_field('OWNER')
        .return_field('TITLE')
        .return_field('ABSTRACT'))

    search_result["docs"] = redis_data.docs
    search_result["fields"] = []
    search_result["duration"] = redis_data.duration
    search_result["total"] = len(redis_data.docs)

    return {"data": search_result}