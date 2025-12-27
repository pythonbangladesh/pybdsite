import os
import csv
from pathlib import Path
import structlog

logger = structlog.get_logger("__name__")


def extract_community_from_ref_code(ref_code):
    """
    Parse and validate ref_code format, extract community code.
    
    Args:
        ref_code (str): Certificate reference code (e.g., "BD-PY-2024-0001")
    
    Returns:
        str: Community code (e.g., "BD")
    
    Raises:
        ValueError: If ref_code format is invalid
    """
    parts = ref_code.split("-")
    if len(parts) < 2:
        raise ValueError(f"Invalid certificate reference code format: {ref_code}")
    community = parts[0].strip().lower()
    if not community:
        raise ValueError(f"Community code cannot be empty in: {ref_code}")
    logger.info(f"Extracted community '{community}' from ref_code '{ref_code}'")
    return community


def list_files_in_directory(directory_path, extension=".csv"):
    """
    Get all files of a specific extension from a directory.
    
    Args:
        directory_path (str): Path to directory (e.g., "db/BD/")
        extension (str): File extension to filter by (default: ".csv")
    
    Returns:
        list: List of CSV file paths
    
    Raises:
        FileNotFoundError: If directory doesn't exist or contains no CSV files
    """
    dir_path = Path(directory_path)
    
    if not dir_path.exists():
        raise FileNotFoundError(f"Community directory not found: {directory_path}")
    
    if not dir_path.is_dir():
        raise FileNotFoundError(f"Path is not a directory: {directory_path}")
    
    files = list(dir_path.glob(f"*{extension}"))
    
    if not files:
        raise FileNotFoundError(f"No certificate files found in: {directory_path}")
    files_list = [str(file) for file in files]
    logger.info(
        f"Found {len(files_list)} '{extension}' files in directory '{directory_path}'",
        files=files_list,
    )
    return files_list


def search_csv_for_ref_code(csv_file_path, ref_code):
    """
    Search a single CSV file for matching ref_code.
    
    Args:
        csv_file_path (str): Path to CSV file
        ref_code (str): Certificate reference code to search for
    
    Returns:
        dict | None: Row data as dict if found, None if not found
    """
    try:
        logger.info(
            f"Searching for participant data with ref_code/certificate_id '{ref_code}' in file '{csv_file_path}'",
            ref_code=ref_code,
            csv_file_path=csv_file_path
        )
        with open(csv_file_path, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                if row.get('certificate_id', '').strip() == ref_code:
                    # Return the row data, removing any empty values
                    data = {k: v.strip() for k, v in row.items() if v}
                    logger.info(f"Found participant data for ref_code/certificate_id '{ref_code}' in file '{csv_file_path}'", data=data)
                    return data
        logger.warning(f"ref_code/certificate_id '{ref_code}' not found in file '{csv_file_path}'")
        return None
    except Exception as e:
        logger.error(f"Error reading CSV file {csv_file_path}: {e}")
        return None


def find_certificate_in_community(community, ref_code):
    """
    Search all CSV files in community folder for certificate.
    
    Args:
        community (str): Community code (e.g., "BD")
        ref_code (str): Certificate reference code
    
    Returns:
        dict: Participant data including event_id, participant_name, score, etc.
    
    Raises:
        FileNotFoundError: If certificate not found
    """
    directory_path = f"src/db/{community}"
    # Get all CSV files in community directory
    csv_files = list_files_in_directory(directory_path)
    # Search each CSV file
    for csv_file in csv_files:
        cert_data = search_csv_for_ref_code(csv_file, ref_code)
        if cert_data:
            return cert_data
    # If we reach here, certificate was not found
    raise FileNotFoundError(f"Certificate not found: {ref_code}")


def get_event_details(event_id):
    """
    Fetch event information from events.csv.
    
    Args:
        event_id (str): Event ID (e.g., "EVT-001")
    
    Returns:
        dict: Event details including type, name, facilitator, director, dates, etc.
    
    Raises:
        FileNotFoundError: If events.csv doesn't exist
        ValueError: If event_id not found (data integrity issue)
    """
    events_file = "src/db/events.csv"
    if not os.path.exists(events_file):
        raise FileNotFoundError(f"Events database not found: {events_file}")
    try:
        logger.info(f"Fetching event details for event_id '{event_id}' from '{events_file}'", event_id=event_id)
        with open(events_file, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                if row.get('event_id', '').strip() == event_id:
                    # Return event data, removing empty values
                    return {k: v.strip() for k, v in row.items() if v}
        # Event ID not found
        raise ValueError(f"Event data not found for event_id: {event_id}. Data integrity issue.")
    except Exception as e:
        if isinstance(e, ValueError):
            raise
        raise ValueError(f"Error reading events database: {e}")


def get_certificate_data(ref_code):
    """
    Main function: Get complete certificate data by orchestrating all other functions.
    
    Args:
        ref_code (str): Certificate reference code (e.g., "BD-PY-2024-0001")
    
    Returns:
        dict: Complete certificate context with participant and event data
    
    Raises:
        ValueError: If ref_code format is invalid or data integrity issues
        FileNotFoundError: If certificate or event not found
    """
    # Step 1: Extract community code
    community = extract_community_from_ref_code(ref_code)
    
    # Step 2: Find certificate in community folder
    cert_data = find_certificate_in_community(community, ref_code)
    
    # Step 3: Get event_id from certificate data
    event_id = cert_data.get('event_id')
    if not event_id:
        raise ValueError(f"Certificate data missing event_id: {ref_code}")
    
    # Step 4: Get event details
    event_data = get_event_details(event_id)
    
    # Step 5: Merge certificate and event data
    complete_data = {
        **cert_data,
        **event_data
    }
    return complete_data

