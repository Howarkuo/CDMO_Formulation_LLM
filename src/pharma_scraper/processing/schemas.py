from pydantic import BaseModel, Field
from typing import List

class QAPair_Part1(BaseModel):
    input_paragraph: str = Field(description="Verbatim paragraph source.")
    question: str = Field(description="The question text.")
    answer_and_reasoning: str = Field(description="Factual answer with reasoning.")
    source_pmid: str = Field(description="PMID or 'Not Available'.")

class Analysis_Part1(BaseModel):
    brief_summary: str = Field(description="Summary of key findings.")
    qa_pairs: List[QAPair_Part1] = Field(description="List of 20 QA pairs.")

# ... [Add Part2 schemas here] ...