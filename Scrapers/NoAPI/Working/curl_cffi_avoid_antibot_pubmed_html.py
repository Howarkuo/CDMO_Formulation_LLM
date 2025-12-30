import requests
import json
import io
import time
from urllib.parse import urljoin
from curl_cffi import requests as crequests
from bs4 import BeautifulSoup
from pypdf import PdfReader

# --- CONFIGURATION ---
NCBI_EMAIL = "howard.kuo@vernus.ai.com"
OUTPUT_FILE = "pubmed_emulsions_final.jsonl"
PUBMED_QUERY = '((Drug Formulation) AND (Emulsion)) AND (dosage forms[MeSH Terms]) NOT Review[Pt] NOT "Clinical trial"[Pt] AND ffrft[Filter]'
MAX_ARTICLES_TO_FETCH = 5

def search_pubmed_ids(query, max_results=5):
    """
    Step 1: Get the list of PMIDs using the standard NCBI API.
    """
    print(f"Searching PubMed for: {query[:50]}...")
    params = {
        "db": "pubmed",
        "term": query,
        "retmode": "json",
        "retmax": max_results,
        "email": NCBI_EMAIL,
        "sort": "date"
    }
    try:
        response = requests.get("https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi", params=params)
        response.raise_for_status()
        id_list = response.json().get("esearchresult", {}).get("idlist", [])
        print(f"Found {len(id_list)} PMIDs.")
        return id_list
    except Exception as e:
        print(f"Error searching PubMed: {e}")
        return []

def get_pmc_id(pmid):
    """
    Step 2: Get the PMC ID (e.g., PMC123456) for a given PMID.
    """
    params = {
        "db": "pubmed",
        "id": pmid,
        "retmode": "json",
        "email": NCBI_EMAIL
    }
    try:
        response = requests.get("https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi", params=params)
        data = response.json()
        item = data.get("result", {}).get(pmid, {})
        
        # Extract Title
        title = item.get("title", "No Title")
        
        # Extract PMC ID
        pmc_id = None
        for id_entry in item.get("articleids", []):
            if id_entry.get("idtype") == "pmc":
                pmc_id = id_entry.get("value")
                break
        
        return pmc_id, title
    except Exception as e:
        print(f"Error fetching metadata: {e}")
        return None, None

def download_paper_workflow(pmc_id, title):
    """
    Step 3 & 4: The robust download workflow using a Session.
    """
    article_url = f"https://www.ncbi.nlm.nih.gov/pmc/articles/{pmc_id}/"
    print(f"\nProcessing: {title[:40]}...")
    print(f"  > Visiting Article Page: {article_url}")

    # --- KEY FIX 1: Use a Session to persist Cookies ---
    session = crequests.Session(impersonate="chrome120")
    
    try:
        # A. Visit the HTML page first (Sets cookies)
        response_html = session.get(article_url, timeout=20)
        if response_html.status_code != 200:
            print(f"  > Failed to load HTML. Status: {response_html.status_code}")
            return None

        # B. Parse HTML to find the PDF link
        soup = BeautifulSoup(response_html.content, "html.parser")
        pdf_relative_link = None
        
        # Find the first link that ends with .pdf
        # (PMC links are usually like "pdf/filename.pdf")
        for link in soup.find_all("a", href=True):
            if link['href'].endswith(".pdf") and "supplement" not in link['href'].lower():
                pdf_relative_link = link['href']
                break
        
        if not pdf_relative_link:
            print("  > No .pdf link found in HTML.")
            return None

        # Create absolute URL
        pdf_url = urljoin(article_url, pdf_relative_link)
        print(f"  > Found PDF Link: {pdf_url}")

        # C. Download PDF with Referer Header (KEY FIX 2)
        # We tell the server: "I am coming from the article page"
        headers = {
            "Referer": article_url,
            "Accept": "application/pdf" # Explicitly ask for PDF
        }
        
        print("  > Downloading binary...")
        response_pdf = session.get(pdf_url, headers=headers, timeout=30)
        
        # D. Validate Content Type
        content_type = response_pdf.headers.get("Content-Type", "").lower()
        if "pdf" in content_type or b"%PDF" in response_pdf.content[:20]:
            print("  > Success! Extracting text...")
            
            with io.BytesIO(response_pdf.content) as f:
                reader = PdfReader(f)
                text = "\n".join([p.extract_text() or "" for p in reader.pages])
                return text
        else:
            print(f"  > Failed. Server returned: {content_type} (Expected pdf)")
            return None

    except Exception as e:
        print(f"  > Error in download workflow: {e}")
        return None

def main():
    # 1. Search
    pmids = search_pubmed_ids(PUBMED_QUERY, MAX_ARTICLES_TO_FETCH)
    if not pmids: return

    extracted_count = 0
    
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f_out:
        for pmid in pmids:
            # 2. Get Info
            pmc_id, title = get_pmc_id(pmid)
            
            if pmc_id:
                # 3. Download
                full_text = download_paper_workflow(pmc_id, title)
                
                if full_text:
                    record = {
                        "pmid": pmid,
                        "pmc_id": pmc_id,
                        "title": title,
                        "full_text": full_text
                    }
                    f_out.write(json.dumps(record) + "\n")
                    f_out.flush() # Ensure it writes immediately
                    extracted_count += 1
            else:
                print(f"  > PMID {pmid}: No PMC ID (Not Open Access in PMC). Skipping.")
            
            # Politeness delay
            time.sleep(2)

    print(f"\n--- Done. Scraped {extracted_count} articles to {OUTPUT_FILE} ---")

if __name__ == "__main__":
    main()


