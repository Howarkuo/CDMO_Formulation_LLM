# CDMO_Formulation_LLM

## Part1: Chemistry, Manufacturing, and Controls Knowledge Extracted Q-A Pairs, Serve as the foundation of next step Supervised Fine-Tuning of Vernus-ReAltX Meta-Llama-3.1 model.

## 🚀 Key Features
* **Standardized APIs**: Streamlines model switching and comparative analyses.
* **CMC & Formulation Analysis**: Automated, deep-reasoning workflows for pharmaceutical risk assessment and formulation optimization.
* **Gemini 2.0 Integration**: Leverages the latest multimodal models (Flash & Flash-Thinking) for direct PDF analysis without external OCR tools.

---

## 📸 Workflows

### Pharmaceutical Formulation & CMC Risk Analysis
The following pipeline illustrates the workflow for processing academic PDFs to extract formulation parameters and assess manufacturing risks.

![PMC QA + PDF Scrape Workflow](https://github.com/Howarkuo/BioLLM/blob/main/Fig/PMC_QA%2BPDF_scrape.png?raw=true)

---

## 📦 Packages Required

To run the CMC analysis and scraping scripts, you must install the Google GenAI SDK and Pydantic.

**Install via pip:**
```bash
pip install google-genai pydantic
