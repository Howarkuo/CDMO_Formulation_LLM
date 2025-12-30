#Source of pdf: Predownloaded PDF at r"C:\Users\howar\Desktop\biollm
# Now Change to source of C:\Users\howar\Desktop\biollm\Scrapers\NoAPI\Working\downloaded_pdf (name: PMC6154611...)
## Create final output with folder opens in C:\Users\howar\Desktop\biollm\QA_Generation\CMC_part1 (name with pmcid attached)

from pydantic import BaseModel, Field
from typing import List
import os
import json
import time
from google import genai
from google.genai import types

# --- Pydantic Models (CMC Part 2 Focus) ---
class QAPair(BaseModel):
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

class FormulationAnalysis(BaseModel):
    """Complete analysis output containing a summary and a list of Risk/Solution pairs."""
      
    brief_summary: str = Field(
        description="A brief summary (max 300 words) focusing on key findings and methods used for improving drug formulation."
    )
    qa_pairs: List[QAPair] = Field(
        description="A list of exactly 5 critical risk factor and solution (QA) pairs labeled 16 to 20."
    )

# --- Helper Functions ---
def load_key_from_desktop():
    key_path = r"C:\Users\howar\Desktop\api_key.txt"
    try:
        with open(key_path, "r") as file:
            return file.read().strip()
    except FileNotFoundError:
        print(f"Error: Could not find the key file at {key_path}")
        return None

def save_to_text_file(data, output_path):
    """Formats the data and writes it to a .txt file."""
    try:
        with open(output_path, "w", encoding="utf-8") as f:
            f.write("=== PHARMACEUTICAL CMC & SCALE-UP ANALYSIS (Part 2) ===\n\n")
            f.write(f"SUMMARY:\n{data.get('brief_summary')}\n")
            f.write("\n" + "="*60 + "\n")
            f.write("CRITICAL RISK FACTORS & SOLUTIONS (16-20)\n")
            f.write("="*60 + "\n\n")
            
            qa_list = data.get('qa_pairs', [])
            for item in qa_list:
                f.write(f"Risk/Question: {item['question']}\n")
                f.write(f"Solution & Reasoning: {item['answer_and_reasoning']}\n")
                f.write(f"Source Paragraph: {item['input_paragraph']}\n")
                f.write(f"PMID: {item['source_pmid']}\n")
                f.write("-" * 40 + "\n")
        print(f" -> Saved: {output_path}")
    except Exception as e:
        print(f"Error saving file: {e}")

def get_dynamic_output_path(pdf_path, model_name):
    directory = os.path.dirname(pdf_path)
    pdf_filename = os.path.splitext(os.path.basename(pdf_path))[0]
    # Suffix ensures unique files for Part 2
    new_filename = f"{pdf_filename}_{model_name}_CMC_Part2.txt"
    return os.path.join(directory, new_filename)

# --- Main Configuration ---
my_api_key = load_key_from_desktop()
if not my_api_key:
    print("Stop: No API Key found.")
    exit()

client = genai.Client(api_key=my_api_key)
MODEL_NAME = "gemini-2.5-flash"  

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

def analyze_formulation_paper(pdf_path: str):
    if not os.path.exists(pdf_path):
        print(f"Skipping: File not found at {pdf_path}")
        return None

    print(f"\nProcessing: {os.path.basename(pdf_path)}...")
    
    try:
        # Upload file
        uploaded_file = client.files.upload(file=pdf_path)
        
        # Generate content
        response = client.models.generate_content(
            model=MODEL_NAME,
            contents=[uploaded_file, PHARMA_PROMPT_TEXT],
            config=types.GenerateContentConfig(
                system_instruction="You are a skeptical pharmaceutical CMC expert specializing in scale-up and risk assessment.",
                response_mime_type="application/json",
                response_schema=FormulationAnalysis, 
                temperature=0.2 
            )
        )

        # Parse response
        if response.text:
            result = json.loads(response.text)
            client.files.delete(name=uploaded_file.name) # Clean up
            return result
        else:
            print("Error: Empty response.")
            return None

    except Exception as e:
        print(f"Error occurred: {e}")
        return None

# --- Execution for Multiple Papers ---
if __name__ == "__main__":
    
    # === INPUT YOUR 4 FILES HERE ===
    # You can simply paste the full paths to your 4 PDFs in this list.
    paper_list = [
        r"C:\Users\howar\Desktop\biollm\Nintedanib_basic.pdf",
        r"C:\Users\howar\Desktop\biollm\amorphization_snedds.pdf",
        r"C:\Users\howar\Desktop\biollm\nintedanib_intestinal.pdf",
        r"C:\Users\howar\Desktop\biollm\Nintedanib_SMDDS_invivo.pdf"
    ]

    print(f"Found {len(paper_list)} papers to process.")

    for pdf_path in paper_list:
        # 1. Analyze
        data = analyze_formulation_paper(pdf_path)
        
        # 2. Save if successful
        if data:
            output_path = get_dynamic_output_path(pdf_path, MODEL_NAME)
            save_to_text_file(data, output_path)
            
            # Optional: Sleep briefly between calls to be gentle on API limits
            time.sleep(2) 

    print("\nAll papers processed.")