
import json
import logging
import os
import warnings
from time import time
from typing import Union, Optional
from redis.commands.search.query import Query

from app.constants import (DEFAULTSIZE, EnumLangType, EnumProviderType,
                           EnumServiceType)
from app.processing.methods import ( generate_knowledge_graph,
                                    import_pkl_into_dataframe, sanitize_and_kg_check,
                                    )
from app.redis.methods import (create_index, drop_redis_db, ingest_data,
                               redis_query_from_parameters, results_ranking, redis_query_from_keywords,
                               search_redis_with_parameters, search_redis_with_keywords )
from app.redis.schemas import (SVC_INDEX_ID, SVC_KEY, SVC_PREFIX,
                               GeoserviceModel, geoservices_schema, KeywordHistogram)
from fastapi import FastAPI, HTTPException
from fastapi.logger import logger as fastapi_logger
from fastapi.middleware.cors import CORSMiddleware
from fastapi_pagination import Page, add_pagination, paginate
from fastapi_pagination.customization import CustomizedPage, UseParamsFields
from collections import Counter
import json


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
language_dict = {'en': 'english', 'fr': 'french', 'de': 'german', 'it': 'italian'}

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



@app.get(
    "/api/getData",
    response_model=GeoharvesterPage[GeoserviceModel],
)
async def get_data(
    query_string: Union[str, None] = None,
    service: EnumServiceType = EnumServiceType.none,
    provider: EnumProviderType = EnumProviderType.none,
    lang: EnumLangType = EnumLangType.de,
    page: int = 0,
    limit: int = 50000,
):
    """Route for the get_data request
        query: The query string used for searching
        service: Service filter - wms, wmts, wfs
        provider: Provider filter
        lang: Language parameter to optimize search
        limit: Redis returns 10 results by default, allow more results to be returned
        service: Service enum, either WMS, WMTS, WFS
    """
    t0 = time()

    # Search step
    try:
        if not query_string:
            redis_query = "@service:(WMS | WMTS | WFS)"
            redis_data, _ = search_redis_with_parameters(redis_query, lang, 0, limit)
            return paginate(redis_data.docs)

        if len(query_string) < 1:
            print("Query string too short")
            return paginate([])

        known_terms, word_list_clean, text_query = sanitize_and_kg_check(query_string, kg, language_dict, lang)
        print(text_query)

        if isinstance(text_query, list):
            text_query = " ".join(text_query)

        redis_query = redis_query_from_parameters(text_query, service, provider, lang.value)
        redis_data, parsed_language  = search_redis_with_parameters(redis_query, lang,  0, limit)

        t1 = time()
        print(
            f"Redis queried in {round(t1 - t0, 2)} seconds"
        )

    except Exception as e:
        print("Redis query failed")
        print(e)
        raise HTTPException(
            status_code=500,
            detail="Search backend failed",
        ) from e

    # Abort if no results found
    if not redis_data.docs:
        fastapi_logger.info("Redis returned 0 documents")
        return paginate([])

    # Ranking step
    try:
        ranked_results = results_ranking(
            redis_data.docs,
            word_list_clean,
            known_terms,
            parsed_language
        )
        fastapi_logger.info(
            f"Ranking ET: {round(time() - t1, 2)} (lang={parsed_language})"
        )
    except Exception as e:
        fastapi_logger.exception("Ranking failed")
        print(e)
        raise HTTPException(
            status_code=500,
            detail="Result ranking failed",
        ) from e

    if not ranked_results:
        fastapi_logger.info("Ranking produced 0 results")
        return paginate([])

    return paginate(ranked_results)

@app.get(
    "/api/getDataByKeywords",
    response_model=GeoharvesterPage[GeoserviceModel],
)
async def get_data_by_keywords(
    query_string: Optional[str] = None,
    lang: EnumLangType = EnumLangType.de,
    page: int = 0,
    limit: int = 50000,
):
    if not query_string or len(query_string) <= 1:
        fastapi_logger.debug("Empty or too short query_string")
        return paginate([])

    try:
        t1 = time()

        known_terms, word_list_clean, text_query = sanitize_and_kg_check(
            query_string, kg, language_dict, lang
        )

        redis_query = redis_query_from_keywords(text_query, lang.value)

        redis_data, parsed_language = search_redis_with_keywords(
            redis_query, lang, 0, limit
        )

    except Exception as e:
        fastapi_logger.exception("Failed during preprocessing / Redis search")
        print(e)
        raise HTTPException(
            status_code=500,
            detail="Internal error while querying data store",
        )

    if not redis_data.docs:
        fastapi_logger.info("No Redis documents found")
        return paginate([])

    try:
        ranked_results = results_ranking(
            redis_data.docs,
            word_list_clean,
            known_terms,
            parsed_language
        )
        fastapi_logger.info(
            "Ranking ET: %.2fs (lang=%s)",
            time() - t1,
            parsed_language,
        )

    except Exception as e:
        fastapi_logger.exception("Ranking failed")
        raise HTTPException(
            status_code=500,
            detail="Internal error while ranking results",
        )

    if not ranked_results:
        fastapi_logger.info("Ranking returned no results")
        return paginate([])

    return paginate(ranked_results)

@app.get(
    "/api/getKeywordHistogram",
    response_model=list[KeywordHistogram],
)
async def build_keyword_histogram(field: str= "keywords_nlp"):
    """
    Build a histogram of values for a given JSON field.

    :param redis_client: redis connection
    :param index_name: RediSearch index name
    :param field: JSON field name (e.g. "keywords", "keywords_nlp")
    :return: List of (keyword, count) sorted by frequency desc
    """

    counter = Counter()

    # Get all document IDs via FT.SEARCH (fast and indexed)
    res = r.ft(SVC_INDEX_ID).search(Query("*").paging(0, 1000000))

    for doc in res.docs:
        key = doc.id

        # Fetch raw JSON
        raw = r.json().get(key)

        if not raw or field not in raw:
            continue

        value = raw[field]

        # If array field
        if isinstance(value, list):
            for v in value:
                if isinstance(v, str) and v.strip():
                    counter[v.strip().lower()] += 1

        # If single string field
        elif isinstance(value, str):
            tokens = value.split()
            for token in tokens:
                token = token.strip().lower()
                if token:
                    counter[token] += 1

    # Sort by frequency descending
    sorted_keywords = sorted(counter.items(), key=lambda x: x[1], reverse=True)
    print(sorted_keywords)
    return [
        KeywordHistogram(keyword=keyword, count=count)
        for keyword, count in sorted_keywords
    ]   



add_pagination(app)