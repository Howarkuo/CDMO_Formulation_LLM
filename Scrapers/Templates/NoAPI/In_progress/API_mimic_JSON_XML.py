import requests
import time
from bs4 import BeautifulSoup
import json

# --- Configuration ---
MDPI_JSON_URL = "https://www.mdpi.com/search/ajax"
MDPI_BASE_URL = "https://www.mdpi.com"
SEARCH_QUERY = "formulation, excipients, emulsifying"
JOURNAL_ID = "pharmaceutics"
OUTPUT_FILE = "mdpi_pharmaceutics.jsonl"
MAX_ARTICLES_TO_FETCH = 5  # Limit for testing

# Request headers to mimic a browser
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                  "AppleWebKit/537.36 (KHTML, like Gecko) "
                  "Chrome/120.0.0.0 Safari/537.36",
    "Accept": "application/json, text/javascript, */*; q=0.01",
    "Accept-Language": "en-US,en;q=0.9",
    "Accept-Encoding": "gzip, deflate, br",
    "Referer": f"https://www.mdpi.com/journal/{JOURNAL_ID}",
    "X-Requested-With": "XMLHttpRequest",
    "Origin": "https://www.mdpi.com"
}


# --- Step 1: Fetch search results JSON ---
params = {
    "journal": JOURNAL_ID,
    "q": SEARCH_QUERY,
    "page": "1"
}

print(f"Fetching search results for query: {SEARCH_QUERY} ...")

response = requests.get(MDPI_JSON_URL, params=params, headers=headers)
response.raise_for_status()
search_data = response.json()

articles = search_data.get("results", [])
if not articles:
    print("No articles found in JSON search results.")
    exit(0)

# Limit the number of articles if needed
articles = articles[:MAX_ARTICLES_TO_FETCH]
print(f"Found {len(articles)} articles to process.")

# --- Step 2: Loop through each article and fetch XML ---
with open(OUTPUT_FILE, "a", encoding="utf-8") as f_out:
    for art in articles:
        title = art.get("title", "")
        url_path = art.get("url", "")
        article_id = url_path.strip("/").split("/")[-1]

        # Construct XML URL
        article_xml_url = f"{MDPI_BASE_URL}{url_path}/xml"

        print(f"\nFetching XML for Article ID: {article_id}")
        print(f"Title: {title}")
        print(f"XML URL: {article_xml_url}")

        try:
            time.sleep(1)  # polite delay
            xml_resp = requests.get(article_xml_url, headers=headers)
            xml_resp.raise_for_status()
            xml_soup = BeautifulSoup(xml_resp.content, "lxml-xml")

            # Extract title from XML (fallback if different from JSON)
            xml_title_tag = xml_soup.find("article-title")
            if xml_title_tag:
                title = xml_title_tag.get_text()

            # Extract full text paragraphs
            body_container = xml_soup.find(["body", "body-text"])
            full_text = ""
            if body_container:
                paragraphs = body_container.find_all("p")
                full_text = "\n".join(p.get_text() for p in paragraphs)

            # Save to JSON Lines
            paper_data = {
                "mdpi_id": article_id,
                "title": title,
                "url_path": url_path,
                "text": full_text
            }
            f_out.write(json.dumps(paper_data, ensure_ascii=False) + "\n")
            print(f"Saved Article ID {article_id} to {OUTPUT_FILE}")

        except requests.exceptions.RequestException as e:
            print(f"Error fetching XML for Article ID {article_id}: {e}")

print("\n--- Scraping complete. ---")
