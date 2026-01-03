import requests
import xml.etree.ElementTree as ET
import tarfile
import os
import shutil
import time
import tempfile
from glob import glob
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

# Bug Log 1
#Failed: Processing PMC9144098...
#    📦 PDF hidden in tar.gz, downloading archive...
#    ❌ Tar processing failed: No connection adapters were found for 'ftp://ftp.ncbi.nlm.nih.gov/pub/pmc/oa_package/90/49/PMC9144098.tar.gz'

# Fix 1
# Change request to urllib 
# --- CONFIGURATION ---

import requests
import xml.etree.ElementTree as ET
import tarfile
import os
import shutil
import time
import tempfile
import urllib.request  # Required for FTP downloads
from glob import glob

# --- CONFIGURATION ---
NCBI_EMAIL = "howard.kuo@vernus.ai.com"
OUTPUT_DIR = "downloaded_pdfs"
PUBMED_QUERY = '((Drug Formulation) AND (Emulsion)) AND (dosage forms[MeSH Terms]) NOT Review[Pt] NOT "Clinical trial"[Pt] AND ffrft[Filter]'
MAX_ARTICLES = 10 

os.makedirs(OUTPUT_DIR, exist_ok=True)

def search_pubmed_ids(query, max_results=5):
    """Step 1: Get PMIDs"""
    print(f"🔍 Searching: {query[:50]}...")
    url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
    params = {
        "db": "pubmed", "term": query, "retmode": "json", 
        "retmax": max_results, "email": NCBI_EMAIL, "sort": "relevance"
    }
    try:
        r = requests.get(url, params=params)
        r.raise_for_status()
        ids = r.json().get("esearchresult", {}).get("idlist", [])
        print(f"📊 Found {len(ids)} PMIDs")
        return ids
    except Exception as e:
        print(f"Search failed: {e}")
        return []

def get_pmc_id(pmid):
    """Step 2: Convert PMID -> PMCID"""
    url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi"
    params = {"db": "pubmed", "id": pmid, "retmode": "json", "email": NCBI_EMAIL}
    try:
        r = requests.get(url, params=params)
        data = r.json()
        item = data.get("result", {}).get(str(pmid), {})
        for aid in item.get("articleids", []):
            if aid.get("idtype") == "pmc":
                return aid.get("value"), item.get("title", "No Title")
    except Exception:
        pass
    return None, None

def get_download_link(pmc_id):
    """Step 3: Get file URL (HTTP or FTP)"""
    oa_url = f"https://www.ncbi.nlm.nih.gov/pmc/utils/oa/oa.fcgi?id={pmc_id}"
    try:
        r = requests.get(oa_url)
        root = ET.fromstring(r.content)
        pdf_link = None
        tgz_link = None
        for link in root.findall(".//link"):
            fmt = link.get("format")
            href = link.get("href")
            if fmt == "pdf":
                pdf_link = href
            elif fmt == "tgz":
                tgz_link = href
        return pdf_link, tgz_link
    except Exception as e:
        print(f"OA Service Error: {e}")
        return None, None

def process_tar_gz(tgz_path, final_pdf_path):
    """Extracts tar.gz and picks the largest PDF"""
    try:
        with tempfile.TemporaryDirectory() as temp_dir:
            with tarfile.open(tgz_path, "r:gz") as tar:
                tar.extractall(path=temp_dir)
            pdfs = glob(os.path.join(temp_dir, "**", "*.pdf"), recursive=True)
            if not pdfs:
                print("   ⚠️ No PDF found inside tar.gz")
                return False
            target_pdf = max(pdfs, key=os.path.getsize)
            shutil.move(target_pdf, final_pdf_path)
            print(f"   ✅ Extracted: {os.path.basename(final_pdf_path)}")
            return True
    except Exception as e:
        print(f"   ❌ Extraction failed: {e}")
        return False

def smart_download(url, dest_path):
    """Handles both HTTP (requests) and FTP (urllib) downloads"""
    try:
        if url.startswith("ftp://"):
            # Use urllib for FTP
            with urllib.request.urlopen(url) as response, open(dest_path, 'wb') as out_file:
                shutil.copyfileobj(response, out_file)
        else:
            # Use requests for HTTP/HTTPS
            r = requests.get(url, stream=True)
            r.raise_for_status()
            with open(dest_path, 'wb') as f:
                for chunk in r.iter_content(chunk_size=8192):
                    f.write(chunk)
        return True
    except Exception as e:
        print(f"   ❌ Download Error ({url[:4]}): {e}")
        return False

def main():
    pmids = search_pubmed_ids(PUBMED_QUERY, MAX_ARTICLES)
    print("-" * 60)
    success_count = 0
    
    for pmid in pmids:
        pmc_id, title = get_pmc_id(pmid)
        if not pmc_id:
            print(f"⏭️  PMID {pmid}: No PMCID. Skipping.")
            continue

        print(f"⬇️  Processing {pmc_id}...")
        pdf_url, tgz_url = get_download_link(pmc_id)
        target_file = os.path.join(OUTPUT_DIR, f"{pmc_id}.pdf")
        
        if os.path.exists(target_file):
            print("   Skipping (Already Exists).")
            continue

        # Scenario A: Direct PDF
        if pdf_url:
            if smart_download(pdf_url, target_file):
                print(f"   ✅ Saved PDF: {pmc_id}.pdf")
                success_count += 1

        # Scenario B: Tar.gz
        elif tgz_url:
            print(f"   📦 Found tar.gz, downloading...")
            tgz_local = os.path.join(OUTPUT_DIR, f"{pmc_id}.tar.gz")
            
            # 1. Download Archive (FTP or HTTP)
            if smart_download(tgz_url, tgz_local):
                # 2. Extract PDF
                if process_tar_gz(tgz_local, target_file):
                    success_count += 1
                # 3. Cleanup
                if os.path.exists(tgz_local):
                    os.remove(tgz_local)
        else:
            print("   ⚠️ No download link found.")

        time.sleep(1)

    print("-" * 60)
    print(f"🎉 Batch Complete. Downloaded {success_count}/{len(pmids)} papers.")

if __name__ == "__main__":
    main()