from elsapy.elsclient import ElsClient
from elsapy.elsdoc import FullDoc
import json
import requests
import os

# --- Configuration ---
CONFIG_FILE = "config.json"
OUTPUT_DIR = "nycu_downloads"
TARGET_DOIS = [
    "10.1016/j.actbio.2022.12.004",
    "10.1016/j.ijpharm.2024.124947",
    "10.1016/j.aohep.2020.10.006",
    "10.1016/j.aquatox.2017.12.007",
    "10.1016/j.jcis.2023.07.055",
    "10.1016/j.ijpharm.2021.120304",
    "10.1016/j.jcis.2024.05.087",
    "10.1016/j.ejps.2023.106585",
    "10.1016/j.jid.2020.01.032",
    "10.1016/j.ejpb.2024.114372",
    "10.1016/j.biopha.2018.12.079",
    "10.1016/j.jvir.2025.01.040",
    "10.1016/j.jconrel.2024.08.021",
    "10.1016/j.ijpharm.2016.04.027",
    "10.1016/j.ultsonch.2016.08.026",
    "10.1016/j.biopha.2024.117109",
    "10.1016/j.ejps.2025.107186",
    "10.1016/j.ejps.2024.106993",
    "10.1016/j.jconrel.2015.12.022",
    "10.1016/j.ejps.2010.11.014",
    "10.1016/j.biopha.2020.111109",
    "10.1016/j.ejps.2024.106844",
    "10.1016/j.ijpharm.2025.125309",
    "10.1016/j.ultsonch.2013.12.017",
    "10.1016/j.ejps.2025.107279",
    "10.1016/j.ejps.2025.107306",
    "10.1016/j.ijbiomac.2024.133295",
    "10.1016/j.colsurfb.2018.01.023",
    "10.1016/j.jcis.2020.06.024",
    "10.1016/j.biopha.2020.111114",
    "10.1016/j.biopha.2019.109373",
    "10.1016/j.colsurfb.2024.114051",
    "10.1016/j.ijpharm.2025.125384",
    "10.1016/j.ejpb.2021.02.012",
    "10.1016/j.ejps.2010.03.008",
    "10.1016/j.jconrel.2013.10.027",
    "10.1016/j.foodres.2024.114412",
    "10.1016/j.ijbiomac.2022.10.207",
    "10.1016/j.foodchem.2025.143650",
    "10.1016/j.ijbiomac.2025.142957",
    "10.1016/j.ultsonch.2011.07.001",
    "10.1016/j.biopha.2020.110369",
    "10.1016/j.ijpharm.2025.126366",
    "10.1016/j.ultsonch.2019.05.021",
    "10.1016/j.foodres.2024.114743",
    "10.1016/s0378-5173(02)00158-8",
    "10.1016/j.ultsonch.2017.09.042",
    "10.1016/j.carbpol.2021.118060",
    "10.1016/j.ijbiomac.2016.01.064",
    "10.1016/j.exer.2016.10.016",
    "10.1016/j.ejps.2024.106835",
    "10.1016/j.ijpharm.2012.02.025",
    "10.1016/j.ijbiomac.2015.12.029",
    "10.1016/j.ejpb.2012.10.016",
    "10.1016/j.ijpharm.2025.126229",
    "10.1016/j.ultsonch.2004.10.004",
    "10.1016/j.ijpharm.2021.120783",
    "10.1016/j.ultsonch.2012.08.010",
    "10.1016/j.neuint.2020.104875",
    "10.1016/j.ijpharm.2024.124536",
    "10.1016/j.colsurfb.2025.114879",
    "10.1016/j.biopha.2020.110980",
    "10.1016/j.ultsonch.2013.10.021",
    "10.1016/j.foodchem.2025.144697",
    "10.1016/j.ijpharm.2025.125934",
    "10.1016/j.jcis.2024.07.233",
    "10.1016/j.ijbiomac.2015.10.025",
    "10.1016/j.foodres.2025.116091",
    "10.1016/j.jcis.2020.02.066",
    "10.1016/s0264-410x(97)00109-6",
    "10.1016/j.farma.2011.10.005",
    "10.1016/j.ejpb.2010.03.005",
    "10.1016/j.ejpb.2008.01.021",
    "10.1016/j.ultsonch.2019.03.018",
    "10.1016/j.ejps.2022.106229",
    "10.1016/j.ejps.2021.106058",
    "10.1016/j.jid.2020.04.009",
    "10.1016/j.ijpharm.2009.07.025",
    "10.1016/j.xphs.2025.104053",
    "10.1016/j.ejps.2022.106159",
    "10.1016/j.biopha.2019.108622",
    "10.1016/j.ijpharm.2024.124267",
    "10.1016/j.ejps.2025.107372",
    "10.1016/j.ultsonch.2016.10.020",
    "10.1016/j.ultsonch.2016.05.037",
    "10.1016/j.ijpharm.2023.122622",
    "10.1016/j.chemphyslip.2021.105113",
    "10.1016/j.ejpb.2018.02.013",
    "10.1016/j.ijpharm.2025.126284",
    "10.1016/j.ijpharm.2019.119003",
    "10.1016/j.ultsonch.2019.104832",
    "10.1016/j.ejps.2024.106912",
    "10.1016/j.ejps.2022.106263",
    "10.1016/j.colsurfb.2025.114733",
    "10.1016/j.foodchem.2024.141006",
    "10.1016/j.ijpharm.2025.125823",
    "10.1016/j.fm.2016.10.031",
    "10.1016/j.ultsonch.2017.05.021",
    "10.1016/j.colsurfb.2011.05.019",
    "10.1016/j.ejps.2021.105778",
    "10.1016/j.ijpharm.2023.123614",
    "10.1016/s0015-0282(00)01636-8",
    "10.1016/j.ijpharm.2018.02.020",
    "10.1016/j.ultsonch.2015.09.015",
    "10.1016/S0034-7094(10)70059-3",
    "10.1016/j.ejpb.2024.114453",
    "10.1016/j.ejps.2025.107015",
    "10.1016/j.jconrel.2014.10.007",
    "10.1016/j.ejps.2025.107077",
    "10.1016/j.ijpharm.2025.125886",
    "10.1016/j.ijpharm.2022.121853",
    "10.1016/j.ijpharm.2012.02.025",
    "10.1016/j.jconrel.2025.113932",
    "10.1016/j.ijpharm.2025.125711",
    "10.1016/j.jconrel.2025.113677",
    "10.1016/j.exppara.2021.108142",
    "10.1016/j.ejps.2018.10.007",
    "10.1016/j.ultsonch.2016.01.035",
    "10.1016/j.ijpharm.2005.10.050",
    "10.1016/j.ejphar.2025.177992",
    "10.1016/j.biopha.2021.111368",
    "10.1016/j.ijpharm.2019.118997",
    "10.1016/j.ijpharm.2009.04.024",
    "10.1016/j.ejps.2025.107061",
    "10.1016/j.ejps.2025.107364",
    "10.1016/j.ijpharm.2023.123473",
    "10.1016/j.ijpharm.2025.126354",
    "10.1016/j.ijpharm.2017.09.072",
    "10.1016/j.ijpharm.2017.02.006",
    "10.1016/j.ejpb.2022.02.010",
    "10.1016/j.actatropica.2020.105595",
    "10.1016/j.ejps.2025.107318",
    "10.1016/j.tox.2015.01.017"
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