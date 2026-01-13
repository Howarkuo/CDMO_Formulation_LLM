from elsapy.elsclient import ElsClient
from elsapy.elsdoc import FullDoc
import json
import requests
import os

# --- Configuration ---
CONFIG_FILE = "config.json"
OUTPUT_DIR = "withpmcidstillmissing_36_Elseveir"
TARGET_DOIS = [
"10.1016/j.actbio.2021.09.038",
"10.1016/j.jconrel.2014.08.029",
"10.1016/j.ijpharm.2017.09.043",
"10.1016/j.jconrel.2009.08.023",
"10.1016/j.ijpharm.2024.124661",
"10.1016/j.ijpharm.2019.118609",
"10.1016/j.jconrel.2009.11.008",
"10.1016/j.jconrel.2008.03.013",
"10.1016/j.vaccine.2006.07.055",
"10.1016/j.vaccine.2016.12.057",
"10.1016/j.ijpharm.2023.123055",
"10.1016/j.canlet.2017.08.004",
"10.1016/j.actbio.2013.08.011",
"10.1016/j.ejpb.2021.03.007",
"10.1016/j.jvir.2020.01.026",
"10.1016/j.actbio.2015.08.039",
"10.1016/j.ijpharm.2007.03.007",
"10.1016/j.ijpharm.2011.02.037",
"10.1016/j.actbio.2011.10.001",
"10.1016/j.ijpharm.2007.05.023",
"10.1016/j.ijpharm.2015.11.045",
"10.1016/j.biomaterials.2020.120238",
"10.1016/j.jconrel.2017.07.003",
"10.1016/j.ijpharm.2011.04.017",
"10.1016/j.ijpharm.2013.11.058",
"10.1016/j.ijpharm.2015.08.089",
"10.1016/j.taap.2012.06.017",
"10.1016/j.biomaterials.2009.06.061",
"10.1016/j.ijpharm.2009.12.040",
"10.1016/j.ijpharm.2015.11.002",
"10.1016/j.colsurfb.2015.01.055",
"10.1016/j.ijpharm.2009.06.004",
"10.1016/j.ijpharm.2017.11.062",
"10.1016/j.actbio.2014.04.024",
"10.1016/j.ijpharm.2011.11.043",
"10.1016/j.ijpharm.2015.11.018"
]

def load_client():
    """Initializes the Elsevier Client using ONLY the API Key"""
    try:
        with open(CONFIG_FILE, "r") as f:
            config = json.load(f)
        
        # Initialize Client without inst_token
        # The API will rely on your VPN IP address for authentication
        client = ElsClient(config['apikey'])
            
        print(f"✅ Client initialized. (Authentication depends on your VPN)")
        return client
    except FileNotFoundError:
        print("❌ Error: config.json not found.")
        return None

def download_pdf(url, filename, api_key):
    """Downloads PDF using VPN access"""
    headers = {
        "X-ELS-APIKey": api_key,
        "Accept": "application/pdf"
        # Note: No X-ELS-Insttoken header is sent
    }

    print(f"   -> Requesting PDF via NYCU VPN...")
    try:
        r = requests.get(url, headers=headers, stream=True)
        
        if r.status_code == 200:
            with open(filename, 'wb') as f:
                for chunk in r.iter_content(chunk_size=1024):
                    f.write(chunk)
            print(f"   -> 📄 Success! Saved to: {filename}")
            return True
        elif r.status_code == 401:
            print("   -> ❌ 401 Unauthorized. VPN might not be recognized or Subscription missing for this journal.")
        else:
            print(f"   -> ⚠️ Failed. Status: {r.status_code}")
            return False
    except Exception as e:
        print(f"   -> Error: {e}")
        return False

# --- Main Execution ---
if __name__ == "__main__":
    # 1. Check VPN Connection (Simple sanity check)
    try:
        # This asks a public server what your IP is. 
        # If it looks like a Taiwan university IP, you are good.
        my_ip = requests.get("https://api.ipify.org").text
        print(f"ℹ️  Current Public IP: {my_ip} (Ensure this is your NYCU VPN IP)")
    except:
        pass

    client = load_client()
    
    if client:
        if not os.path.exists(OUTPUT_DIR):
            os.mkdir(OUTPUT_DIR)

        for doi in TARGET_DOIS:
            print(f"\nProcessing DOI: {doi}")
            
            # Initialize Document
            doc = FullDoc(doi=doi)
            
            # Read metadata
            if doc.read(client):
                print(f"   -> Metadata Found: {doc.title}")
                doc.write() 

                # Download PDF
                pdf_filename = os.path.join(OUTPUT_DIR, f"{doi.replace('/', '_')}.pdf")
                pdf_url = f"https://api.elsevier.com/content/article/doi/{doi}"
                
                download_pdf(pdf_url, pdf_filename, client.api_key)
            else:
                print("   -> ❌ Could not read document metadata.")