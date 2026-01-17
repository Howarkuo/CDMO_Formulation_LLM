import os
import csv
import glob
from .config import Config
from .scrapers.pubmed import PubMedScraper
from .scrapers.elsevier import ElsevierScraper
from .scrapers.unpaywall import UnpaywallScraper
from .scrapers.publisher_map import PublisherMap
from .processing.gemini import GeminiProcessor
from .utils import setup_logger

logger = setup_logger("Pipeline", Config.LOG_FILE)

def run_pipeline():
    # =========================================================================
    # STEP 1: PubMed Scraping (The Foundation)
    # =========================================================================
    logger.info("Step 1: PubMed Scraping")
    pubmed = PubMedScraper()
    
    # NOTE: max_results=5 is set for testing. Change to 1500 for production.
    pmids = pubmed.search_pmids(
        query='((Drug Formulation) AND (dosage forms[MeSH Terms]) '
              'NOT "Review"[pt] '
              'NOT "Clinical trial"[pt]) '
              'AND "free full text"[filter] '
              'AND 2000/01/01:2025/12/31[dp]',
        max_results=5
    )
    pubmed.download_batch(pmids)

    # =========================================================================
    # STEP 2: Elsevier Scraping (Targeted via PublisherMap)
    # =========================================================================
    logger.info("Step 2: Elsevier Scraping")
    
    elsevier_scraper = ElsevierScraper()
    
    # 1. Read the Metadata CSV created by PubMedScraper
    metadata_path = os.path.join(Config.OUTPUT_DIR, "pubmed_metadata.csv")
    
    if os.path.exists(metadata_path):
        elsevier_dois = []
        
        with open(metadata_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                doi = row.get("DOI")
                filename = row.get("Filename")
                
                # Construct full path to check if file exists
                # Note: Filename might be "Not Downloaded" or actual file name
                if filename and filename != "Not Downloaded":
                    full_path = os.path.join(Config.OUTPUT_DIR, filename)
                else:
                    # If PubMed didn't even get a filename, we construct one safely or skip
                    continue

                # Condition: File is MISSING locally AND we have a valid DOI
                if not os.path.exists(full_path) and doi and doi != "None":
                    
                    # *** PRE-SELECTION LOGIC ***
                    if PublisherMap.is_elsevier(doi):
                        logger.info(f" -> Identified Elsevier DOI: {doi}. Queueing for API.")
                        elsevier_dois.append(doi)
                    else:
                        publisher = PublisherMap.identify_publisher(doi)
                        logger.info(f" -> Skipping {doi} (Publisher: {publisher}). Not for Elsevier API.")

        # 2. Batch Download only the confirmed Elsevier DOIs
        if elsevier_dois:
            logger.info("=" * 40)
            logger.info(f" ELSEVIER REPORT: Found {len(elsevier_dois)} Elsevier papers.")
            elsevier_scraper.batch_process(elsevier_dois)
        else:
            logger.info("No missing Elsevier DOIs found.")
            
    else:
        logger.warning("No metadata file found from Step 1. Skipping Elsevier step.")

    # =========================================================================
    # STEP 3: Unpaywall Scraping (The Fallback)
    # =========================================================================
    logger.info("Step 3: Unpaywall Scraping")
    
    # Initialize Unpaywall Scraper (Assuming implementation exists)
    unpaywall_scraper = UnpaywallScraper()
    
    # Logic: If file is STILL missing after PubMed and Elsevier, try Unpaywall
    # (You can implement similar CSV reading logic here if needed)
    # unpaywall_scraper.process_missing(metadata_path) 

    # =========================================================================
    # STEP 4: QA Generation (Gemini)
    # =========================================================================
    logger.info("Step 4: QA Generation")
    processor = GeminiProcessor()
    
    # Find all PDFs in the output directory
    pdfs = glob.glob(os.path.join(Config.OUTPUT_DIR, "*.pdf"))
    
    if not pdfs:
        logger.warning("No PDFs found to process!")
    else:
        logger.info(f"Found {len(pdfs)} PDFs to analyze.")
        for pdf in pdfs:
            processor.process_pdf(pdf)

    # =========================================================================
    # FINISH: Open Results Folder
    # =========================================================================
    logger.info("Pipeline Complete!")
    
    if os.name == 'nt':  # Windows only
        try:
            os.startfile(Config.RESULTS_DIR)
            logger.info(f"Opened results folder: {Config.RESULTS_DIR}")
        except Exception:
            pass

if __name__ == "__main__":
    run_pipeline()
# from .config import Config
# from .scrapers.pubmed import PubMedScraper
# from .scrapers.elsevier import ElsevierScraper
# from .scrapers.publisher_map import PublisherMap  # <--- Import this
# from .utils import setup_logger
# import os
# import csv

# logger = setup_logger("Pipeline", Config.LOG_FILE)

# def run_pipeline():
#     # ... [Step 1: PubMed happens here] ...
    
#     # === Step 2: Elsevier Scraping (Targeted) ===
#     logger.info("Step 2: Elsevier Scraping")
    
#     elsevier_scraper = ElsevierScraper()
    
#     # 1. Read the Metadata CSV created by PubMedScraper to see what we found
#     metadata_path = os.path.join(Config.OUTPUT_DIR, "pubmed_metadata.csv")
#     if not os.path.exists(metadata_path):
#         logger.warning("No metadata file found. Skipping Step 2.")
#         return

#     # 2. Identify DOIs that need downloading
#     dois_to_download = []
    
#     with open(metadata_path, 'r', encoding='utf-8') as f:
#         reader = csv.DictReader(f)
#         for row in reader:
#             doi = row.get("DOI")
#             filename = row.get("Filename")
            
#             # Check if we missed the file in Step 1 (PubMed)
#             full_path = os.path.join(Config.OUTPUT_DIR, filename)
            
#             # Condition: File doesn't exist locally AND we have a valid DOI
#             if not os.path.exists(full_path) and doi:
                
#                 # *** THE PRE-SELECTION LOGIC ***
#                 if PublisherMap.is_elsevier(doi):
#                     logger.info(f" -> Identified Elsevier DOI: {doi}. Queueing for API.")
#                     dois_to_download.append(doi)
#                 else:
#                     publisher = PublisherMap.identify_publisher(doi)
#                     logger.info(f" -> Skipping {doi} (Publisher: {publisher}). Not for Elsevier API.")

#     # 3. Batch Download only the confirmed Elsevier DOIs
#     if dois_to_download:
#         elsevier_scraper.batch_process(dois_to_download)
#     else:
#         logger.info("No Elsevier DOIs found to download.")

#     # ... [Step 3: Unpaywall happens here for the remaining ones] ...
# # from .config import Config
# # from .scrapers.pubmed import PubMedScraper
# # from .scrapers.elsevier import ElsevierScraper
# # from .scrapers.unpaywall import UnpaywallScraper
# # from .processing.gemini import GeminiProcessor
# # from .utils import setup_logger
# # import os

# # logger = setup_logger("Pipeline", Config.LOG_FILE)

# # def run_pipeline():
# #     # 1. Query Generation & PubMed
# #     logger.info("Step 1: PubMed Scraping")
# #     pubmed = PubMedScraper()
# #     pmids = pubmed.search_pmids('((Drug Formulation) AND (dosage forms[MeSH Terms]) '
# #     'NOT "Review"[pt] '
# #     'NOT "Clinical trial"[pt]) '
# #     'AND "free full text"[filter] '
# #     'AND 2000/01/01:2025/12/31[dp]')
# #     pubmed.download_batch(pmids)

# #     # 2. Identify Missing DOIs -> Elsevier
# #     # (Logic to check output dir vs list of expected DOIs)
# #     logger.info("Step 2: Elsevier Scraping")
# #     # ... call ElsevierScraper ...

# #     # 3. Fallback -> Unpaywall/VPN
# #     logger.info("Step 3: Unpaywall Scraping")
# #     # ... call UnpaywallScraper ...

# #     # 4. QA Generation
# #     logger.info("Step 4: QA Generation")
# #     processor = GeminiProcessor()
    
# #     import glob
# #     pdfs = glob.glob(os.path.join(Config.OUTPUT_DIR, "*.pdf"))
# #     for pdf in pdfs:
# #         processor.process_pdf(pdf)

# # if __name__ == "__main__":
# #     run_pipeline()