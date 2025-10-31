import os
import logging

# Set up logging configuration

LOG_FILE = "scraper/tools/geocat_logfile.log"

# Clear the log file before each run
# if os.path.exists(LOG_FILE):
#     with open(LOG_FILE, "w") as file:
#         file.truncate(0)  # Clears the file content

logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

def log_error(message, level="error", exception=None):
    """
    Log a message with different severity levels.

    Args:
        message (str): The log message.
        level (str): Logging level ('info', 'warning', 'error', 'critical').
        exception (Exception, optional): Exception object to log full traceback.

    Returns:
        None
    """
    if exception:
        message = f"{message} | Exception: {exception}"

    if level == "info":
        logging.info(message)
    elif level == "warning":
        logging.warning(message)
    elif level == "error":
        logging.error(message)
    elif level == "critical":
        logging.critical(message)
    else:
        logging.debug(message)  # Default to debug if level is unknown

    print(message)


def log_start_message():
    """
    Logs a start message with text art to indicate the process has begun.

    Returns:
        None
    """
    start_banner = """
    ==============================================================================================
         ____  ____  ____  ______________________    ______________    ____  ________________
        / __ \/ __ \/ __ \/ ____/ ____/ ___/ ___/   / ___/_  __/   |  / __ \/_  __/ ____/ __ \ 
       / /_/ / /_/ / / / / /   / __/  \__ \\__ \    \__ \ / / / /| | / /_/ / / / / __/ / / / /
      / ____/ _, _/ /_/ / /___/ /___ ___/ /__/ /   ___/ // / / ___ |/ _, _/ / / / /___/ /_/ / _ _
     /_/   /_/ |_|\____/\____/_____//____/____/   /____//_/ /_/  |_/_/ |_| /_/ /_____/_____(_|_|_)

    PROCESS STARTED...
    =============================================================================================="""
    logging.info("\n" + start_banner)