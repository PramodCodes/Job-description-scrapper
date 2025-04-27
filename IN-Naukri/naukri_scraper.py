"""
Core scraping logic for fetching job data from Naukri.com for a specific filter.
"""
import requests
import time
import traceback
import os   
# Import from our modules
import scraper_config as cfg
import scraper_utils as utils

def fetch_page_data(page_num: int, params: dict, headers: dict) -> dict | None:
    """
    Fetches and parses JSON data for a single page from the Naukri API.

    Args:
        page_num: The page number to fetch.
        params: The request parameters.
        headers: The request headers (including nkparam).

    Returns:
        The parsed JSON data as a dictionary, or None if fetching/parsing fails critically.

    Raises:
        requests.exceptions.RequestException: For network or HTTP errors (e.g., 4xx, 5xx).
        ValueError: If nkparam generation fails.
        json.JSONDecodeError: If the response is not valid JSON.
    """
    print(f"Fetching Page {page_num}...")
    try:
        response = requests.get(cfg.BASE_URL, params=params, headers=headers, timeout=cfg.REQUEST_TIMEOUT)
        response.raise_for_status() # Raises HTTPError for bad responses (4xx or 5xx)

        print(f"Status Code: {response.status_code} for page {page_num}")
        page_data = response.json() # Raises JSONDecodeError if not valid JSON
        return page_data

    except requests.exceptions.Timeout:
        print(f"Request timed out for page {page_num}.")
        raise # Re-raise to be caught by the main loop
    except requests.exceptions.HTTPError as e:
        print(f"HTTP Error fetching page {page_num}: {e}")
        print(f"Response Body Snippet: {e.response.text[:500]}...")
        raise # Re-raise to be caught by the main loop
    except requests.exceptions.RequestException as e:
        print(f"Request Exception fetching page {page_num}: {e}")
        raise # Re-raise to be caught by the main loop
    except json.JSONDecodeError:
        print(f"Error decoding JSON for page {page_num}.")
        # Optionally log response.text here if needed for debugging
        raise # Re-raise to be caught by the main loop

def scrape_single_filter(keyword: str, ctc_filter: str):
    """
    Scrapes all pages for a given keyword and CTC filter, saving the results.
    """
    print(f"\n=================================================")
    print(f"Starting scrape for Keyword: '{keyword}', CTC Filter: '{ctc_filter}'")
    print(f"=================================================")

    # --- Setup for this filter run ---
    try:
        output_path = utils.setup_output_directory(cfg.OUTPUT_BASE_DIR, keyword, ctc_filter)
    except OSError:
        print(f"Skipping CTC filter: {ctc_filter} due to directory creation error.")
        return # Stop processing this filter

    run_timestamp = os.path.basename(output_path).split('_run_')[-1] # Extract timestamp from dir name
    output_jobdetails_json = os.path.join(output_path, f'{keyword}-{ctc_filter}_job_details_{run_timestamp}.json')
    output_raw_responses_json = os.path.join(output_path, f'{keyword}-{ctc_filter}_raw_api_responses_{run_timestamp}.json')
    output_pattern_csv = os.path.join(output_path, f'{keyword}-{ctc_filter}_job_patterns_{run_timestamp}.csv')

    # --- Data Storage for this run ---
    all_raw_responses = []
    all_job_details = [] # Flat list of job detail dicts (from API)
    all_jobs_for_csv = [] # Flat list of formatted job dicts for CSV
    processed_job_ids = set() # Avoid duplicates in CSV

    # --- Page Scraping Loop ---
    for page_num in range(1, cfg.MAX_PAGES_PER_FILTER + 1):
        print(f"--- Preparing Page {page_num} for CTC: {ctc_filter} ---")

        try:
            # 1. Construct Parameters for this request
            current_params = utils.construct_request_params(
                cfg.BASE_PARAMS, keyword, ctc_filter, page_num,
                cfg.BASE_SID_PATTERN, cfg.LOCATION_SEO_PART
            )

            # 2. Get Dynamic nkparam
            current_headers = cfg.BASE_HEADERS.copy()
            try:
                nkparam_value = utils.get_dynamic_nkparam(page_num, current_params, current_headers)
                current_headers['nkparam'] = nkparam_value
            except ValueError as e:
                print(f"CRITICAL: nkparam error for page {page_num}, CTC {ctc_filter}: {e}. Stopping filter.")
                break # Stop page loop for this filter

            # 3. Fetch Data
            page_data = fetch_page_data(page_num, current_params, current_headers)
            if page_data is None: # Should not happen if exceptions are raised, but safety check
                 print(f"Warning: fetch_page_data returned None for page {page_num}, CTC {ctc_filter}. Skipping.")
                 continue

            # 4. Store Raw Response
            all_raw_responses.append(page_data)

            # 5. Extract and Process Job Details
            jobs_array = page_data.get("jobDetails") # jobDetails is the key in the API response
            if jobs_array is not None and isinstance(jobs_array, list):
                print(f"Found {len(jobs_array)} jobs in jobDetails for page {page_num}, CTC: {ctc_filter}.")
                all_job_details.extend(jobs_array) # Add jobs from this page to the flat list

                # Process for CSV
                for job in jobs_array:
                    formatted_job = utils.format_job_for_csv(job, run_timestamp)
                    if formatted_job and formatted_job['jobId'] not in processed_job_ids:
                        all_jobs_for_csv.append(formatted_job)
                        processed_job_ids.add(formatted_job['jobId'])

                # Check if the results are empty (might signal end of data)
                if not jobs_array and page_num > 1:
                     print(f"Received empty jobDetails list on page {page_num} for CTC: {ctc_filter}. Assuming end of results.")
                     break # Stop processing pages for this filter

            else:
                 print(f"Warning: 'jobDetails' key not found or not a list in response for page {page_num}, CTC: {ctc_filter}.")
                 # Decide if this is fatal - maybe stop after a few pages?
                 if page_num > 5: # Example threshold
                     print("Stopping page loop for this filter due to missing/invalid 'jobDetails' on later page.")
                     break

        # --- Error Handling for the Page Loop ---
        except requests.exceptions.RequestException as e:
            print(f"Request Error processing page {page_num}, CTC {ctc_filter}: {e}")
            if hasattr(e, 'response') and e.response is not None and e.response.status_code in [401, 403, 429]:
                print(f"CRITICAL: Status {e.response.status_code}. Likely nkparam/rate limit issue. Stopping run for CTC: {ctc_filter}.")
            else:
                 print(f"Network/Connection error likely. Stopping run for CTC: {ctc_filter}.")
            break # Stop page loop for this filter on significant errors
        except json.JSONDecodeError:
             print(f"JSON Decode Error processing page {page_num}, CTC {ctc_filter}. Stopping run for this filter.")
             break # Stop page loop
        except Exception as e:
            print(f"An unexpected error occurred on page {page_num}, CTC {ctc_filter}: {e}")
            traceback.print_exc()
            break # Stop page loop for this filter

        # --- Delay ---
        delay = cfg.FETCH_DELAY_BASE + (time.time() % cfg.FETCH_DELAY_RANDOM)
        print(f"Sleeping for {delay:.2f} seconds...")
        time.sleep(delay)

    # --- Post-Processing & Saving for this filter ---
    print(f"\n--- Scraping loop finished for CTC Filter: {ctc_filter} ---")
    print(f"Collected {len(all_raw_responses)} raw page responses.")
    print(f"Collected {len(all_job_details)} job details entries (before CSV deduplication).")
    print(f"Processed {len(all_jobs_for_csv)} unique jobs for CSV.")

    utils.save_json_data(all_raw_responses, output_raw_responses_json)
    utils.save_json_data(all_job_details, output_jobdetails_json) # Save the raw jobDetails combined
    utils.save_jobs_to_csv(all_jobs_for_csv, output_pattern_csv, cfg.CSV_COLUMN_ORDER)

    print(f"\n--- Finished processing CTC Filter: {ctc_filter} ---")