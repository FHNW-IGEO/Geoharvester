import pandas as pd
import re
from gpt4all import GPT4All
from langdetect import detect
from cog.torque import Graph

def collect_keywords(kwds:list, kwds_lang:str, trns_dict:dict,
                         df_kg:pd.DataFrame)->pd.DataFrame:
    """
    ----
    """
    df = pd.DataFrame({kwds_lang: kwds})
    translations = {}
    for lang in [k for k in trns_dict.keys()]:
        llama_translation = ask_llama(trns_dict[lang], ", ".join(kwds))
        translations[lang] = read_translation(llama_translation)
    if check_length(translations, len(kwds)):
        for lang in [k for k in trns_dict.keys()]:
            df[lang] = translations[lang]
        df_kg = pd.concat([df_kg, df], axis=0, ignore_index=True)
    else:
        print("Skipping differing translation lengths!")

    return df_kg

def read_translation(response:str)->list:
    """
    
    """
    if response:
        response = response.split("\n\n")[1]
        translation = [w.strip() if ' ' in w else w.replace('.','') for w in response.split(", ")]
    else:
        translation = []
    return translation

def read_keyowrds(response:str)->list:
    """
    ...
    """
    if response:
        response = response.split("\n\n")[1]
        kwds = [w.strip() if ' ' in w else w for w in response.split(", ")]
    else:
        kwds = []
    return kwds


def ask_llama(task:str, payload:str,
              model_name:str='Meta-Llama-3-8B-Instruct.Q4_0.gguf')->str:
    """
    ----
    """
    model = GPT4All(model_name)
    with model.chat_session():
        response = model.generate(f"{task} : {payload}")
    return response

def verify_response(response:str, languages:list, idx:int):
    """
    ----
    """
    check = True
    for lang in languages:
        if lang not in response:
            print(f"{lang} not in response at index {idx}")
            print(response)
            check = False
    return check
    

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
        exception = 'not_found'
    else:
        exception = 'english'
    language_dict = {'en': 'english', 'fr': 'french', 'de': 'german', 'it': 'italian'}
    try:
        lang = language_dict[detect(phrase)]
    except:
        lang = exception
    return lang

def check_length(translations:dict, length:int):
    for translation in translations.values():
        if len(translation) != length:
            return False
        
    return True

def open_knowledge_graph(cog_home:str, kg_name:str)->Graph:
    return Graph(kg_name, cog_home=cog_home)
def generate_knowledge_graph(kg_data_path:str, cog_home:str,
                             load_synonyms:bool=False, update:bool=False):
    """
    initializes the knowledge graph loading the data from the dataframe
    Parameters
    ----------
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
    kg = Graph("Geoharvester", cog_home=cog_home)
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
        print("No edges found")
    return response

def traverse_knowledge_graph(kg:Graph, language:str, query:str)->list:
    """
    traverses the graph to find terms in the query.
    """
    lang_terms = find_nodes_by_language(kg, language)
    return [t for t in lang_terms if t in query]


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