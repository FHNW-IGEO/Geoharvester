
import json
import logging
import os
import re
import warnings
from time import time
from typing import Union

from app.constants import (DEFAULTSIZE, EnumLangType, EnumProviderType,
                           EnumServiceType)
from app.processing.methods import (find_translation, generate_knowledge_graph,
                                    import_pkl_into_dataframe,
                                    open_knowledge_graph, split_search_string,
                                    traverse_knowledge_graph)
from app.redis.methods import (create_index, drop_redis_db, ingest_data,
                               redis_query_from_parameters, results_ranking,
                               search_redis, transform_wordlist_to_query)
from app.redis.schemas import (SVC_INDEX_ID, SVC_KEY, SVC_PREFIX,
                               GeoserviceModel, geoservices_schema)
from fastapi import FastAPI, Query
from fastapi.logger import logger as fastapi_logger
from fastapi.middleware.cors import CORSMiddleware
from fastapi_pagination import Page, add_pagination, paginate
from fastapi_pagination.customization import CustomizedPage, UseParamsFields
from nltk.corpus import stopwords
from pydantic import Field

from server.app.redis.redis_manager import r

# filter package warnings
warnings.simplefilter("ignore")

origins = [
    # Adjust to your frontend localhost port if not default
    "http://localhost:3000"
]
app = FastAPI(
    debug=True,
    version="0.2.0",
    docs_url='/api/docs',
    redoc_url='/api/redoc',
    openapi_url='/api/openapi.json'
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Logging:
gunicorn_logger = logging.getLogger('gunicorn.error')
fastapi_logger.handlers = gunicorn_logger.handlers
if __name__ != "main":
    fastapi_logger.setLevel("DEBUG")
else:
    fastapi_logger.setLevel(logging.DEBUG)


# Pagination settings. Adjust FE table calculations accordingly when changing these!
GeoharvesterPage = CustomizedPage[
    Page,
    UseParamsFields(size=DEFAULTSIZE)
]


dataframe=None
datajson=None

@app.on_event("startup")
async def startup_event():
    """Startup Event: Load csv into data frame and knwoledge graph"""
    # Overwrite config limit for a maximum of 10000 search results:
    r.ft().config_set("MAXSEARCHRESULTS", "-1" )

    global dataframe, kg
    url_github_repo = "https://raw.githubusercontent.com/FHNW-IGEO/Geoharvester/main/"
    url_geoservices_CH_pkl = os.path.join(url_github_repo, 'scraper/data/', "merged_data.pkl")
    dataframe = import_pkl_into_dataframe(url_geoservices_CH_pkl)
    url_kg_dataframe = os.path.join(url_github_repo, 'knowledge_graph', "kg_data.pkl")
    t0 = time()
    kg = generate_knowledge_graph('GeoHarvester', url_kg_dataframe, "knowledge_graph",
                                  load_synonyms=True)
    print(f"Knowledge graph generated in {round(time() - t0,2)} seconds")
    
    global datajson
    datajson = json.loads(dataframe.to_json(orient='records'))

    try:
        # Flush DB on startup
        drop_redis_db()

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


# Can be removed:
# @app.get("/api")
# async def root():
#     '''Root endpoint'''

#     return {"message": "running"}

@app.get("/api/getData", response_model=GeoharvesterPage[GeoserviceModel])
async def get_data(query_string: Union[str, None] = None,  service: EnumServiceType = EnumServiceType.none, provider:EnumProviderType = EnumProviderType.none, lang: EnumLangType = EnumLangType.de, page: int = 0, limit: int = 1000):
    """Route for the get_data request
        query: The query string used for searching
        service: Service filter - wms, wmts, wfs
        provider: Provider filter
        lang: Language parameter to optimize search
        limit: Redis returns 10 results by default, allow more results to be returned
        service: Service enum, either WMS, WMTS, WFS
    """

    t0 = time()
    if (query_string is None or query_string == ""):
        redis_query = redis_query_from_parameters("", service, provider)
        fastapi_logger.info("Redis queried without query_text: {}".format(redis_query))

        redis_data, parsed_language = search_redis(redis_query, lang, 0, 40000)
        # print(f"Total ET query: {round((time()-t0),2)}")
        return paginate(redis_data.docs)

    elif (query_string is not None and len(query_string) > 1):
        language_dict = {'en': 'english', 'fr': 'french', 'de': 'german', 'it': 'italian'}
        # Traverse knowledge graph for search terms
        known_terms = traverse_knowledge_graph(kg, language_dict[lang], query_string)
        for known_term in known_terms:
            if len(known_term.split()) == 1:
                known_terms.remove(known_term)
        print(f"Known terms and synonyms from KG: {known_terms}")
        # create word list without known terms
        word_list = split_search_string(query_string, known_terms)
        # stop words removal just for redis
        stop_words = stopwords.words(language_dict[lang])
        word_list_clean = [re.escape(word) for word in word_list if word not in stop_words] # Escape all special chars except _, otherwise Redis throws error
        text_query = transform_wordlist_to_query(word_list_clean, lang)

        redis_query = redis_query_from_parameters(text_query, service, provider)
        fastapi_logger.info("Redis queried with: {}".format(redis_query))

        redis_data, parsed_language = search_redis(redis_query, lang, 0, 40000)
        t1 = time()
        fastapi_logger.info(f"Redis queried in {round(t1-t0,2)} seconds")

        # print(redis_data.docs)

        if len(redis_data.docs) > 0:
            
            ranked_results = results_ranking(redis_data.docs, word_list_clean, known_terms, parsed_language)
            fastapi_logger.info(f"Ranking ET: {round((time()-t1),2)} on columns with lang={parsed_language}")
            if ranked_results:
                return paginate(ranked_results)
            else:
                pass
        else:
            pass
    else:
        print("Error...")

    return paginate([])

add_pagination(app)