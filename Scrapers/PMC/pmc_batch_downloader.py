import requests
import xml.etree.ElementTree as ET
import tarfile
import os
import shutil
import time
import tempfile
import urllib.request  # Required for FTP downloads
from glob import glob
import math

# --- CONFIGURATION ---
NCBI_EMAIL = "howard.kuo@vernus.ai.com"
OUTPUT_DIR = "downloaded_pdfs"
PUBMED_QUERY = '((Drug Formulation) AND (Emulsion)) AND (dosage forms[MeSH Terms]) NOT Review[Pt] NOT "Clinical trial"[Pt] AND ffrft[Filter]'

# 更新設定：目標 1500 篇，每批次處理 100 篇
MAX_ARTICLES = 1500 
BATCH_SIZE = 100

os.makedirs(OUTPUT_DIR, exist_ok=True)

def search_pubmed_ids(query, max_results=1500):
    """Step 1: Get PMIDs (Fetch all IDs at once)"""
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
        print(f"📊 Found {len(ids)} PMIDs matching query.")
        return ids
    except Exception as e:
        print(f"Search failed: {e}")
        return []

def batch_get_pmcids(pmid_list):
    """
    Step 2: Convert a LIST of PMIDs -> PMCID Dictionary (Batch Mode)
    Optimized to do 100 IDs in 1 request instead of 100 requests.
    Returns: { 'pmid': 'pmc_id' }
    """
    if not pmid_list: return {}
    
    url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi"
    pmids_str = ",".join(pmid_list)
    
    params = {
        "db": "pubmed", 
        "id": pmids_str, 
        "retmode": "json", 
        "email": NCBI_EMAIL
    }
    
    mapping = {}
    try:
        r = requests.get(url, params=params)
        r.raise_for_status()
        data = r.json()
        result = data.get("result", {})
        
        # Parse result (The 'uids' list contains valid IDs found)
        uids = result.get("uids", [])
        for pmid in uids:
            item = result.get(pmid, {})
            # Look for pmc in articleids
            for aid in item.get("articleids", []):
                if aid.get("idtype") == "pmc":
                    mapping[pmid] = aid.get("value")
                    break
    except Exception as e:
        print(f"   ⚠️ Batch ID conversion failed: {e}")
    
    return mapping

def get_download_link(pmc_id):
    """Step 3: Get file URL (HTTP or FTP)"""
    oa_url = f"https://www.ncbi.nlm.nih.gov/pmc/utils/oa/oa.fcgi?id={pmc_id}"
    try:
        r = requests.get(oa_url)
        # Using ElementTree to parse XML
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
        # Some PMIDs don't have OA entries, expected behavior
        return None, None

def process_tar_gz(tgz_path, final_pdf_path):
    """Extracts tar.gz and picks the largest PDF"""
    try:
        with tempfile.TemporaryDirectory() as temp_dir:
            with tarfile.open(tgz_path, "r:gz") as tar:
                tar.extractall(path=temp_dir)
            
            pdfs = glob(os.path.join(temp_dir, "**", "*.pdf"), recursive=True)
            if not pdfs:
                return False
            
            # Heuristic: Main paper is usually the largest PDF
            target_pdf = max(pdfs, key=os.path.getsize)
            shutil.move(target_pdf, final_pdf_path)
            return True
    except Exception as e:
        print(f"      ❌ Extraction Error: {e}")
        return False

def smart_download(url, dest_path):
    """Handles both HTTP (requests) and FTP (urllib) downloads"""
    try:
        if url.startswith("ftp://"):
            # Use urllib for FTP (Fix for Bug Log 1)
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
        print(f"      ❌ Download Error: {e}")
        return False

def main():
    # 1. Fetch all PMIDs
    all_pmids = search_pubmed_ids(PUBMED_QUERY, MAX_ARTICLES)
    if not all_pmids:
        print("No papers found.")
        return

    total_pmids = len(all_pmids)
    num_batches = math.ceil(total_pmids / BATCH_SIZE)
    
    print("-" * 60)
    print(f"🚀 Starting Batch Process: {total_pmids} articles in {num_batches} batches.")
    print("-" * 60)

    success_total = 0
    
    # 2. Loop in Batches
    for i in range(num_batches):
        start_idx = i * BATCH_SIZE
        end_idx = start_idx + BATCH_SIZE
        batch_pmids = all_pmids[start_idx:end_idx]
        
        print(f"\n📦 Batch {i+1}/{num_batches} (Items {start_idx+1}-{min(end_idx, total_pmids)})")
        
        # 3. Batch Convert ID (Optimized)
        pmcid_map = batch_get_pmcids(batch_pmids)
        print(f"   -> Found {len(pmcid_map)} PMCIDs in this batch.")

        if not pmcid_map:
            print("   -> No open access papers in this batch. Skipping.")
            time.sleep(1)
            continue

        # 4. Download Loop for this Batch
        batch_success = 0
        for pmid, pmc_id in pmcid_map.items():
            target_file = os.path.join(OUTPUT_DIR, f"{pmc_id}.pdf")
            
            if os.path.exists(target_file):
                print(f"   ⏭️  {pmc_id} exists. Skipping.")
                continue

            # print(f"   ⬇️  Downloading {pmc_id}...")
            pdf_url, tgz_url = get_download_link(pmc_id)

            downloaded = False
            # Method A: Direct PDF
            if pdf_url:
                if smart_download(pdf_url, target_file):
                    print(f"      ✅ Saved PDF: {pmc_id}.pdf")
                    downloaded = True
            
            # Method B: Tar.gz
            elif tgz_url and not downloaded:
                tgz_local = os.path.join(OUTPUT_DIR, f"{pmc_id}.tar.gz")
                if smart_download(tgz_url, tgz_local):
                    if process_tar_gz(tgz_local, target_file):
                        print(f"      ✅ Extracted PDF: {pmc_id}.pdf")
                        downloaded = True
                    if os.path.exists(tgz_local):
                        os.remove(tgz_local)
            
            if downloaded:
                batch_success += 1
                success_total += 1
            
            # Tiny sleep to be polite within batch downloading
            time.sleep(0.2)

        print(f"   -> Batch Complete. Downloaded: {batch_success}")
        
        # Sleep between batches to respect NCBI API limits
        time.sleep(1)

    print("-" * 60)
    print(f"🎉 Job Complete. Total Downloaded: {success_total}/{total_pmids}")

if __name__ == "__main__":
    main()