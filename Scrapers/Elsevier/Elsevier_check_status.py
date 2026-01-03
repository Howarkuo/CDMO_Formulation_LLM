import json
import os

LOG_FILE = "download_log.jsonl"

if not os.path.exists(LOG_FILE):
    print("❌ No log file found yet.")
else:
    success_count = 0
    fail_count = 0
    
    with open(LOG_FILE, "r", encoding="utf-8") as f:
        for line in f:
            try:
                entry = json.loads(line)
                if entry.get("status") == "success":
                    success_count += 1
                else:
                    fail_count += 1
            except:
                pass

    print("-" * 30)
    print(f"📊 BATCH DOWNLOAD REPORT")
    print("-" * 30)
    print(f"✅ Successful: {success_count}")
    print(f"❌ Failed:     {fail_count}")
    print(f"Σ  Total:      {success_count + fail_count}")
    print("-" * 30)


# ------------------------------
# 📊 BATCH DOWNLOAD REPORT
# ------------------------------
# ✅ Successful: 133
# ❌ Failed:     0
# Σ  Total:      133
# ------------------------------