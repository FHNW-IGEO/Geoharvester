"""
title: geocat data scraping job for the keyword enrichment of the GeoHarvestr 
Author: xx
Date: 2025-10-20
"""



import os
import sys
import logging




# Ensure repository root is on sys.path so 'scraper' package resolves
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

import configuration as config



# geocat functions
from geocat.error_logger import log_start_message
from geocat.download_geocat import download_geocat_metadata
from geocat.download_geocat import download_xml_metadata_from_csv
import geocat.xml_cleaner as xml_cleaner
from geocat.extract_metadata_geocat import extract_and_save_all_geocat
from geocat.transform_metadata_geocat import process_dataset_metadata, clean_csv_file
from geocat.apply_all_schemas import apply_schemas
from geocat.load_metadata_pickle import reset_database, reset_database,load_metadata
from geocat.language_correction import language_correction






if __name__ == "__main__":

    log_start_message()
    try:
        # -------------------------------
        # 2.0 Parse metadatacatalog geocat.ch and save dataset list to CSV
        # -------------------------------

        # download_geocat_metadata(
        #     save_dir=config.WORKFLOW_GEOCAT_DATA,
        #     csv_file= config.WORKFLOW_GEOCAT_DATASET_LIST,
        #     log_file="logfile_geocat.log",
        #     start_pos=15000,
        #     batch_size=250
        # )

        # -------------------------------
        # 2.1 Download XML-files from geocat.ch based on CSV list
        # -------------------------------

        # download_xml_metadata_from_csv(
        #     save_dir=config.WORKFLOW_GEOCAT_XML,
        #     csv_file=config.WORKFLOW_GEOCAT_DATASET_LIST,
        #     max_files=100  # oder None für alle
        # )

        # -------------------------------
        # 2.2 Clean XML-files
        # -------------------------------

        # xml_cleaner.process_folders([
        #     config.WORKFLOW_GEOCAT_XML
        # ])

        # -------------------------------
        # 2.3 Extract metadata and save to new folder
        # -------------------------------
        extract_and_save_all_geocat(
            input_folder=config.WORKFLOW_GEOCAT_XML,
            output_folder=config.WORKFLOW_GEOCAT_DATA
        )

        # -------------------------------
        # 2.5 Transform extracted metadata
        # -------------------------------

        for f in config.WORKFLOW_GEOCAT_FILES:
            clean_csv_file(f)
            process_dataset_metadata(f)

        # 2.6 Merge metadata files from different runs
        apply_schemas(config.WORKFLOW_GEOCAT_FILES, config.WORKFLOW_GEOCAT_DATA)


        # 3.0 Load metadata into database
        db_name = "geocat_metadata"
        base_dir = config.WORKFLOW_GEOCAT_DATA
        files = config.WORKFLOW_GEOCAT_FILES
        # Always recreate pickle DB
        reset_database(db_name, base_dir)
        # Load your 3 CSVs into the pickle DB
        load_metadata(files, base_dir, db_name)

        # -------------------------------
        # 5. Language Detection
        # -------------------------------

        # language_correction(
        #     db_name = db_name,
        #     table_name = "merged_dataset_metadata",
        #     language_prefixes = ["DE", "EN", "FR", "IT"],   
        #     base_columns = ["dataset_title", "dataset_keyword", "dataset_description"],
        #     table_set_type = "dataset",
        #     min_length_lang_detect = 20
        # )

        language_correction(
            base_dir = config.WORKFLOW_GEOCAT_DATA,
            db_name = "geocat_metadata",
            table_name = "dataset",
            language_prefixes = ["de", "en", "fr", "it" , "unknown"],
            base_columns = ["dataset_title", "dataset_keyword", "dataset_description"],
            table_set_type = "dataset",
            min_length_lang_detect = 20
        )

        
        language_correction(
            base_dir = config.WORKFLOW_GEOCAT_DATA,
            db_name = "geocat_metadata",
            table_name = "distribution",
            language_prefixes = ["de", "en", "fr", "it","unknown"],   
            base_columns = ["distribution_title","distribution_description"],
            table_set_type = "distribution",
            min_length_lang_detect = 20
        )

    except Exception as e:
        print(f"Error occurred: {e}")
