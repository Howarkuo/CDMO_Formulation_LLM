import os

# --- CONFIGURATION ---
INPUT_FILE = r"C:\Users\howar\Desktop\biollm\failed_Non_PMCID_scraped_content_articles.txt"
OUTPUT_FILE = r"C:\Users\howar\Desktop\biollm\failed_Non_PMCID_scraped_content_articles_converted_source_data.txt"

def convert_and_save():
    if not os.path.exists(INPUT_FILE):
        print(f"❌ Error: Input file not found at {INPUT_FILE}")
        return

    formatted_entries = []
    
    print(f"📖 Reading from: {INPUT_FILE}...")
    
    try:
        with open(INPUT_FILE, "r", encoding="utf-8") as f:
            lines = f.readlines()
            
            # Skip the header row
            for line in lines[1:]: 
                line = line.strip()
                if not line: continue
                
                # Split by comma
                parts = line.split(",")
                
                # Ensure we have at least 3 columns (PMID, Publisher, DOI)
                if len(parts) >= 3:
                    pmid = parts[0].strip()
                    publisher = parts[1].strip()
                    doi = parts[2].strip()
                    
                    # Format exactly as Python tuple string
                    # Indented with 4 spaces for clean pasting
                    entry = f'    ("{pmid}", "{publisher}", "{doi}")'
                    formatted_entries.append(entry)

        # Write to the output file
        with open(OUTPUT_FILE, "w", encoding="utf-8") as out:
            out.write("SOURCE_DATA = [\n")
            # Join all entries with a comma and newline
            out.write(",\n".join(formatted_entries))
            out.write("\n]")
            
        print(f"✅ Success! Converted {len(formatted_entries)} entries.")
        print(f"💾 Saved to: {OUTPUT_FILE}")

    except Exception as e:
        print(f"❌ An error occurred: {e}")

if __name__ == "__main__":
    convert_and_save()