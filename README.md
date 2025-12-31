# CDMO_Formulation_LLM

## Part1: Chemistry, Manufacturing, and Controls Knowledge Extracted Q-A Pairs
Serve as the foundation of next step Supervised Fine-Tuning of Vernus-ReAltX Meta-Llama-3.1 model.

BioLLM employs a **Hybrid Reasoning Architecture** that orchestrates multiple Gemini 2.0 models to mirror the workflow of a pharmaceutical development team. Instead of a generic "summarize this" approach, our pipeline utilizes specialized prompt engineering techniques:

### 1. Dual-Model Cognitive Split
We decouple data extraction from complex reasoning to maximize accuracy and efficiency:
* **The "Broad Scanner" (Gemini 2.0 Flash)**: Used for *Part 1 (Formulation)*. It is optimized to scan the entire document and extract a high volume of factual data (20 distinct data points) regarding experimental values, excipient ratios, and physical properties.
* **The "Deep Reasoner" (Gemini 2.0 Flash-Thinking)**: Used for *Part 2 (CMC Risks)*. This model employs "Chain-of-Thought" capabilities to simulate a skeptical CMC Engineer. It looks beyond the text to infer potential failure points in scale-up and tech-transfer that may not be explicitly stated in the paper.

### 2. Evidence-Anchored Verification
To eliminate hallucinations common in scientific LLM applications, our prompts enforce an **Evidence-First Constraint**.
* Every generated Q&A pair requires a `input_paragraph` field.
* The model must extract the **verbatim text** from the source PDF that supports its answer.
* This creates a built-in "citation layer" allowing researchers to instantly verify the model's output against the original document.

### 3. Role-Based Persona Switching
The pipeline dynamically switches expert personas to analyze the same text from different angles:
* **Persona A**: *Pharmaceutical Formulation Expert* (Focus: Composition, Ratios, API properties).
* **Persona B**: *CMC Process Expert* (Focus: Feasibility, Operability, Stability, QA/QC).

### 4. Structured Schema Enforcement
Unlike standard chat-based interactions, this tool uses `Pydantic` to enforce strict output schemas. This ensures that the unstructured text of a PDF is converted into a deterministic, queryable JSON database with standardized fields (`source_pmid`, `answer_and_reasoning`, `brief_summary`).

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
