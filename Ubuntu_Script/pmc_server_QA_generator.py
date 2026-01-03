#!/usr/bin/env python3
import os
import glob
import json
import time
from pydantic import BaseModel, Field
from typing import List
from google import genai
from google.genai import types

# ================= CONFIGURATION =================
# [SERVER SETUP] Relative paths for Linux compatibility
KEY_PATH = "api_key.txt"
INPUT_PDF_DIR = "downloaded_pdfs"
OUTPUT_DIR = "QA_Results_CMC"

# [MODEL SETUP]
# Part 1: Fast extraction (Standard Flash)
MODEL_PART1 = "gemini-2.5-flash" 
# Part 2: Deep reasoning (The "Gemini 3" equivalent for complex logic)
MODEL_PART2 = "gemini-2.5-flash"

# ================= DATA MODELS =================

# --- Part 1: General Formulation Models ---
class QAPair_Part1(BaseModel):
    """Structure for a single Q&A entry based on the pharmaceutical formulation requirements."""
    
    input_paragraph: str = Field(
        description="Extract the specific verbatim paragraph from the text which refers to the question, answer, and reasoning."
    )
    question: str = Field( 
        description="The question text. Ensure it is numbered (e.g., '1. What is...')."
    )
    answer_and_reasoning: str = Field(
        description="The answer must be factual and directly mentioned in the text. Follow this with detailed reasoning (either from text or based on chemical/physical/thermodynamic properties of API/excipients)."
    )
    source_pmid: str = Field(
        description="The Pubmed ID (PMID) of the source article. If not explicitly found, state 'Not Available'."
    )

class Analysis_Part1(BaseModel):
    """Complete analysis output containing a summary and a list of Q&A pairs."""
      
    brief_summary: str = Field(
        description="A brief summary focusing on key findings and methods used for improving drug formulation."
    )
    qa_pairs: List[QAPair_Part1] = Field(
        description="A list of exactly 20 high-quality question and answer pairs using precise pharmaceutical terminology."
    )

# --- Part 2: CMC Risk Models ---
class QAPair_Part2(BaseModel):
    """Structure for a single Risk & Solution entry based on CMC and scale-up analysis."""
    
    input_paragraph: str = Field(
        description="Extract the specific verbatim paragraph from the text which refers to the identified risk, answer, and reasoning. Do not use ellipsis."
    )
    question: str = Field( 
        description="The risk-focused question. It must be numbered 16 through 20 (e.g., '16. What is the risk associated with...'). Focus on tech-transfer or scale-up issues."
    )
    answer_and_reasoning: str = Field(
        description="Provide a solution for the potential risk with detailed reasoning. Be skeptical but do not hallucinate. Discuss feasibility, operability, or stability."
    )
    source_pmid: str = Field(
        description="The Pubmed ID (PMID) of the source article. If not explicitly found, state 'Not Available'."
    )

class Analysis_Part2(BaseModel):
    """Complete analysis output containing a summary and a list of Risk/Solution pairs."""
      
    brief_summary: str = Field(
        description="A brief summary (max 300 words) focusing on key findings and methods used for improving drug formulation."
    )
    qa_pairs: List[QAPair_Part2] = Field(
        description="A list of exactly 5 critical risk factor and solution (QA) pairs labeled 16 to 20."
    )

# ================= PROMPTS =================

PROMPT_PART1 = """
You are a pharmaceutical formulation expert.

**Instruction:** Given the scientific article, provide a **brief summary** focusing on key findings and methods used for improving drug formulation and also generate **20 high quality question and answer (QA) pairs** as output. Use precise, pharmaceutical terminology.

**Questions should focus on but not be limited to the following points. Avoid redundant questions.**
1) Key finding and conclusion from articles including experimental values.
2) Defining subproblems and basic property of APIs.
3) Key methodology use in the article to improve the subproblems.
4) Best composition or ratio of particular excipients used in formulation.
5) Key measurable parameters improvements before and after specific formulation.
6) Negative or failure example tested in the article that does not improve the subproblem or even lead to worse outcome and any trade-offs (such as safety, stability, cost, or manufacturing...etc).
7) Future perspective or alternative methods should be tested and any concern in this formulation.
8) Any potential issues in scale-up manufacturing process for such formulation, especially in the method section.
"""

PROMPT_PART2 = """
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

# ================= HELPER FUNCTIONS =================

def setup_client():
    try:
        if not os.path.exists(KEY_PATH):
            print(f"❌ Error: {KEY_PATH} not found. Please upload it.")
            return None
        with open(KEY_PATH, "r") as f:
            api_key = f.read().strip()
        return genai.Client(api_key=api_key)
    except Exception as e:
        print(f"❌ Error loading API key: {e}")
        return None

def save_text_file(data, output_path, mode="Part1", model_used="Unknown"):
    try:
        with open(output_path, "w", encoding="utf-8") as f:
            if mode == "Part1":
                header = "=== PHARMACEUTICAL FORMULATION ANALYSIS (Part 1) ==="
            else:
                header = "=== CMC & SCALE-UP RISK ANALYSIS (Part 2) ==="
            
            f.write(f"{header}\n")
            f.write(f"Model Used: {model_used}\n\n")
            f.write(f"SUMMARY:\n{data.get('brief_summary')}\n")
            f.write("\n" + "="*50 + "\n")
            f.write("Q&A PAIRS\n")
            f.write("="*50 + "\n\n")
            
            for item in data.get('qa_pairs', []):
                f.write(f"Q: {item['question']}\n")
                f.write(f"A: {item['answer_and_reasoning']}\n")
                f.write(f"Source: {item['input_paragraph']}\n")
                f.write(f"PMID: {item['source_pmid']}\n")
                f.write("-" * 30 + "\n")
        print(f"   -> Saved ({mode}): {os.path.basename(output_path)}")
    except Exception as e:
        print(f"   ❌ Error saving file: {e}")

def process_single_pdf(client, pdf_path):
    filename = os.path.basename(pdf_path)
    base_name = os.path.splitext(filename)[0]
    print(f"\n📄 Processing: {filename}")

    try:
        # 1. Upload File (Shared)
        uploaded_file = client.files.upload(file=pdf_path)
        print("   -> File uploaded successfully.")

        # --- PART 1: General (Flash Model) ---
        print(f"   -> Generating Part 1 (Model: {MODEL_PART1})...")
        try:
            res1 = client.models.generate_content(
                model=MODEL_PART1,
                contents=[uploaded_file, PROMPT_PART1],
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                    response_schema=Analysis_Part1,
                    temperature=0.2
                )
            )
            if res1.text:
                data1 = json.loads(res1.text)
                out1 = os.path.join(OUTPUT_DIR, f"{base_name}_Part1.txt")
                save_text_file(data1, out1, mode="Part1", model_used=MODEL_PART1)
        except Exception as e:
            print(f"   ❌ Part 1 Failed: {e}")

        # --- PART 2: CMC Risk (Thinking Model) ---
        print(f"   -> Generating Part 2 (Model: {MODEL_PART2})...")
        try:
            res2 = client.models.generate_content(
                model=MODEL_PART2,
                contents=[uploaded_file, PROMPT_PART2],
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                    response_schema=Analysis_Part2,
                    temperature=0.2
                )
            )
            if res2.text:
                data2 = json.loads(res2.text)
                out2 = os.path.join(OUTPUT_DIR, f"{base_name}_Part2.txt")
                save_text_file(data2, out2, mode="Part2", model_used=MODEL_PART2)
        except Exception as e:
            print(f"   ❌ Part 2 Failed: {e}")

        # Cleanup
        client.files.delete(name=uploaded_file.name)

    except Exception as e:
        print(f"   ❌ Failed to process {filename}: {e}")

# ================= MAIN EXECUTION =================

if __name__ == "__main__":
    # Ensure output dir exists
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    client = setup_client()
    if not client: exit()

    # Find PDFs in the folder relative to this script
    pdf_files = glob.glob(os.path.join(INPUT_PDF_DIR, "*.pdf"))
    
    if not pdf_files:
        print(f"No PDFs found in folder: {INPUT_PDF_DIR}")
        exit()

    print(f"Found {len(pdf_files)} PDFs to process.")

    for i, pdf in enumerate(pdf_files, 1):
        print(f"\n--- File {i}/{len(pdf_files)} ---")
        process_single_pdf(client, pdf)
        # Sleep to be polite to the API
        time.sleep(5) 

    print("\n✅ All jobs finished.")