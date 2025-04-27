"""
Configuration settings for the Naukri scraper.
"""

# --- Search Settings ---
KEYWORD = "sre" # <<< SET YOUR PRIMARY SEARCH KEYWORD HERE
CTC_FILTERS = [
            #    "0to3", 
            #    "3to6", 
            #    "6to10", 
            #    "10to15", 
            #    "15to25", 
               "25to50", 
            #    "50to75", 
            #    "75to100", 
            #    "100to500", 
            #    "501"
               ]
# CTC_FILTERS = ["3to6", "6to10"] # Example: Limit filters for testing
# LOCATIONS = "bangalore, bengaluru, hyderabad, hyderabad/secunderabad, chennai, pune, mumbai (all areas), noida, greater noida, gurugram" # Adjust locations if needed
EXPERIENCE = "6" # Adjust experience if needed

# --- API Settings ---
BASE_URL = "https://www.naukri.com/jobapi/v3/search"
MAX_PAGES_PER_FILTER = 500 # Limit pages for testing, original was 400
REQUEST_TIMEOUT = 45 # seconds
FETCH_DELAY_BASE = 2.5 # seconds base delay between requests
FETCH_DELAY_RANDOM = 2.0 # seconds random component for delay

# --- Output Settings ---
OUTPUT_BASE_DIR = "output" # Base directory for all output

# --- Base Request Parameters (Static part) ---
# Dynamic parts like pageNo, ctcFilter, seoKey, sid will be added per request
BASE_PARAMS = {
    "noOfResults": "20",
    "urlType": "search_by_key_loc",
    "searchType": "adv",
    # "location": LOCATIONS, # Uncomment if you want to filter by location in params
    "keyword": KEYWORD,
    "sort": "r",
    "experience": EXPERIENCE,
    # "ctcFilter": Will be set in the loop
    "k": KEYWORD,
    # "l": LOCATIONS, # Uncomment if you want to filter by location in params
    "nignbevent_src": "jobsearchDeskGNB",
    "src": "jobsearchDesk",
    "latLong": ""
}

# --- Base Request Headers (Static part) ---
# nkparam will be added dynamically
BASE_HEADERS = {
    "accept": "application/json",
    "appid": "109",
    "clientid": "d3skt0p",
    "gid": "LOCATION,INDUSTRY,EDUCATION,FAREA_ROLE",
    "host": "www.naukri.com",
    "systemid": "Naukri",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36", # Keep User-Agent updated
    "sec-ch-ua": "\"Google Chrome\";v=\"135\", \"Not-A.Brand\";v=\"8\", \"Chromium\";v=\"135\"",
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": "\"Windows\"",
}

# --- Dynamic Parameter Patterns (Potentially needs adjustment) ---
# Extract base SID and SEO Key root - ensure these are correct for your search
# !! Update if yours are different !!
BASE_SID_PATTERN = "17457332530584631" # Example SID root
LOCATION_SEO_PART = "in-bangalore" # Simplified example, adjust if needed for seoKey


# --- CSV Columns ---
CSV_COLUMN_ORDER = [
    'jobId', 'title', 'companyName', 'experience', 'salary',
    'location', 'tagsAndSkills', 'jobDescription', 'jdURL',
    'fetchTimestamp'
]