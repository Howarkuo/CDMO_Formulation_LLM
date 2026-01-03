from curl_cffi import requests as crequests
from bs4 import BeautifulSoup
from pypdf import PdfReader
import io

# --- Configuration ---
# We scrape the standard human-readable search page (more reliable than hidden AJAX APIs)
SEARCH_BASE_URL = "https://www.mdpi.com/search"
MDPI_BASE_URL = "https://www.mdpi.com"
SEARCH_QUERY = "formulation, excipients, emulsifying"
JOURNAL_ID = "pharmaceutics"
OUTPUT_FILE = "mdpi_pharmaceutics.jsonl"
MAX_ARTICLES_TO_FETCH = 2  # Limit for testing

# Your specific search parameters
SEARCH_PARAMS = {
    "q": SEARCH_QUERY,
    "journal": JOURNAL_ID,
    "page_count": MAX_ARTICLES_TO_FETCH, # Items per page
    "sort": "pubdate", # Optional: sort by date
    "view": "abstract"
}


def get_soup(url, params=None):
    """Helper to fetch a page with Chrome impersonation to bypass 403."""
    try:
        # 'impersonate="chrome120"' is the magic key that fixes the 403
        response = crequests.get(url, params=params, impersonate="chrome120", timeout=20)
        if response.status_code == 200:
            print(f"DEBUG: Actual URL accessed: {response.url}")
            return BeautifulSoup(response.content, "html.parser")
        else:
            print(f"Warning: Failed to fetch {url}. Status: {response.status_code}")
            return None
    except Exception as e:
        print(f"Error fetching {url}: {e}")
        return None
    

def extract_full_text(pdf_url):
    response = crequests.get(
        pdf_url, 
        impersonate="chrome120", 
        timeout=30
    )
    try:
        if response.status_code == 200:
            print("Download successful! Extracting text...")
            
            with io.BytesIO(response.content) as f:
                reader = PdfReader(f)
                
                # Extract text from all pages
                full_text = []
                for page_num, page in enumerate(reader.pages):
                    full_text.append(page.extract_text())
                    
                final_text = "\n".join(full_text)

            # 3. Print/Save the result
            print("\n--- Extracted Text Preview (First 500 chars) ---")
            print(final_text[:500])
            
            return final_text

        else:
            print(f"Failed to download. Status Code: {response.status_code}")
            return None
        
    except Exception as e:
        print(f"An error occurred while extracting full text: {e}")
        return None







# --- Step 1: Get Search Results ---
print(f"Searching for: {SEARCH_PARAMS['q']}...")
soup = get_soup(SEARCH_BASE_URL, params=SEARCH_PARAMS)

articles_to_process = []

if soup:
    # MDPI search results are usually in generic-item or article-item divs
    # We look for the title links
    article_divs = soup.find_all("div", class_="article-content")
    
    for div in article_divs:
        # Extract title and URL
        title_tag = div.find("a", class_="UD_Listings_ArticlePDF")
        print(title_tag)
        if title_tag:
            title = title_tag.get("data-name")
            link = title_tag.get("href") # e.g., /1999-4923/17/12/1551
            title = title_tag
            full_context_link = f"https://www.mdpi.com{link}"
            full_context = extract_full_text(full_context_link)
            
            
            ############ to do ############
            # if full_context:
            #    maybe only extract (introductin, method, result according to the section title)
            # else:
            #   continue
            # and save 
            ############ to do ############

            
        break # to do: need to uncomment