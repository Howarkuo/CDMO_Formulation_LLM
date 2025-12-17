from pydantic import BaseModel, Field
from typing import List
import os
import json
from google import genai
from google.genai import types
#oop: Class- field, constructor, method, instance
# pydantic- basemodel= data validation, 
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


client = genai.Client(api_key='AIzaSyCNFFT-Dc0F-7evD8UMB9hsK8YnHDasjtA')
MODEL_NAME = "gemini-2.5-flash"
PDF_PATH = "/home/qwerthjkl45/roche/biollm/test.pdf"  # <--- UPDATE THIS PATH

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
    print(f"1. Uploading file: {os.path.basename(pdf_path)}...")
    
    # Upload file
    uploaded_file = client.files.upload(
        file=pdf_path
    )
    print(f"   -> File uploaded: {uploaded_file.name}")

    # Generate content using the schema defined above
    print("2. Generating analysis (Summary + 20 Q&A)...")
    
    try:
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
        result = json.loads(response.text)
        print(response.usage_metadata)
        print('******')
        # Clean up file
        client.files.delete(name=uploaded_file.name)
        
        return result

    except Exception as e:
        print(f"Error occurred: {e}")
        return None

# --- Execution ---
if __name__ == "__main__":
    if not os.path.exists(PDF_PATH):
        print("Please set the correct PDF_PATH.")
    else:
        data = analyze_formulation_paper(PDF_PATH)
        
        if data:
            print("\n" + "="*50)
            print(f"SUMMARY: {data.get('brief_summary')}")
            print("="*50 + "\n")
            
            qa_list = data.get('qa_pairs', [])
            for item in qa_list:
                print(f"Q: {item['question']}")
                print(f"A & Reasoning: {item['answer_and_reasoning']}")
                print(f"Source Paragraph: {item['input_paragraph'][:100]}...") # Printing first 100 chars
                print(f"PMID: {item['source_pmid']}")
                print("-" * 30)