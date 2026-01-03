# CDMO_Formulation_LLM

## Part1: Chemistry, Manufacturing, and Controls Knowledge Extracted Q-A Pairs
Serve as the foundation of next step Supervised Fine-Tuning of Vernus-ReAltX Meta-Llama-3.1 model.

### 🚀 Key Features
* **Smart PDF Retrieval**: Automated pipeline to fetch full-text PDFs from PubMed Central using NCBI E-utilities.
* **CMC & Formulation Analysis**: Automated, deep-reasoning workflows for pharmaceutical risk assessment.
* **Gemini 2.5 Integration**: Leverages the latest multimodal models for direct PDF analysis.

---
## 0. 🧢 White Hat and Gray Hat Solution: Smart Paper Content Retrieval


**NCBI & PMC (Open Access)**
- Target Service: [NCBI E-utilities](https://www.ncbi.nlm.nih.gov/books/NBK25501/) & [PMC Open Access Service](https://www.ncbi.nlm.nih.gov/pmc/tools/openftlist/)

**How it works:**


1.  **Query Handling**: Uses `esearch.fcgi` to find relevant articles (PMIDs) based on complex boolean queries (e.g., "(Drug Formulation) AND (Emulsion)").
2.  **ID Mapping**: Automatically converts PMIDs to PMCIDs using `esummary.fcgi`, as only PMCIDs allow direct Open Access downloads.
3.  **Dynamic Link Resolution**: Queries the **PMC Open Access API (`oa.fcgi`)** to retrieve the exact file location for every paper.
4.  **Archive Handling**: If a direct PDF is missing, the script intelligently downloads the `.tar.gz` package, extracts it, and locates the hidden PDF file inside.
---
**Elsevier (Subscription Access)**

- Library Used: [elsapy Target Service: Elsevier Developer API (ScienceDirect & Scopus)](https://github.com/ElsevierDev/elsapy)

**How it works:**

1. **Authorized Handshake**: Initiates a secure ElsClient session using an institutional API Key and Token (or VPN-authenticated IP), establishing a trusted connection that validates subscription rights upfront.

2. **Object-Oriented Retrieval**: Instead of parsing raw HTML, the script initializes a FullDoc object using the article's DOI. This fetches structured JSON metadata directly from the server, bypassing the need for web scraping.

3. **Deep Link Parsing**: Automatically navigates the complex JSON response tree to locate the specific link node tagged with @ref='pdf', strictly separating the file download URL from abstract or HTML links.

4. **Header-Based Download**: Executes the final download by re-sending the authenticated client headers to the specific PDF endpoint, ensuring the request is recognized as a valid API call rather than an unauthorized browser attempt.

---

**Other Publishers (for Cloudflare-protected sites)**
- Library Used: [curl_cffi](https://github.com/lexiforest/curl_cffi)

- The "Gray Hat" method: You put on a disguise. You wear the same clothes as everyone else (Chrome Browser User-Agent), you walk like them, and most importantly, you speak their secret dialect (TLS Fingerprint). The bouncer thinks you are a normal human and lets you in.
- This module handles publishers that do not provide public APIs or are protected by advanced anti-bot firewalls (Cloudflare/Akamai). It allows the script to legally access content via University VPN by mimicking a legitimate user browser.



**How it works:**
1. **TLS Fingerprint Spoofing**: Unlike standard Python requests, curl_cffi modifies the TLS/SSL Handshake (JA3 fingerprint) to be bit-for-bit identical to a real Chrome browser. This allows the bot to pass network-level checks that usually block automated scripts.

2. **WAF Evasio**n: Successfully bypasses "403 Forbidden" and "Verify you are human" screens by actively impersonating modern browser headers and HTTP/2 protocols.

3. **DOI Resolution**: Visits the publisher's page via the University VPN (IP Authentication) exactly as a human researcher would.

4. **Meta-Tag Extraction**: Once inside, uses BeautifulSoup to locate the standardized <meta name="citation_pdf_url"> tag hidden in the HTML, ensuring the correct PDF file is targeted regardless of the page layout.
---

### 1. 🔎 Evidence-Anchored Verification
To eliminate hallucinations common in scientific LLM applications, our prompts enforce an **Evidence-First Constraint**.
* Every generated Q&A pair requires a `input_paragraph` field.
* The model must extract the **verbatim text** from the source PDF that supports its answer.
* This creates a built-in "citation layer" allowing researchers to instantly verify the model's output against the original document.
---
### 2. 🎭 Role-Based Persona Switching
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
---
### 3. 📝 Structured Schema Enforcement
Unlike standard chat-based interactions, this tool uses `Pydantic` to enforce strict output schemas. This ensures that the unstructured text of a PDF is converted into a deterministic, queryable JSON database with standardized fields (`source_pmid`, `answer_and_reasoning`, `brief_summary`).

---

## 📸 Workflows

### Pharmaceutical Formulation & CMC Risk Analysis
The following pipeline illustrates the workflow for processing academic PDFs to extract formulation parameters and assess manufacturing risks.

![PMC QA + PDF Scrape Workflow](https://github.com/Howarkuo/BioLLM/blob/main/Fig/PMC_QA%2BPDF_scrape.png?raw=true)

---

## 📦 Packages Required

To run the CMC analysis and scraping scripts, you must install the following packages.

**Install via pip (Ubuntu Server) / poetry (Local PC):**
```bash
pip install elsapy curl_cffi beautifulsoup4 pypdf google-genai pydantic requests
```
```bash
poetry add elsapy curl_cffi beautifulsoup4 pypdf google-genai pydantic requests
```
---
## Supplementary

### Major Publisher DOI Prefixes

| Publisher / Distributor | Common Prefix(es) | Example Journals |
| ----------------------- | ----------------- | ---------------- |
| **Elsevier** | `10.1016` | The Lancet, Cell, ScienceDirect journals |
| **Springer Nature** | `10.1007` (Springer)<br>`10.1038` (Nature)<br>`10.1186` (BMC) | Nature, Scientific Reports, SpringerLink |
| **Wiley** | `10.1002`<br>`10.1111` | Advanced Materials, Angewandte Chemie |
| **Taylor & Francis** | `10.1080` | Routledge, CRC Press journals |
| **ACS** (American Chemical Society) | `10.1021` | JACS, Chemical Reviews |
| **IEEE** | `10.1109` | IEEE Transactions, IEEE Xplore |
| **AAAS** (Science) | `10.1126` | Science, Science Immunology |
| **MDPI** | `10.3390` | Molecules, Sensors, IJMS |
| **PLOS** (Public Library of Science) | `10.1371` | PLOS ONE, PLOS Biology |
| **Frontiers** | `10.3389` | Frontiers in Immunology, Frontiers in Psychology |
| **Oxford University Press** | `10.1093` | Academic.oup.com journals |
| **Cambridge University Press** | `10.1017` | Cambridge Core journals |
| **SAGE Publishing** | `10.1177` | SAGE Journals |
| **RSC** (Royal Society of Chemistry) | `10.1039` | ChemComm, Dalton Transactions |
| **AIP** (American Institute of Physics) | `10.1063` | Applied Physics Letters, JCP |
| **APS** (American Physical Society) | `10.1103` | Physical Review Letters (PRL) |

### Comparison: `elsapy` vs. `curl_cffi` Scraper

| Feature | **Previous Script (`curl_cffi` Scraper)** | **New Script (`elsapy`)** |
| :--- | :--- | :--- |
| **Method** | **"Grey Hat" (Browser Impersonation)**<br>Uses `curl_cffi` to spoof **TLS/JA3 fingerprints** and HTTP/2 headers. This makes the Python script mathematically indistinguishable from a real Chrome browser at the network packet level, bypassing advanced anti-bot systems (like Cloudflare) that block standard Python requests. | **"White Hat" (Authorized API)**<br>Uses official developer keys to authenticate directly with the Elsevier server. The server knows you are a script and grants access based on your institutional rights. |
| **Reliability** | **Volatile**<br>Vulnerable to breakage if the website updates its HTML structure (DOM changes) or upgrades its anti-bot security. | **Stable**<br>APIs are versioned and designed for machine use; they rarely change their structure. |
| **Access** | **Open / Flexible**<br>Can theoretically access any public-facing URL (Open Access or public HTML pages), regardless of API permissions. | **Restricted**<br>Strictly limited to content your university subscribes to. Returns `403 Forbidden` for non-subscribed content even if technically viewable on the web. |
| **Speed** | **Medium (Throttled)**<br>Faster than Selenium/Playwright (no GUI overhead), but requires artificial pauses (`sleep`) to avoid IP bans. | **Fast (Optimized)**<br>Limited only by official API quotas. No need to "sleep" to pretend to be human. |

### Comparison: `curl_cffi` vs. `Playwright`

| Feature | `curl_cffi` (`crequests`) | `Playwright` (`sync_playwright`) |
| :--- | :--- | :--- |
| **Type** | **HTTP Client** (Network Layer) | **Browser Automation** (Application Layer) |
| **How it works** | Sends raw HTTP requests but spoofs TLS/JA3 fingerprints and HTTP/2 headers to look like a browser. | Launches a real browser engine (Chromium/Firefox) and controls it programmatically. |
| **JavaScript Support** | ❌ **None.** It fetches the HTML code exactly as the server sends it. It cannot run scripts. | ✅ **Full.** It renders the page, runs JS, executes React/Vue/Angular, and waits for dynamic content. |
| **Anti-Bot Evasion** | **High (Network Level).** Excellent at bypassing "Access Denied" screens (Cloudflare/Akamai) that check TLS signatures. | **Medium/Hard.** Anti-bots can detect the "automation" flags in the browser. Often requires extra plugins (`playwright-stealth`) to hide. |
| **Speed** | 🚀 **Very Fast.** Lightweight, low CPU/RAM usage. Can scrape thousands of pages quickly. | 🐢 **Slow.** Heavy CPU/RAM usage. Loading a full browser for every page takes time and memory. |
| **Resource Usage** | Low (Kilobytes of RAM). | High (Hundreds of Megabytes of RAM per page). |
| **Complexity** | **Simple.** Very similar to the standard Python `requests` library. | **Complex.** Requires managing browser contexts, pages, selectors, and timeouts. |
| **Best For** | • Bypassing Cloudflare/Incapsula.<br>• Scraping APIs.<br>• Static websites (like MDPI/PubMed). | • Websites that render content after loading (SPA).<br>• Complex interactions (Login flows, clicking "Show More").<br>• Taking screenshots/PDFs of pages. |
