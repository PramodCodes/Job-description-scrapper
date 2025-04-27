"""
Main script to orchestrate the Naukri job scraping process.
It iterates through configured CTC filters and calls the scraper for each.
"""
import time

# Import from our modules
import scraper_config as cfg
from naukri_scraper import scrape_single_filter

def run_scraper():
    """Runs the full scraping process based on configuration."""
    print("--- Starting Naukri Scraper ---")
    print(f"Keyword: {cfg.KEYWORD}")
    print(f"CTC Filters to process: {cfg.CTC_FILTERS}")
    print(f"Max pages per filter: {cfg.MAX_PAGES_PER_FILTER}")
    print(f"Output base directory: {cfg.OUTPUT_BASE_DIR}")
    # Add other relevant config logging if desired

    if not cfg.CTC_FILTERS:
        print("\nWarning: No CTC_FILTERS defined in scraper_config.py. Exiting.")
        return

    for ctc_filter in cfg.CTC_FILTERS:
        scrape_single_filter(cfg.KEYWORD, ctc_filter)

        # Optional: Add a delay between different filter runs
        if len(cfg.CTC_FILTERS) > 1: # Only sleep if there are more filters
            inter_filter_delay = 5.0
            print(f"\n---\nSleeping for {inter_filter_delay} seconds before next filter...\n---")
            time.sleep(inter_filter_delay)

    print("\n--- All CTC Filter processing finished ---")

if __name__ == "__main__":
    run_scraper()