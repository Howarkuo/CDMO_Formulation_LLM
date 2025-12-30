# BioLLM: A Standardized Framework for Integrating and Benchmarking Single-Cell Foundation Models

**BioLLM** is a standardized framework designed to facilitate the integration and application of single-cell Foundation Models (scFMs) in single-cell RNA sequencing analyses. It provides a cohesive interface, enabling researchers to access various scFMs regardless of architectural differences or coding standards.

## 🚀 Key Features
* **Standardized APIs**: Streamlines model switching and comparative analyses.
* **Comprehensive Documentation**: Incorporates best practices for consistent model evaluation.
* **PMC QA & PDF Scraping**: Automated workflows for retrieving and analyzing literature from PubMed Central.

---

## 📸 Workflows

### PMC QA and PDF Scraping Pipeline
The following figure illustrates the workflow for scraping PDFs from PMC and performing Question Answering (QA).

![PMC QA + PDF Scrape Workflow](https://github.com/Howarkuo/BioLLM/blob/main/Fig/PMC_QA%2BPDF_scrape.png?raw=true)

---

## 🛠️ Installation

### From Source
```bash
git clone [https://github.com/Howarkuo/BioLLM.git](https://github.com/Howarkuo/BioLLM.git)
cd BioLLM
python ./setup.py
