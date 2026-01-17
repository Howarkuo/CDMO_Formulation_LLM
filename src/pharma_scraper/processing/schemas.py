from pydantic import BaseModel, Field
from typing import List

# ==========================================
# PART 1: Formulation Analysis Schemas
# ==========================================

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


# ==========================================
# PART 2: CMC & Scale-Up Risk Schemas
# ==========================================

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