import os
import requests
import time
from elsapy.elsclient import ElsClient
from elsapy.elsdoc import FullDoc
from ..config import Config
from ..utils import setup_logger, sanitize_filename

logger = setup_logger("Elsevier", Config.LOG_FILE)

class ElsevierScraper:
    def __init__(self, api_key=Config.ELSEVIER_API_KEY, output_dir=Config.OUTPUT_DIR):
        self.api_key = api_key
        self.output_dir = output_dir
        
        # Initialize Client
        # Note: We rely on IP authentication (VPN), so we only pass the API Key
        if self.api_key:
            self.client = ElsClient(self.api_key)
            logger.info(" Elsevier Client initialized (IP Auth mode)")
        else:
            logger.error(" Elsevier API Key missing in Config")
            self.client = None

        os.makedirs(self.output_dir, exist_ok=True)

    def download_pdf(self, doi):
        """Attempts to download the PDF for a specific DOI."""
        if not self.client:
            logger.warning("Skipping download: Client not initialized.")
            return False

        filename = sanitize_filename(doi)
        output_path = os.path.join(self.output_dir, filename)

        # Skip if already exists
        if os.path.exists(output_path):
            logger.info(f"Skipping {doi} - File exists.")
            return True

        # 1. Get Metadata to confirm access/URL
        doc = FullDoc(doi=doi)
        if not doc.read(self.client):
            logger.warning(f"Metadata read failed for {doi}")
            return False

        logger.info(f"Metadata found: {doc.title}")

        # 2. Construct Download URL
        # The API endpoint for PDF retrieval
        pdf_url = f"https://api.elsevier.com/content/article/doi/{doi}"
        
        headers = {
            "X-ELS-APIKey": self.api_key,
            "Accept": "application/pdf"
        }

        logger.info(f"Requesting PDF for {doi}...")
        try:
            r = requests.get(pdf_url, headers=headers, stream=True)
            
            if r.status_code == 200:
                with open(output_path, 'wb') as f:
                    for chunk in r.iter_content(chunk_size=1024):
                        f.write(chunk)
                logger.info(f"✅ Success! Saved to: {filename}")
                return True
            
            elif r.status_code == 401:
                logger.error(f" 401 Unauthorized for {doi}. Check VPN or Subscription.")
            else:
                logger.error(f" Failed {doi}. Status: {r.status_code}")
                
        except Exception as e:
            logger.error(f"Network error for {doi}: {e}")
            
        return False

    def batch_process(self, doi_list):
        """Processes a list of DOIs sequentially with delays."""
        success_count = 0
        for doi in doi_list:
            if self.download_pdf(doi):
                success_count += 1
            # Be polite to the API
            time.sleep(1)
        
        logger.info(f"Elsevier Batch Complete. Success: {success_count}/{len(doi_list)}")