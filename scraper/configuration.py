import os
import sys
from datetime import datetime

SCRAPER_REQUEST_TIMEOUT = 65 # Value in seconds - to be used in owslib requests when scraping
SOURCE_COLLECTION_CSV = "sources.csv"
SOURCE_COLLECTION_VERSION = {"KT_AI": "1.3.0",
                             "KT_AR": "1.3.0", "Geodienste": "1.3.0"}
SOURCE_SCRAPER_DIR = "scraper"
GEOSERVICES_CH_CSV = os.path.join("data", "geoservices_CH.csv")
TEMP_PROCESSED_DATA_PKL = os.path.join("temp_data","merged_data.pkl")
WORKFLOW_ARTIFACT_FOLDER = "artifacts"
WORKFLOW_TRANSLATE_LANGUAGES = ['de','en','fr','it']
WORKFLOW_TRANSLATE_COLUMNS = ["title","abstract","keywords","keywords_nlp"]
WORKFLOW_MERGE_COLUMNS = ['name','title','provider','keywords','abstract','endpoint']
LOG_FILE = os.path.join("tools",  f"scraper-{datetime.now().strftime('%Y%m%d-%H%M')}.log")
DEAD_SERVICES_PATH = "tools"
preview_PREFIX = \
    "https://map.geo.admin.ch/?bgLayer=ch.swisstopo.pixelkarte-grau&"

# Google Indexing API
# JSON_KEY_FILE = "geoharvester-indexing-credentials.json"
# SCOPES = ["https://www.googleapis.com/auth/indexing"]

# Config to make the logger work (in GitHub actions and artifacts)
LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "simple": {
            "format": "%(asctime)s [%(levelname)s] %(message)s"
        },
        "detailed": {
            "format": (
                "%(asctime)s - %(name)s - %(filename)s >"
                "%(funcName)17s(): Line %(lineno)s - "
                "%(levelname)s - %(message)s"
            )
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "stream": sys.stdout,
            "level": "INFO",
            "formatter": "simple",
        },
        "file": {
            "class": "logging.FileHandler",
            "filename": str(LOG_FILE),
            "mode": "w",
            "encoding": "utf-8",
            "level": "INFO",
            "formatter": "detailed",
        },
    },
    "loggers": {
        "Scraping log": {
            "level": "INFO",
            "handlers": ["console", "file"],
            "propagate": False
        },
    },
}
