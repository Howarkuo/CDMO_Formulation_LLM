
# Documentation: https://pmc.ncbi.nlm.nih.gov/tools/developers/
# 
# #API Endpoint:
# # 1. esearch - to find pmids 
# # 2. id conv - to convert pmids to pmcids 

# #URL package
# # 1. get.request() -> data type : HTTP object 
# 2. json()  -> dict -> data["esearchresult"]["idlist"] ->  List[str]
## output: ['36509402', ....]

# Fetching DOI
# 


import requests
import time
import math
from collections import Counter

# --- CONFIGURATION ---
PUBMED_QUERY = '((Drug Formulation) AND (Emulsion)) AND (dosage forms[MeSH Terms]) NOT Review[Pt] NOT "Clinical trial"[Pt] AND ffrft[Filter]'

# NCBI URLs
ESEARCH_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
ID_CONV_URL = "https://www.ncbi.nlm.nih.gov/pmc/utils/idconv/v1.0/"

NCBI_EMAIL = "howard.kuo@vernus.ai.com"
TOOL_NAME = "vernus_scraper"
FETCH_LIMIT = 1500 # Slightly higher to ensure we cover everything
BATCH_SIZE = 100   
OUTPUT_FILE = "pubmed_conversion_report.txt"

# Common DOI Prefix Mappings
DOI_PREFIXES = {
    "10.1016": "Elsevier (ScienceDirect)",
    "10.3390": "MDPI",
    "10.1002": "Wiley",
    "10.1007": "Springer",
    "10.1021": "ACS Publications",
    "10.1038": "Nature Portfolio",
    "10.1080": "Taylor & Francis",
    "10.1155": "Hindawi",
    "10.1371": "PLOS",
    "10.3389": "Frontiers"
}

def get_publisher_from_doi(doi):
    if not doi: return "Unknown/No DOI"
    prefix = doi.split('/')[0]
    return DOI_PREFIXES.get(prefix, f"Other ({prefix})")

def get_pmids(query, limit):
    print(f"🔍 Searching Query: {query}")
    params = {
        "db": "pubmed", "term": query, "retmode": "json",
        "email": NCBI_EMAIL, "retmax": limit, "sort": "relevance"
    }
    try:
        r = requests.get(ESEARCH_URL, params=params)
        r.raise_for_status()
        data = r.json()
        count = int(data.get("esearchresult", {}).get("count", 0))
        pmids = data.get("esearchresult", {}).get("idlist", [])
        print(f"📊 Total Matches: {count} | Fetching Top: {len(pmids)}")
        return pmids
    except Exception as e:
        print(f"Error in ESEARCH: {e}")
        return []

def batch_convert_ids(pmid_list):
    # send batch 15 times with 0.3 timeout
    all_records = []
    total_pmids = len(pmid_list)
    num_batches = math.ceil(total_pmids / BATCH_SIZE)

    print(f"\n🔄 Converting {total_pmids} PMIDs in {num_batches} batches...")

    for i in range(num_batches):
        start = i * BATCH_SIZE
        end = start + BATCH_SIZE
        batch = pmid_list[start:end]
        
        # Join IDs as string for the API
        ids_str = ",".join(batch)
        params = {"tool": TOOL_NAME, "email": NCBI_EMAIL, "ids": ids_str, "format": "json"}

        try:
            r = requests.get(ID_CONV_URL, params=params)
            r.raise_for_status()
            data = r.json()
            records = data.get("records", [])
            all_records.extend(records)
            print(f"   Batch {i+1}/{num_batches}: Found {len(records)} records")
        except Exception as e:
            print(f"   ❌ Error in Batch {i+1}: {e}")
        
        time.sleep(0.3)

    return all_records

def generate_report(pmids, records):
    # --- FIX IS HERE: Normalize keys to String to prevent mismatch ---
    # Create a lookup map where keys are strictly Strings
    record_map = {str(rec.get('pmid', '')): rec for rec in records}

    has_pmcid = []     # TARGET 1: List you want
    no_pmcid_list = [] # TARGET 2: Needs Publisher API
    publisher_stats = []

    for pmid in pmids:
        # Normalize lookup key to String
        pmid_str = str(pmid)
        item = record_map.get(pmid_str)
        
        if item and item.get("pmcid"):
            # Found a PMCID!
            has_pmcid.append(item)
        else:
            # No PMCID found
            doi = item.get("doi") if item else None
            publisher = get_publisher_from_doi(doi)
            no_pmcid_list.append({"pmid": pmid_str, "doi": doi, "publisher": publisher})
            publisher_stats.append(publisher)

    # Stats
    total = len(pmids)
    success_count = len(has_pmcid)
    success_rate = (success_count / total) * 100 if total > 0 else 0
    publisher_counts = Counter(publisher_stats).most_common()

    # Write Report
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write("="*60 + "\n")
        f.write(f"PUBMED CONVERSION REPORT\n")
        f.write("="*60 + "\n\n")

        f.write(f"1. OVERVIEW\n")
        f.write(f"   - Total PMIDs: {total}\n")
        f.write(f"   - ✅ Full Text Available (Has PMCID): {success_count} ({success_rate:.1f}%)\n")
        f.write(f"   - ❌ Publisher Access Only (No PMCID): {len(no_pmcid_list)}\n\n")

        f.write(f"2. SOURCE ANALYSIS (Where are the missing papers?)\n")
        f.write(f"   {'Publisher':<30} | {'Count':<10}\n")
        f.write(f"   {'-'*30} | {'-'*10}\n")
        for pub, count in publisher_counts:
            f.write(f"   {pub:<30} | {count:<10}\n")
        f.write("\n")

        f.write("="*60 + "\n")
        f.write("3. DETAILED LISTS\n")
        f.write("="*60 + "\n\n")

        # This is the list you want:
        f.write(f"[LIST A] Papers WITH PMCID (Target 1 - Use OA API)\n")
        f.write(f"format: PMID, PMCID, DOI\n")
        for item in has_pmcid:
            f.write(f"{item.get('pmid')}, {item.get('pmcid')}, {item.get('doi')}\n")
        
        f.write("\n" + "-"*40 + "\n\n")

        f.write(f"[LIST B] Papers WITHOUT PMCID (Target 2 - Needs Publisher API)\n")
        f.write(f"format: PMID, Publisher, DOI\n")
        for item in no_pmcid_list:
            f.write(f"{item['pmid']}, {item['publisher']}, {item['doi']}\n")

    print(f"\n✅ Report generated: {OUTPUT_FILE}")
    print(f"   Correct Success Rate: {success_rate:.1f}%")

if __name__ == "__main__":
    pmids = get_pmids(PUBMED_QUERY, FETCH_LIMIT)
    if pmids:
        records = batch_convert_ids(pmids)
        generate_report(pmids, records)