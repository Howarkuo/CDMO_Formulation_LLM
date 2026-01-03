# Now Change to source of C:\Users\howar\Desktop\biollm\Scrapers\NoAPI\Working\downloaded_pdf (name: PMC6154611...)
# Create final output with folder opens in C:\Users\howar\Desktop\biollm\QA_Generation\formulation_analysis_part1 (name with pmcid attached)

from pydantic import BaseModel, Field
from typing import List
import os
import json
from google import genai
from google.genai import types

# --- Pydantic Models ---
class QAPair(BaseModel):
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

class FormulationAnalysis(BaseModel):
    """Complete analysis output containing a summary and a list of Q&A pairs."""
      
    brief_summary: str = Field(
        description="A brief summary focusing on key findings and methods used for improving drug formulation."
    )
    qa_pairs: List[QAPair] = Field(
        description="A list of exactly 20 high-quality question and answer pairs using precise pharmaceutical terminology."
    )

# --- Helper Function ---
def load_key_from_desktop():
    # 'r' tells Python to treat backslashes as literal characters
    key_path = r"C:\Users\howar\Desktop\api_key.txt"
    
    try:
        with open(key_path, "r") as file:
            # .strip() is crucial! It removes hidden newlines (\n) or spaces
            api_key = file.read().strip()
            return api_key
    except FileNotFoundError:
        print(f"Error: Could not find the key file at {key_path}")
        return None
def save_to_text_file(data, output_path):
    """Formats the data and writes it to a .txt file."""
    try:
        with open(output_path, "w", encoding="utf-8") as f:
            f.write("=== PHARMACEUTICAL FORMULATION ANALYSIS ===\n\n")
            f.write(f"SUMMARY:\n{data.get('brief_summary')}\n")
            f.write("\n" + "="*50 + "\n")
            f.write("QUESTION & ANSWER PAIRS\n")
            f.write("="*50 + "\n\n")
            
            for i, item in enumerate(data.get('qa_pairs', []), 1):
                f.write(f"Pair #{i}\n")
                f.write(f"Q: {item['question']}\n")
                f.write(f"A & Reasoning: {item['answer_and_reasoning']}\n")
                f.write(f"Source Paragraph: {item['input_paragraph']}\n")
                f.write(f"PMID: {item['source_pmid']}\n")
                f.write("-" * 30 + "\n")
        print(f"Successfully saved output to: {output_path}")
    except Exception as e:
        print(f"Error saving file: {e}")
def get_dynamic_output_path(pdf_path, model_name):
    directory = os.path.dirname(pdf_path)
    pdf_filename = os.path.splitext(os.path.basename(pdf_path))[0]
    new_filename = f"{pdf_filename}_{model_name}_qa-pairs.txt"
    return os.path.join(directory, new_filename)
# --- Main Configuration ---

# 1. Load the key
my_api_key = load_key_from_desktop()

# 2. Initialize Client (Stop if no key)
if not my_api_key:
    print("Stop: No API Key found.")
    exit()

# Initialize the client from the new 'google.genai' library
client = genai.Client(api_key=my_api_key)
print("Success: API Key loaded and Client configured.")

# Constants
MODEL_NAME = "gemini-2.5-flash"  
PDF_PATH = r"C:\Users\howar\Desktop\biollm\Nintedanib_basic.pdf"  # Fixed path slashes
OUTPUT_TXT_PATH = get_dynamic_output_path(PDF_PATH, MODEL_NAME)
PHARMA_PROMPT_TEXT = """
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

def analyze_formulation_paper(pdf_path: str):
    if not os.path.exists(pdf_path):
        print(f"Error: File not found at {pdf_path}")
        return None

    print(f"1. Uploading file: {os.path.basename(pdf_path)}...")
    
    try:
        # Upload file
        uploaded_file = client.files.upload(
            file=pdf_path
        )
        print(f"   -> File uploaded: {uploaded_file.name}")

        # Generate content using the schema defined above
        print("2. Generating analysis (Summary + 20 Q&A)...")
        
        response = client.models.generate_content(
            model=MODEL_NAME,
            contents=[
                uploaded_file, 
                PHARMA_PROMPT_TEXT
            ],
            config=types.GenerateContentConfig(
                system_instruction="You are a helpful assistant specialized in pharmaceutical analysis.",
                response_mime_type="application/json",
                response_schema=FormulationAnalysis, # Pass the Pydantic class here
                temperature=0.2 # Lower temperature for more factual extraction
            )
        )

        # Parse the response
        if response.text:
            result = json.loads(response.text)
            print(f"Usage: {response.usage_metadata}")
            print('******')
            
            # Clean up file to save storage
            client.files.delete(name=uploaded_file.name)
            
            return result
        else:
            print("Error: Empty response text.")
            return None

    except Exception as e:
        print(f"Error occurred: {e}")
        return None

# --- Execution ---
if __name__ == "__main__":
    data = analyze_formulation_paper(PDF_PATH)
    
    if data:
        # Save to the specific file path requested
        save_to_text_file(data, OUTPUT_TXT_PATH)
        
        # Also print a small preview to console
        print("\nProcess Complete. File written to Desktop.")
        # print("\n" + "="*50)
        # print(f"SUMMARY: {data.get('brief_summary')}")
        # print("="*50 + "\n")
        
        # qa_list = data.get('qa_pairs', [])
        # for item in qa_list:
        #     print(f"Q: {item['question']}")
        #     print(f"A & Reasoning: {item['answer_and_reasoning']}")
        #     print(f"Source Paragraph: {item['input_paragraph'][:100]}...") 
        #     print(f"PMID: {item['source_pmid']}")
        #     print("-" * 30)