# metadata_downloader.py

import requests
import xml.etree.ElementTree as ET
import os
import time
import csv
import pandas as pd
import re
from datetime import datetime

CSW_URL = "https://www.geocat.ch/geonetwork/srv/deu/csw"
WAIT_TIME = 0


# ===========================
# CSW FETCH FUNCTIONS
# ===========================

def fetch_records_sorted_by_identifier(start_position=1, max_records=100, ascending=True):
    sort_order = "ASC" if ascending else "DESC"
    headers = {'Content-Type': 'application/xml'}
    xml_payload = f"""<?xml version="1.0" encoding="UTF-8"?>
<csw:GetRecords
    xmlns:csw="http://www.opengis.net/cat/csw/2.0.2"
    xmlns:ogc="http://www.opengis.net/ogc"
    xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
    service="CSW"
    version="2.0.2"
    resultType="results"
    startPosition="{start_position}"
    maxRecords="{max_records}"
    outputFormat="application/xml"
    outputSchema="http://www.opengis.net/cat/csw/2.0.2"
    xsi:schemaLocation="http://www.opengis.net/cat/csw/2.0.2
        http://schemas.opengis.net/csw/2.0.2/CSW-discovery.xsd">
    <csw:Query typeNames="csw:Record">
        <csw:ElementSetName>full</csw:ElementSetName>
        <ogc:SortBy>
            <ogc:SortProperty>
                <ogc:PropertyName>dc:identifier</ogc:PropertyName>
                <ogc:SortOrder>{sort_order}</ogc:SortOrder>
            </ogc:SortProperty>
        </ogc:SortBy>
    </csw:Query>
</csw:GetRecords>"""

    response = requests.post(CSW_URL, headers=headers, data=xml_payload)
    response.raise_for_status()
    return response.text

def is_exception_report(xml_text):
    try:
        root = ET.fromstring(xml_text)
        return root.tag.endswith("ExceptionReport")
    except ET.ParseError:
        return False

def extract_title_and_id(xml_text, start_position):
    namespaces = {
        "csw": "http://www.opengis.net/cat/csw/2.0.2",
        "dc": "http://purl.org/dc/elements/1.1/"
    }
    try:
        if is_exception_report(xml_text):
            raise ValueError(f"ExceptionReport at position {start_position}")

        root = ET.fromstring(xml_text)
        records = root.findall(".//csw:Record", namespaces)
        results = []
        for record in records:
            title_el = record.find("dc:title", namespaces)
            identifier_el = record.find("dc:identifier", namespaces)
            title = title_el.text.strip() if title_el is not None else "(kein Titel)"
            identifier = identifier_el.text.strip() if identifier_el is not None else "(kein Identifier)"
            results.append((identifier, title))
        return results, len(records), root
    except ET.ParseError as e:
        return [], 0, None

def get_total_records(xml_root):
    search_results = xml_root.find(".//{http://www.opengis.net/cat/csw/2.0.2}SearchResults")
    if search_results is not None and "numberOfRecordsMatched" in search_results.attrib:
        return int(search_results.attrib["numberOfRecordsMatched"])
    return None

def robust_fetch(start, end, ascending=True, log_file=None):
    batch_size = end - start + 1
    try:
        xml_data = fetch_records_sorted_by_identifier(start_position=start, max_records=batch_size, ascending=ascending)
        title_id_pairs, _, _ = extract_title_and_id(xml_data, start)
        return title_id_pairs
    except Exception as e:
        if batch_size == 1:
            if log_file:
                direction = "(reversed)" if not ascending else "(forward)"
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                with open(log_file, mode="a", encoding="utf-8") as log:
                    log.write(f"[{timestamp}] FinalFetchError {direction} at position {start}: {type(e).__name__}: {e}\n")
            return []
        else:
            mid = (start + end) // 2
            results1 = robust_fetch(start, mid, ascending, log_file)
            results2 = robust_fetch(mid + 1, end, ascending, log_file)
            return results1 + results2

def download_geocat_metadata(save_dir=r"01_ETL\02_geocat.ch", csv_file="geocat_dataset_id_title.csv", log_file=None, start_pos=None, batch_size=1000):
    os.makedirs(save_dir, exist_ok=True)
    path_csv = os.path.join(save_dir, csv_file)
    if log_file:
        log_file = os.path.join(save_dir, log_file)

    log_initialized = False

    all_titles_and_ids = []
    total_fetched = 0
    ascending = True

    try:
        initial_xml = fetch_records_sorted_by_identifier(start_position=1, max_records=1, ascending=ascending)
        _, _, root = extract_title_and_id(initial_xml, 1)
        total_records = get_total_records(root)
        print(f"Total records available: {total_records}")
    except Exception as e:
        print(f"Failed to fetch total number of records: {e}")
        return

    first_half_limit = 15000

    if start_pos:
        ascending = True
        start = start_pos
        while start < first_half_limit:
            if log_file and not log_initialized:
                open(log_file, mode="w").close()
                log_initialized = True

            end = min(start + batch_size - 1, first_half_limit - 1)
            title_id_pairs = robust_fetch(start, end, ascending, log_file)
            print(f"Fetched records {start} to {end}")
            all_titles_and_ids.extend(title_id_pairs)
            total_fetched += len(title_id_pairs)
            start += batch_size
            time.sleep(WAIT_TIME)

        # total_reverse_fetch = total_records - first_half_limit
        #! HARDCOED START POSITION INSIEDE FUNCTION FOR TESTING PURPOSES!
        total_reverse_fetch = total_records - 17000
        #! HARDCOED START POSITION INSIEDE FUNCTION FOR TESTING PURPOSES!

        ascending = False
        for i in range(0, total_reverse_fetch, batch_size):
            rel_start = i + 1
            rel_end = min(i + batch_size, total_reverse_fetch)
            title_id_pairs = robust_fetch(rel_start, rel_end, ascending, log_file)
            print(f"Fetched records {rel_start} to {rel_end} (reversed)")
            all_titles_and_ids.extend(title_id_pairs[::-1])
            total_fetched += len(title_id_pairs)
            time.sleep(WAIT_TIME)
    else:
        start = 1
        while start <= first_half_limit:
            if log_file and not log_initialized:
                open(log_file, mode="w").close()
                log_initialized = True

            end = min(start + batch_size - 1, first_half_limit)
            title_id_pairs = robust_fetch(start, end, ascending, log_file)
            print(f"Fetched records {start} to {end}")
            all_titles_and_ids.extend(title_id_pairs)
            total_fetched += len(title_id_pairs)
            start += batch_size
            time.sleep(WAIT_TIME)

        start = total_records
        ascending = False
        while start > first_half_limit:
            end = max(start - batch_size + 1, first_half_limit + 1)
            title_id_pairs = robust_fetch(end, start, ascending, log_file)
            print(f"Fetched records {end} to {start}")
            all_titles_and_ids.extend(title_id_pairs[::-1])
            total_fetched += len(title_id_pairs)
            start = end - 1
            time.sleep(WAIT_TIME)

    with open(path_csv, mode="w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["Identifier", "Title"])
        writer.writerows(all_titles_and_ids)

    print(f"Done. Total records fetched: {total_fetched}")
    print(f"Results saved to {path_csv}")




# ===========================
# XML METADATA RETRIEVAL
# ===========================





def sanitize_filename(identifier):
    return re.sub(r'[<>:"/\\|?*]', '_', identifier)


def fetch_and_save_metadata(identifier, save_folder):
    url = f"https://www.geocat.ch/geonetwork/srv/api/records/{identifier}/formatters/xml?approved=true"
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()

        xml_content = response.content.decode('utf-8')
        xml_content = '\n'.join([line.strip() for line in xml_content.splitlines() if line.strip()])

        safe_identifier = sanitize_filename(identifier)
        xml_path = os.path.join(save_folder, f"{safe_identifier}.xml")

        with open(xml_path, "w", encoding="utf-8") as file:
            file.write(xml_content)

        return True

    except requests.exceptions.RequestException as e:
        print(f"Error fetching metadata for {identifier}: {e}")
    except OSError as e:
        print(f"Error saving metadata for {identifier}: {e}")
    return False

from concurrent.futures import ThreadPoolExecutor, as_completed

def download_xml_metadata_from_csv(save_dir="01_ETL\\02_geocat.ch", csv_file="geocat_dataset_id_title.csv", max_files=None, max_workers=20):
    """
    Downloads XML metadata files listed in a CSV using parallel threads.

    Args:
        save_dir (str): Folder where XML files will be saved.
        csv_file (str): CSV filename containing the 'Identifier' column.
        max_files (int, optional): Limit the number of records to download.
        max_workers (int): Number of parallel threads.
    """

    print("Save folder:", save_dir)
    os.makedirs(save_dir, exist_ok=True)

    path_csv = os.path.join(save_dir, csv_file)
    print("CSV path:", path_csv)

    df_datasets = pd.read_csv(path_csv)
    num_records = len(df_datasets) if max_files is None else min(max_files, len(df_datasets))

    identifiers = df_datasets["Identifier"].head(num_records).tolist()
    total = len(identifiers)

    print(f"Starting parallel download with {max_workers} workers for {total} records...")

    downloaded = 0
    failed = 0

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_id = {executor.submit(fetch_and_save_metadata, identifier, save_dir): identifier for identifier in identifiers}

        for future in as_completed(future_to_id):
            identifier = future_to_id[future]
            try:
                success = future.result()
                if success:
                    downloaded += 1
                else:
                    failed += 1
            except Exception as e:
                print(f"Error for {identifier}: {e}")
                failed += 1

            if downloaded % 500 == 0 and downloaded > 0:
                print(f"{downloaded} downloaded so far...")

    print(f"Metadata retrieval completed. Total downloaded: {downloaded}/{total}, failed: {failed}")



