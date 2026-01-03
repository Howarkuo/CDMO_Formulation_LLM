import requests
import json
import os

# --- CONFIGURATION ---
# Problem of the  query- ffrft[Filter]: free on publisher websites but no pmcid (which the API cannot download).
# The corrected query
# PUBMED_QUERY = '((Drug Formulation) AND (Emulsion)) AND (dosage forms[MeSH Terms]) NOT Review[Pt] NOT "Clinical trial"[Pt] AND ffrft[Filter]'
# PUBMED_QUERY = '((Drug Formulation) AND (Emulsion)) AND (dosage forms[MeSH Terms]) NOT "Review"[Pt] NOT "Clinical trial"[Pt] AND ffrft[Filter]'
PUBMED_QUERY = '((Drug Formulation) AND (Emulsion)) AND (dosage forms[MeSH Terms]) NOT Review[Pt] NOT "Clinical trial"[Pt] AND ffrft[Filter]'

# PUBMED_QUERY = '((Drug Formulation) AND (Emulsion)) '

#trial case

# NCBI Configuration
BASE_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
NCBI_EMAIL = "howard.kuo@vernus.ai.com" 
API_KEY_PATH = r"C:\Users\howar\Desktop\api_key.txt"

def load_api_key(path):
    """Safely loads the API key if the file exists."""
    if os.path.exists(path):
        with open(path, 'r') as f:
            return f.read().strip()
    return None

def test_pubmed_count():
    print(f"Testing Query: {PUBMED_QUERY}")
    print("-" * 50)

    # Prepare parameters for ESearch
    params = {
        "db": "pubmed",
        "term": PUBMED_QUERY,
        "retmode": "json",
        "email": NCBI_EMAIL,
        # "rettype": "count" # Optional: strictly asks for count, but json includes it anyway
    }

    # Load API Key if available (increases rate limit to 10 requests/sec)
    # api_key = 'none'

    try:
        # Send Request
        response = requests.get(BASE_URL, params=params)
        response.raise_for_status() # Check for HTTP errors

        # Parse JSON
        data = response.json()
        
        # Extract Count
        count = data.get("esearchresult", {}).get("count")
        
        print("-" * 50)
        print(f"Total Papers Found: {count}")
        print("-" * 50)

        # Print Translation Stack (To see how PubMed interpreted your terms)
        # This is useful to debug if 'Drug Formulation' mapped correctly
        translations = data.get("esearchresult", {}).get("querytranslation")
        print("PubMed Query Translation (How NCBI interpreted it):")
        print(translations)

    except requests.exceptions.RequestException as e:
        print(f"Network Error: {e}")
    except json.JSONDecodeError:
        print("Error: Failed to parse JSON response. (Check if NCBI is down or query is invalid)")

if __name__ == "__main__":
    test_pubmed_count()

#     Testing Query: ((Drug Formulation) AND (Emulsion)) AND (dosage forms[MeSH Terms]) NOT "Review"[Pt] NOT "Clinical trial"[Pt] AND ffrft[Filter]
# --------------------------------------------------
# --------------------------------------------------
# # Total Papers Found: 1196
# --------------------------------------------------
# PubMed Query Translation (How NCBI interpreted it):
# (((("drug compounding"[MeSH Terms] OR ("drug"[All Fields] AND "compounding"[All Fields]) OR "drug compounding"[All Fields] OR ("drug"[All Fields] AND "formulation"[All Fields]) OR "drug formulation"[All Fields]) AND ("emulsion s"[All Fields] OR "emulsions"[Supplementary Concept] OR "emulsions"[All Fields] OR "emulsion"[All Fields] OR "emulsions"[MeSH Terms] OR "emulsive"[All Fields]) AND "dosage forms"[MeSH Terms]) NOT "Review"[Publication Type]) NOT "Clinical trial"[Publication Type]) AND "loattrfree full text"[Filter]