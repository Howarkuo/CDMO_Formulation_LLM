import os
import requests
import math
import time
import shutil
import tarfile
import tempfile
import urllib.request
import xml.etree.ElementTree as ET
from ..config import Config
from ..utils import setup_logger, sanitize_filename

logger = setup_logger("PubMed", Config.LOG_FILE)

class PubMedScraper:
    BATCH_SIZE = 100

    def __init__(self, output_dir=Config.OUTPUT_DIR, email=Config.NCBI_EMAIL):
        self.output_dir = output_dir
        self.email = email
        os.makedirs(self.output_dir, exist_ok=True)
        
        if not self.email:
            logger.warning("NCBI Email not set in Config! PubMed requests may be throttled.")

    def search_pmids(self, query, max_results=1500):
        """Searches PubMed and returns a list of PMIDs."""
        logger.info(f"🔍 Searching: {query[:50]}...")
        url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
        params = {
            "db": "pubmed", 
            "term": query, 
            "retmode": "json", 
            "retmax": max_results, 
            "email": self.email, 
            "sort": "relevance"
        }
        
        try:
            r = requests.get(url, params=params)
            r.raise_for_status()
            ids = r.json().get("esearchresult", {}).get("idlist", [])
            logger.info(f"📊 Found {len(ids)} PMIDs matching query.")
            return ids
        except Exception as e:
            logger.error(f"Search failed: {e}")
            return []

    def download_batch(self, pmids):
        """
        Takes a list of PMIDs, converts them to PMCIDs in batches, 
        and downloads the available PDFs.
        """
        total_pmids = len(pmids)
        if total_pmids == 0:
            logger.warning("No PMIDs provided to download.")
            return

        num_batches = math.ceil(total_pmids / self.BATCH_SIZE)
        logger.info("-" * 60)
        logger.info(f"🚀 Starting Batch Process: {total_pmids} articles in {num_batches} batches.")
        logger.info("-" * 60)

        success_total = 0

        for i in range(num_batches):
            start_idx = i * self.BATCH_SIZE
            end_idx = start_idx + self.BATCH_SIZE
            batch_pmids = pmids[start_idx:end_idx]

            logger.info(f"📦 Batch {i+1}/{num_batches} (Items {start_idx+1}-{min(end_idx, total_pmids)})")

            # 1. Convert PMID -> PMCID
            pmcid_map = self._get_pmcids(batch_pmids)
            logger.info(f"   -> Found {len(pmcid_map)} PMCIDs in this batch.")

            if not pmcid_map:
                time.sleep(1)
                continue

            # 2. Process Downloads
            batch_success = 0
            for pmid, pmc_id in pmcid_map.items():
                # Define Filename
                target_file = os.path.join(self.output_dir, f"{pmc_id}.pdf")
                
                # Skip if exists
                if os.path.exists(target_file):
                    continue

                # Get Links
                pdf_url, tgz_url = self._get_download_link(pmc_id)
                downloaded = False

                # Strategy A: Direct PDF
                if pdf_url and self._smart_download(pdf_url, target_file):
                    logger.info(f"      ✅ Saved PDF: {pmc_id}.pdf")
                    downloaded = True
                
                # Strategy B: Tarball Extraction
                elif tgz_url:
                    tgz_local = os.path.join(self.output_dir, f"{pmc_id}.tar.gz")
                    if self._smart_download(tgz_url, tgz_local):
                        if self._process_tar_gz(tgz_local, target_file):
                            logger.info(f"      ✅ Extracted PDF: {pmc_id}.pdf")
                            downloaded = True
                        # Cleanup .tar.gz
                        if os.path.exists(tgz_local): 
                            os.remove(tgz_local)
                
                if downloaded:
                    batch_success += 1
                    success_total += 1
                
                # Politeness sleep
                time.sleep(0.2)

            logger.info(f"   -> Batch Complete. Downloaded: {batch_success}")
            time.sleep(1)

        logger.info("-" * 60)
        logger.info(f"🎉 Job Complete. Total Downloaded: {success_total}/{total_pmids}")

    # --- INTERNAL HELPER METHODS ---

    def _get_pmcids(self, pmid_list):
        """Converts a list of PMIDs to PMCIDs using E-Utilities."""
        if not pmid_list: return {}
        
        url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi"
        pmids_str = ",".join(pmid_list)
        params = {
            "db": "pubmed", 
            "id": pmids_str, 
            "retmode": "json", 
            "email": self.email
        }
        
        mapping = {}
        try:
            r = requests.get(url, params=params)
            r.raise_for_status()
            data = r.json()
            result = data.get("result", {})
            uids = result.get("uids", [])
            
            for pmid in uids:
                item = result.get(pmid, {})
                for aid in item.get("articleids", []):
                    if aid.get("idtype") == "pmc":
                        mapping[pmid] = aid.get("value")
                        break
        except Exception as e:
            logger.error(f"   ⚠️ Batch ID conversion failed: {e}")
        
        return mapping

    def _get_download_link(self, pmc_id):
        """Fetches PDF or TGZ download link from PMC OA service."""
        oa_url = f"https://www.ncbi.nlm.nih.gov/pmc/utils/oa/oa.fcgi?id={pmc_id}"
        try:
            r = requests.get(oa_url)
            # Parse XML
            root = ET.fromstring(r.content)
            pdf_link, tgz_link = None, None
            
            for link in root.findall(".//link"):
                fmt = link.get("format")
                href = link.get("href")
                if fmt == "pdf": 
                    pdf_link = href
                elif fmt == "tgz": 
                    tgz_link = href
            return pdf_link, tgz_link
        except Exception:
            return None, None

    def _smart_download(self, url, dest_path):
        """Handles both HTTP and FTP downloads."""
        try:
            if url.startswith("ftp://"):
                with urllib.request.urlopen(url) as response, open(dest_path, 'wb') as out_file:
                    shutil.copyfileobj(response, out_file)
            else:
                r = requests.get(url, stream=True)
                r.raise_for_status()
                with open(dest_path, 'wb') as f:
                    for chunk in r.iter_content(chunk_size=8192):
                        f.write(chunk)
            return True
        except Exception as e:
            logger.warning(f"      ❌ Download Error: {e}")
            return False

    def _process_tar_gz(self, tgz_path, final_pdf_path):
        """Extracts the largest PDF from a tar.gz archive."""
        try:
            with tempfile.TemporaryDirectory() as temp_dir:
                with tarfile.open(tgz_path, "r:gz") as tar:
                    tar.extractall(path=temp_dir)
                
                # Find all PDFs
                pdfs = []
                for root, dirs, files in os.walk(temp_dir):
                    for file in files:
                        if file.endswith(".pdf"):
                            pdfs.append(os.path.join(root, file))
                
                if not pdfs: 
                    return False
                
                # Assume the largest PDF is the main article (avoids supplementary tables)
                target_pdf = max(pdfs, key=os.path.getsize)
                shutil.move(target_pdf, final_pdf_path)
                return True
        except Exception:
            return False