import requests
import json

# --- CONFIGURATION ---
# Use your email to be polite to NCBI servers
NCBI_EMAIL = "your.email@example.com" 

def test_pubmed_fetch():
    print("🚀 Starting Test...")
    
    # 1. SEARCH for PMIDs
    # Query: Drug Formulation AND Emulsion
    search_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
    search_params = {
        "db": "pubmed",
        "term": '((Drug Formulation) AND (dosage forms[MeSH Terms]) '
    'NOT "Review"[pt] '
    'NOT "Clinical trial"[pt]) '
    'AND "free full text"[filter] '
    'AND 2000/01/01:2025/12/31[dp]',
        "retmode": "json",
        "retmax": 2,  # LIMIT TO 2 ARTICLES
        "email": NCBI_EMAIL,
        "sort": "relevance"
    }
    
    try:
        print("🔍 Searching PubMed...")
        r = requests.get(search_url, params=search_params)
        r.raise_for_status()
        pmids = r.json().get("esearchresult", {}).get("idlist", [])
        
        if not pmids:
            print("❌ No PMIDs found.")
            return

        print(f"✅ Found PMIDs: {pmids}")
    except Exception as e:
        print(f"❌ Search failed: {e}")
        return

    # 2. FETCH METADATA (DOI & PMCID)
    # This mimics the logic inside your `_get_article_metadata` function
    summary_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi"
    summary_params = {
        "db": "pubmed",
        "id": ",".join(pmids),
        "retmode": "json",
        "email": NCBI_EMAIL
    }
    
    print("\n📥 Fetching Metadata...")
    try:
        r = requests.get(summary_url, params=summary_params)
        r.raise_for_status()
        data = r.json()
        result = data.get("result", {})
        uids = result.get("uids", [])
        
        print("-" * 40)
        for pmid in uids:
            item = result.get(pmid, {})
            title = item.get("title", "No Title")
            
            pmc_id = "Not Found"
            doi = "Not Found"
            
            # THE CRITICAL LOGIC LOOP
            for aid in item.get("articleids", []):
                if aid.get("idtype") == "pmc":
                    pmc_id = aid.get("value")
                elif aid.get("idtype") == "doi":
                    doi = aid.get("value")
            
            print(f"📄 PMID:   {pmid}")
            print(f"   Title:  {title[:60]}...") # Truncate title for readability
            print(f"   PMCID:  {pmc_id}")
            print(f"   DOI:    {doi}")
            print("-" * 40)

    except Exception as e:
        print(f"❌ Metadata fetch failed: {e}")

if __name__ == "__main__":
    test_pubmed_fetch()

# 🚀 Starting Test...
# 🔍 Searching PubMed...
# ✅ Found PMIDs: ['37207857', '31536731']

# 📥 Fetching Metadata...
# ----------------------------------------
# 📄 PMID:   37207857
#    Title:  Formulation and processing of solid self-emulsifying drug de...
#    PMCID:  PMC10429704
#    DOI:    10.1016/j.ijpharm.2023.123055
# ----------------------------------------
# 📄 PMID:   31536731
#    Title:  Understanding drug distribution and release in ophthalmic em...
#    PMCID:  Not Found
#    DOI:    10.1016/j.jconrel.2019.09.010
# ----------------------------------------