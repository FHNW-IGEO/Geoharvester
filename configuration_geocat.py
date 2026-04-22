import os

# Base directory of this configuration file (i.e., the 'scraper' folder)
_BASE_DIR = os.path.dirname(__file__)

# Where to store Geocat outputs (CSV + XMLs). Resolved relative to this file.
WORKFLOW_GEOCAT_XML = os.path.join(_BASE_DIR, "data", "geocat_xml")

# Output CSV filename for the identifier-title list
WORKFLOW_DATA =  os.path.join(_BASE_DIR, "data")
WORKFLOW_GEOCAT_DATASET_LIST =  os.path.join(_BASE_DIR, "data", "geocat_dataset_id_title.csv")



# SOURCE_COLLECTION_CSV = "sources.csv"
# SOURCE_COLLECTION_VERSION = {"KT_AI": "1.3.0",
#                              "KT_AR": "1.3.0", "Geodienste": "1.3.0"}
# SOURCE_SCRAPER_DIR = "scraper"
# GEOSERVICES_CH_CSV = os.path.join("data", "geoservices_CH.csv")
# TEMP_PROCESSED_DATA_PKL = os.path.join("temp_data","merged_data.pkl")
# WORKFLOW_ARTIFACT_FOLDER = "artifacts"
# WORKFLOW_TRANSLATE_LANGUAGES = ['de','en','fr','it']
# WORKFLOW_TRANSLATE_COLUMNS = ["title","abstract","keywords","keywords_nlp"]
# WORKFLOW_MERGE_COLUMNS = ['name','title','provider','keywords','abstract','endpoint']
# LOG_FILE = os.path.join("tools", "debug.log")
# DEAD_SERVICES_PATH = "tools"
# preview_PREFIX = \
#     "https://map.geo.admin.ch/?bgLayer=ch.swisstopo.pixelkarte-grau&"

# Google Indexing API
# JSON_KEY_FILE = "geoharvester-indexing-credentials.json"
# SCOPES = ["https://www.googleapis.com/auth/indexing"]
