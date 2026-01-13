import json
import re

# ================= CONFIGURATION =================
# Replace these filenames with your actual file paths
FULL_LIST_FILE = "444_full_list_withoutpmcid"
SUCCESS_LOG_FILE = "133_Without_pmcid_Elsevier_download_log.jsonl"
MISSING_LIST_FILE = "283_without_pmcid_still_missing"
# =================================================

def normalize_doi(doi_string):
    """Cleans DOI strings for accurate comparison."""
    if not doi_string:
        return None
    clean = doi_string.strip()
    if clean.lower() == "none" or clean == "":
        return None
    return clean.lower()

def load_full_list(filepath):
    """Parses List A (The 444 list)"""
    dois = set()
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                # Skip headers or separators
                if "======" in line or "[LIST" in line or "format:" in line:
                    continue
                
                parts = line.split(',')
                if len(parts) >= 3:
                    # format: PMID, Publisher, DOI
                    doi = parts[-1]
                    norm_doi = normalize_doi(doi)
                    if norm_doi:
                        dois.add(norm_doi)
    except FileNotFoundError:
        print(f"❌ Error: Could not find {filepath}")
    return dois

def load_success_log(filepath):
    """Parses List B (The JSONL logs)"""
    dois = set()
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if not line: continue
                try:
                    data = json.loads(line)
                    if "doi" in data:
                        norm_doi = normalize_doi(data["doi"])
                        if norm_doi:
                            dois.add(norm_doi)
                except json.JSONDecodeError:
                    pass
    except FileNotFoundError:
        print(f"❌ Error: Could not find {filepath}")
    return dois

def load_missing_list(filepath):
    """Parses List C (The # MISSING list)"""
    dois = set()
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                # Look for lines starting with # MISSING:
                if "MISSING:" in line:
                    # Remove the prefix "# MISSING:"
                    content = line.split("MISSING:")[1]
                    parts = content.split(',')
                    if len(parts) >= 3:
                        doi = parts[-1]
                        norm_doi = normalize_doi(doi)
                        if norm_doi:
                            dois.add(norm_doi)
    except FileNotFoundError:
        print(f"❌ Error: Could not find {filepath}")
    return dois

# ================= EXECUTION =================

print("--- processing ---")

# 1. Load Sets
full_set = load_full_list(FULL_LIST_FILE)
success_set = load_success_log(SUCCESS_LOG_FILE)
known_missing_set = load_missing_list(MISSING_LIST_FILE)

print(f"Full List Count (valid DOIs): {len(full_set)}")
print(f"Success Log Count:            {len(success_set)}")
print(f"Known Missing Count:          {len(known_missing_set)}")

# 2. Calculate the Discrepancy
# Union of what we have accounted for (Success + Known Missing)
accounted_for = success_set.union(known_missing_set)

# The 'True Missing' are items in Full Set that are NOT in Accounted For
true_missing = full_set - accounted_for

print("-" * 40)
print(f"Total Accounted For: {len(accounted_for)}")
print(f"TRUE MISSING COUNT:  {len(true_missing)}")
print("-" * 40)

# 3. Output the missing items
if len(true_missing) > 0:
    print("\nHere are the DOIs missing from both lists:\n")
    for doi in true_missing:
        print(doi)
        
    # Optional: Save to file
    with open("final_missing_gap.txt", "w") as out:
        for doi in true_missing:
            out.write(f"{doi}\n")
    print(f"\nSaved list to 'final_missing_gap.txt'")
else:
    print("✅ All items match! No gap found.")