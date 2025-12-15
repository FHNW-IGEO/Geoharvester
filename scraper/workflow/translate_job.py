"""
title: The ultimate translator for GeoHarvester
Author: Elia Ferrari
Date: 2024-04-29
"""

import logging
import logging.config
import os
import sys
from time import time

import pandas as pd

sys.path.append('../')

import scraper.configuration as config
import scraper.utils as utils

# Initialize and configure the logger
logging.config.dictConfig(config.LOGGING_CONFIG)
logger = logging.getLogger("Scraping log")


def translate_new_data(db, translate_column, languages, one_shot=True):
    """
    Translates the preprocessed data

    Parameters
    ----------
    db : df
        Dataframe to be translated
    translate_column : string
        Column name from the list of columns to translate as defined in WORKFLOW_TRANSLATE_COLUMNS
    languages : list
        Language to translate into, defined by LANG_FROM_PIPELINE
    one_shot : bool
        if true, it will translate all the data in one shot

    Output 
    ----------
    <language_abbr>_translated.pkl : pickle
        Outputs a pickle file of the translation which is uploaded as artifact to github
    """

    db = db.fillna("nan")
    chunk_size = 200
    for lang in languages:
        new_col = translate_column+'_'+lang
        if not one_shot:
            if translate_column == 'title':
                tlang1 = time()
                db[new_col] = db.apply(lambda row: utils.translate_text(
                    row[translate_column],to_lang=lang, from_lang=row['lang_3']), axis=1)
                tlang2 = time()
                logger.info(f"Processed 'Title' in {lang} {round(tlang2-tlang1)} s'")
            elif translate_column == 'abstract':
                tlang1 = time()
                db[new_col] = db.apply(lambda row: utils.translate_abstract(
                    row[translate_column], to_lang=lang, from_lang=row['lang_3']), axis=1)
                tlang2 = time()
                logger.info(f"Processed 'Abstract' in {lang} {round(tlang2-tlang1)} s'")
            elif translate_column == 'keywords':
                tlang1 = time()
                db[new_col] = db.apply(lambda row: utils.translate_keywords(
                    row[translate_column], to_lang=lang, from_lang=row['lang_3']), axis=1)
                tlang2 = time()
                logger.info(f"Processed 'Keywords' in {lang} {round(tlang2-tlang1)} s'")
            elif translate_column == 'keywords_nlp':
                tlang1 = time()
                db[new_col] = db.apply(lambda row: utils.translate_keywords(
                    row[translate_column].split(','), to_lang=lang, from_lang=row['lang_3']), axis=1)
                tlang2 = time()
                logger.info(f"Processed 'Keywords_NLP' in {lang} {round(tlang2-tlang1)} s'")
            else:
                logger.error(f"Column {translate_column} could not be translated")
            continue
        else:
            # Abstracts must be processed one by one
            if translate_column == 'abstract':
                db[new_col] = db.apply(lambda row: utils.translate_abstract(
                                row[translate_column], to_lang=lang, from_lang=row['lang_3']), axis=1)
                continue
            # Batched translation other columns
            for source_lang in db['lang_3'].unique():
                db_lang = db[db['lang_3'] == source_lang].copy()
                if db_lang.empty:
                    continue

                translated_results = []
                for i in range(0, len(db_lang), chunk_size):
                    chunk_df = db_lang.iloc[i:i+chunk_size]
                    col_chunk = chunk_df[translate_column].to_list()
                    if not col_chunk:
                        continue

                    if translate_column == 'title':
                        translated_chunk = utils.translate_text([t.replace('_',' ') for t in col_chunk],
                                                                to_lang=lang, from_lang=source_lang, one_shot=True)
                        
                    elif translate_column in ('keywords', 'keywords_nlp'):
                        translated_chunk = utils.translate_keywords(col_chunk, to_lang=lang,
                                                                        from_lang=source_lang, one_shot=True)
                    else:
                        logger.warning(f"Column {translate_column} can't be translated")
                        translated_chunk = col_chunk
                    
                    translated_results.extend(translated_chunk)

                if translated_results:
                    db.loc[db_lang.index, new_col] = translated_results
                if len(translated_results) != len(db_lang):
                    logger.warning(f"Mismatch in columns length: {len(translated_results)} != {len(db_lang)}")

    return db

if __name__ == "__main__":
    """
    Is triggered by github action pipeline which runs this script once per language.

    Parameters
    ----------
    LANG_FROM_PIPELINE : string
        Passes in the language abbr. to translate (e.g. de for german)
    """
    tstart = time()
    # Read language from pipeline variable
    language = os.environ['LANG_FROM_PIPELINE']

    preprd_data = pd.read_pickle(os.path.join(config.WORKFLOW_ARTIFACT_FOLDER,'preprd_data.pkl'))

    for trns_col in config.WORKFLOW_TRANSLATE_COLUMNS:
        logger.info(f"Start translating {trns_col} {round(time()-tstart)}s after process start")
        preprd_data = preprd_data.sort_values(by='lang_3', inplace=True)
        preprd_data = translate_new_data(preprd_data, translate_column=trns_col, languages=[language], one_shot=False)
    preprd_data.to_pickle(os.path.join(config.WORKFLOW_ARTIFACT_FOLDER, '{}_translated.pkl'.format(language)))
    preprd_data.to_csv(os.path.join(config.WORKFLOW_ARTIFACT_FOLDER, '{}_translated.csv'.format(language)))

    logger.info("\nNLP translation completed for {}".format(language))

