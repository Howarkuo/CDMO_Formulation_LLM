# Documentation: https://pmc.ncbi.nlm.nih.gov/tools/developers/
# 
# #API Endpoint:
# # 1. esearch - to find pmids 
# # 2. id conv - to convert pmids to pmcids, to get DOI (metadata)
## 3. esummary - to get DOI (METAdata) of id conv not available part

# #URL package
# # 1. get.request() -> data type : HTTP object 
# 2. json()  -> dict -> data["esearchresult"]["idlist"] ->  List[str]
## output: ['36509402', ....]

# Fetching DOI
# 1. idconv 
# 2. esummary
import requests
import time
import math
from collections import Counter

# --- CONFIGURATION ---
PUBMED_QUERY = '((Drug Formulation) AND (Emulsion)) AND (dosage forms[MeSH Terms]) NOT Review[Pt] NOT "Clinical trial"[Pt] AND ffrft[Filter]'

# 1. ID Converter (Best for PMCID & PMC-DOIs)
ID_CONV_URL = "https://www.ncbi.nlm.nih.gov/pmc/utils/idconv/v1.0/"
# 2. ESummary (Best for "Rescue" DOIs)
ESUMMARY_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi"
ESEARCH_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"

NCBI_EMAIL = "howard.kuo@vernus.ai.com"
TOOL_NAME = "vernus_scraper"
FETCH_LIMIT = 1500 
BATCH_SIZE = 100   
OUTPUT_FILE = "pubmed_conversion_report.txt"

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
        ids = data.get("esearchresult", {}).get("idlist", [])
        print(f"📊 Total Matches: {data.get('esearchresult', {}).get('count')} | Fetching Top: {len(ids)}")
        return ids
    except Exception as e:
        print(f"Error in ESEARCH: {e}")
        return []

def batch_convert_ids(pmid_list):
    """Phase 1: ID Converter"""
    all_records = []
    num_batches = math.ceil(len(pmid_list) / BATCH_SIZE)
    print(f"\nPhase 1: Checking PMC Availability ({len(pmid_list)} IDs)...")

    for i in range(num_batches):
        batch = pmid_list[i*BATCH_SIZE : (i+1)*BATCH_SIZE]
        params = {"tool": TOOL_NAME, "email": NCBI_EMAIL, "ids": ",".join(batch), "format": "json"}
        try:
            r = requests.get(ID_CONV_URL, params=params)
            r.raise_for_status()
            all_records.extend(r.json().get("records", []))
        except Exception as e:
            print(f"   ❌ Batch {i+1} failed: {e}")
        time.sleep(0.3)
    return all_records

def rescue_dois_via_esummary(pmid_list):
    """Phase 2: ESummary Rescue"""
    if not pmid_list: return {}
    doi_map = {}
    num_batches = math.ceil(len(pmid_list) / BATCH_SIZE)
    print(f"\nPhase 2: Rescuing missing DOIs via ESummary ({len(pmid_list)} IDs)...")

    for i in range(num_batches):
        batch = pmid_list[i*BATCH_SIZE : (i+1)*BATCH_SIZE]
        params = {"db": "pubmed", "id": ",".join(batch), "retmode": "json", "email": NCBI_EMAIL}
        try:
            r = requests.get(ESUMMARY_URL, params=params)
            r.raise_for_status()
            result = r.json().get("result", {})
            result.pop("uids", None)
            
            for pmid, doc in result.items():
                found_doi = None
                for aid in doc.get("articleids", []):
                    if aid.get("idtype") == "doi":
                        found_doi = aid.get("value")
                        break
                if found_doi:
                    doi_map[str(pmid)] = found_doi
        except Exception as e:
            print(f"   ❌ Rescue Batch {i+1} failed: {e}")
        time.sleep(0.3)
        
    print(f"   ✅ Successfully rescued {len(doi_map)} DOIs.")
    return doi_map

def generate_report(pmids, conv_records):
    record_map = {str(rec.get('pmid', '')): rec for rec in conv_records}
    
    # Lists for final output
    target1_list = [] # PMC Available
    target2_list = [] # Publisher API Needed
    missing_doi_pmids = [] # Temporary list for rescue

    # --- 1. First Pass (Classification) ---
    for pmid in pmids:
        pmid_str = str(pmid)
        item = record_map.get(pmid_str)
        
        if item and item.get("pmcid"):
            # Target 1 found
            doi = item.get("doi")
            publisher = get_publisher_from_doi(doi)
            target1_list.append({"pmid": pmid_str, "pmcid": item["pmcid"], "doi": doi, "publisher": publisher})
        else:
            # Not in PMC
            if item and item.get("doi"):
                 publisher = get_publisher_from_doi(item['doi'])
                 target2_list.append({"pmid": pmid_str, "doi": item['doi'], "publisher": publisher})
            else:
                missing_doi_pmids.append(pmid_str)

    # --- 2. Phase 2 (Rescue) ---
    rescued_dois = rescue_dois_via_esummary(missing_doi_pmids)
    
    for pmid in missing_doi_pmids:
        doi = rescued_dois.get(pmid)
        publisher = get_publisher_from_doi(doi)
        target2_list.append({"pmid": pmid, "doi": doi, "publisher": publisher})

    # --- 3. Statistics ---
    total = len(pmids)
    
    # Count Publishers for Target 1
    t1_publishers = Counter([x['publisher'] for x in target1_list]).most_common()
    
    # Count Publishers for Target 2
    t2_publishers = Counter([x['publisher'] for x in target2_list]).most_common()

    # --- 4. Write Report ---
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write("="*60 + "\n")
        f.write(f"PUBMED ACCESS AUDIT REPORT (v3)\n")
        f.write(f"Date: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write("="*60 + "\n\n")

        f.write(f"1. OVERVIEW\n")
        f.write(f"   - Total PMIDs: {total}\n")
        f.write(f"   - ✅ Target 1 (PMC - Downloadable): {len(target1_list)} ({(len(target1_list)/total)*100:.1f}%)\n")
        f.write(f"   - ⚠️ Target 2 (Publisher - External): {len(target2_list)}\n")
        
        f.write(f"\n2. PUBLISHER BREAKDOWN\n")
        f.write("-" * 40 + "\n")
        
        f.write(f"\n[2.1] Target 1: PMC Sources (Open Access)\n")
        f.write(f"   {'Publisher':<30} | {'Count':<10}\n")
        f.write(f"   {'-'*30} | {'-'*10}\n")
        for pub, count in t1_publishers:
            f.write(f"   {pub:<30} | {count:<10}\n")
            
        f.write(f"\n[2.2] Target 2: External Sources (Locked/Redirect)\n")
        f.write(f"   {'Publisher':<30} | {'Count':<10}\n")
        f.write(f"   {'-'*30} | {'-'*10}\n")
        for pub, count in t2_publishers:
            f.write(f"   {pub:<30} | {count:<10}\n")
        
        f.write(f"\n3. DETAILED LISTS\n")
        f.write("="*60 + "\n")
        f.write(f"[LIST A] Target 1: PMC Papers (Use oa_downloader.py)\n")
        f.write(f"format: PMID, PMCID, Publisher, DOI\n")
        for item in target1_list:
            f.write(f"{item['pmid']}, {item['pmcid']}, {item['publisher']}, {item['doi']}\n")
        
        f.write("\n" + "="*60 + "\n")
        f.write(f"[LIST B] Target 2: External Papers (Needs Publisher API)\n")
        f.write(f"format: PMID, Publisher, DOI\n")
        for item in target2_list:
            f.write(f"{item['pmid']}, {item['publisher']}, {item['doi']}\n")

    print(f"\n✅ Report generated: {OUTPUT_FILE}")

if __name__ == "__main__":
    pmids = get_pmids(PUBMED_QUERY, FETCH_LIMIT)
    if pmids:
        records = batch_convert_ids(pmids)
        generate_report(pmids, records)