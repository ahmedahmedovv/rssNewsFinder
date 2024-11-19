import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# SerpAPI Configuration
SERPAPI_KEY = os.getenv('SERPAPI_KEY')

# SerpAPI Search Parameters
SEARCH_CONFIG = {
    "engine": "google",           # Search engine to use
    "num": 10,                    # Number of results per page
    "gl": "pl",                   # Country to search from (Poland)
    "hl": "pl",                   # Language for search (Polish)
    "safe": "active",            # Safe search setting
    "start": 0,                  # Starting result (pagination)
    "filter": 1,                 # Filter duplicate results
    "tbm": "nws",               # Specifically search for news
    "google_domain": "google.pl", # Use Polish Google domain
    "location": "Poland",        # Location for local context
}

# Search Configuration
MAX_RESULTS = 10

# Folder Configuration
RESULTS_FOLDER = "results"
SEARCH_TERMS_FILE = "data/search_terms.txt"

# Create required folders
for folder in [RESULTS_FOLDER, os.path.dirname(SEARCH_TERMS_FILE)]:
    if not os.path.exists(folder):
        os.makedirs(folder)

# Messages
WELCOME_MESSAGE = "Starting batch search process..."
ERROR_NO_RESULTS = "No results found!"
SAVE_SUCCESS = "Results saved to: {}"
ERROR_NO_TERMS = "No search terms found in file. Please add terms to search_terms.txt"