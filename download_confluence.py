import logging
import os
import requests
from requests.auth import HTTPBasicAuth
from urllib.parse import urljoin
from dotenv import load_dotenv
from json import dump

# Load environment variables from .env file
load_dotenv()

# Configurations from .env

ATLASSIAN_TOKEN = os.getenv("ATLASSIAN_TOKEN")
ATLASSIAN_USER = os.getenv("ATLASSIAN_USER")
OUTPUT_DIR = os.getenv("OUTPUT_DIR", "./confluence_backup")  # Default to ./confluence_backup

# This should be the base URL of your Confluence instance. e.g.: "https://yourdomain.atlassian.net"

BASE_URL = os.getenv("BASE_URL")
BASE_API_URL = urljoin(BASE_URL, "/wiki/rest/api")


# Set up authentication
auth = HTTPBasicAuth(ATLASSIAN_USER, ATLASSIAN_TOKEN)

# Ensure output directory exists
os.makedirs(OUTPUT_DIR, exist_ok=True)

def fetch_spaces():
    """Fetch all spaces in Confluence."""
    url = f"{BASE_API_URL}/space"
    response = requests.get(url, auth=auth)
    response.raise_for_status()
    return response.json()

def fetch_pages(space_key):
    """Fetch all pages for a given space."""
    url = f"{BASE_API_URL}/content"
    params = {"spaceKey": space_key}
    response = requests.get(url, auth=auth, params=params)
    response.raise_for_status()
    return response.json()

def save_page_content(page, space_key):
    """Save a page as HTML."""
    format="html"
    title = page['title'].replace("/", "-")  # Sanitize file name
    page_id = page['id']
    file_extension = "html" if format == "html" else format
    filepath = os.path.join(OUTPUT_DIR, space_key, f"{title}.{file_extension}")
    
    # Ensure space directory exists
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    
    # Save as HTML
    url = f"{BASE_API_URL}/content/{page_id}?expand=body.storage"
    response = requests.get(url, auth=auth)
    response.raise_for_status()
    content = response.json()['body']['storage']['value']
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)


def save_confluence_export_spec(download_spec: dict[str, list[str]]):
    """Save the download specification as a JSON file which the confluence-export
    tool can use to download all the pages into a consolidated PDF file.
    """
    
    download_spec_path = os.path.join(OUTPUT_DIR, "download_spec.json")
    export_spec = {
        "Server": {
            "Confluence": BASE_URL
        },
        "Pages to export": download_spec
    }
    with open(download_spec_path, "w") as f:
        dump(export_spec, f, indent=2)


def main():
    logging.basicConfig(level=logging.INFO)
    spaces = fetch_spaces()
    download_spec = {}
    for space in spaces['results']:
        space_key = space['key']
        download_spec[space_key] = []
        logging.info("Processing space: %s", space_key)
        pages = fetch_pages(space_key)
        for page in pages['results']:
            download_spec[space_key].append(page['title'])
            logging.info("Saving page: %s (%s)", page['title'], page['id'])
            save_page_content(page, space_key)
            
    save_confluence_export_spec(download_spec)

if __name__ == "__main__":
    main()
