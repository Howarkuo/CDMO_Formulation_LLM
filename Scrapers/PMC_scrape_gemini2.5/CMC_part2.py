import requests
from bs4 import BeautifulSoup
import json
import time
import os
from pydantic import BaseModel, Field
from typing import List
from google import genai
from google.genai import types

# --- CONFIGURATION ---
API_KEY_PATH = r"C:\Users\howar\Desktop\api_key.txt"
WORK_DIR = r"C:\Users\howar\Desktop\biollm\PMC_scrape_gemini2.5"
MODEL_NAME = "gemini-2.5-flash"
NCBI_EMAIL = "howard.kuo@vernus.ai.com"  # REQUIRED by PubMed
USER_AGENT = "MyFormulationMiner/1.0"

# Target Query
# Please read the guidance of Phrase Searching in PubMed https://www.nlm.nih.gov/oet/ed/pubmed/phrase/index.html
# latest Query
PUBMED_QUERY = '((Drug Formulation) AND (Emulsion)) AND (dosage forms[MeSH Terms]) NOT Review[Pt]  NOT "Clinical trial"[Pt] '
# Problem of the  query- ffrft[Filter]: free on publisher websites but no pmcid (which the API cannot download).
# PUBMED_QUERY = '((Drug Formulation) AND (Emulsion)) AND (dosage forms[MeSH Terms]) NOT Review[Pt]  NOT "Clinical trial"[Pt]  AND ffrft[Filter]'
# PUBMED_QUERY = '((Drug Formulation) AND (Emulsion)) AND (dosage forms [MeSH Terms]) NOT "Review" [Pt] NOT "Clinical trial"[Pt] AND "open access"[filter]'

# NCBI E-Utils URLs
BASE_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"

# Ensure the working directory exists
os.makedirs(WORK_DIR, exist_ok=True)

# --- PYDANTIC MODELS ---
class QAPair(BaseModel):
    """Structure for a single Q&A entry based on the pharmaceutical formulation requirements."""
    input_paragraph: str = Field(description="Extract the specific verbatim paragraph from the text which refers to the question, answer, and reasoning.")
    question: str = Field(description="The question text. Ensure it is numbered (e.g., '1. What is...').")
    answer_and_reasoning: str = Field(description="The answer must be factual and directly mentioned in the text. Follow this with detailed reasoning.")
    source_pmid: str = Field(description="The Pubmed ID (PMID) of the source article.")

class FormulationAnalysis(BaseModel):
    """Complete analysis output containing a summary and a list of Q&A pairs."""
    brief_summary: str = Field(description="A brief summary focusing on key findings and methods used for improving drug formulation.")
    qa_pairs: List[QAPair] = Field(description="A list of exactly 20 high-quality question and answer pairs using precise pharmaceutical terminology.")

# --- PROMPT TEXT ---
PHARMA_PROMPT_TEXT = """
You are a pharmaceutical CMC (Chemistry, Manufacturing, and Controls) process expert.

**Instruction:** Given the scientific article, provide a **brief summary (max 300 words)** focusing on key findings and methods used for improving drug formulation, and generate **5 most critical risk factor and solution (QA) pairs** as output.

**Output Requirements:**
1.  **Input Paragraph:** Extract the specific verbatim paragraph from the text which refers to the corresponding question, answer, and reasoning. Do not use ellipsis.
2.  **Question (n):** List the top 5 potential risk issues related to tech-transfer or scale-up for the article’s proposed final formulation and manufacturing methods. **Label n = number from 16 to 20.**
3.  **Answer:** Provide a solution for the potential risks and detailed reasoning. Be skeptical but do not hallucinate.
4.  **Source:** Provide the article's Pubmed ID (PMID).

**Questions should focus on, but are not limited to, the following points:**
1.  **Excipient Applicability:** Suitability for scale-up based on commercial availability, FDA approval/pharmacopeia grade, cost, compatibility, stability, and safety.
2.  **Production Feasibility:** The scale-up feasibility and operability of the technical methods used in production.
3.  **QA/QC Feasibility:** The scale-up feasibility of technical methods used for quality analysis (QA and QC).
4.  **Critical Process Parameters (CPPs):** Evaluate which parameters may affect product quality (e.g., stirring speed, time, temperature control, size control, feeding time, pressure, equipment limitations).
"""


# --- HELPERS ---

def load_api_key():
    try:
        with open(API_KEY_PATH, "r") as f:
            return f.read().strip()
    except FileNotFoundError:
        print("Error: API Key file not found.")
        return None

def get_pmcids_from_query(query, max_results=5):
    """Searches PubMed for PMIDs, then maps them to PMCIDs."""
    print(f"🔍 Searching PubMed for: {query}")
    
    # 1. Search PubMed
    # for "retmax": 20, only identified 1 papers with full text available.
    params = {
        "db": "pubmed", "term": query, "retmax": 100, "sort": "relevance", 
        "retmode": "json", "email": NCBI_EMAIL
    }
    r = requests.get(f"{BASE_URL}/esearch.fcgi", params=params)
    r.raise_for_status()
    pmid_list = r.json().get("esearchresult", {}).get("idlist", [])
    
    if not pmid_list: return []

    print(f"   -> Found {len(pmid_list)} PMIDs. Checking for Open Access (PMC) links...")
    
    # 2. Map PMID -> PMCID via ELink
    params_link = {
        "dbfrom": "pubmed", "db": "pmc", "id": ",".join(pmid_list),
        "cmd": "neighbor", "retmode": "json", "email": NCBI_EMAIL
    }
    r = requests.get(f"{BASE_URL}/elink.fcgi", params=params_link)
    r.raise_for_status()
    link_data = r.json()
    
    valid_papers = [] 
    
    # Parse ELink results
    for ls in link_data.get("linksets", []):
        src_pmid = ls.get("ids", [])[0]
        if "linksetdbs" in ls:
            for db_link in ls["linksetdbs"]:
                if db_link["linkname"] == "pubmed_pmc":
                    pmc_id = db_link["links"][0]
                    valid_papers.append({"pmid": src_pmid, "pmcid": f"PMC{pmc_id}"})
                    break
        if len(valid_papers) >= max_results: break
            
    print(f"   -> Identified {len(valid_papers)} papers with full text available.")
    return valid_papers

def fetch_and_save_text(pmcid):
    """Fetches XML, parses it, and saves raw text to disk."""
    params = {
        "db": "pmc", "id": pmcid, "ret  type": "full", "retmode": "xml", "email": NCBI_EMAIL
    }
    try:
        start_time = time.time()
        r = requests.get(f"{BASE_URL}/efetch.fcgi", params=params)
        r.raise_for_status()
        elapsed = time.time() - start_time
        print(f"   -> ⏱️ PubMed API Response: {elapsed:.2f} seconds")
        # Parse the XML to get the "Inside Text"
        # Using 'lxml-xml' is generally faster and more robust than 'xml'
        soup = BeautifulSoup(r.content, "lxml-xml")
        
        # Get Title
        title_tag = soup.find('article-title')
        title = title_tag.get_text() if title_tag else "Unknown Title"
        
        # Get Body Paragraphs
        body = soup.find('body')
        if not body: return None, None


        # Clean text extraction
        paragraphs = [p.get_text(separator=" ", strip=True) for p in body.find_all('p')]
        full_text = f"TITLE: {title}\n\n" + "\n\n".join(paragraphs)
        
        # Save to disk
        filename = f"{pmcid}.txt"
        file_path = os.path.join(WORK_DIR, filename)
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(full_text)
            
        return full_text, file_path
        
    except Exception as e:
        print(f"   -> Error fetching {pmcid}: {e}")
        return None, None
# modify analyze and save result so that I can track the API response time 
def analyze_and_save_result(client, text, pmid, pmcid):
    """Sends text to Gemini and saves the formatted output text file."""
    
    print(f"   -> Sending to Gemini ({len(text)} chars)...")
    
    try:
        start_time = time.time()
        response = client.models.generate_content(
            model=MODEL_NAME,
            contents=[
                PHARMA_PROMPT_TEXT, 
                f"Source Article (PMID: {pmid}):\n{text[:60000]}" 
            ],
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=FormulationAnalysis,
                temperature=0.2
            )
        )
        end_time = time.time()
        elapsed_time = end_time - start_time
        print(f"   -> ⏱️ Gemini Response Time: {elapsed_time:.2f} seconds")
        data = json.loads(response.text)
        
        # Save the result to .txt file
        output_filename = f"{pmcid}_gemini2.5_qapairs.txt"
        output_path = os.path.join(WORK_DIR, output_filename)
        
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(f"=== ANALYSIS FOR {pmcid} (PMID: {pmid}) ===\n\n")
            f.write(f"SUMMARY:\n{data.get('brief_summary')}\n")
            f.write("\n" + "="*50 + "\n")
            f.write("QUESTION & ANSWER PAIRS (20)\n")
            f.write("="*50 + "\n\n")
            
            for i, item in enumerate(data.get('qa_pairs', []), 1):
                f.write(f"Pair #{i}\n")
                f.write(f"Q: {item['question']}\n")
                f.write(f"A & Reasoning: {item['answer_and_reasoning']}\n")
                f.write(f"Source Paragraph: {item['input_paragraph']}\n")
                f.write(f"PMID: {item['source_pmid']}\n")
                f.write("-" * 30 + "\n")
                
        print(f"   -> ✅ Saved Analysis: {output_filename}")
        
    except Exception as e:
        print(f"   -> ❌ Gemini Analysis Error: {e}")

# --- MAIN EXECUTION ---
if __name__ == "__main__":
    
    # 1. Setup
    api_key = load_api_key()
    if not api_key: exit()
    
    client = genai.Client(api_key=api_key)
    
    # 2. Get Papers (Dynamic Search)
    papers = get_pmcids_from_query(PUBMED_QUERY, max_results=5)
    
    # 3. Process Loop
    print(f"\nProcessing {len(papers)} papers inside: {WORK_DIR}\n")
    
    for paper in papers:
        pmcid = paper['pmcid']
        pmid = paper['pmid']
        
        print(f"Processing {pmcid} (PMID: {pmid})...")
        
        # A. Fetch & Save Raw Text
        text, txt_path = fetch_and_save_text(pmcid)
        
        if not text or len(text) < 1000:
            print("   -> Text too short or missing. Skipping.")
            continue
            
        print(f"   -> Raw text scraped to: {os.path.basename(txt_path)}")
        time.sleep(1) # Be polite to NCBI
        
        # B. Analyze & Save Q&A
        analyze_and_save_result(client, text, pmid, pmcid)
        
        time.sleep(2) # Rate limit buffer

    print(f"\nDone. All files are in {WORK_DIR}")