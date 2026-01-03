import os

LOG_FILE = "failed_Non_Elsevier_scraped_content_articles.txt"

if not os.path.exists(LOG_FILE):
    print(f"❌ No log file found: {LOG_FILE}")
else:
    elsevier_fail_count = 0
    non_elsevier_fail_count = 0
    total_failures = 0
    
    with open(LOG_FILE, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            
            # Skip empty lines or the header line
            if not line or line.startswith("PMID,"):
                continue
            
            total_failures += 1
            
            # Split the line by comma: "36509402, Elsevier, 10.1016/..."
            parts = line.split(",")
            
            # Safety check to ensure line has enough data
            if len(parts) >= 2:
                publisher = parts[1].strip() # Get the Publisher column (2nd item)
                
                if "Elsevier" in publisher:
                    elsevier_fail_count += 1
                else:
                    non_elsevier_fail_count += 1
            else:
                # If line is malformed, count as non-elsevier
                non_elsevier_fail_count += 1

    print("-" * 35)
    print(f"📊 FAILURE LOG ANALYSIS")
    print("-" * 35)
    print(f"❌ Total Failed Articles: {total_failures}")
    print(f"🔴 Elsevier Publishers:   {elsevier_fail_count}")
    print(f"🔵 Other Publishers:      {non_elsevier_fail_count}")
    print("-" * 35)


# -----------------------------------
# 📊 FAILURE LOG ANALYSIS
# -----------------------------------
# ❌ Total Failed Articles: 269
# 🔴 Elsevier Publishers:   132
# 🔵 Other Publishers:      137
# -----------------------------------