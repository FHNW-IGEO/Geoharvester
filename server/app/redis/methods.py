
import uuid
from string import punctuation
from time import time
from typing import Union

import pandas as pd
from app.constants import EnumLangType, EnumProviderType, EnumServiceType
from app.redis.schemas import SVC_INDEX_ID
from fastapi.logger import logger as fastapi_logger
from langdetect import detect
from nltk.stem import SnowballStemmer
from redis.commands.search.indexDefinition import IndexDefinition, IndexType
from redis.commands.search.query import Query, SortbyField
import json

from server.app.redis.redis_manager import r

lang_dict = {'english':'en', 'french':'fr', 'german':'de', 'italian':'it'}

def check_if_index_exists(INDEX_ID):
    """Helper method as Redis does not allow for checking if an index exists, except for .info(). This however throws an exception instead of a boolean."""

    try:
         r.ft(INDEX_ID).info()
    except:
        # Return boolean instead of exception
        return False
    else:
        # Return boolean instead of info object
        return True


def create_index(PREFIX, INDEX_ID, schema):
    "Create index based on stopword, schema and index definition"
    index_def = IndexDefinition(
        index_type=IndexType.JSON,
        prefix = [PREFIX],
    )

    if(check_if_index_exists(INDEX_ID)):
        # Drop index in case it is cached by Docker
        r.ft(INDEX_ID).dropindex()
    r.ft(INDEX_ID).create_index(schema, definition = index_def)
    return


def drop_redis_db():
    "Drop redis. Return database size"

    r.flushdb()

    remaining_records = r.dbsize()
    fastapi_logger.info("Redis dropped with {} records remaining".format(remaining_records))

    return remaining_records


def ingest_data(json, KEY):
    "Ingest data from a json array and assign uuid. Return database size"

    pipeline = r.pipeline(transaction=False)

    redis_size_before_ingest = r.dbsize()

    try:
        for element in json:
            key = KEY.format(uuid.uuid4()) # Keys need to be unique
            pipeline.json().set(key, "$", element)
        pipeline.execute()

    except:
        raise Exception("ERROR: Ingestion failed")


    finally:    
        redis_size_after_ingest = r.dbsize()
        fastapi_logger.info("Redis received {} additional records".format(redis_size_after_ingest - redis_size_before_ingest))
    
    return redis_size_after_ingest


def detect_language(phrase, not_found=False):
    """
    Detects the language of a str using langdetect.

    Parameters
    ----------
    phrase : str
        String element to be elaborated
    Returns
    -------
    _ : str
        Detected language.
    """
    if not_found:
        excep = 'not_found'
    else:
        excep = 'english'
    language_dict = {'en': 'english', 'fr': 'french', 'de': 'german', 'it': 'italian'}
    try:
        lang = language_dict[detect(phrase)]
    except:
        lang = excep
    return lang


def is_not_num(str) -> bool:
    """
    Tests if a str element contains a number and return True or False.
    
    Parameters
    ----------
    str : str
          String element to be checked
    Returns
    -------
    _ : False if numeric / True if text
    """
    try:
        float(str)
        return False
    except ValueError:
        return True

def restore_capital(word: str, original_word: str):
    if not original_word.isupper() and not original_word.islower():
        w = word.capitalize()
    else:
        w = word
    return w

def stemming_sentence(list_of_words: list[str], lang: str):
    """
    Stems and cleans the words in a sentence returning a list
    of cleaned words.

    Parameters
    ----------
    sentence : [str, str]
        List of str to be stemmed
    lang : str
        language of the query in format "xx"
    Returns
    -------
    _ : list
    """
    if len(list_of_words) > 1:
        lang = detect_language(' '.join(list_of_words))
    else:
        lang = detect_language(list_of_words)

    stemmer = SnowballStemmer(lang)
    if lang != 'german':
        words_cleaned_list = [stemmer.stem(word.lower()) for word in list_of_words
                            if word not in list(punctuation) and is_not_num(word)]
    else:
        words_cleaned_list = [restore_capital(stemmer.stem(word), word) for word in list_of_words
                            if word not in list(punctuation) and is_not_num(word)]
    return words_cleaned_list


def transform_wordlist_to_query(wordlist: list[str], lang: str):
    """Whitespaces in redis queries are parsed as AND, thus this method adds pipes (|) to force OR logic.
       See: https://redis.io/docs/stack/search/reference/query_syntax/
    """
    query_string = ""
    cleaned_wordlist = stemming_sentence(wordlist, lang)
    print(f"Quering Redis with: {cleaned_wordlist} ...")
    for index, word in enumerate(cleaned_wordlist):
        query_string += "{} | ".format(word+'*') if index < (len(cleaned_wordlist)-1) else "{}".format(word+'*') # the * allows the contain opt
    return query_string


def redis_query_from_parameters(query_string: Union[str, None] = None, 
                                service: EnumServiceType = EnumServiceType.none,
                                provider:str = ""):
    """Build a query string based on the parameters provided.
    """
    queryable_parameters = []

    if (bool(query_string)):
        queryable_parameters.append(
            '@title|title_en|title_de|title_it|title_fr|abstract|abstract_en|abstract_de|abstract_it|abstract_fr|keywords|keywords_en|keywords_de|keywords_it|keywords_fr|keywords_nlp|keywords_nlp_en|keywords_nlp_de|keywords_nlp_it|keywords_nlp_fr:({})'.format(query_string)
        )

    if (bool(service)):
        queryable_parameters.append(
            '@service:({})'.format(service)
        )

    if (bool(provider)):
        queryable_parameters.append(
            '@provider:({})'.format(provider)
        )

    if (len(queryable_parameters) < 1):
        # In this case all available datasets should be returned:
        return '@service:(WMS | WMTS | WFS)'
    elif (len(queryable_parameters) == 1):
        return queryable_parameters[0]
    else:
        return "&".join(queryable_parameters)
    

def search_redis(redis_query, lang: EnumLangType, offset, limit):
    parsed_language = "french" if lang == EnumLangType.fr else "italian" if lang == EnumLangType.it else "english" if lang == EnumLangType.en else "german"
    lang_string = "fr" if lang == EnumLangType.fr else "it" if lang == EnumLangType.it else "en" if lang == EnumLangType.en else "de"
    
    return r.ft(SVC_INDEX_ID).search(Query(redis_query)
            # Define all fields that should be searched here, as limit_fields restricts searching to a list of field names:
            .limit_fields("provider", "service", "name", "keywords", "keywords_nlp", f"title_{lang_string}", f"abstract_{lang_string}", f"keywords_{lang_string}", f"keywords_nlp_{lang_string}")
            .sort_by('metaquality', asc=False)
            .paging(offset, 50000)
            .return_field('title')
            .return_field('abstract')
            .return_field('provider')
            .return_field('service')
            .return_field('name')
            .return_field('preview')
            .return_field('tree')
            .return_field('group')
            .return_field('keywords')
            .return_field('keywords_nlp')
            .return_field('legend')
            .return_field('contact')
            .return_field('endpoint')
            .return_field('metadata')
            .return_field('max_zoom')
            .return_field('center_lat')
            .return_field('center_lon')
            .return_field('bbox')
            .return_field('summary')
            .return_field('lang_3')
            .return_field('metaquality')
            .return_field(f'title_{lang}')
            .return_field(f'abstract_{lang}')
            .return_field(f'keywords_{lang}')
            .return_field(f'keywords_nlp_{lang}')
            ), parsed_language


def redis_documents_to_pandas(docs):
    """
    Convert RediSearch Document objects to a pandas DataFrame.
    """
    rows = []

    for doc in docs:
        row = {}

        for key, value in doc.__dict__.items():
            # Skip internal attributes
            if key.startswith("_"):
                continue

            # Decode Redis bytes safely
            if isinstance(value, bytes):
                value = value.decode("utf-8", errors="replace")

            row[key] = value

        rows.append(row)

    return pd.DataFrame(rows)


def pandas_to_dict(ranked_results_df):
    """
    Transform the pandas dataframe into a json-like 
    output to be passed to the front-end.
    
    Parameters
    ----------
    ranked_results_df : pandas.DataFrame
        ranked results in a data frame

    Returns
    -------
    _ : dict
        json-like output for the front-end
    """
 
    ranked_results_dict = ranked_results_df.to_dict(orient='records') # after ranking we will have an index -> orient='index' https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.to_json.html

    return ranked_results_dict

def contains_match_scoring(df, cols, word, score):
    """
    Calculate the ranking score if a word is contained
    in a pandas data frame
    
    Parameters
    ----------
    df : pandas.DataFrame
        Data frame in which we want to search
    cols : list[str]
        columns of the df in which we want to search
    word : str
        single query word
    score : int
        score we add to the row if word contained

    Returns
    -------
    _ : pd.DataFrame
        dataframe with additional score column
    """
    df_red = df[cols]
    mask = df_red.apply(lambda x: x.str.contains(word, regex=False, case=False)).any(axis=1)
    df.loc[mask, 'score'] += score
    return df

def exact_match_scoring(df, cols, word, score):
    """
    Calculate the ranking score for an exact match of
    a word in a pandas data frame
    
    Parameters
    ----------
    df : pandas.DataFrame
        Data frame in which we want to search
    cols : list[str]
        columns of the df in which we want to search
    word : str
        single query word
    score : int
        score we add to the row if word exact matched

    Returns
    -------
    _ : pd.DataFrame
        dataframe with additional score column
    """
    df_red = df[cols]
    mask = df_red.apply(lambda x: x.str.match(word, case=False)).any(axis=1)
    df.loc[mask, 'score'] += score
    return df

def evaluate_metaquality(df, denominator):
    """
    Calculate the ranking score based on the metadata quality
    
    Parameters
    ----------
    df : pandas.DataFrame
        Data frame in which we want to elaborate
    denominator : int
        number by which the metadata score mus be divisible

    Returns
    -------
    _ : pd.DataFrame
        dataframe with recalculated score column
    """
    df['score'] *= df['metaquality'] / denominator
    return df

def results_ranking(redis_output, query_words_list, known_terms, parsed_lang):
    """
    Ranks the results according to the assigned scores
    
    Parameters
    ----------
    redis_output : pd.DataFrame
        output from redis search
    redis_et : float
        elapsed time for the redis search
    query_words_list : list[str]
        query words splitted into a list

    Returns
    -------
    _ : pd.DataFrame
        ranked data frame (descending)
    """
    t0 = time()
    query_results_df = redis_documents_to_pandas(redis_output)

    if query_results_df.empty:
        return None
    
    query_results_df['title'] = query_results_df.get('title', '').fillna('').astype(str)
    query_results_df['metaquality'] = (
        pd.to_numeric(query_results_df.get('metaquality', 0), errors='coerce')
        .fillna(0)
        .astype(int)
    )

    # initialize ranking score and the length counter
    lang = lang_dict[parsed_lang]
    for col in [
        'keywords_nlp',
        f'title_{lang}', f'keywords_{lang}', f'keywords_nlp_{lang}'
    ]:
        if col not in query_results_df:
            query_results_df[col] = ""

    if len(query_results_df) > 0:
        query_results_df['score'] = 0
        query_results_df['inv_title_length'] = 200 - query_results_df['title'].str.len()

        # Calculate the scores
        if query_words_list:
            print(f"Sorting results with: {query_words_list} ...")
            for query_word in query_words_list:
                bs = 1
                if query_word in known_terms:
                    bs += 2
                query_results_df = exact_match_scoring(query_results_df, ['title', 'keywords_nlp'], query_word, 1)
                query_results_df = contains_match_scoring(query_results_df, ['title_'+lang, 'keywords_'+lang], query_word, 4)
                query_results_df = contains_match_scoring(query_results_df, ['keywords_nlp_'+lang], query_word, 2)
                query_results_df = exact_match_scoring(query_results_df, ['title_'+lang, 'keywords_'+lang], query_word, bs + 5)
                query_results_df = exact_match_scoring(query_results_df, ['keywords_nlp_'+lang], query_word, bs + 2)
        else:
            query_results_df['score'] = 1
        query_results_df = evaluate_metaquality(query_results_df, 25)


        query_results_df.sort_values(by=['score', 'inv_title_length', 'title'], axis=0, inplace=True, ascending=False)
        # Replace nans with empty str for a cleaner visualisation
        query_results_df = query_results_df.replace(to_replace='nan', value="", regex=True)

        ranked_results = pandas_to_dict(query_results_df)
        # print(f'ET ranking: {round(time()-t0, 2)}')
    else:
        ranked_results = None
    json.dumps(ranked_results)

    return ranked_results
