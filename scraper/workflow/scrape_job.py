# -*- coding: utf-8 -*-
"""
title: Scraper a.k.a Geoharvester
Author: David Oesch
Date: 2022-11-05
Purpose: Retrieve information about a web map service and save it to a file
Notes:
- Uses Python 3.9
- Uses the OWSLib library to access the geo services
- Processes the service information to extract the layer names and other details
- Writes the extracted information to  files for future use
"""

import csv
import glob
import importlib
import logging
import logging.config
import os
import re
import sys
import warnings
import xml.etree.ElementTree as ET
from pathlib import Path
import requests
from requests.exceptions import ReadTimeout, ConnectTimeout
from owslib.wfs import WebFeatureService
from owslib.wms import WebMapService
from owslib.wmts import WebMapTileService
import json
from datetime import datetime, timezone
from time import time
from collections import defaultdict
import pytz
import pandas as pd

sys.path.append('../')
import scraper.configuration as config

# globals
warnings.filterwarnings('ignore')
#sys.path.insert(0, config.SOURCE_SCRAPER_DIR)

service_keys = (("WMSGetCap", "n.a."),
                ("WMTSGetCap", "n.a."), ("WFSGetCap", "n.a."))

# Initialize and configure the logger
logging.config.dictConfig(config.LOGGING_CONFIG)
logger = logging.getLogger("Scraping log")

# Only these will be processed, no longer full scrape of everything
DATASETS_TO_PROCESS = Path("../artifacts/datasets_to_process.json")
OUTPUT_CSV = Path("scrape_job_output.csv")
OUTPUT_PKL = Path("scrape_job_output.pkl")

from urllib.parse import urlparse, urlunparse

def normalize_url(url: str) -> str:
    parsed = urlparse(url)
    # Keep only scheme + netloc + path, ignore query params
    normalized = urlunparse((parsed.scheme, parsed.netloc, parsed.path, '', '', ''))
    return normalized.lower()  

def load_layers_by_service(path: Path):
    """
    Returns:
        dict[str, dict[str, str]]
        {
            service_url: {
                layer_name: layer_hash
            }
        }
    """
    if not path.exists():
        raise FileNotFoundError(f"{path} not found")

    with open(path, encoding="utf-8") as f:
        records = json.load(f)

    layers_by_service = defaultdict(set)

    for r in records:
        service_url = normalize_url(r.get("service_url", ""))
        layer_name = r.get("layer_name")
        layer_hash = r.get("preflight_hash")

        if not service_url or not layer_name:
            continue

    layers_by_service[service_url][layer_name] = layer_hash

    return layers_by_service


def service_result_empty():
    """
    This function creates a dictionary object with default values for various
    service related fields.

    The default values are represented by the string "n.a." and are used as
    placeholders until actual data is available.

    The fields in the dictionary include:
    provider, title, name, preview, tree, group, abstract, keywords, legend,
    contact, endpoint, metadata, update, legend, service, max_zoom,
    center_lat, center_lon, preview, bbox.

    Returns:
        A dictionary object with default values for various service related
        fields.

    """
    SERVICE_RESULT = {"provider": "n.a.", "title": "n.a", "name": "n.a",
                      "preview": "n.a.", "tree": "n.a.", "group": "",
                      "abstract": "n.a", "keywords": "n.a.", "legend": "n.a.",
                      "contact": "n.a.", "endpoint": "n.a.",
                      "metadata": "n.a.", "update": "n.a.", "legend": "n.a.",
                      "service": "n.a.", "max_zoom": "n.a.",
                      "center_lat": "n.a.", "center_lon": "n.a.",
                      "bbox": "n.a."}
    return SERVICE_RESULT


def get_version(input_url):
    """
    Retrieve the version attribute from an XML response from a geoservice at
    the input URL.

    Parameters:
    input_url (str): URL to retrieve XML data from.

    Returns:
    str or None: The version attribute value or None if not found.
    """
    response = requests.get(input_url)
    xml_data = response.content
    root = ET.fromstring(xml_data)
    try:
        version = root.attrib["version"]
    except KeyError:
        logger.warning("%s: Version attribute not found" % (input_url))
        version = None
    return version


def write_file(input_dict, output_file):
    """
    Write a dictionary to a CSV file.
    Overwrites the file on first write in this job.

    Parameters:
    input_dict (dict): Dictionary to be written to file.
    output_file (str): Path of the output file.

    Returns:
    None
    """
    file_exists = os.path.isfile(output_file)

    with open(output_file, "a", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=list(input_dict.keys()),
            delimiter=",",
            quotechar='"',
            lineterminator="\n"
        )

        if not file_exists:
            writer.writeheader()

        writer.writerow(input_dict)


def load_source_collection():
    """Function to open the file of sources and to load all
    sources  into a list of dicts where each list entry corresponds
    to an individual source (an individual line in the data file).
    Load a collection of sources from a CSV file into a list of dictionaries.

    Returns:
    list: A list of dictionaries, where each dictionary represents a source.
    """
    with open(config.SOURCE_COLLECTION_CSV, mode="r", encoding="utf8") as f:
        sources = csv.DictReader(f, delimiter=",", quotechar='"',
                                 lineterminator="\n")
        sources = list(sources)
    return sources


def is_online(source):
    """
    Test if a server is online and reachable.

    Parameters:
    source (dict): A dictionary with GetCapabilities source parameters,
        including 'URL'.

    Returns:
    bool: True if the server is online, False otherwise.
    """
    server_operator = source['Description']
    server_url = source['URL']
    try:
        request = requests.get(server_url)
        if request.status_code == 200:
            success = True
        else:
            success = False
            error_details = ("GET requested yielded HTTP response status "
                             "code %s" % request.status_code)
    except Exception as e_request:
        success = False
        error_details = e_request
        logger.info("%s %s: %s" % (server_operator, server_url, e_request))

    # If there has been a problem, add the details to the operator's error
    # log file
    if not success:
        log_to_operator_csv(server_operator, server_url, error_details)
    return success

def get_service_info(source, only_layers: dict[str, str] | None = None):
    """
    Extracts information from an OGC web service (WMS, WMTS, WFS) using the 
    OWSLib library. This function takes a dictionary called "source" as input 
    and runs an OGC GetCapabilities extraction. The function tries to determine 
    if the service is a Web Map Service (WMS), Web Map Tile Service (WMTS), or 
    Web Feature Service (WFS) based on the version number in the source URL. If 
    the version number is invalid, the function writes an error message to a 
    log file.

    The function then creates a service object using either WebMapService, 
    WebMapTileService, or WebFeatureService from the OWSLib library. The 
    function then loops through all the layers in the service contents and 
    checks if the layer is a parent or child layer. For each layer, the function 
    calls write_service_info to write the service information and layer tree.

    If an error occurs, the function writes an error message to a log file and 
    returns False.

    Parameters:
        source (dict): A dictionary containing the GetCapabilities URL and 
        Description of the OGC web service.

    Returns:
        None
    """
    server_operator = source['Description']
    server_url = source['URL']
    service_type = None
    children_possible = False

    try:
        # Check if this service has a valid service version number. If not,
        # set version to None (i.e., use default)
        source_version = get_version(source['URL'])
        if source_version is None or not re.match(r"^\d+\.\d+(\.\d+)?$", source_version):

            error_details = "Invalid service version number. Scraper will try the default."
            log_to_operator_csv(server_operator, server_url, error_details)
            logger.warning("%s, %s: %s" % (server_operator, server_url,
                                           error_details))
            source_version = None

        if service_type is None:
            candidates = [
                ("WMS", True, lambda: WebMapService(
                    server_url, version=source_version or None, timeout=config.SCRAPER_REQUEST_TIMEOUT
                )),  
                ("WMTS", False, lambda: WebMapTileService(
                    server_url, timeout=config.SCRAPER_REQUEST_TIMEOUT
                )),
                ("WFS", False, lambda: WebFeatureService(
                    server_url,
                    version=source_version or "2.0.0",
                    timeout=config.SCRAPER_REQUEST_TIMEOUT
                )),
            ]

            for candidate_type, children_possible, ctor in candidates:
                try:
                    service = ctor()
                    service_type = candidate_type
                    children_possible = children_possible
                    break
                except Exception as e:
                        logger.debug(f"Service probe failed: {candidate_type} @ {server_url}: {e}")

        if service_type is not None:
            # I.e., we have found a valid service endpoint of type WMS, WTMS or
            # WFS
            service_title = service.identification.title

            # Extract all layer names
            layers = list(service.contents)
            layers_done = []
            for i in layers:
                this_layer = service.contents[i].id

                # Only process layers that changed, not all
                if only_layers is not None and this_layer not in only_layers:
                    continue

                layer_hash = only_layers.get(this_layer) if only_layers is not None else None
                # Check that we have not yet processed this layer as a child of
                # another layer before
                if this_layer not in layers_done:
                    # get root layer / extracting the description for simple layer
                    # Some root WMS layers are blocked so no get map is
                    # possible, so we check if we can load them as TOPIC
                    # (aka al children layer active)
                    if service_type == "WMS":
                        # Even some Root layers do not have titles therfore
                        # skipping as well
                        if service.contents[i].title is None:
                            logger.warning("%s: Title is empty. Skipping." % i)
                        else:
                            try:
                                # check if root layer is loadable, by trying to
                                # call a Get Map, if it is blocked it will
                                # raise an error
                                service.getmap(layers=[i], srs='EPSG:4326',
                                               bbox=(service.contents[i].boundingBoxWGS84[0],
                                                     service.contents[i].boundingBoxWGS84[1],
                                                     service.contents[i].boundingBoxWGS84[2],
                                                     service.contents[i].boundingBoxWGS84[3]),
                                               size=(256, 256), format='image/png',
                                               transparent=True, timeout=10)
                                # Then extract abstract etc
                                if service_title is not None:
                                    layertree = "%s/%s/%s" % (server_operator,
                                                              service_title,
                                                              i.replace('"', ''))
                                else:
                                    layertree = "%s/%s" % (server_operator,
                                                           i.replace('"', ''))

                                write_service_info(source, service, layer_hash,
                                                   this_layer,
                                                   layertree, group=i)
                                layers_done.append(this_layer)
                            except Exception as e:
                                # Check if the exception indicates that the
                                # request was not allowed or forbidden
                                if any([msg in str(e) for msg in service.exceptions]):
                                    logger.warning(
                                        "%s: GetMap request is blocked for this layer" % i)
                                else:
                                    logger.error(
                                        "%s: %s" % (
                                            i, str(e).replace('\n', ' ').replace('\r', '')))
                    else:
                        if service_title is not None:
                            layertree = "%s/%s/%s" % (server_operator,
                                                      service_title,
                                                      i.replace('"', ''))
                        else:
                            layertree = "%s/%s" % (server_operator,
                                                   i.replace('"', ''))
                        logger.debug("Analysing %s > %s > %s" % (server_operator,
                                                                server_url,
                                                                this_layer))
                        write_service_info(source, service, this_layer,
                                           layertree, group=i)
                        layers_done.append(this_layer)

                    # Check if this layer is parent to child layers. If it is,
                    # check the child layers
                    if children_possible:
                        try:
                            number_children = len(service.contents[i].children)
                        except AttributeError:
                            number_children = 0

                    if children_possible and number_children > 0:
                        for j in range(number_children):
                            this_child_layer = service.contents[i]._children[j].id
                            if only_layers is not None and this_child_layer not in only_layers:
                                continue
                            
                            child_layer_hash = (
                                only_layers.get(this_child_layer)
                                if only_layers is not None
                                else None
                            )

                            if this_child_layer not in layers_done:
                                if service_title is not None:
                                    layertree = "%s/%s/%s" % (server_operator,
                                                              service_title,
                                                              i.replace('"', ''))
                                else:
                                    layertree = "%s/%s" % (server_operator,
                                                           i.replace('"', ''))
                                logger.debug("Analysing %s > %s > %s >> %s" % (
                                    server_operator, server_url, this_layer,
                                    this_child_layer))
                                write_service_info(source, service, child_layer_hash, 
                                                   this_child_layer, layertree,
                                                   group=i)
                                layers_done.append(this_child_layer)

                else:
                    # This layer has already been processed
                    pass
        else:
            # Service could not be identified as valid WMS, WMTS or WFS by
            # OWSLib
            error_details = "Service does not seem to be a valid WMS, WMTS or WFS"
            log_to_operator_csv(server_operator, server_url, error_details)
            logger.warning("%s > %s: %s" %
                           (server_operator, server_url, error_details))

    except Exception as e_request:
        error_details = str(e_request)
        log_to_operator_csv(server_operator, server_url, error_details)
        logger.error("%s > %s: %s" %
                     (server_operator, server_url, error_details))
        return False


def log_to_operator_csv(server_operator, server_url, error_details):
    CET = pytz.timezone('Europe/Zurich')
    timestamp = datetime.now(timezone.utc).astimezone(CET).isoformat()

    log_file_name = "%s_errors.csv" % server_operator
    log_file_path = os.path.join(config.DEAD_SERVICES_PATH, log_file_name)

    error_log = '%s,%s,%s,"%s"' % (timestamp, server_operator, server_url,
                                   error_details)
    append_or_write = "a" if os.path.isfile(log_file_path) else "w"
    with open(log_file_path, append_or_write, encoding="utf-8") as f:
        if append_or_write == "w":
            f.write("Timestamp,Operator,URL,Issue\n")
        f.write(error_log + "\n")
    return

# keep:
def write_service_info(source, service, hash, i, layertree, group):
    """
    Write OGC GetCap results for a service, using a custom or default scraper 
    based on availability.

    Parameters:
    source (dict): Source information.
    service (var): GetCap results.
    hash: The hash carried over from preflight, to be matched against db later
    i (str): Layer name.
    layertree (str): Tree structure.
    group (str): Group name.

    Returns:
    bool: Returns `True` if the function runs successfully, `False` otherwise.
    """
    server_operator = source['Description']
    # Load Empty parameter list
    layer_data = service_result_empty()

    try:
        # check if custom scraper is available
        scraper_spec = importlib.util.find_spec(server_operator)

        # run custom scraper
        if scraper_spec is not None:
            scraper = importlib.import_module(server_operator, package=None)
            layer_data = scraper.scrape(source, service, hash, i, layertree, group,
                                        layer_data, config.preview_PREFIX)

        # run default scraper
        else:
            BASE_DIR = Path(__file__).resolve().parent / "scraper"
            sys.path.insert(0, str(BASE_DIR))
            scraper = importlib.import_module('default') 
            layer_data = scraper.scrape(source, service, hash, i, layertree, group,
                                        layer_data, config.preview_PREFIX)

        # Writing the Result file
        write_file(layer_data, OUTPUT_CSV)

        return True

    except Exception as e_request:
        error_details = str(e_request)
        log_to_operator_csv(server_operator, i, error_details)
        logger.error("%s, %s: %s" % (server_operator, i, error_details))
        return False

# Later job
# def preprocessing_NLP(raw_data_path, output_folder=None, column='abstract'):
#     """
#     Preprocesses the data collected by the scraper using different NLP
#     functions, which are stored in preprocessing/utils.py

#     Parameters
#     ----------
#     raw_data_path : str
#         path of pickle file containing the new raw data output of the scraper
#     output_folder : str
#         path-to-folder where the elaborated data will be saved as pkl
#     column : str
#         column of the dataframe to be used for the NLP preprocessing
#     """
#     t0 = time()
#     # Read the data
#     raw_data = pd.read_pickle(raw_data_path)
#     raw_data = raw_data.fillna("nan") # needed for the preprocessing
#     # Extract the keywords and add them to the data
#     NLP = utils.NLP_spacy()
#     keywords_dataset = NLP.extract_refined_keywords(raw_data, use_rake=True, column=column, keyword_length=3, num_keywords=15)
#     def join_keywords(keywords_list):
#         keywords = ', '.join(kw for kw in keywords_list)
#         return keywords
#     raw_data['keywords_nlp'] = list(map(join_keywords, keywords_dataset))
#     t1 = time()
#     print(f"Keywords extracted succesfully in {t1-t0} seconds")
#     # Summarize the abstracts and add them to the data
#     # summaries = NLP.summarize_texts(raw_data, column=column)
#     raw_data['summary'] = ['summary']*len(raw_data)#summaries
#     t2 = time()
#     # print(f"Abstracts summarized succesfully in {t2-t1} seconds")
#     # Add the detected dataset language (applied on title)
#     language_dict = {'english':('EN', 'ENG'), 'french':('FR','FRA'), 'german':('DE','DEU'), 'italian':('IT','ITA'), 'not_found':('NA','NAN')}
#     raw_data['lang_3'] = raw_data.apply(lambda row: language_dict[utils.detect_language(row['abstract'], not_found=True)][1], axis=1)
#     raw_data['lang_2'] = raw_data.apply(lambda row: language_dict[utils.detect_language(row['abstract'], not_found=True)][0], axis=1)
#     raw_data['lang_3'] = raw_data.apply(lambda row: language_dict[utils.detect_language(row['title'], not_found=True)][1] if row['lang_3']=='NAN' else row['lang_3'], axis=1)
#     raw_data['lang_2'] = raw_data.apply(lambda row: language_dict[utils.detect_language(row['title'], not_found=True)][0] if row['lang_2']=='NAN' else row['lang_2'], axis=1)
#     t3 = time()
#     print(f"Languages detected succesfully in {t3-t2} seconds")

#     # Check and add metadata quality
#     print(f"Adding metadata scores...")
#     raw_data = utils.check_metadata_quality(raw_data, search_word='nan',
#                                             search_columns=['abstract', 'keywords', 'metadata','contact'],
#                                             case_sensitive=False)
    
#     # Characters cleaning for compatibility with redis -> Already done by checking the new data
#     print(f"Cleaning up metadata...")
#     raw_data = raw_data.replace(to_replace="\'", value=" ", regex=True)
#     raw_data = raw_data.replace(to_replace='\"', value="-", regex=True)
#     # raw_data = raw_data.replace(to_replace="  ", value = " ", regex=True)
#     # raw_data = raw_data.replace(to_replace="    ", value = " ", regex=True)
    
#     # Save data as pickle for a faster reading/writing
#     if output_folder:
#         raw_data.to_pickle(output_folder+'/preprocessed_data.pkl')
#         print(f"Preprocessed data saved in {output_folder+'/preprocessed_data.pkl'}")
#     return raw_data

if __name__ == "__main__":
    """
    This code block is the main function of the script. It performs the 
    following operations:

    1 Clean up: Deletes previous log files and scraped data.
    2 Load sources: Calls the load_source_collection function to get a list of 
      sources to scrape.
    3 For each source:
        a. Check if a scraper exists for the source. If not, it sets a message 
           indicating that the default scraper will be used.
        b. Prints and logs a message indicating the start of the scraper for 
           the source.
        c. Calls the is_online function to check if the server is online.
        d. If the server is online, calls the get_service_info function to get 
           information from the service.
        e. If the server is not online, logs a message indicating the scraper 
           was aborted.
    4 Create dataset view and stats: Calls the write_dataset_info and 
      write_dataset_stats functions to generate the dataset files.
    5 Preprocess the data using NLP: Calls the preprocessing_NLP function
      reading the csv, preprocessing the data and generating a pickle
    6 Logs and prints a message indicating that the scraper has completed.
    """
    process_startT=time()

    error_log_files = glob.glob(os.path.join(
        config.DEAD_SERVICES_PATH, "*_errors.csv"))
    for error_log_file in error_log_files:
        try:
            os.remove(error_log_file)
        except OSError as e:
            logger.error("Could not delete %s: %s" % (error_log_file, e))

    if OUTPUT_CSV.exists():
        OUTPUT_CSV.unlink()

    layers_by_service = load_layers_by_service(DATASETS_TO_PROCESS)

    logger.info(
        f"Loaded {sum(len(v) for v in layers_by_service.values())} layers "
        f"across {len(layers_by_service)} services to process"
    )

    scraping_startT = time()
    # Load sources
    sources = load_source_collection()
    num_sources = len(sources)

    logger.info(f"Startup time until scraping: {int((scraping_startT-process_startT) / 60)} mins")
    for source in sources:
        service_url = normalize_url(source.get("URL"))
        only_layers = layers_by_service.get(service_url)

        # Skip services with no changed layers
        if not only_layers:
            continue

        get_service_info(source, only_layers=only_layers)
           
    scraping_endT = time()
    logger.info(f"Scraping took: {int((scraping_endT-scraping_startT) / 60)} mins")

    if OUTPUT_CSV.exists():
        logger.info("Converting scraped CSV to pickle")

        df = pd.read_csv(OUTPUT_CSV)
        df.to_pickle(OUTPUT_PKL)

        logger.info(
            f"Wrote {len(df)} records to "
            f"{OUTPUT_CSV.name} and {OUTPUT_PKL.name}"
        )
    else:
        logger.warning("No CSV output found – skipping pickle generation")

    # write_dataset_info(config.GEOSERVICES_CH_CSV,config.GEOSERVICES_CH_CSV)
    # Copy to artifact folder

    # artifact_csv_path = os.path.join(config.WORKFLOW_ARTIFACT_FOLDER, 'geoservices_CH.csv')
    # shutil.copyfile(config.GEOSERVICES_CH_CSV, artifact_csv_path)
    # logger.info(f"Scraping finished. CSV stored as artifact: {artifact_csv_path}")

    # TODO: Needs replacing
    # data_to_keep = check_new_data(os.path.join(config.PROCESSED_DATA_PKL),
    #                config.GEOSERVICES_CH_CSV,
    #                match_columns=['name','title','provider','keywords','abstract','endpoint', 'contact'],
    #                output_path=os.path.split(config.GEOSERVICES_CH_CSV)[0])
    

    # preprd_data = preprocessing_NLP(os.path.join(os.path.split(config.GEOSERVICES_CH_CSV)[0],
    #                                              'to_preprocess.pkl'))
    # pathpart = os.path.join(config.WORKFLOW_ARTIFACT_FOLDER,'preprd_data.pkl')
    # logger.info(f"Found {len(preprd_data)} datasets for processing")


    # preprd_data.to_csv(os.path.join(config.WORKFLOW_ARTIFACT_FOLDER,'preprd_data.csv'))
    # preprd_data.to_pickle(os.path.join(config.WORKFLOW_ARTIFACT_FOLDER,'preprd_data.pkl'))
    # TODO REMOVE: Save to data for last pipeline stage
    # data_to_keep.to_pickle(os.path.join(os.path.split(config.GEOSERVICES_CH_CSV)[0],'data_to_keep.pkl'))
    # data_to_keep.to_csv(os.path.join(os.path.split(config.GEOSERVICES_CH_CSV)[0],'data_to_keep.csv'))

    process_endT = time()
    logger.info(f"Job took: {int((process_endT-process_startT) / 60)} mins")
