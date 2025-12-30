#XML Input -> lxml Parsing -> jsonL output
import requests
from bs4 import BeautifulSoup
import json
import time

ESEARCH_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
EFETCH_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi"
OUTPUT_FILE = 'test_1.jsonl'

headers = {
    "User-Agent": "MyTextMiningProject/1.0 (mailto:howard.kuo@vernus.ai)"
}

# --- Step 1: Define the target PMCIDs ---
# Note: EFetch (for full XML text) works best with PMCID, not PMID.
# We will use the PMCIDs you provided for the first two and find the third:
# 1. PMCID: PMC6847991 (from PMID: 31806968)
# 2. PMCID: PMC11068415 (from PMID: 38703930 - I searched and confirmed this is the PMCID)
# 3. PMCID: PMC7333068 (from PMID: 32592899 - I searched and confirmed this is the PMCID)

# Hardcoded list of PMCIDs for testing:
id_list = [
    "PMC6847991", 
] 

print(f"Fetching full text for {len(id_list)} known papers: {id_list}")
# --- End of Step 1 ---

# --- Step 2: Loop through each ID to fetch and parse its full text ---
try:
    with open(OUTPUT_FILE, 'a', encoding='utf-8') as f_out:
        for pmcid in id_list:
            print(f"\n=======================================================")
            print(f"Fetching full text for PMCID: {pmcid}...")
            print(f"=======================================================")
            
            fetch_params = {
                "db": "pmc",
                "id": pmcid,
                "rettype": "full", # Get the full text
                "retmode": "xml"  # Get it in XML format
            }
            
            # Pause for 1 second between each full-text request. (Good practice!)
            time.sleep(1) 
            
            try:
                fetch_response = requests.get(EFETCH_URL, params=fetch_params, headers=headers)
                fetch_response.raise_for_status()
                
                # Parse the XML to get the "Inside Text"
                # Using 'lxml-xml' is generally faster and more robust than 'xml'
                soup = BeautifulSoup(fetch_response.content, "lxml-xml")
                body = soup.find('body')
                
                if body:
                    # Find all <p> (paragraph) tags within the <body>
                    all_paragraphs = body.find_all('p')
                    if not all_paragraphs:
                        print(f"[No <p> tags found in the body for {pmcid}. It might be structured differently.]")
                        continue

                    # The original script had a print loop for debug, removing it for cleaner execution:
                    # for p in all_paragraphs:
                    #     print(p.get_text()) 
                    #     print("-----") 

                    full_text = "\n".join([p.get_text() for p in all_paragraphs])
                    
                    # Extract some metadata (e.g., title)
                    title = ""
                    title_tag = soup.find('article-title')
                    if title_tag:
                        title = title_tag.get_text()

                    paper_data = {
                        "pmcid": pmcid,
                        "title": title,
                        "text": full_text
                    }

                    f_out.write(json.dumps(paper_data) + "\n")
                    print(f" 💾 Successfully saved PMCID: {pmcid} (Title: {title[:50]}...) to {OUTPUT_FILE}")
                    
                else:
                    print(f"[Could not find the <body> tag for {pmcid}.]")
                    continue

            except requests.exceptions.RequestException as e:
                print(f" ❌ Error fetching {pmcid}: {e}")

except Exception as e:
    print(f"An unexpected error occurred: {e}")

print("\n--- Curation complete. ---")