import os
import re
import xml.etree.ElementTree as ET
from geocat.error_logger import log_error  # Import log_error from error_logger.py

# Counters for successful and failed XML files
success_count = 0
error_count = 0


def remove_html_tags(text):
    """Remove HTML tags from a string while preserving its content."""
    clean = re.compile('<.*?>')
    return re.sub(clean, '', text)

def clean_xml_file(file_path):
    """Clean an XML file by removing HTML tags and formatting it properly."""
    global success_count, error_count  # Access the counters

    if not os.path.exists(file_path):
        log_error(f"File not found: {file_path}", "error")
        error_count += 1
        return

    try:
        tree = ET.parse(file_path)
        root = tree.getroot()
    except ET.ParseError as e:
        log_error(f"XML parsing failed for {file_path}", "error", e)
        error_count += 1
        return
    except Exception as e:
        log_error(f"Unexpected error while parsing {file_path}", "error", e)
        error_count += 1
        return

    try:
        for elem in root.iter():
            if elem.text:
                elem.text = remove_html_tags(elem.text)
    except Exception as e:
        log_error(f"Error while processing text in {file_path}", "error", e)
        error_count += 1
        return

    try:
        cleaned_xml = ET.tostring(root, encoding='utf-8').decode('utf-8')
        cleaned_xml = cleaned_xml.replace('\n', '').replace('\t', '')
        cleaned_xml = re.sub(r"(&#13;|&#10;|&#xD;|&#xA;)", " ", cleaned_xml)

        cleaned_lines = []
        temp_line = ""

        for line in cleaned_xml.splitlines():
            line = line.strip()
            if not line.endswith(">"):
                temp_line += line + " "
            else:
                temp_line += line
                cleaned_lines.append(temp_line.strip())
                temp_line = ""

        if temp_line:
            cleaned_lines.append(temp_line.strip())

        with open(file_path, "w", encoding="utf-8") as file:
            file.write("\n".join(cleaned_lines) + "\n")



    except Exception as e:
        log_error(f"Error writing cleaned XML for {file_path}", "error", e)
        error_count += 1

def process_folder(folder_path):
    """Process all XML files in a specified folder."""
    global success_count, error_count  # Access the counters

    if not os.path.exists(folder_path):
        log_error(f"Warning: Folder '{folder_path}' not found. Skipping...", "error")
        return

    for filename in os.listdir(folder_path):
        if filename.endswith(".xml"):
            file_path = os.path.join(folder_path, filename)
            clean_xml_file(file_path)

def process_folders(folders):
    """Process multiple folders containing XML files."""
    log_error(f"Starting cleaning of XML {folders}", "info")
    for folder in folders:
        process_folder(folder)

    # Save statistics for future analysis
    log_error(f"Finished cleaning of XML {folders} successfully", "info")
