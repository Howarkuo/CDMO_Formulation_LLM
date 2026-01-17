import os
from dotenv import load_dotenv

load_dotenv()  # Load variables from .env file

class Config:
    # API Keys
    NCBI_EMAIL = os.getenv("NCBI_EMAIL", "email@example.com")
    ELSEVIER_API_KEY = os.getenv("ELSEVIER_API_KEY")
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
    UNPAYWALL_EMAIL = os.getenv("UNPAYWALL_EMAIL")
    
    # Paths
    BASE_DIR = os.getcwd()
    OUTPUT_DIR = os.path.join(BASE_DIR, "data", "pdfs")
    QA_OUTPUT_DIR = os.path.join(BASE_DIR, "data", "qa_results")
    LOG_FILE = os.path.join(BASE_DIR, "pipeline.log")
    RESULTS_DIR = os.path.join(BASE_DIR, "data", "results")

    # Models
    MODEL_FAST = "gemini-2.5-flash"
    MODEL_REASONING = "gemini-2.5-flash"