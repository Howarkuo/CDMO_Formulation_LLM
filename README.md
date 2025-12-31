# CDMO_Formulation_LLM

## Part1: Chemistry, Manufacturing, and Controls Knowledge Extracted Q-A Pairs
Serve as the foundation of next step Supervised Fine-Tuning of Vernus-ReAltX Meta-Llama-3.1 model.



### 1. Evidence-Anchored Verification
To eliminate hallucinations common in scientific LLM applications, our prompts enforce an **Evidence-First Constraint**.
* Every generated Q&A pair requires a `input_paragraph` field.
* The model must extract the **verbatim text** from the source PDF that supports its answer.
* This creates a built-in "citation layer" allowing researchers to instantly verify the model's output against the original document.

### 2. Role-Based Persona Switching
The pipeline dynamically switches expert personas to analyze the same text from different angles:
* **Persona A**: *Pharmaceutical Formulation Expert* (Focus: Composition, Ratios, API properties).
* **Persona B**: *CMC Process Expert* (Focus: Feasibility, Operability, Stability, QA/QC).

```
System Instruction: "You are a pharmaceutical formulation expert. Given the scientific article, provide a brief summary focusing on key findings and methods used for improving drug formulation and also generate 20 high quality question and answer (QA) pairs as output. Use precise, pharmaceutical terminology.

**Questions should focus on**:
1.Key finding and conclusion from articles including experimental values.

2.Defining subproblems and basic property of APIs.

3.Key methodology use in the article to improve the subproblems.

4.Best composition or ratio of particular excipients used in formulation.

5.Key measurable parameters improvements before and after specific formulation.

6.Negative or failure example tested in the article that does not improve the subproblem or even lead to worse outcome and any trade-offs (such as safety, stability, cost, or manufacturing...etc).

7.Future perspective or alternative methods should be tested and any concern in this formulation.

8.Any potential issues in scale-up manufacturing process for such formulation, especially in the method section.
```

```
System Instruction: "You are a pharmaceutical CMC (Chemistry, Manufacturing, and Controls) process expert. Given the scientific article... generate 5 most critical risk factor and solution (QA) pairs as output.

**Output Requirements**:

1.Input Paragraph: Extract the specific verbatim paragraph from the text which refers to the corresponding question, answer, and reasoning. Do not use ellipsis.

2.Question (n): List the top 5 potential risk issues related to tech-transfer or scale-up for the article’s proposed final formulation and manufacturing methods. Label n = number from 16 to 20.

3.Answer: Provide a solution for the potential risks and detailed reasoning. Be skeptical but do not hallucinate.

4. Source: Provide the article's Pubmed ID (PMID).



**Questions should focus on, but are not limited to, the following points:**

1.  Excipient Applicability: Suitability for scale-up based on commercial availability, FDA approval/pharmacopeia grade, cost, compatibility, stability, and safety.

2.  Production Feasibility: The scale-up feasibility and operability of the technical methods used in production.

3.  QA/QC Feasibility: The scale-up feasibility of technical methods used for quality analysis (QA and QC).

4.  Critical Process Parameters (CPPs): Evaluate which parameters may affect product quality (e.g., stirring speed, time, temperature control, size control, feeding time, pressure, equipment limitations
```

### 3. Structured Schema Enforcement
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
