import os
import xml.etree.ElementTree as ET
import pandas as pd
from geocat.error_logger import log_error  # Import log_error from error_logger.py


def extract_metadata(xml_file):
    """
    Extract metadata fields from a GeoCat XML metadata file.

    Parameters:
        xml_file (str): Path to the XML metadata file.

    Returns:
        tuple: A tuple containing extracted values.
    """
    try:
        tree = ET.parse(xml_file)
        root = tree.getroot()
    except Exception as e:
        log_error(f"Failed to parse XML file: {xml_file}", exception=e)
        raise

    namespace = {
        "gmd": "http://www.isotc211.org/2005/gmd",
        "gco": "http://www.isotc211.org/2005/gco",
        "che": "http://www.geocat.ch/2008/che",
        "xsi": "http://www.w3.org/2001/XMLSchema-instance"
    }

    def safe_find_text(path, default="N/A"):
        try:
            el = root.find(path, namespace)
            return el.text.strip() if el is not None and el.text else default
        except Exception as e:
            log_error(f"Error extracting path '{path}' in {xml_file}", exception=e)
            return default

    def safe_find_all(path):
        try:
            return root.findall(path, namespace)
        except Exception as e:
            log_error(f"Error finding all elements at '{path}' in {xml_file}", exception=e)
            return []

    file_identifier = safe_find_text(".//gmd:fileIdentifier/gco:CharacterString")

    dataset_language = safe_find_text(".//gmd:language/gmd:LanguageCode")
    if dataset_language == "N/A":
        dataset_language = safe_find_text(".//gmd:language/gco:CharacterString")

    titles = {}
    titles["dataset_title"] = safe_find_text(".//gmd:identificationInfo//gmd:citation//gmd:title/gco:CharacterString")
    try:
        title_localized_element = root.find(".//gmd:identificationInfo//gmd:citation//gmd:title/gmd:PT_FreeText", namespace)
        if title_localized_element is not None:
            for text_group in title_localized_element.findall("gmd:textGroup/gmd:LocalisedCharacterString", namespace):
                locale = text_group.attrib.get("locale", "").replace("#", "").strip()
                if text_group.text:
                    titles[f"dataset_title_{locale}"] = text_group.text.strip()
    except Exception as e:
        log_error(f"Failed to extract localized titles from {xml_file}", exception=e)

    descriptions = {}
    descriptions["dataset_description"] = safe_find_text(".//gmd:identificationInfo//gmd:abstract/gco:CharacterString")
    try:
        description_localized_element = root.find(".//gmd:identificationInfo//gmd:abstract/gmd:PT_FreeText", namespace)
        if description_localized_element is not None:
            for text_group in description_localized_element.findall("gmd:textGroup/gmd:LocalisedCharacterString", namespace):
                locale = text_group.attrib.get("locale", "").replace("#", "").strip()
                if text_group.text:
                    descriptions[f"dataset_description_{locale}"] = text_group.text.strip()
    except Exception as e:
        log_error(f"Failed to extract localized descriptions from {xml_file}", exception=e)

    issued_date = safe_find_text(".//gmd:identificationInfo//gmd:citation/gmd:CI_Citation/gmd:date/gmd:CI_Date/gmd:date/gco:Date")
    if issued_date == "N/A":
        issued_date = safe_find_text(".//gmd:identificationInfo//gmd:citation/gmd:CI_Citation/gmd:date/gmd:CI_Date/gmd:date/gco:DateTime")

    publisher_name = "N/A"
    for path in [
        ".//gmd:contact//gmd:organisationName/gco:CharacterString",
        ".//gmd:pointOfContact//gmd:organisationName/gco:CharacterString"
    ]:
        val = safe_find_text(path)
        if val != "N/A":
            publisher_name = val
            break

    publisher_url = "N/A"
    for path in [
        ".//gmd:pointOfContact//gmd:contactInfo//gmd:CI_Contact//gmd:onlineResource//gmd:linkage/gco:CharacterString",
        ".//gmd:contact//gmd:contactInfo//gmd:CI_Contact//gmd:onlineResource//gmd:CI_OnlineResource//gmd:linkage/gmd:URL",
        ".//gmd:contact//gmd:contactInfo//gmd:CI_Contact//gmd:onlineResource//gmd:CI_OnlineResource//gmd:linkage[@xsi:type='che:PT_FreeURL_PropertyType']/gmd:URL"
    ]:
        val = safe_find_text(path)
        if val != "N/A":
            publisher_url = val
            break

    dataset_theme = [el.text.strip() for el in safe_find_all(".//gmd:topicCategory/gmd:MD_TopicCategoryCode") if el is not None and el.text]
    if not dataset_theme:
        dataset_theme = ["N/A"]

    keywords = {"UNKNOWN": []}
    for keyword_element in safe_find_all(".//gmd:descriptiveKeywords/gmd:MD_Keywords/gmd:keyword"):
        try:
            keyword_text_element = keyword_element.find("gco:CharacterString", namespace)
            if keyword_text_element is not None and keyword_text_element.text:
                keywords["UNKNOWN"].append(keyword_text_element.text.strip())
            localized_texts = keyword_element.findall("gmd:PT_FreeText/gmd:textGroup/gmd:LocalisedCharacterString", namespace)
            for text_element in localized_texts:
                lang_code = text_element.attrib.get("locale", "").replace("#", "").strip()
                if text_element.text and lang_code:
                    keywords.setdefault(lang_code, []).append(text_element.text.strip())
        except Exception as e:
            log_error(f"Failed to extract keyword from element in {xml_file}", exception=e)

    distribution_formats = []

    # 1) Extract ALL OnlineResources under transferOptions
    for el in safe_find_all(".//gmd:distributionInfo/gmd:MD_Distribution/gmd:transferOptions//gmd:CI_OnlineResource"):
        try:
            distribution_formats.append({
                "dataset_identifier": file_identifier,
                "xml_filename": xml_file,   
                "distribution_format": el.findtext("gmd:protocol/gco:CharacterString", default="N/A", namespaces=namespace),
                "distribution_access_url": el.findtext("gmd:linkage/gmd:URL", default="N/A", namespaces=namespace),
                "distribution_download_url": el.findtext("gmd:linkage/gmd:URL", default="N/A", namespaces=namespace),
                "distribution_title_UNKNOWN": el.findtext("gmd:name/gco:CharacterString", default="N/A", namespaces=namespace),
                "distribution_description_UNKNOWN": el.findtext("gmd:description/gco:CharacterString", default="N/A", namespaces=namespace)
            })
        except Exception as e:
            log_error(f"Failed to extract distribution format in {xml_file}", exception=e)

    # 2) Extract the correct main URL from distributorTransferOptions
    stac_url = safe_find_text(
        ".//gmd:distributionInfo/gmd:MD_Distribution/"
        "gmd:distributor/gmd:MD_Distributor/"
        "gmd:distributorTransferOptions/gmd:MD_DigitalTransferOptions/"
        "gmd:onLine/gmd:CI_OnlineResource/gmd:linkage/gmd:URL"
    )

    if stac_url != "N/A":
        distribution_formats.append({
            "dataset_identifier": file_identifier,
            "xml_filename": xml_file,
            "distribution_format": "WWW:DOWNLOAD-URL",
            "distribution_access_url": stac_url,
            "distribution_download_url": stac_url,
            "distribution_title_UNKNOWN": "Main Distribution URL",
            "distribution_description_UNKNOWN": "Primary online access URL"
        })



    contact_points = []
    contact_elements = safe_find_all(".//gmd:identificationInfo//gmd:pointOfContact//gmd:CI_ResponsibleParty")
    contact_elements += safe_find_all(".//gmd:identificationInfo/che:CHE_MD_DataIdentification/gmd:pointOfContact/che:CHE_CI_ResponsibleParty")
    for el in contact_elements:
        try:
            contact_points.append({
                "contact_name": el.findtext("gmd:organisationName/gco:CharacterString", default="N/A", namespaces=namespace),
                "contact_email": el.findtext(".//gmd:electronicMailAddress/gco:CharacterString", default="N/A", namespaces=namespace)
            })
        except Exception as e:
            log_error(f"Failed to extract contact point in {xml_file}", exception=e)
    
    return (
        file_identifier,
        dataset_language,
        titles,
        descriptions,
        publisher_name,
        publisher_url,
        dataset_theme,
        issued_date,
        keywords,
        distribution_formats,
        contact_points
    )

def extract_and_save_all_geocat(input_folder, output_folder):
    success_count = 0
    fail_count = 0
    """
    Extract metadata from all XML files in the input folder and save results to CSV files.

    Parameters:
        input_folder (str): Folder containing GeoCat XML files.
        output_folder (str): Folder to save output CSV files.
    """
    log_error(f"Start extraction form geocat.ch XML files", level="info")

    dataset_data, distribution_data, contact_data = [], [], []

    for filename in os.listdir(input_folder):
        if filename.endswith(".xml"):
            file_path = os.path.join(input_folder, filename)
            try:
                (
                    file_id, lang, titles, descs, pub_name, pub_url,
                    theme, date, keywords, dists, contacts
                ) = extract_metadata(file_path)
            except Exception as e:
                log_error(f"Failed to process {file_path}", exception=e)
                fail_count += 1
                continue

            entry = {
                "dataset_identifier": file_id,
                "dataset_language": lang,
                "dataset_publisher_name": pub_name,
                "dataset_publisher_URL": pub_url,
                "dataset_theme": theme,
                "dataset_issued": date,
                "xml_filename": filename,
                "origin": "geocat.ch"
            }
            entry.update(titles)
            entry.update(descs)
            for code, words in keywords.items():
                entry[f"dataset_keyword_{code}"] = words

            dataset_data.append(entry)
            success_count += 1

            for d in dists:
                d.update({"xml_filename": filename, "origin": "geocat.ch"})
                distribution_data.append(d)

            for c in contacts:
                c.update({"dataset_identifier": file_id,"xml_filename": filename, "origin": "geocat.ch"})
                contact_data.append(c)

    os.makedirs(output_folder, exist_ok=True)

    try:
        pd.DataFrame(dataset_data).to_csv(os.path.join(output_folder, "geocat_dataset_metadata.csv"), index=False)
        pd.DataFrame(distribution_data).to_csv(os.path.join(output_folder, "geocat_distribution_metadata.csv"), index=False)
        pd.DataFrame(contact_data).to_csv(os.path.join(output_folder, "geocat_contact_point_metadata.csv"), index=False)
        log_error("GeoCat metadata extraction completed successfully.", level="info")
    except Exception as e:
        log_error("Failed to write CSV files.", exception=e)





def main():
    """
    Main entry point for standalone use.
    Extracts metadata from default folder and writes output CSVs to current directory.
    """
    input_folder = "saved_metadata_xml"
    output_folder = "."
    extract_and_save_all_geocat(input_folder, output_folder)
    log_error("GeoCat metadata extraction completed successfully.", level="info")


if __name__ == "__main__":
    main()


