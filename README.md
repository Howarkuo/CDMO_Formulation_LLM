```
pharma_scraper/
│
├── pyproject.toml           # Dependency management
├── README.md
├── .env                     # API Keys (GitIgnore this!)
│
└── src/
    └── pharma_scraper/
        ├── __init__.py
        ├── config.py        # Centralized paths and API keys
        ├── utils.py         # Logging, filename sanitization
        │
        ├── scrapers/        # Modules for downloading data
        │   ├── __init__.py
        │   ├── pubmed.py    # Your PMC/PubMed logic
        │   ├── elsevier.py  # Your ElsClient logic
        │   ├── unpaywall.py # Your curl_cffi/VPN logic
        │   └── publisher_map.py
        │
        └── processing/      # Modules for LLM analysis
            ├── __init__.py
            ├── schemas.py   # Pydantic models (Part1/Part2) shared file
            ├── prompts.py   # Prompts stored as text/variables
            └── gemini.py    # Google GenAI logic (PDF & Txt)
        │
        └── pipeline.py      # The main orchestrator script
```
