#!/usr/bin/env python3
import requests
import xml.etree.ElementTree as ET
import os
import time
import math
import logging

# --- CONFIGURATION ---
NCBI_EMAIL = "howard.kuo@vernus.ai.com"
OUTPUT_FILE = "pmc_oa_failures.txt"  # The file you asked for
PUBMED_QUERY = '((Drug Formulation) AND (Emulsion)) AND (dosage forms[MeSH Terms]) NOT Review[Pt] NOT "Clinical trial"[Pt] AND ffrft[Filter]'

# Max items to scan
MAX_ARTICLES = 1500 
BATCH_SIZE = 100

# --- SETUP LOGGING ---
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(message)s',
    handlers=[logging.StreamHandler()] # Print to screen only
)

def search_pubmed_ids(query, max_results):
    logging.info(f"🔍 Searching: {query[:50]}...")
    url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
    params = {
        "db": "pubmed", "term": query, "retmode": "json", 
        "retmax": max_results, "email": NCBI_EMAIL, "sort": "relevance"
    }
    try:
        r = requests.get(url, params=params)
        r.raise_for_status()
        return r.json().get("esearchresult", {}).get("idlist", [])
    except Exception as e:
        logging.error(f"Search failed: {e}")
        return []

def batch_get_metadata(pmid_list):
    """
    Fetches DOI, PMCID, and Journal Name (Source) for a list of PMIDs.
    """
    if not pmid_list: return {}
    
    url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi"
    pmids_str = ",".join(pmid_list)
    params = {"db": "pubmed", "id": pmids_str, "retmode": "json", "email": NCBI_EMAIL}
    
    mapping = {}
    try:
        r = requests.get(url, params=params)
        r.raise_for_status()
        result = r.json().get("result", {})
        uids = result.get("uids", [])
        
        for pmid in uids:
            item = result.get(pmid, {})
            
            # 1. Get Journal Name (Proxy for Publisher)
            source = item.get("source", "Unknown Journal")
            
            # 2. Get PMCID and DOI from articleids list
            pmc_id = None
            doi = "No DOI"
            
            for aid in item.get("articleids", []):
                id_type = aid.get("idtype")
                if id_type == "pmc":
                    pmc_id = aid.get("value")
                elif id_type == "doi":
                    doi = aid.get("value")
            
            # Store data
            mapping[pmid] = {
                "pmc": pmc_id,
                "doi": doi,
                "publisher": source # Using Journal name as Publisher info
            }
            
    except Exception as e:
        logging.error(f"   ⚠️ Metadata fetch failed: {e}")
    
    return mapping

def check_oa_availability(pmc_id):
    """
    Checks if PMC allows PDF download. Returns True if available, False if not.
    """
    if not pmc_id: return False
    
    oa_url = f"https://www.ncbi.nlm.nih.gov/pmc/utils/oa/oa.fcgi?id={pmc_id}"
    try:
        r = requests.get(oa_url, timeout=10)
        root = ET.fromstring(r.content)
        # Look for any link with format="pdf"
        pdf_node = root.find(".//link[@format='pdf']")
        return pdf_node is not None
    except Exception:
        return False

def main():
    all_pmids = search_pubmed_ids(PUBMED_QUERY, MAX_ARTICLES)
    if not all_pmids: return

    total_pmids = len(all_pmids)
    num_batches = math.ceil(total_pmids / BATCH_SIZE)
    
    logging.info("-" * 60)
    logging.info(f"🚀 Audit Started: Checking {total_pmids} articles for PMC Access Failures")
    logging.info(f"💾 Saving list to: {OUTPUT_FILE}")
    logging.info("-" * 60)

    failed_count = 0
    
    # Open file in write mode to clear previous runs
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write("PMID,Publisher,DOI,PMCID\n") # Header

        for i in range(num_batches):
            start_idx = i * BATCH_SIZE
            end_idx = start_idx + BATCH_SIZE
            batch_pmids = all_pmids[start_idx:end_idx]
            
            # 1. Get Metadata
            metadata_map = batch_get_metadata(batch_pmids)
            
            # 2. Check each article
            for pmid, info in metadata_map.items():
                pmc_id = info['pmc']
                
                # Only check items that HAVE a PMCID (Target group)
                if pmc_id:
                    is_downloadable = check_oa_availability(pmc_id)
                    
                    if not is_downloadable:
                        # This is one of the ~232 files!
                        line = f"{pmid},{info['publisher']},{info['doi']},{pmc_id}"
                        f.write(line + "\n")
                        failed_count += 1
            
            # Force write to disk every batch
            f.flush()
            logging.info(f"📦 Batch {i+1}/{num_batches} checked. Total Failures Found: {failed_count}")
            
            # Polite sleep
            time.sleep(0.5)

    logging.info("-" * 60)
    logging.info(f"🎉 Audit Complete.")
    logging.info(f"❌ Identified {failed_count} articles with PMCID but no API access.")
    logging.info(f"📄 List saved to {OUTPUT_FILE}")

if __name__ == "__main__":
    main()