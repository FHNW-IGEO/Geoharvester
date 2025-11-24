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
from geocat.keyword_finder import load_pickle_db, save_pickle_db


if __name__ == "__main__":

    log_start_message()
    try:
        print("test")


    except Exception as e:
        print(f"Error occurred: {e}")