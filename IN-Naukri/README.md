
# Job-description-scrapper/README.md

# Naukri Job Scraper (IN-Naukri)

This Python script scrapes job listings from Naukri.com based on a specified keyword and CTC (Cost To Company) salary brackets. It fetches data directly from Naukri's internal API, extracts relevant job details, and saves the results into structured JSON and CSV files.

## Purpose

The primary goal is to gather job description data for analysis, such as understanding required skills, experience levels, and salary expectations for specific roles (e.g., "sre") across different salary bands in India.

## Features

* Searches based on a primary keyword.
* Filters results by multiple CTC brackets.
* Handles pagination to scrape multiple pages per filter.
* Includes configurable delays to avoid overwhelming the server.
* Saves raw API responses (JSON).
* Saves extracted and combined job details (JSON).
* Saves formatted job details suitable for analysis (CSV).
* Organizes output into timestamped directories for each run.
* Modular structure (`main.py`, `naukri_scraper.py`, `scraper_config.py`, `scraper_utils.py`) for better maintainability.

## Disclaimer

* **Web scraping can be against the Terms of Service of websites.** Use this script responsibly and ethically. Avoid overly aggressive scraping (high frequency, many concurrent requests) which could lead to your IP being blocked.
* **Naukri.com may change its API structure or authentication mechanisms (like `nkparam`) at any time.** This script might break without notice if such changes occur. You may need to update the code, especially the `nkparam` generation logic, to keep it functional.
* The `nkparam` generation is **critical** and **not implemented** in the provided `scraper_utils.py`. You **must** provide your own working logic for it.

## Prerequisites

* Python 3.x
* Required Python libraries: `requests` and `pandas`

## Installation

1. **Clone the repository (if you haven't already):**
   ```bash
   git clone <your-repository-url>
   cd Job-description-scrapper/IN-Naukri
   ```
2. **Install dependencies:**
   ```bash
   pip install requests pandas
   ```

   *(Consider using a virtual environment: `python -m venv venv`, `source venv/bin/activate` or `venv\Scripts\activate`, then `pip install ...`)*

## Configuration

All major settings are located in `scraper_config.py`. Edit this file before running the script:

1. **`KEYWORD`**: Set the primary job title or skill you want to search for (e.g., `"sre"`, `"python developer"`, `"data scientist"`).
2. **`CTC_FILTERS`**: Define a list of CTC brackets (strings) to iterate through. The script will run separately for each filter in this list. Examples are provided in the file (e.g., `"0to3"`, `"3to6"`, `"25to50"`). Uncomment or add the ones you need.
3. **`MAX_PAGES_PER_FILTER`**: Set the maximum number of pages (each page typically contains 20 results) to scrape for *each* CTC filter. Be mindful of the total number of requests.
4. **`OUTPUT_BASE_DIR`**: The directory where all output subdirectories will be created (defaults to `"output"`).
5. **(Optional) Other Settings:**
   * `REQUEST_TIMEOUT`: Timeout for network requests.
   * `FETCH_DELAY_BASE`, `FETCH_DELAY_RANDOM`: Control the delay between page fetches to be polite to the server.
   * `BASE_URL`, `BASE_PARAMS`, `BASE_HEADERS`: These define the API endpoint and static request details. Usually, you don't need to change these unless Naukri significantly alters its API. **Note:** The `User-Agent` might need occasional updates.
   * `BASE_SID_PATTERN`, `LOCATION_SEO_PART`: These are used to construct dynamic parameters (`sid`, `seoKey`). They might need updating if Naukri changes URL/parameter patterns. Inspect network requests in your browser to verify if needed.
   * `CSV_COLUMN_ORDER`: Defines the columns and their order in the output CSV file.

## CRITICAL STEP: `nkparam` Generation

Naukri's API uses a dynamic parameter, often named `nkparam` (or similar), in its request headers for authentication, rate limiting, or request validation. **This script will fail (likely with 401 Unauthorized or 403 Forbidden errors) without a correctly generated `nkparam` for each request.**

1. **Locate the Function:** Open `scraper_utils.py`. Find the function `get_dynamic_nkparam`.
2. **Understand the Placeholder:** The current code inside this function is **just a placeholder** and **will not work**.
   ```python
   # --- !!! YOUR ACTUAL NKPARAM GENERATION/RETRIEVAL LOGIC GOES HERE !!! ---
   # Example: This is just a placeholder, it will NOT work reliably.
   new_nkparam = f"your_generated_param_for_page_{page_num}_{int(time.time())}"
   # --- !!! END OF YOUR LOGIC !!! ---
   ```
3. **Implement Your Logic:** You need to replace the placeholder section with your **actual, working code** to generate the valid `nkparam` for the given request context (page number, parameters, headers, potentially time, etc.).
   * **How to find the logic?** This usually involves:
     * Inspecting the network requests made by your web browser when browsing Naukri job listings.
     * Analyzing the JavaScript code on the Naukri website to see how this parameter is generated.
     * This can be complex and may involve reverse-engineering obfuscated code.
   * **Failure to do this step correctly will prevent the scraper from fetching any data.**

## Usage

Once you have:

1. Installed dependencies.
2. Configured `scraper_config.py`.
3. **Implemented the `get_dynamic_nkparam` function in `scraper_utils.py`**.

Run the main script from the `IN-Naukri` directory in your terminal:

```bash
python main.py
```
