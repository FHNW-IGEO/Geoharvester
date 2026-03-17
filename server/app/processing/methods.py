import re
import shlex
from typing import List
from cog.torque import Graph
from nltk.corpus import stopwords

import pandas as pd

from ..constants import fields_to_output
from ..redis.methods import transform_wordlist_to_query


def import_csv_into_dataframe(url, column_limit=None):
    """Load csv into data frame"""
    if(column_limit):
        dataframe = pd.read_csv(url, nrows=column_limit)
    else: 
        dataframe = pd.read_csv(url, low_memory=False)

        dataframe.fillna('', inplace=True)
    return dataframe

def import_pkl_into_dataframe(url):
    """
    Load a pickle into a data frame
    """
    return pd.read_pickle(url)

def split_search_string(query: str, known_terms: List[str]) -> List[str]:
    """Split the incoming request by delimiter to create a list of terms"""
    query_clean = query
    if known_terms:
        for term in known_terms:
            if len(term.split()) > 1:
                query_clean = query_clean.replace(term, "")
    if len(query_clean.split()) > 0:
        query = query_clean
    word_list_with_delimiters = shlex.split(query)

    def split_delimiters(word_list_with_delimiters: List[str]) -> List[str]:
        """Take care of left over delimiters, split strings even if in qoutes
           Return a list of words """
        delimiters = [";", ","]

        new_word_list = []

        for word in word_list_with_delimiters:
            if (any(delimiter in word for delimiter in delimiters)):
                splitted_words = re.split(r',|;', word)
                for splitted_word_ in splitted_words:
                    new_word_list.append(splitted_word_)
            else:
                new_word_list.append(word)
        return new_word_list

    # Also split terms with delimiters
    word_list_without_delimiters = split_delimiters(word_list_with_delimiters)

    strings_to_remove = [""]
    filtered_word_list = list(filter(lambda string: string not in strings_to_remove, word_list_without_delimiters))

    # Trim whitespaces of terms which may originate from splitting:
    trimmed_word_list = list(map(lambda string: string.strip(), filtered_word_list))
    if trimmed_word_list:
        trimmed_word_list.extend(known_terms)
        return trimmed_word_list
    else:
        return known_terms


def search_by_terms_dataframe(word_list: List[str], dataframe):
    """Search the geodata collection based on the search terms
       Return response object aligned with redis response format"""

    search_result = {}
    docs = []
    total = 0

    try:
        for term in word_list:
            result = dataframe[dataframe.apply(lambda dataset: dataset.astype(str).str.contains(term, case=False).any(), axis=1)]

            result_without_nan = result.fillna("")
            truncated_dataframe = result_without_nan[fields_to_output]

            # This does not handle duplicates at all:
            docs += truncated_dataframe.values.tolist()
            total += len(result_without_nan)
            search_result["fields"] = truncated_dataframe.columns.tolist()
    except:
        raise Exception

    finally:
        search_result["total"] = total
        search_result["duration"] = 99
        search_result["docs"] = docs

    return search_result


def open_knowledge_graph(cog_home:str, kg_name:str)->Graph:
    return Graph(kg_name, cog_home=cog_home)
def generate_knowledge_graph(kg_name:str,kg_data_path:str, cog_home:str,
                             load_synonyms:bool=False, update:bool=False):
    """
    initializes the knowledge graph loading the data from the dataframe
    Parameters
    ----------
    kg_name : str
        name of the knowledge graph
    kg_data : pd.DataFrame
        data frame with the data to be loaded
    cog_home : str
        path of the cog home
    load_synonyms : bool
        if the synonyms should be built (requires more time)
    update : bool
        if the knowledge graph should be updated

    Returns
    -------
    _: Graph
        initialized graph
    """
    kg = Graph(kg_name, cog_home=cog_home)
    print("KG: Filtering translations...")
    kg_data = pd.read_pickle(kg_data_path)
    kg_data = filter_translations(kg_data)
    print("KG: Loading data in the knowledge graph...")
    for i, row in kg_data.iterrows():
        kg.put(row["ENG"].lower(), "means", row["DEU"].title(), update=update)
        kg.put(row["ITA"].lower(), "means", row["DEU"].title(), update=update)
        kg.put(row["FRA"].lower(), "means", row["DEU"].title(), update=update)
        kg.put(row["DEU"].title(), "lang", "german", update=update)
        kg.put(row["FRA"].lower(), "lang", "french", update=update)
        kg.put(row["ENG"].lower(), "lang", "english", update=update)
        kg.put(row["ITA"].lower(), "lang", "italian", update=update)
    if load_synonyms:
        print("KG: Building synonyms...")

        build_synonyms(kg, "german", ["english", "french", "italian"])
    return kg

def filter_translations(kg_data:pd.DataFrame):
    """
    Filters rows if all languages are the same
    Parameters
    """
    for i, row in kg_data.iterrows():
        if row["DEU"].lower().replace(" ", "") == row["ENG"].lower().replace(" ", "") == row["ITA"].lower().replace(" ", "") == row["FRA"].lower().replace(" ", ""):
            kg_data.drop(i, inplace=True)
    return kg_data

def build_synonyms(kg:Graph, reference_language:str,
                   synonyms_languages:list, update:bool=False)->None:
    """
    builds synonyms basing on the reference language (german) for all other languages
    """
    for reference in find_nodes_by_language(kg, reference_language):
        for lang in synonyms_languages:
            assert lang in ["english", "french", "german", "italian"], "Invalid language encountred"
            trns = [k['id'] for k in kg.v(vertex=reference).inc("means").has('lang', lang).all()['result']]
            if len(trns) > 1:
                for word in trns:
                    for synonym in trns:
                        if word != synonym:
                            kg.put(word, "synonym", synonym, update=update)

def find_nodes_by_language(kg:Graph, language:str)->list:
    """
    Returns all incoming edges from a given language vertex
    """
    assert language in ["english", "french", "german", "italian"], "Invalid language"
    response = [k['id'] for k in kg.v(vertex=language).inc().all()['result']]
    if not response:
        print("No nodes found")
    else:
        node_list = []
        # remove duplicates
        for w in response:
            if w not in node_list:
                node_list.append(w)
    return node_list

def traverse_knowledge_graph(kg:Graph, language:str, query:str)->list:
    """
    traverses the graph to find terms in the query.
    """
    terms_synonyms = []
    lang_terms = find_nodes_by_language(kg, language)
    known_terms = [t for t in lang_terms if t in query]
    if known_terms:
        for known_term in known_terms:
            synonyms = find_sysnoms(kg, known_term)
            if synonyms:
                terms_synonyms.extend(synonyms)
    terms_synonyms.extend(known_terms)
    return terms_synonyms

def find_sysnoms(kg:Graph, text:str)->list:
    return [k['id'] for k in kg.v(vertex=text).inc("synonym").all()['result']]

def find_translation(kg:Graph, text:str, verify_language:str=None)->list:
    # TODO: Maybe a dictionary would be better using .has('lang', 'german')
    if verify_language:
        assert verify_language in ["english", "french", "german", "italian"], "Invalid language"
        graph_lang = kg.v(vertex=text).out("lang").all()['result'][0]['id']
        assert graph_lang == verify_language, "Language mismatch"
    if graph_lang != "german":
        text = kg.v(vertex=text).out("means").all()['result'][0]['id']
    translations = [k['id'] for k in kg.v(vertex=text).inc("means").all()['result']]
    translations.append(text)
    return translations

def sanitize_and_kg_check(query_string, kg,language_dict, lang ):
    if not query_string:
        return [] , [],  ""
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
    return known_terms, word_list_clean, text_query