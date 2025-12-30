
import requests
import json
import os
import time

# --- CONFIGURATION ---
# Query Options:
# 1. "pmc free article"[Filter] -> Will result in near 100% downloadable (Target)
# 2. ffrft[Filter] -> Will include publisher sites (API cannot download these)

PUBMED_QUERY = '((Drug Formulation) AND (Emulsion)) AND (dosage forms[MeSH Terms]) NOT Review[Pt] NOT "Clinical trial"[Pt] AND ffrft[Filter]'

# NCBI URLs
ESEARCH_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
ELINK_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/elink.fcgi"

NCBI_EMAIL = "howard.kuo@vernus.ai.com" 
# Optional: Increase retmax to check more papers (max 100 per request is safe without batching)
CHECK_LIMIT = 100  
def check_pmc_availability():
    print(f"🔍 Analyzing Query: {PUBMED_QUERY}")
    print("-" * 60)
    # --- STEP 1: ESEARCH (Get PMIDs) ---
    search_params = {
        "db": "pubmed",
        "term": PUBMED_QUERY,
        "retmode": "json",
        "email": NCBI_EMAIL,
        "retmax": CHECK_LIMIT, # Limit how many IDs we fetch to check
        "sort": "relevance"
    }

    try:
        # 1. Run Search
        r_search = requests.get(ESEARCH_URL, params=search_params)
        r_search.raise_for_status()
        search_data = r_search.json()
        
        # Get basic stats
        total_count = int(search_data.get("esearchresult", {}).get("count", 0))
        pmid_list = search_data.get("esearchresult", {}).get("idlist", [])

        print(f"📊 Total Papers Matching Query: {total_count}")
        print(f"   (Checking a sample of top {len(pmid_list)} results for API download availability...)\n")

        if not pmid_list:
            print("No papers found. Exiting.")
            return

        # --- STEP 2: ELINK (Map PMID -> PMCID) ---
        # This asks NCBI: "Which of these PMIDs have a full-text link in PMC?"
        link_params = {
            "dbfrom": "pubmed",
            "db": "pmc",
            "linkname": "pubmed_pmc",
            "id": ",".join(pmid_list),
            "retmode": "json",
            "email": NCBI_EMAIL,
            "cmd": "neighbor"
        }

        r_link = requests.get(ELINK_URL, params=link_params)
        r_link.raise_for_status()
        link_data = r_link.json()​
        # Count successful mappings
        downloadable_count = 0
        valid_pmcids = []

        # Parse the 'linksets' to see which input PMIDs have a "pubmed_pmc" link
        linksets = link_data.get("linksets", [])
        
        for linkset in linksets:
            # Check if this PMID has "linksetdbs" (connections to other databases)
            if "linksetdbs" in linkset:
                for db_link in linkset["linksetdbs"]:
                    # We only care about links to PMC
                    if db_link["linkname"] == "pubmed_pmc":
                        downloadable_count += 1
                        pmc_id = db_link["links"][0]
                        valid_pmcids.append(f"PMC{pmc_id}")
                        break # Found a PMC link for this paper, move to next

        # --- STEP 3: REPORT ---
        print("-" * 60)
        print(f"Results for top {len(pmid_list)} papers:")
        print(f"✅ Downloadable via API (Have PMCID): {downloadable_count}")
        print(f"❌ Not Downloadable (Publisher site only): {len(pmid_list) - downloadable_count}")
        print("-" * 60)
        
        availability_rate = (downloadable_count / len(pmid_list)) * 100
        print(f"📉 API Success Rate: {availability_rate:.1f}%")

        if downloadable_count < 5:
            print("\n⚠️ WARNING: Low yield. Your script might fail to find 5 papers.")
            print("   Suggestion: Remove strict filters or check 'Free Full Text' logic.")
        else:
            print("\n✅ Good yield. You have enough papers for scraping.")

    except requests.exceptions.RequestException as e:
        print(f"Network Error: {e}")
    except json.JSONDecodeError:
        print("Error: Failed to parse JSON response.")

if __name__ == "__main__":
    check_pmc_availability()