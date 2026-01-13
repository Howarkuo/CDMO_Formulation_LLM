from .config import Config
from .scrapers.pubmed import PubMedScraper
from .scrapers.elsevier import ElsevierScraper
from .scrapers.unpaywall import UnpaywallScraper
from .processing.gemini import GeminiProcessor
from .utils import setup_logger

logger = setup_logger("Pipeline", Config.LOG_FILE)

def run_pipeline():
    # 1. Query Generation & PubMed
    logger.info("Step 1: PubMed Scraping")
    pubmed = PubMedScraper()
    pmids = pubmed.search_pmids("((Drug Formulation) AND (Emulsion))")
    pubmed.download_batch(pmids)

    # 2. Identify Missing DOIs -> Elsevier
    # (Logic to check output dir vs list of expected DOIs)
    logger.info("Step 2: Elsevier Scraping")
    # ... call ElsevierScraper ...

    # 3. Fallback -> Unpaywall/VPN
    logger.info("Step 3: Unpaywall Scraping")
    # ... call UnpaywallScraper ...

    # 4. QA Generation
    logger.info("Step 4: QA Generation")
    processor = GeminiProcessor()
    
    import glob
    pdfs = glob.glob(os.path.join(Config.OUTPUT_DIR, "*.pdf"))
    for pdf in pdfs:
        processor.process_pdf(pdf)

if __name__ == "__main__":
    run_pipeline()