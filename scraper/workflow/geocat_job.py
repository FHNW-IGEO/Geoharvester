"""
title: geocat data scraping job for the keyword enrichment of the GeoHarvestr 
Author: xx
Date: 2025-10-20
"""



import os
import sys

# Ensure repository root is on sys.path so 'scraper' package resolves
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

import scraper.configuration_geocat as config


# from scraper.geocat.download_geocat import download_geocat_metadata
# download_geocat_metadata(
#     save_dir=config.WORKFLOW_DATA,
#     csv_file= config.WORKFLOW_GEOCAT_DATASET_LIST,
#     log_file="my_errors.log",
#     start_pos=15000,
#     batch_size=250
# )


from scraper.geocat.download_geocat import download_xml_metadata_from_csv
download_xml_metadata_from_csv(
    save_dir=config.WORKFLOW_GEOCAT_XML,
    csv_file=config.WORKFLOW_GEOCAT_DATASET_LIST,
    max_files=100  # oder None für alle
)
