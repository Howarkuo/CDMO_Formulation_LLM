import os
import requests
import pandas as pd
import logging
import time
from elsapy.elsclient import ElsClient
from elsapy.elsdoc import ElsDoc
from Bio import Entrez
import json

# --- CONFIGURATION ---
EMAIL = "howard.kuo@vernus.ai.com"
API_KEY_ELSEVIER = "YOUR_ELSEVIER_API_KEY"
Entrez.email = EMAIL
OUTPUT_DIR = "CDMO_Corpus"
LOG_FILE = "download_pipeline.log"

# Setup Logging
logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format='%(asctime)s - [%(levelname)s] - %(message)s'
)

# Create Directories
os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs("logs", exist_ok=True)

# --- HELPER FUNCTIONS ---

def sanitize_doi(doi):
    """Converts DOI to a safe filename string (replaces / with _)"""
    return str(doi).replace('/', '_')

def get_pubmed_metadata(query, max_results=100):
    """Step 1 & 2: Search PubMed and return DataFrame with DOI & Publisher"""
    print(f"🔍 Querying PubMed: {query}")
    
    # 1. Search
    handle = Entrez.esearch(db="pubmed", term=query, retmax=max_results)
    record = Entrez.read(handle)
    id_list = record["IdList"]
    
    # 2. Fetch Details (Batch)
    data = []
    if not id_list: return pd.DataFrame()
    
    handle = Entrez.esummary(db="pubmed", id=",".join(id_list))
    records = Entrez.read(handle)
    
    for r in records:
        # Extract DOI
        doi = ""
        for article_id in r.get('ArticleIds', []):
            if article_id.attributes.get('IdType') == 'doi':
                doi = article_id
                break
        
        # Basic Publisher Guess (Refine with CrossRef if needed)
        pub_guess = r.get('Source', 'Unknown')
        
        data.append({
            'PMID': r['Id'],
            'DOI': doi,
            'Title': r['Title'],
            'Publisher': pub_guess,
            'Status': 'Pending',
            'File_Path': ''
        })
        
    return pd.DataFrame(data)

# --- DOWNLOAD MODULES ---

def download_elsevier(row, client):
    """Step 3: Try Elsevier API"""
    if 'Elsevier' not in row['Publisher'] and 'ScienceDirect' not in row['Publisher']:
        return False, "Not Elsevier"
    
    if not row['DOI']: return False, "No DOI"

    try:
        doi_doc = ElsDoc(doi=row['DOI'])
        if doi_doc.read(client):
            # Naming Convention: PMID_DOI.pdf
            filename = f"{row['PMID']}_{sanitize_doi(row['DOI'])}.pdf"
            path = os.path.join(OUTPUT_DIR, filename)
            doi_doc.write(path)
            return True, path
    except Exception as e:
        return False, str(e)
    return False, "Download Failed"

def download_unpaywall(row):
    """Step 5: Try Unpaywall URL (Simulates Step 5 scraper logic)"""
    if not row['DOI']: return False, "No DOI"
    
    url = f"https://api.unpaywall.org/v2/{row['DOI']}?email={EMAIL}"
    try:
        r = requests.get(url)
        data = r.json()
        
        # Get best PDF link
        best_oa = data.get('best_oa_location', {})
        pdf_url = best_oa.get('url_for_pdf')
        
        if pdf_url:
            # Naming Convention
            filename = f"{row['PMID']}_{sanitize_doi(row['DOI'])}.pdf"
            path = os.path.join(OUTPUT_DIR, filename)
            
            # Download content
            pdf_data = requests.get(pdf_url, timeout=10)
            with open(path, 'wb') as f:
                f.write(pdf_data.content)
            return True, path
    except Exception as e:
        return False, str(e)
    
    return False, "No OA Link Found"

# --- MAIN CONTROLLER ---

def main():
    # 1. Query
    PUBMED_QUERY = '((Drug Formulation) AND (Emulsion)) AND (dosage forms [MeSH Terms])'
    df = get_pubmed_metadata(PUBMED_QUERY, max_results=50) # Set limit for testing
    
    # 2. Setup Elsevier Client
    els_client = ElsClient(API_KEY_ELSEVIER)
    
    print(f"📋 Processing {len(df)} articles...")

    # Iterate through Waterfall
    for index, row in df.iterrows():
        pmid = row['PMID']
        logging.info(f"Processing PMID: {pmid}")
        
        # --- STRATEGY 3: ELSEVIER ---
        success, info = download_elsevier(row, els_client)
        if success:
            df.at[index, 'Status'] = 'Downloaded (Elsevier)'
            df.at[index, 'File_Path'] = info
            logging.info(f"✅ Elsevier Success: {pmid}")
            continue # Skip to next article
        else:
            logging.warning(f"⚠️ Elsevier Failed {pmid}: {info}")

        # --- STRATEGY 4: PMC (Placeholder for your Ubuntu Script integration) ---
        # Logic: If row['PMID'] exists in your downloaded PMC tar files, move it and update df
        # df.at[index, 'Status'] = 'Downloaded (PMC)'
        # continue 

        # --- STRATEGY 5: UNPAYWALL / SCRAPER ---
        success, info = download_unpaywall(row)
        if success:
            df.at[index, 'Status'] = 'Downloaded (Unpaywall)'
            df.at[index, 'File_Path'] = info
            logging.info(f"✅ Unpaywall Success: {pmid}")
            continue
        else:
            logging.error(f"❌ Unpaywall Failed {pmid}: {info}")
            
        # --- STRATEGY 6: MANUAL ---
        df.at[index, 'Status'] = 'Failed - Requires Manual'

    # 3. Export Report for Manual Review
    df.to_csv("download_report.csv", index=False)
    print("🎉 Job Complete. Check download_report.csv for failures.")

if __name__ == "__main__":
    main()