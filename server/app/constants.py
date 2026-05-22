from enum import Enum

#---------------------------------------------------------------------------------------------------------------
# Redis:
REDIS_HOST = "redis" # See docker-compose, hostname
REDIS_PORT = 6379 # See docker-compose, port / expose

#---------------------------------------------------------------------------------------------------------------  
# URLs:
# Scraper related URLs:
url_github_repo = "https://raw.githubusercontent.com/FHNW-IGEO/Geoharvester/main/scraper/data/"
url_github_repo_suffix = "?raw=true"

url_geodata_CH_csv = f"{url_github_repo}geodata_CH.csv{url_github_repo_suffix}"
url_geodata_simple_CH_csv = f"{url_github_repo}geodata_simple_CH.csv{url_github_repo_suffix}"
url_geoservices_CH_csv = f"{url_github_repo}geoservices_CH.csv{url_github_repo_suffix}"
url_geoservices_stats_CH_csv = f"{url_github_repo}geoservices_CH.csv{url_github_repo_suffix}"

#---------------------------------------------------------------------------------------------------------------  
# Variables:
# Used to create a subset of the full csv data:
fields_to_include = ["provider","title", "keywords", "abstract", "service", "endpoint", "preview"]
fields_to_output = ["title", "keywords", "provider", "service", "endpoint", "preview"]

class EnumServiceType(str, Enum):
    wms = "wms"
    wmts = "wmts"
    wfs = "wfs"


class EnumProviderType(str, Enum):
    BUND = "Bund",
    GEODIENSTE = "Geodienste",
    KT_AG = "KT_AG",
    KT_AI = "KT_AI",
    KT_AR = "KT_AR",
    KT_BE = "KT_BE",
    KT_BL = "KT_BL",
    KT_BS = "KT_BS",
    KT_FR = "KT_FR",
    KT_GE = "KT_GE",
    KT_GL = "KT_GL",
    KT_GR = "KT_GR",
    KT_JU = "KT_JU",
    KT_LU = "KT_LU",
    KT_NE = "KT_NE",
    KT_NW = "KT_NW",
    KT_OW = "KT_OW",
    KT_SG = "KT_SG",
    KT_SH = "KT_SH",
    KT_SO = "KT_SO",
    KT_SZ = "KT_SZ",
    KT_TG = "KT_TG",
    KT_TI = "KT_TI",
    KT_UR = "KT_UR",
    KT_VD = "KT_VD",
    KT_VS = "KT_VS",
    KT_ZG = "KT_ZG",
    KT_ZH = "KT_ZH",
    FL_LI = "FL_LI",
    ST_ZH = "ST_ZH",
    ST_BE = "ST_BE",
    ASIT = "ASIT",
    SOSM = "SOSM",

class EnumLangType(str, Enum):
    en = "en",
    de = "de",
    fr = "fr",
    it = "it"


#---------------------------------------------------------------------------------------------------------------
# Constants:
DEFAULTSIZE = 1000 # Chunk size retrieved with a single call from redis. Needs to match FE variable of same name!
