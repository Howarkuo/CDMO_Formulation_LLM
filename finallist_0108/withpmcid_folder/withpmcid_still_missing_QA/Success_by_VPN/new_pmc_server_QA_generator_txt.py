#!/usr/bin/env python3
import os
import glob
import json
import time
import re  # Added for filename sanitization
from pydantic import BaseModel, Field
from typing import List
from google import genai
from google.genai import types
from google.api_core import exceptions

# ================= CONFIGURATION =================
# [SERVER SETUP]
KEY_PATH = r"C:\Users\howar\Desktop\api_key.txt"
# Directory path
INPUT_FILENAME = "new_trial.txt"
# Where the final analysis results will be saved
OUTPUT_DIR = "new_trial_withpmcidstillmissing_split"  
# Temporary folder to store the split text files
TEMP_SPLIT_DIR = "new_trial_withpmcidstillmissing_temp_split_articles" 

# The separator used in your text file
SEPARATOR_PATTERN = "=================================================="
# [MODEL SETUP] (Unchanged)
MODEL_PART1 = "gemini-2.5-flash" 
MODEL_PART2 = "gemini-2.5-flash"

# ================= DATA MODELS (Unchanged) =================

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

# ================= PROMPTS (Unchanged) =================

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
            print(f"❌ Error: {KEY_PATH} not found.")
            return None
        with open(KEY_PATH, "r") as f:
            api_key = f.read().strip()
        return genai.Client(api_key=api_key)
    except Exception as e:
        print(f"❌ Error loading API key: {e}")
        return None

def generate_with_retry(client, model_name, contents, config):
    """Wraps the generation in a retry loop for 429 errors."""
    retries = 0
    max_retries = 10
    
    while retries < max_retries:
        try:
            response = client.models.generate_content(
                model=model_name,
                contents=contents,
                config=config
            )
            return response
        except exceptions.ResourceExhausted:
            wait_time = 30 + (retries * 5)
            print(f"    ⚠️ Quota Exceeded (429). Waiting {wait_time}s...")
            time.sleep(wait_time)
            retries += 1
        except Exception as e:
            print(f"    ❌ API Error: {e}")
            return None
    return None

def save_result(filename, data, mode):
    filepath = os.path.join(OUTPUT_DIR, filename)
    try:
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(f"=== {mode} ANALYSIS ===\n")
            f.write(f"SUMMARY:\n{data.get('brief_summary', '')}\n")
            f.write("\n" + "="*40 + "\n\n")
            for item in data.get('qa_pairs', []):
                f.write(f"Q: {item['question']}\n")
                f.write(f"A: {item['answer_and_reasoning']}\n")
                f.write(f"Source: {item['input_paragraph']}\n")
                f.write("-" * 30 + "\n")
        print(f"    -> Saved: {filename}")
    except Exception as e:
        print(f"    ❌ Error saving result: {e}")

# ================= STEP 1: SPLIT FILES (MODIFIED) =================

def sanitize_filename(name):
    """Removes illegal characters for Windows/Linux filenames."""
    # Remove characters like / \ : * ? " < > |
    name = re.sub(r'[\\/*?:"<>|]', "", name)
    # Remove extension if accidentally grabbed (we add it back later)
    name = os.path.splitext(name)[0]
    return name.strip()

def split_large_file():
    print(f"📂 Step 1: Splitting large file '{INPUT_FILENAME}'...")
    
    if not os.path.exists(INPUT_FILENAME):
        print("❌ Input file not found!")
        return []

    with open(INPUT_FILENAME, 'r', encoding='utf-8') as f:
        full_text = f.read()

    # Split by separator
    raw_fragments = full_text.split(SEPARATOR_PATTERN)
    fragments = [frag.strip() for frag in raw_fragments if frag.strip()]

    print(f"ℹ️  Found {len(fragments)} fragments. Creating individual files...")

    file_list = []
    
    # Process in pairs (Header + Body)
    article_idx = 1
    existing_filenames = set()

    for i in range(0, len(fragments), 2):
        if i + 1 >= len(fragments): 
            break
            
        header = fragments[i]
        body = fragments[i+1]
        content = f"{header}\n\n{body}"
        
        # --- Logic to extract Original Filename from Header ---
        extracted_name = ""
        
        # Strategy A: Look for "Filename: xxxx"
        match = re.search(r"Filename:\s*(.+)", header, re.IGNORECASE)
        if match:
            extracted_name = match.group(1)
        else:
            # Strategy B: If no label, take the first non-empty line of the header
            header_lines = [line.strip() for line in header.split('\n') if line.strip()]
            if header_lines:
                extracted_name = header_lines[0]
            else:
                extracted_name = f"article_{article_idx:03d}"

        # Clean the name
        clean_name = sanitize_filename(extracted_name)
        
        # Fallback if cleaning made it empty
        if not clean_name:
            clean_name = f"article_{article_idx:03d}"

        # Handle duplicates (e.g. if multiple articles have same name in header)
        original_clean_name = clean_name
        counter = 1
        while clean_name in existing_filenames:
            clean_name = f"{original_clean_name}_{counter}"
            counter += 1
        existing_filenames.add(clean_name)

        # Create individual text file with the Extracted Name
        fname = f"{clean_name}.txt"
        fpath = os.path.join(TEMP_SPLIT_DIR, fname)
        
        with open(fpath, "w", encoding="utf-8") as out:
            out.write(content)
            
        file_list.append(fpath)
        article_idx += 1

    print(f"✅ Successfully created {len(file_list)} separate text files in '{TEMP_SPLIT_DIR}'")
    return file_list

# ================= STEP 2: PROCESS FILES =================

def process_files(client, file_list):
    total = len(file_list)
    print(f"\n🚀 Step 2: Starting Batch Processing of {total} articles...\n")

    for i, file_path in enumerate(file_list, 1):
        filename = os.path.basename(file_path)
        base_name = os.path.splitext(filename)[0] # Extract "MyFile" from "MyFile.txt"
        
        print(f"[{i}/{total}] Processing: {base_name}")
        
        with open(file_path, "r", encoding="utf-8") as f:
            text_content = f.read()

        # --- PART 1 ---
        print("    -> Generating Part 1...")
        res1 = generate_with_retry(
            client, MODEL_PART1, [text_content, PROMPT_PART1],
            types.GenerateContentConfig(
                response_mime_type="application/json", response_schema=Analysis_Part1
            )
        )
        if res1 and res1.text:
            data1 = json.loads(res1.text)
            # Naming format: [Original_Filename]_Part1.txt
            save_result(f"{base_name}_Part1.txt", data1, "Part1")

        # --- PART 2 ---
        print("    -> Generating Part 2...")
        res2 = generate_with_retry(
            client, MODEL_PART2, [text_content, PROMPT_PART2],
            types.GenerateContentConfig(
                response_mime_type="application/json", response_schema=Analysis_Part2
            )
        )
        if res2 and res2.text:
            data2 = json.loads(res2.text)
            # Naming format: [Original_Filename]_Part2.txt
            save_result(f"{base_name}_Part2.txt", data2, "Part2")

        # Sleep to act as a buffer
        print("    -> Sleeping 5s...")
        time.sleep(5)

# ================= MAIN =================

if __name__ == "__main__":
    # Setup directories
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    os.makedirs(TEMP_SPLIT_DIR, exist_ok=True)

    # Setup Client
    client = setup_client()
    
    if client:
        # 1. Split the big file
        split_files = split_large_file()
        
        # 2. Process the split files
        if split_files:
            process_files(client, split_files)
            print("\n✅ All jobs finished.")