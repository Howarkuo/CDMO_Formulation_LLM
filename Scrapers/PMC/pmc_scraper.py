import requests
from bs4 import BeautifulSoup
import os
import time

# --- CONFIGURATION ---
# 1. Directory to save files
WORK_DIR = r"C:\Users\howar\Desktop\biollm\PMC_scrape_gemini2.5"

# 2. PubMed Query
# PUBMED_QUERY = '((Drug Formulation) AND (Emulsion)) AND (dosage forms [MeSH Terms]) NOT "Review [Pt]" NOT "Clinical trial"[Pt] AND "open access"[filter]'
PUBMED_QUERY = '((Drug Formulation) AND (Emulsion)) AND (dosage forms [MeSH Terms])'
# 3. NCBI Settings (Required)
NCBI_EMAIL = "howard.kuo@vernus.ai.com"  # <--- REPLACE WITH YOUR EMAIL
BASE_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"

# Ensure the output directory exists
os.makedirs(WORK_DIR, exist_ok=True)

# --- FUNCTIONS ---

def get_pmcids_from_query(query, max_results=5):
    """
    1. Searches PubMed for PMIDs.
    2. Links them to PMCIDs (required for full text).
    """
    print(f"1. Searching PubMed for: {query}")
    
    # A. Search (ESearch)
    params = {
        "db": "pubmed",
        "term": query,
        "retmax": 20,  # Fetch extra PMIDs to find enough with PMC links
        "sort": "relevance",
        "retmode": "json",
        "email": NCBI_EMAIL
    }
    
    try:
        r = requests.get(f"{BASE_URL}/esearch.fcgi", params=params)
        r.raise_for_status()
        data = r.json()
        pmid_list = data.get("esearchresult", {}).get("idlist", [])
        
        if not pmid_list:
            print("   -> No PMIDs found.")
            return []

        print(f"   -> Found {len(pmid_list)} PMIDs. Checking for Full Text (PMC)...")
        
        # B. Link to PMC (ELink)
        params_link = {
            "dbfrom": "pubmed",
            "db": "pmc",
            "id": ",".join(pmid_list),
            "cmd": "neighbor",
            "retmode": "json",
            "email": NCBI_EMAIL
        }
        
        r = requests.get(f"{BASE_URL}/elink.fcgi", params=params_link)
        r.raise_for_status()
        link_data = r.json()
        
        valid_papers = []
        
        # Parse Link Results
        for ls in link_data.get("linksets", []):
            src_pmid = ls.get("ids", [])[0]
            if "linksetdbs" in ls:
                for db_link in ls["linksetdbs"]:
                    if db_link["linkname"] == "pubmed_pmc":
                        pmc_id = db_link["links"][0]
                        # Create a valid PMC ID string (e.g., "PMC123456")
                        valid_papers.append({"pmid": src_pmid, "pmcid": f"PMC{pmc_id}"})
                        break
            
            if len(valid_papers) >= max_results:
                break
                
        print(f"   -> Selected {len(valid_papers)} papers with Open Access.")
        return valid_papers

    except Exception as e:
        print(f"   -> Search Error: {e}")
        return []

def fetch_and_save_text(paper_info):
    """
    Fetches XML from PMC, parses text, and saves to .txt file.
    """
    pmcid = paper_info['pmcid']
    pmid = paper_info['pmid']
    
    print(f"\n2. Fetching content for {pmcid}...")
    
    params = {
        "db": "pmc",
        "id": pmcid,
        "rettype": "full",
        "retmode": "xml",
        "email": NCBI_EMAIL
    }
    
    try:
        r = requests.get(f"{BASE_URL}/efetch.fcgi", params=params)
        r.raise_for_status()
        
        # Parse XML
        soup = BeautifulSoup(r.content, "lxml-xml")
        
        # Extract Title
        title_tag = soup.find('article-title')
        title = title_tag.get_text() if title_tag else "Unknown Title"
        
        # Extract Body Paragraphs
        body = soup.find('body')
        if not body:
            print(f"   -> [Warning] No body text found for {pmcid}. Skipping.")
            return

        # Get all paragraph text
        paragraphs = [p.get_text(separator=" ", strip=True) for p in body.find_all('p')]
        full_text = f"PMID: {pmid}\nPMCID: {pmcid}\nTITLE: {title}\n\n" + "\n\n".join(paragraphs)
        
        # Save to File
        filename = f"{pmcid}.txt"
        file_path = os.path.join(WORK_DIR, filename)
        
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(full_text)
            
        print(f"   -> ✅ Saved: {filename} ({len(full_text)} chars)")
        
    except Exception as e:
        print(f"   -> ❌ Error fetching {pmcid}: {e}")

# --- MAIN EXECUTION ---
if __name__ == "__main__":
    print(f"--- STARTING PUBMED SCRAPER ---\nOutput Folder: {WORK_DIR}\n")
    
    # 1. Get List of Papers
    papers = get_pmcids_from_query(PUBMED_QUERY, max_results=5)
    
    # 2. Loop through and save
    if papers:
        for paper in papers:
            fetch_and_save_text(paper)
            time.sleep(1) # Be polite to the server
    else:
        print("No papers found to process.")
        
    print("\n--- DONE ---")