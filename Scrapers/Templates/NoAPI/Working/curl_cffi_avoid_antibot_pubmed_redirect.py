import requests
import json
import io
import time
import re
from curl_cffi import requests as crequests
from bs4 import BeautifulSoup
from pypdf import PdfReader

# --- Configuration ---
# Your Email (Required by NCBI)
NCBI_EMAIL = "howard.kuo@vernus.ai.com"
NCBI_API_KEY = None  # Add if you have one to increase rate limits

# The Query
PUBMED_QUERY = '((Drug Formulation) AND (Emulsion)) AND (dosage forms[MeSH Terms]) NOT Review[Pt] NOT "Clinical trial"[Pt] AND ffrft[Filter]'

# Settings
MAX_ARTICLES_TO_FETCH = 5
OUTPUT_FILE = "pubmed_emulsions.jsonl"
BASE_URL_ESEARCH = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
BASE_URL_ESUMMARY = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi"

def search_pubmed_ids(query, max_results=10):
    """
    Step 1: Search PubMed and retrieve PMIDs.
    """
    print(f"Searching PubMed for: {query}...")
    params = {
        "db": "pubmed",
        "term": query,
        "retmode": "json",
        "retmax": max_results,
        "email": NCBI_EMAIL,
        "sort": "date"
    }
    if NCBI_API_KEY:
        params["api_key"] = NCBI_API_KEY

    try:
        response = requests.get(BASE_URL_ESEARCH, params=params)
        response.raise_for_status()
        data = response.json()
        id_list = data.get("esearchresult", {}).get("idlist", [])
        print(f"Found {len(id_list)} PMIDs.")
        return id_list
    except Exception as e:
        print(f"Error searching PubMed: {e}")
        return []

def get_article_details(pmid_list):
    """
    Step 2: Get metadata (Title, DOI, PMC ID) for the PMIDs.
    We specifically look for the 'pmc' ID to build a reliable PDF link.
    """
    if not pmid_list:
        return {}

    print("Fetching article metadata...")
    params = {
        "db": "pubmed",
        "id": ",".join(pmid_list),
        "retmode": "json",
        "email": NCBI_EMAIL
    }
    
    try:
        response = requests.get(BASE_URL_ESUMMARY, params=params)
        response.raise_for_status()
        data = response.json()
        articles = data.get("result", {})
        
        results = {}
        for pmid in pmid_list:
            if pmid not in articles: 
                continue
            
            item = articles[pmid]
            title = item.get("title", "No Title")
            
            # Extract IDs (DOI, PMC)
            article_ids = item.get("articleids", [])
            pmc_id = None
            doi = None
            
            for id_entry in article_ids:
                if id_entry.get("idtype") == "pmc":
                    pmc_id = id_entry.get("value") # e.g., "PMC123456"
                elif id_entry.get("idtype") == "doi":
                    doi = id_entry.get("value")
            
            results[pmid] = {
                "title": title,
                "pmc_id": pmc_id,
                "doi": doi
            }
        return results
    except Exception as e:
        print(f"Error fetching details: {e}")
        return {}

def extract_pdf_text(pdf_url):
    """
    Step 3: Download PDF using curl_cffi (impersonating Chrome) and extract text.
    """
    print(f"Attempting download: {pdf_url}")
    try:
        # Use curl_cffi to bypass basic bot protections / 403s
        response = crequests.get(
            pdf_url, 
            impersonate="chrome120", 
            timeout=30,
            follow_redirects=True
        )
        
        if response.status_code == 200 and b"%PDF" in response.content[:10]:
            print("  Download successful. Parsing PDF...")
            with io.BytesIO(response.content) as f:
                reader = PdfReader(f)
                full_text = []
                for page in reader.pages:
                    full_text.append(page.extract_text() or "")
                
                return "\n".join(full_text)
        else:
            print(f"  Failed. Status: {response.status_code}. Content-Type: {response.headers.get('Content-Type')}")
            return None
            
    except Exception as e:
        print(f"  Error downloading/extracting PDF: {e}")
        return None

def process_pubmed_results():
    # 1. Get PMIDs
    pmids = search_pubmed_ids(PUBMED_QUERY, MAX_ARTICLES_TO_FETCH)
    if not pmids:
        return

    # 2. Get Details (Check for PMC IDs)
    details = get_article_details(pmids)
    
    extracted_count = 0
    
    # Open output file
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f_out:
        for pmid, info in details.items():
            print(f"\nProcessing PMID {pmid}: {info['title'][:50]}...")
            
            pdf_text = None
            source_used = "None"

            # STRATEGY A: If PMC ID exists (Most Reliable)
            if info.get('pmc_id'):
                pmc_id = info['pmc_id']
                # Standard PMC PDF URL structure
                pdf_url = f"https://www.ncbi.nlm.nih.gov/pmc/articles/{pmc_id}/pdf/"
                print(f"  Found PMC ID ({pmc_id}). Using PMC URL.")
                pdf_text = extract_pdf_text(pdf_url)
                source_used = "PMC"
            
            # STRATEGY B: Fallback (Unpaywall / MDPI Logic could go here)
            # For now, we skip if not in PMC to keep script stable.
            else:
                print("  No PMC ID found. Skipping external publisher scrape (complex).")
                continue

            # Save if we got text
            if pdf_text:
                record = {
                    "pmid": pmid,
                    "title": info['title'],
                    "doi": info['doi'],
                    "source": source_used,
                    "full_text": pdf_text  # You might want to slice this if too large
                }
                f_out.write(json.dumps(record) + "\n")
                print("  Saved to JSONL.")
                extracted_count += 1
            
            # Be polite to servers
            time.sleep(1)

    print(f"\nDone. Successfully scraped {extracted_count} articles to {OUTPUT_FILE}.")

if __name__ == "__main__":
    process_pubmed_results()