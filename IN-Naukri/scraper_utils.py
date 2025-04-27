"""
Utility functions for the Naukri scraper, including nkparam generation,
data extraction, and file handling.
"""
import time
import json
import csv
import pandas as pd
from datetime import datetime
import os
import requests # Import requests here for type hinting if needed

# --- Placeholder for nkparam generation ---
def get_dynamic_nkparam(page_num: int, request_params: dict, request_headers: dict) -> str:
    """
    Generates the dynamic 'nkparam' required for Naukri API requests.

    **IMPORTANT:** Replace the placeholder logic with your actual, working
    implementation for generating the correct nkparam based on the
    request details (page number, parameters, headers, time, etc.).
    Failure to provide the correct nkparam will result in API errors (401/403).

    Args:
        page_num: The page number being requested.
        request_params: The parameters for the specific API request.
        request_headers: The headers for the specific API request (before adding nkparam).

    Returns:
        The calculated nkparam string.

    Raises:
        ValueError: If nkparam generation fails.
    """
    # print(f"      (Debug) Generating nkparam for page {page_num}...") # Keep disabled unless debugging
    # --- !!! YOUR ACTUAL NKPARAM GENERATION/RETRIEVAL LOGIC GOES HERE !!! ---
    # Example: This is just a placeholder, it will NOT work reliably.
    new_nkparam = f"your_generated_param_for_page_{page_num}_{int(time.time())}"
    # --- !!! END OF YOUR LOGIC !!! ---

    if not new_nkparam:
         raise ValueError(f"Failed to get nkparam for page {page_num}")
    # print(f"      (Debug) Generated nkparam: {new_nkparam[:10]}...") # Keep disabled unless debugging
    return new_nkparam

# --- Data Extraction ---
def extract_placeholder_info(placeholders: list) -> tuple[str, str, str]:
    """Extracts experience, salary, and location from the placeholders list."""
    exp = "Not Specified"
    salary = "Not Specified"
    location = "Not Specified"
    if not isinstance(placeholders, list): # Add safety check
        return exp, salary, location
    for item in placeholders:
        if not isinstance(item, dict): continue # Safety check
        item_type = item.get('type')
        label = item.get('label')
        if label: # Only update if label is not empty/None
            if item_type == 'experience':
                exp = label
            elif item_type == 'salary':
                salary = label
            elif item_type == 'location':
                 location = label
    return exp, salary, location

def format_job_for_csv(job_dict: dict, timestamp: str) -> dict | None:
    """Formats a single job dictionary from the API into a flat dictionary for CSV."""
    if not isinstance(job_dict, dict):
        return None # Skip if not a dictionary

    job_id = job_dict.get('jobId')
    if not job_id:
        return None # Skip if no job ID

    placeholders = job_dict.get('placeholders', [])
    exp, salary, loc = extract_placeholder_info(placeholders)

    # Fallback for experience if not in placeholders
    if exp == "Not Specified":
        exp_text = job_dict.get("experienceText", "Not Specified")
        if exp_text and exp_text != "Not Specified": # Use if valid fallback exists
            exp = exp_text

    return {
        'jobId': job_id,
        'title': job_dict.get('title', ''),
        'companyName': job_dict.get('companyName', ''),
        'jdURL': job_dict.get('jdURL', ''),
        'experience': exp,
        'salary': salary,
        'location': loc,
        'tagsAndSkills': job_dict.get('tagsAndSkills', ''),
        'jobDescription': job_dict.get('jobDescription', ''),
        'fetchTimestamp': timestamp
    }

# --- File System and Saving ---
def setup_output_directory(base_dir: str, keyword: str, ctc_filter: str) -> str:
    """Creates a timestamped output directory for a specific filter run."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    run_directory_name = f'{keyword}-{ctc_filter}_run_{timestamp}'
    output_path = os.path.join(base_dir, run_directory_name)

    try:
        os.makedirs(output_path, exist_ok=True)
        print(f"Output directory created/exists: {output_path}")
        return output_path
    except OSError as e:
        print(f"Error creating directory {output_path}: {e}")
        raise # Re-raise the exception to be handled by the caller

def save_json_data(data: list | dict, filename: str):
    """Saves data (list or dict) to a JSON file."""
    print(f"Attempting to save data to {filename}...")
    if not data:
        print(f"No data provided to save to {filename}.")
        return
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f"Successfully saved data to {filename}")
    except Exception as e:
        print(f"ERROR saving data to {filename}: {e}")

def save_jobs_to_csv(jobs_data: list[dict], filename: str, column_order: list[str]):
    """Saves a list of job dictionaries to a CSV file using pandas."""
    print(f"Attempting to save {len(jobs_data)} jobs to {filename}...")
    if not jobs_data:
        print(f"No job data provided to save to {filename}.")
        return
    try:
        df = pd.DataFrame(jobs_data)
        # Ensure all desired columns exist, adding empty ones if needed
        for col in column_order:
            if col not in df.columns:
                df[col] = None # Or pd.NA
        # Reorder columns
        df = df[column_order]
        df.to_csv(filename, index=False, encoding='utf-8', quoting=csv.QUOTE_MINIMAL)
        print(f"Successfully saved pattern analysis CSV to {filename}")
    except Exception as e:
        print(f"ERROR saving pattern analysis CSV to {filename}: {e}")

# --- Request Parameter Generation ---
def construct_request_params(base_params: dict, keyword: str, ctc_filter: str, page_num: int,
                             base_sid: str, location_seo: str) -> dict:
    """Constructs the dynamic parameters for a specific page request."""
    current_params = base_params.copy()
    current_params["pageNo"] = str(page_num)
    current_params["ctcFilter"] = ctc_filter
    current_params["keyword"] = keyword # Ensure keyword consistency
    current_params["k"] = keyword

    # Construct dynamic SID and seoKey (Adjust logic if Naukri changes pattern)
    keyword_seo = keyword.replace(' ', '-')
    if page_num == 1:
        current_params["seoKey"] = f"{keyword_seo}-jobs-{location_seo}" # No -{page_num} for page 1
        current_params["sid"] = f"{base_sid}_1"
    else:
        current_params["seoKey"] = f"{keyword_seo}-jobs-{location_seo}-{page_num}"
        current_params["sid"] = f"{base_sid}_{page_num}"

    return current_params