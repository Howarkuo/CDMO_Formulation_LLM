#!/usr/bin/env python3
import requests
import xml.etree.ElementTree as ET
import tarfile
import os
import shutil
import time
import tempfile
import urllib.request
from glob import glob
import math
import logging

# --- CONFIGURATION ---
NCBI_EMAIL = "howard.kuo@vernus.ai.com"
OUTPUT_DIR = "downloaded_pdfs"
LOG_FILE = "scraper.log"
PUBMED_QUERY = '((Drug Formulation) AND (Emulsion)) AND (dosage forms[MeSH Terms]) NOT Review[Pt] NOT "Clinical trial"[Pt] AND ffrft[Filter]'

# 目標 1500 篇，每批次處理 100 篇
MAX_ARTICLES = 1500 
BATCH_SIZE = 100

# --- SETUP LOGGING ---
# 這會讓程式同時顯示在螢幕上，並寫入 scraper.log 檔案
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler()
    ]
)

os.makedirs(OUTPUT_DIR, exist_ok=True)

def search_pubmed_ids(query, max_results=1500):
    logging.info(f"🔍 Searching: {query[:50]}...")
    url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
    params = {
        "db": "pubmed", "term": query, "retmode": "json", 
        "retmax": max_results, "email": NCBI_EMAIL, "sort": "relevance"
    }
    try:
        r = requests.get(url, params=params)
        r.raise_for_status()
        ids = r.json().get("esearchresult", {}).get("idlist", [])
        logging.info(f"📊 Found {len(ids)} PMIDs matching query.")
        return ids
    except Exception as e:
        logging.error(f"Search failed: {e}")
        return []

def batch_get_pmcids(pmid_list):
    if not pmid_list: return {}
    url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi"
    pmids_str = ",".join(pmid_list)
    params = {"db": "pubmed", "id": pmids_str, "retmode": "json", "email": NCBI_EMAIL}
    mapping = {}
    try:
        r = requests.get(url, params=params)
        r.raise_for_status()
        data = r.json()
        result = data.get("result", {})
        uids = result.get("uids", [])
        for pmid in uids:
            item = result.get(pmid, {})
            for aid in item.get("articleids", []):
                if aid.get("idtype") == "pmc":
                    mapping[pmid] = aid.get("value")
                    break
    except Exception as e:
        logging.error(f"   ⚠️ Batch ID conversion failed: {e}")
    return mapping

def get_download_link(pmc_id):
    oa_url = f"https://www.ncbi.nlm.nih.gov/pmc/utils/oa/oa.fcgi?id={pmc_id}"
    try:
        r = requests.get(oa_url)
        root = ET.fromstring(r.content)
        pdf_link, tgz_link = None, None
        for link in root.findall(".//link"):
            fmt = link.get("format")
            href = link.get("href")
            if fmt == "pdf": pdf_link = href
            elif fmt == "tgz": tgz_link = href
        return pdf_link, tgz_link
    except Exception:
        return None, None

def process_tar_gz(tgz_path, final_pdf_path):
    try:
        with tempfile.TemporaryDirectory() as temp_dir:
            with tarfile.open(tgz_path, "r:gz") as tar:
                tar.extractall(path=temp_dir)
            pdfs = glob(os.path.join(temp_dir, "**", "*.pdf"), recursive=True)
            if not pdfs: return False
            target_pdf = max(pdfs, key=os.path.getsize)
            shutil.move(target_pdf, final_pdf_path)
            return True
    except Exception:
        return False

def smart_download(url, dest_path):
    try:
        if url.startswith("ftp://"):
            with urllib.request.urlopen(url) as response, open(dest_path, 'wb') as out_file:
                shutil.copyfileobj(response, out_file)
        else:
            r = requests.get(url, stream=True)
            r.raise_for_status()
            with open(dest_path, 'wb') as f:
                for chunk in r.iter_content(chunk_size=8192):
                    f.write(chunk)
        return True
    except Exception as e:
        logging.warning(f"      ❌ Download Error: {e}")
        return False

def main():
    all_pmids = search_pubmed_ids(PUBMED_QUERY, MAX_ARTICLES)
    if not all_pmids: return

    total_pmids = len(all_pmids)
    num_batches = math.ceil(total_pmids / BATCH_SIZE)
    
    logging.info("-" * 60)
    logging.info(f"🚀 Starting Batch Process: {total_pmids} articles in {num_batches} batches.")
    logging.info("-" * 60)

    success_total = 0
    
    for i in range(num_batches):
        start_idx = i * BATCH_SIZE
        end_idx = start_idx + BATCH_SIZE
        batch_pmids = all_pmids[start_idx:end_idx]
        
        logging.info(f"📦 Batch {i+1}/{num_batches} (Items {start_idx+1}-{min(end_idx, total_pmids)})")
        
        pmcid_map = batch_get_pmcids(batch_pmids)
        logging.info(f"   -> Found {len(pmcid_map)} PMCIDs in this batch.")

        if not pmcid_map:
            time.sleep(1)
            continue

        batch_success = 0
        for pmid, pmc_id in pmcid_map.items():
            target_file = os.path.join(OUTPUT_DIR, f"{pmc_id}.pdf")
            if os.path.exists(target_file):
                continue

            pdf_url, tgz_url = get_download_link(pmc_id)
            downloaded = False
            
            if pdf_url and smart_download(pdf_url, target_file):
                logging.info(f"      ✅ Saved PDF: {pmc_id}.pdf")
                downloaded = True
            elif tgz_url:
                tgz_local = os.path.join(OUTPUT_DIR, f"{pmc_id}.tar.gz")
                if smart_download(tgz_url, tgz_local):
                    if process_tar_gz(tgz_local, target_file):
                        logging.info(f"      ✅ Extracted PDF: {pmc_id}.pdf")
                        downloaded = True
                    if os.path.exists(tgz_local): os.remove(tgz_local)
            
            if downloaded:
                batch_success += 1
                success_total += 1
            time.sleep(0.2)

        logging.info(f"   -> Batch Complete. Downloaded: {batch_success}")
        time.sleep(1)

    logging.info("-" * 60)
    logging.info(f"🎉 Job Complete. Total Downloaded: {success_total}/{total_pmids}")

if __name__ == "__main__":
    main()