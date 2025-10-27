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
import os
import re
import sys
import warnings
import xml.etree.ElementTree as ET
from collections import defaultdict
from statistics import mean

import configuration as config
import requests
import utils
from owslib.wfs import WebFeatureService
from owslib.wms import WebMapService
from owslib.wmts import WebMapTileService

""" from oauth2client.service_account import ServiceAccountCredentials
from googleapiclient.discovery import build
from googleapiclient.http import BatchHttpRequest """
import json
import shutil
from datetime import datetime, timezone
from time import time

import httplib2
import pandas as pd
import pytz

# globals
warnings.filterwarnings('ignore')
sys.path.insert(0, config.SOURCE_SCRAPER_DIR)

service_keys = (("WMSGetCap", "n.a."),
                ("WMTSGetCap", "n.a."), ("WFSGetCap", "n.a."))


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
                      "preview": "n.a.", "bbox": "n.a."}
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
    Write a dictionary to a CSV file. If the file exists, the data is appended
    to it. If the file does not exist, a new file is created with a header.

    Parameters:
    input_dict (dict): Dictionary to be written to file.
    output_file (str): Path of the output file.

    Returns:
    None
    """
    append_or_write = "a" if os.path.isfile(output_file) else "w"
    with open(output_file, append_or_write, encoding="utf-8") as f:
        dict_writer = csv.DictWriter(f, fieldnames=list(input_dict.keys()),
                                     delimiter=",", quotechar='"',
                                     lineterminator="\n")
        if append_or_write == "w":
            dict_writer.writeheader()
        dict_writer.writerow(input_dict)
    return


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


def get_service_info(source):
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

    try:
        # Check if this service has a valid service version number. If not,
        # set version to None (i.e., use default)
        source_version = get_version(source['URL'])
        match = re.match(r"^\d+\.\d+\.\d+$", source_version)
        if not match:
            error_details = "Invalid service version number. Scraper will try the default."
            log_to_operator_csv(server_operator, server_url, error_details)
            logger.warning("%s, %s: %s" % (server_operator, server_url,
                                           error_details))
            source_version = None

        # Check if this service is a WMS, a WMTS or a WFS
        service_type = None
        try:
            if source_version is not None:
                service = WebMapService(server_url, version=source_version)
            else:
                service = WebMapService(server_url)
            service_type = "WMS"
            # We assume WMSs can have child/parent relations
            children_possible = True
        except:
            pass

        if service_type is None:
            try:
                service = WebMapTileService(server_url)
                service_type = "WMTS"
                # We assume WMTSs can't have child/parent relations
                children_possible = False
            except:
                pass

        if service_type is None:
            try:
                if source_version is None:
                    service = WebFeatureService(server_url, version='2.0.0')
                else:
                    service = WebFeatureService(server_url,
                                                version=source_version)
                service_type = "WFS"
                # We assume WFSs can't have child/parent relations
                children_possible = False
            except:
                pass

        if service_type is not None:
            # I.e., we have found a valid service endpoint of type WMS, WTMS or
            # WFS
            service_title = service.identification.title

            # Extract all layer names
            layers = list(service.contents)
            layers_done = []
            for i in layers:
                this_layer = service.contents[i].id
                # Check that we have not yet processed this layer as a child of
                # another layer before
                if this_layer not in layers_done:
                    # get root layer / extracting the description for simple layer
                    # Some root WMS layers are blocked so no get map is
                    # possible, so we check if we can load them as TOPIC
                    # (aka al children layer active)
                    if "wms" in server_url.lower():
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

                                write_service_info(source, service,
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
                        logger.info("Analysing %s > %s > %s" % (server_operator,
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
                            if this_child_layer not in layers_done:
                                if service_title is not None:
                                    layertree = "%s/%s/%s" % (server_operator,
                                                              service_title,
                                                              i.replace('"', ''))
                                else:
                                    layertree = "%s/%s" % (server_operator,
                                                           i.replace('"', ''))
                                logger.info("Analysing %s > %s > %s >> %s" % (
                                    server_operator, server_url, this_layer,
                                    this_child_layer))
                                write_service_info(source, service,
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


def write_service_info(source, service, i, layertree, group):
    """
    Write OGC GetCap results for a service, using a custom or default scraper 
    based on availability.

    Parameters:
    source (dict): Source information.
    service (var): GetCap results.
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
            layer_data = scraper.scrape(source, service, i, layertree, group,
                                        layer_data, config.preview_PREFIX)

        # run default scraper
        else:
            scraper = importlib.import_module('default', package=None)
            layer_data = scraper.scrape(source, service, i, layertree, group,
                                        layer_data, config.preview_PREFIX)

        # Writing the Result file
        write_file(layer_data, config.GEOSERVICES_CH_CSV)

        return True

    except Exception as e_request:
        error_details = str(e_request)
        log_to_operator_csv(server_operator, i, error_details)
        logger.error("%s, %s: %s" % (server_operator, i, error_details))
        return False


def write_dataset_info(csv_filename, output_file):
    """
    Writes the processed data in First Normal Form (NF1) to two output files:
    one with detailed information and one with simple information (title and 
    map geo link). This function reads data from a CSV file and processes it to 
    bring the data into first normal form (NF1) with one entry per dataset. The 
    processed data is then written to two output files.

    Inputs
    csv_filename: the name of the input CSV file
    output_file: the name of the output file for the full dataset information
    output_simple_file: the name of the output file for the simplified dataset 
        information

    Functionality
    1. Store processed dataset IDs in geo_data_done to avoid processing the 
       same dataset multiple times.
    2. Loop over all rows in the CSV file and filter for unique datasets by 
       comparing the title, name, and provider fields.
    3. For each unique dataset, create a new empty layer using the 
       service_result_empty function and update it with the dataset information.
    4. If there are multiple datasets with the same title, name, and provider, 
       combine the information from all datasets into a single layer.
    5. Perform post-processing on the dataset information, such as removing 
       duplicates from the keywords field and updating the service links 
       (WMSGetCap, WMTSGetCap, WFSGetCap) based on the service and 
       endpoint fields in the CSV file. Write the processed dataset 
       information to the output files using the write_file function, with 
       different keys for each file.
    6. The full dataset information is written to output_file, while a 
       simplified version containing only the provider, title, and preview fields 
       is written to output_simple_file.

    Parameters:
    csv_filename: str
        Path to the source CSV file
    output_file: str
        Path to the output file with detailed information
    output_simple_file: str
        Path to the output file with simple information

    Returns:
    None
    """
    # create an empty list to store already processed  datasetUID
    geo_data_done = []

    # read CSV in dict
    lst = [*csv.DictReader(open(csv_filename, encoding="utf-8"),
                           delimiter=",", quotechar='"', lineterminator="\n")]

    for i in lst:
        # filter for unique ID consisting of title name and provider
        lst_layers = list(filter(lambda lst: (lst['title'] == i['title']) and (
            lst['name'] == i['name']) and (lst['provider'] == i['provider']), lst))

        checklayer = i['provider']+"_"+i['title'] + \
            "_"+i['name']  # create a datasetUID

        if checklayer not in geo_data_done:
            # get new empty layer
            dataset = service_result_empty()
            dataset.update(service_keys)
            dataset['provider'] = i['provider']
            dataset['title'] = i['title']
            dataset['name'] = i['name']
            # check if multiple datasets are found, ege there must be WMS  WFS
            # or WMTS if lst_layers is bigger

            for j in range(len(lst_layers)):
                # check if multiple datasets are found, ege there must be WMS,
                # WFS or WMTS if lst_layers is bigger
                if "layers=WMS" in dataset['preview']:
                    dataset['preview'] = dataset['preview']
                elif "layers=WMS" in lst_layers[j]['preview']:
                    dataset['preview'] = lst_layers[j]['preview']
                elif "layers=WMTS" in lst_layers[j]['preview']:
                    dataset['preview'] = lst_layers[j]['preview']
                dataset['abstract'] = lst_layers[j]['abstract'] if lst_layers[j]['abstract'] != "n.a." else dataset['abstract']
                dataset['metadata'] = lst_layers[j]['metadata'] if lst_layers[j]['metadata'] != "n.a." else dataset['metadata']
                dataset['contact'] = lst_layers[j]['contact'] if lst_layers[j]['contact'] != "n.a." else dataset['contact']
                dataset['keywords'] = lst_layers[j]['keywords'] if lst_layers[j]['keywords'] != "n.a." else ""
                dataset['WMSGetCap'] = lst_layers[j]['endpoint'] if "wms".casefold(
                ) in lst_layers[j]['service'].casefold() else dataset['WMSGetCap']
                dataset['WMTSGetCap'] = lst_layers[j]['endpoint'] if "wmts".casefold(
                ) in lst_layers[j]['service'].casefold() else dataset['WMTSGetCap']
                dataset['WFSGetCap'] = lst_layers[j]['endpoint'] if "wfs".casefold(
                ) in lst_layers[j]['service'].casefold() else dataset['WFSGetCap']
            # remove duplicates from keywords
            keywordlist = dataset['keywords']
            li = list(keywordlist.split(","))
            keywords = list(dict.fromkeys(li))
            dataset['keywords'] = ','.join(keywords)

            # writing the datasetfile
            datasetfile_keys = ['provider', 'title', 'name', 'preview', 'abstract',
                                'keywords', 'contact', 'WMSGetCap', 'WMTSGetCap', 'WFSGetCap']
            datasetfile = dict((k, dataset[k])
                               for k in datasetfile_keys if k in dataset)
            write_file(datasetfile, output_file)
            # add datasetID to lyer done
            geo_data_done.append(checklayer)
    return

def check_new_data(actual_db_path, new_data_path, match_columns, output_path):
    """
    It compares the old and new databases to extract and preprocess
    only the new datasets.
    
    Parameters
    ----------
    actual_db_path : str
        path to actual pkl dataframe
    new_data_path : str
        path to new scraped csv file
    match_columns : List
        Columns to be used for the comparision between databases
    Returns:
    data_to_preprocessing_path : str
        Path to data to be preprocessed with NLP
    data_to_keep_path : str
        Path to data already preprocessed from the old database with no
        modifications.
    """
    old_db = pd.read_pickle(actual_db_path)
    new_db = pd.read_csv(new_data_path, low_memory=False)
    new_db = new_db.fillna("nan")
    new_db = new_db.replace(to_replace="'", value="-", regex=True)
    new_db = new_db.replace(to_replace='\"', value="-", regex=True)
    new_db = new_db.replace(to_replace="  ", value = " ", regex=True)
    new_db = new_db.replace(to_replace="    ", value = " ", regex=True)
    
    to_preprocessing = new_db.merge(old_db, on=match_columns, how='left',
                                    indicator='_lmerge', suffixes=(None, "_drop"))
    to_preprocessing = to_preprocessing.loc[to_preprocessing['_lmerge']=='left_only']
    to_keep = old_db.merge(new_db, on=match_columns, how='inner', indicator='_innermerge',
                           suffixes=(None,"_drop"))
    to_keep = to_keep[old_db.columns.to_list()]
    to_preprocessing = to_preprocessing[new_db.columns.to_list()]

    to_preprocessing.to_pickle(os.path.join(output_path, 'to_preprocess.pkl'))
    return to_keep

def preprocessing_NLP(raw_data_path, output_folder=None, column='abstract'):
    """
    Preprocesses the data collected by the scraper using different NLP
    functions, which are stored in preprocessing/utils.py

    Parameters
    ----------
    raw_data_path : str
        path of pickle file containing the new raw data output of the scraper
    output_folder : str
        path-to-folder where the elaborated data will be saved as pkl
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
    
    # Save data as pickle for a faster reading/writing
    if output_folder:
        raw_data.to_pickle(output_folder+'/preprocessed_data.pkl')
        print(f"Preprocessed data saved in {output_folder+'/preprocessed_data.pkl'}")
    return raw_data

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
    # Initialize and configure the logger
    logger = logging.getLogger("Scraping log")
    logger.setLevel(logging.INFO)
    fh = logging.FileHandler(config.LOG_FILE, "w", "utf-8")
    fh.setLevel(logging.INFO)
    formatter = logging.Formatter("%(asctime)s - %(name)s - %(filename)s >"
                                  "%(funcName)17s(): Line %(lineno)s - "
                                  "%(levelname)s - %(message)s")
    fh.setFormatter(formatter)
    logger.addHandler(fh)

    # Get the credentials for the Google Index API. The approach depends on
    # whether this script is running on GitHub (via GitHub Actions) or
    # locally. In the latter case you need a valid config.JSON_KEY_FILE in
    # this repo.
    #if os.path.exists(config.JSON_KEY_FILE):
        # This script is running locally
    #    google_credentials = ServiceAccountCredentials.from_json_keyfile_name(
    #        config.JSON_KEY_FILE, scopes=config.SCOPES)
    #else:
    #    # This script is running on GitHub
    #    client_secret = os.environ.get('CLIENT_SECRET')
    #    client_secret = json.loads(client_secret)
    #    client_secret_str = json.dumps(client_secret)
    #    google_credentials = ServiceAccountCredentials.from_json_keyfile_dict(
    #    json.loads(client_secret_str), scopes=config.SCOPES)

    # Clean up main data file and operator-specific error log files
    try:
        os.remove(config.GEOSERVICES_CH_CSV)
    except OSError as e:
        logger.error("Could not delete %s: %s" %
                     (config.GEOSERVICES_CH_CSV, e))
    error_log_files = glob.glob(os.path.join(
        config.DEAD_SERVICES_PATH, "*_errors.csv"))
    for error_log_file in error_log_files:
        try:
            os.remove(error_log_file)
        except OSError as e:
            logger.error("Could not delete %s: %s" % (error_log_file, e))

    # Load sources
    sources = load_source_collection()
    num_sources = len(sources)
    n = 1

    scraping_startT = time()
    print(f"Startup time until scraping: {int((process_startT-scraping_startT) / 60)} mins")
    for source in sources:
        scrape_source_startT = time()
        server_operator = source['Description']
        server_url = source['URL']
        # Check if a custom scraper exists for this source
        if os.path.isfile(os.path.join(config.SOURCE_SCRAPER_DIR,
                                       "%s.py" % server_operator)):
            scraper_type = "custom"
        else:
            scraper_type = "default"

        status_msg = "Running %s scraper on %s > %s (source %s/%s)" % (
            scraper_type, server_operator, server_url, n, num_sources)
        print(status_msg)
        logger.info(status_msg)

        # Check if this server is online. If yes, proceed to gather
        # information
        if is_online(source):
            get_service_info(source)
           
        else:
            logger.warning("Scraping %s > %s aborted" % (
                server_operator, server_url))
        n += 1
        scrape_source_endT = time()
        logger.info(f"Dataset {source['URL']} processed in {int(scrape_source_endT-scrape_source_startT)} seconds")

    scraping_endT = time()
    print(f"Scraping took: {int((scraping_endT-scraping_startT) / 60)} mins")

    write_dataset_info(config.GEOSERVICES_CH_CSV,config.GEOSERVICES_CH_CSV)

    data_to_keep = check_new_data(os.path.join(config.TEMP_PROCESSED_DATA_PKL),
                   config.GEOSERVICES_CH_CSV,
                   match_columns=['name','title','provider','keywords','abstract','endpoint'],
                   output_path=os.path.split(config.GEOSERVICES_CH_CSV)[0])
    
    print("\nKeeping "+str(len(data_to_keep))+" datasets from old database")
    logger.info(f"Keeping {len(data_to_keep)} datasets from old database")

    preprd_data = preprocessing_NLP(os.path.join(os.path.split(config.GEOSERVICES_CH_CSV)[0],
                                                 'to_preprocess.pkl'))
    pathpart = os.path.join(config.WORKFLOW_ARTIFACT_FOLDER,'preprd_data.pkl')

    preprd_data.to_pickle(os.path.join(config.WORKFLOW_ARTIFACT_FOLDER,'preprd_data.pkl'))
    preprd_data.to_csv(os.path.join(config.WORKFLOW_ARTIFACT_FOLDER,'preprd_data.csv'))
    # Save to data for last pipeline stage
    data_to_keep.to_pickle(os.path.join(os.path.split(config.GEOSERVICES_CH_CSV)[0],'data_to_keep.pkl'))
    data_to_keep.to_csv(os.path.join(os.path.split(config.GEOSERVICES_CH_CSV)[0],'data_to_keep.csv'))

    process_endT = time()
    print(f"Job took: {int((process_endT-process_startT) / 60)} mins")
