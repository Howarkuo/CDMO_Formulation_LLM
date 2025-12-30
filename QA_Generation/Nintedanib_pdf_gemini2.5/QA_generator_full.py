import os
import glob
import json
import time
from pydantic import BaseModel, Field
from typing import List
from google import genai
from google.genai import types

# ================= CONFIGURATION =================
# 1. API Key Path
KEY_PATH = r"C:\Users\howar\Desktop\api_key.txt"

# 2. Input Directory (Where your downloaded PDFs are)
INPUT_PDF_DIR = r"C:\Users\howar\Desktop\biollm\Scrapers\NoAPI\Working\downloaded_pdf"

# 3. Output Directory (Where QA text files will go)
OUTPUT_DIR = r"C:\Users\howar\Desktop\biollm\QA_Generation\CMC_Combined"

# 4. Model Settings
MODEL_NAME = "gemini-2.5-flash"

# ================= DATA MODELS =================

# --- Part 1: General Formulation Models ---
class QAPair_Part1(BaseModel):
    input_paragraph: str = Field(description="Verbatim paragraph from text.")
    question: str = Field(description="Numbered question (1-20).")
    answer_and_reasoning: str = Field(description="Factual answer with reasoning.")
    source_pmid: str = Field(description="PMID of the article.")

class Analysis_Part1(BaseModel):
    brief_summary: str = Field(description="Summary of findings and methods.")
    qa_pairs: List[QAPair_Part1] = Field(description="List of 20 QA pairs.")

# --- Part 2: CMC Risk Models ---
class QAPair_Part2(BaseModel):
    input_paragraph: str = Field(description="Verbatim paragraph related to risk.")
    question: str = Field(description="Risk-focused question (numbered 16-20).")
    answer_and_reasoning: str = Field(description="Solution with skepticism and reasoning.")
    source_pmid: str = Field(description="PMID of the article.")

class Analysis_Part2(BaseModel):
    brief_summary: str = Field(description="Summary focusing on CMC aspects.")
    qa_pairs: List[QAPair_Part2] = Field(description="List of 5 critical risk factors.")

# ================= PROMPTS =================

PROMPT_PART1 = """
You are a pharmaceutical formulation expert.
Instruction: Provide a brief summary focusing on key findings and methods used for improving drug formulation and generate **20 high quality question and answer (QA) pairs**. Use precise terminology.

Focus Areas:
1) Key findings/values. 2) API properties. 3) Methodology. 4) excipient ratios. 5) Measurable improvements. 6) Negative results/trade-offs. 7) Future perspective. 8) Scale-up issues.
"""

PROMPT_PART2 = """
You are a pharmaceutical CMC (Chemistry, Manufacturing, and Controls) process expert.
Instruction: Provide a brief summary and generate **5 most critical risk factor and solution (QA) pairs** related to tech-transfer or scale-up.

Output Requirements:
1. Question (n): Label n = number from 16 to 20.
2. Focus: Excipient applicability (cost/grade), Production feasibility, QA/QC feasibility, Critical Process Parameters (CPPs).
3. Answer: Provide a solution with skepticism.
"""

# ================= HELPER FUNCTIONS =================

def setup_client():
    try:
        with open(KEY_PATH, "r") as f:
            api_key = f.read().strip()
        return genai.Client(api_key=api_key)
    except Exception as e:
        print(f"❌ Error loading API key: {e}")
        return None

def save_text_file(data, output_path, mode="Part1"):
    try:
        with open(output_path, "w", encoding="utf-8") as f:
            if mode == "Part1":
                header = "=== PHARMACEUTICAL FORMULATION ANALYSIS (Part 1) ==="
            else:
                header = "=== CMC & SCALE-UP RISK ANALYSIS (Part 2) ==="
            
            f.write(f"{header}\n\n")
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
        print(f"   -> Saved: {os.path.basename(output_path)}")
    except Exception as e:
        print(f"   ❌ Error saving file: {e}")

def process_single_pdf(client, pdf_path):
    filename = os.path.basename(pdf_path)
    base_name = os.path.splitext(filename)[0]
    print(f"\n📄 Processing: {filename}")

    try:
        # 1. Upload File (Shared for both parts)
        uploaded_file = client.files.upload(file=pdf_path)
        print("   -> File uploaded successfully.")

        # --- PART 1: GENERAL FORMULATION ---
        print("   -> Generating Part 1 (General QA)...")
        res1 = client.models.generate_content(
            model=MODEL_NAME,
            contents=[uploaded_file, PROMPT_PART1],
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=Analysis_Part1,
                temperature=0.2
            )
        )
        if res1.text:
            data1 = json.loads(res1.text)
            out1 = os.path.join(OUTPUT_DIR, f"{base_name}_Part1_General.txt")
            save_text_file(data1, out1, mode="Part1")

        # --- PART 2: CMC RISK ---
        print("   -> Generating Part 2 (CMC Risk)...")
        res2 = client.models.generate_content(
            model=MODEL_NAME,
            contents=[uploaded_file, PROMPT_PART2],
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=Analysis_Part2,
                temperature=0.2
            )
        )
        if res2.text:
            data2 = json.loads(res2.text)
            out2 = os.path.join(OUTPUT_DIR, f"{base_name}_Part2_CMC.txt")
            save_text_file(data2, out2, mode="Part2")

        # Cleanup
        client.files.delete(name=uploaded_file.name)
        print("   -> Cleanup complete.")

    except Exception as e:
        print(f"   ❌ Failed to process {filename}: {e}")

# ================= MAIN EXECUTION =================

if __name__ == "__main__":
    # 1. Setup
    if not os.path.exists(KEY_PATH):
        print(f"Stop: Key not found at {KEY_PATH}")
        exit()
    
    # Ensure output dir exists
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    client = setup_client()
    if not client: exit()

    # 2. Find PDFs
    pdf_files = glob.glob(os.path.join(INPUT_PDF_DIR, "*.pdf"))
    
    if not pdf_files:
        print(f"No PDFs found in {INPUT_PDF_DIR}")
        exit()

    print(f"Found {len(pdf_files)} PDFs to process.")

    # 3. Loop through files
    for i, pdf in enumerate(pdf_files, 1):
        print(f"\n--- File {i}/{len(pdf_files)} ---")
        process_single_pdf(client, pdf)
        time.sleep(2) # Politeness delay

    print("\n✅ All jobs finished.")