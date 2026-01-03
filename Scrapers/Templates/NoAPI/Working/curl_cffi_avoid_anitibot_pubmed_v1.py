import requests
import json
import io
import time
import os
import urllib.request
import xml.etree.ElementTree as ET
import tarfile
from glob import glob
import shutil

# #API Endpoint:
# # 1. esearch - to find pmids 
## 2. esummary - to get DOI (METAdata) of id conv not available part
## 3. oa.fcgi: Retrieve Open Access Service 


#Logic Flow (Package) 
# request.get() + esearch -> Get PMID list 
# request + esummarty -> Check if PMID has a PMCID 
# urllib, read(), decode('utf-8') + oa.fcgi -> Get downloaded URL (XML)
# ET.fromstring(data) -> Parse XML to find PDF link
# urllib + tarfile -> Download and Extract file

# Data Transformation
# List [str] -> url (query) -> Structured Data (JSON/ XML) -> Binary file (PDF)

# Progression
# 1. Change urllib to request
# 2. tempfile to store temporary files
# 3. Pick the largest file assuming it's the main paper / target_pdf = max()

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


def parse_data(data):
    root = ET.fromstring(data)
    records = root.find("records")
    res_url = None 
    res_format = None
    for record in records.findall("record"):
        for link_tag in record.findall("link"):
            if link_tag is not None:
                res_url = link_tag.get("href")
                res_format = link_tag.get("format")
                if res_format == 'pdf':
                    return res_format, res_url
            else:
                print("No download link found.")
    return res_format, res_url

def download_file(url):
    filename = os.path.basename(url)
    try:
        print(f"Downloading {filename} from {url}...")
        urllib.request.urlretrieve(url, filename)
        print(f"Success! File saved as: {os.path.abspath(filename)}")

        if 'tar.gz' in filename:
            with tarfile.open(filename, "r:gz") as tar:
                tar.extractall()
            pdfs = glob(os.path.join(os.path.abspath(filename).rsplit('.', 2)[0], '*.pdf'))
            print(pdfs)
            if pdfs:
                # todo!!! need to check if there are mutiple pdf cases!
                source = pdfs[0]
                destination = f"{os.path.abspath(filename).rsplit('.', 2)[0]}.pdf"
                print(f"extract file from {source} to {destination}")
                shutil.move(source, destination)
            if os.path.exists(filename):
                # todo!!! check permission so you can fully delete the extract directory
                os.remove(filename) 
    except Exception as e:
        print(f"An error occurred: {e}")


def main():
    # 1. Search
    pmids = search_pubmed_ids(PUBMED_QUERY, MAX_ARTICLES_TO_FETCH)
    pubchem_api = "https://www.ncbi.nlm.nih.gov/pmc/utils/oa/oa.fcgi?id="
    if not pmids: return

    extracted_count = 0
    
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f_out:
        for pmid in pmids:
            # 2. Get Info
            pmc_id, title = get_pmc_id(pmid)
            
            if pmc_id:
                # 3. Download
                try:
                    url = f"{pubchem_api}{pmc_id}"
                    print(url)
                    print(f"Fetching response from: {url}\n")
                    
                    # 4. Send the GET request
                    with urllib.request.urlopen(url) as response:
                        data = response.read().decode('utf-8')
                        file_format, file_url = parse_data(data)
                        download_file(file_url)
                        # todo!!! not sure if write into json file as you originally did, or directly create QA Pairs here and remove the file so won't spend too much space 
                        extracted_count += 1
                except Exception as e:
                     print(f"An error occurred: {e}")
            else:
                print(f"  > PMID {pmid}: No PMC ID (Not Open Access in PMC). Skipping.")
            
            # Politeness delay
            time.sleep(2)

    print(f"\n--- Done. Scraped {extracted_count} articles to {OUTPUT_FILE} ---")

if __name__ == "__main__":
    main()

# It worked, however, it retrieved multiple files 