"""
title: Matching the equal datasets from geocat and GeoHarvester and extract keywords from geocat
Author: xx
Date: 2025-11-24
"""

import os
import sys


# Ensure repository root is on sys.path so 'scraper' package resolves
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

import configuration as config
from geocat.error_logger import log_start_message
from geocat.keyword_finder import keyword_finder


if __name__ == "__main__":

    log_start_message()
    try:
        print("starting keyword_finder_in_geocat.py")
    
        keyword_finder(
            base_dir_geocat = config.WORKFLOW_GEOCAT_DATA,
            base_dir_geoharvester = config.WORKFLOW_DATA,
            pkl_geocat_data_name = config.WORKFLOW_GEOCAT_DATABASE_NAME,
            pkl_geoharvester_data_name = config.WORKFLOW_KEYWORD_FINDER_MERGED_DATA,
            pkl_geoharvester_data_name_with_geocat_keywords = config.WORKFLOW_KEYWORD_FINDER_MERGED_DATA_WITH_GEOCAT_KEYWORDS
        )
        print("finished keyword_finder_in_geocat.py")
    except Exception as e:
        print(f"Error occurred: {e}")