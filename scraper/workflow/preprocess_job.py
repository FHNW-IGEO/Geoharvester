# -*- coding: utf-8 -*-
import logging
import logging.config
import sys
import warnings
from pathlib import Path
from time import time
import pandas as pd

sys.path.append('../')
import scraper.configuration as config
import scraper.utils as utils

# globals
warnings.filterwarnings('ignore')

# Initialize and configure the logger
logging.config.dictConfig(config.LOGGING_CONFIG)
logger = logging.getLogger("Scraping log")

# Only these will be processed, no longer full scrape of everything
SCRAPED_DATA = Path("../artifacts/scrape_job_output.pkl")
OUTPUT_CSV = Path("preprocessed_data.csv")
OUTPUT_PKL = Path("preprocessed_data.pkl")

def preprocessing_NLP(raw_data_path, column='abstract'):
    """
    Preprocesses the data collected by the scraper using different NLP
    functions, which are stored in preprocessing/utils.py

    Parameters
    ----------
    raw_data_path : str
        path of pickle file containing the new raw data output of the scraper
    column : str
        column of the dataframe to be used for the NLP preprocessing
    """
    t0 = time()
    # Read the data
    raw_data = pd.read_pickle(raw_data_path)
    raw_data = raw_data.fillna("nan") # needed for the preprocessing
    # Extract the keywords and add them to the data
    NLP = utils.NLP_spacy()
    keywords_dataset = NLP.extract_refined_keywords(raw_data, use_rake=True, column=column, keyword_length=3, num_keywords=15)
    def join_keywords(keywords_list):
        keywords = ', '.join(kw for kw in keywords_list)
        return keywords
    raw_data['keywords_nlp'] = list(map(join_keywords, keywords_dataset))
    t1 = time()
    print(f"Keywords extracted succesfully in {t1-t0} seconds")
    # Summarize the abstracts and add them to the data
    # summaries = NLP.summarize_texts(raw_data, column=column)
    raw_data['summary'] = ['summary']*len(raw_data)#summaries
    t2 = time()
    # print(f"Abstracts summarized succesfully in {t2-t1} seconds")
    # Add the detected dataset language (applied on title)
    language_dict = {'english':('EN', 'ENG'), 'french':('FR','FRA'), 'german':('DE','DEU'), 'italian':('IT','ITA'), 'not_found':('NA','NAN')}
    raw_data['lang_3'] = raw_data.apply(lambda row: language_dict[utils.detect_language(row['abstract'], not_found=True)][1], axis=1)
    raw_data['lang_2'] = raw_data.apply(lambda row: language_dict[utils.detect_language(row['abstract'], not_found=True)][0], axis=1)
    raw_data['lang_3'] = raw_data.apply(lambda row: language_dict[utils.detect_language(row['title'], not_found=True)][1] if row['lang_3']=='NAN' else row['lang_3'], axis=1)
    raw_data['lang_2'] = raw_data.apply(lambda row: language_dict[utils.detect_language(row['title'], not_found=True)][0] if row['lang_2']=='NAN' else row['lang_2'], axis=1)
    t3 = time()
    print(f"Languages detected succesfully in {t3-t2} seconds")

    # Check and add metadata quality
    print(f"Adding metadata scores...")
    raw_data = utils.check_metadata_quality(raw_data, search_word='nan',
                                            search_columns=['abstract', 'keywords', 'metadata','contact'],
                                            case_sensitive=False)
    
    # Characters cleaning for compatibility with redis -> Already done by checking the new data
    print(f"Cleaning up metadata...")
    raw_data = raw_data.replace(to_replace="\'", value=" ", regex=True)
    raw_data = raw_data.replace(to_replace='\"', value="-", regex=True)
    # raw_data = raw_data.replace(to_replace="  ", value = " ", regex=True)
    # raw_data = raw_data.replace(to_replace="    ", value = " ", regex=True)
    
    return raw_data

if __name__ == "__main__":
    """
    Preprocess the data using NLP: Calls the preprocessing_NLP function
    reading the csv, preprocessing the data and generating a pickle
    """
    process_startT=time()

    preprd_data = preprocessing_NLP(SCRAPED_DATA)
    preprd_data.to_pickle(OUTPUT_PKL)
    preprd_data.to_csv(OUTPUT_CSV, index=False)

    process_endT = time()
    logger.info(f"Wrote outputs: {OUTPUT_CSV}, {OUTPUT_PKL}")
    logger.info(f"Job took: {int((process_endT-process_startT) / 60)} mins")
