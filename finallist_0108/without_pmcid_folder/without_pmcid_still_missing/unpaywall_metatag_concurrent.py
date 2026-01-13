# from curl_cffi import requests as crequests
# from bs4 import BeautifulSoup
# from pypdf import PdfReader
# import io
# import time
# import random
# import concurrent.futures # IMPORTED FOR BATCHING

# # --- Configuration ---
# BATCH_SIZE = 5 # How many articles to download at the same time
# OUTPUT_FILE = "withpmcidstillmissing_196_upayrwall.txt"
# FAILED_LOG_FILE = "withpmcidstillmissing_196_upayrwall.txt"
# EMAIL_FOR_UNPAYWALL = "howard.kuo@vernus.ai" 


# withpmcidstillmissing_196_list=
# ["10.1002/jps.22475",
# "10.1208/s12249-011-9721-z",
# "10.1208/s12249-013-9996-3",
# "10.1039/d3bm01765f",
# "10.1208/s12249-010-9455-3",
# "10.1208/s12249-014-0280-y",
# "10.1208/s12249-015-0370-5",
# "10.1007/s13346-017-0435-y",
# "10.1208/s12249-008-9178-x",
# "10.1208/s12249-010-9438-4",
# "10.1111/j.2042-7158.2011.01376.x",
# "10.1208/s12249-010-9432-x",
# "10.1007/s11095-014-1370-y",
# "10.1021/acsnano.5b01696",
# "10.1208/s12249-011-9675-1",
# "10.3109/02652048.2010.520093",
# "10.1208/pt010105",
# "10.1208/s12249-010-9486-9",
# "10.1208/s12249-012-9855-7",
# "10.1080/10837450.2020.1725893",
# "10.1007/s00280-011-1749-y",
# "10.1021/acsami.6b08153",
# "10.1089/jamp.2009.0766",
# "10.1049/iet-nbt.2018.5248",
# "10.1117/1.JBO.18.10.101312",
# "10.2217/nnm.14.4",
# "10.1208/s12249-011-9680-4",
# "10.1007/s13346-019-00619-0",
# "10.1208/pt070377",
# "10.1208/s12249-010-9445-5",
# "10.1208/s12249-014-0147-2",
# "10.1177/0884533617722759",
# "10.1208/pt0804116",
# "10.1208/pt020205",
# "10.1208/s12249-008-9089-x",
# "10.1208/pt030103",
# "10.1208/pt070489",
# "10.1208/s12249-008-9063-7",
# "10.1128/AEM.72.3.2280-2282.2006",
# "10.1002/jps.24053",
# "10.1007/s11095-018-2495-1",
# "10.1208/s12249-018-0973-8",
# "10.1080/17435889.2024.2386923",
# "10.1208/s12249-010-9453-5",
# "10.1208/s12249-014-0238-0",
# "10.1208/s12249-010-9510-0",
# "10.1002/mabi.201100107",
# "10.1007/s13346-024-01620-y",
# "10.1208/s12249-012-9847-7",
# "10.1208/s12249-012-9821-4",
# "10.1007/s11095-011-0474-x",
# "10.1021/mp300319m",
# "10.1007/BF02830623",
# "10.1208/pt040332",
# "10.1208/s12249-014-0258-9",
# "10.1208/s12249-010-9568-8",
# "10.1208/s12249-010-9478-9",
# "10.1208/s12249-007-9022-8",
# "10.1049/iet-nbt.2018.0006",
# "10.3109/10837450.2012.737806",
# "10.1128/aac.28.1.103",
# "10.1208/s12249-007-9016-6",
# "10.1208/s12249-011-9583-4",
# "10.1208/aapsj060326",
# "10.1208/s12249-011-9663-5",
# "10.1208/s12249-009-9235-0",
# "10.1208/s12249-009-9328-9",
# "10.1002/jps.23450",
# "10.1208/s12249-008-9183-0",
# "10.1208/s12249-008-9036-x",
# "10.1208/s12249-007-9023-7",
# "10.3748/wjg.v16.i27.3437",
# "10.1093/jbcr/irab118",
# "10.1208/s12249-008-9172-3",
# "10.1208/s12249-009-9218-1",
# "10.1208/s12249-014-0199-3",
# "10.1007/s00280-015-2851-3",
# "10.1208/s12249-021-02108-5",
# "10.1002/adhm.202101427",
# "10.1089/can.2022.0176",
# "10.1208/s12249-013-0048-9",
# "10.1073/pnas.1310214110",
# "10.1021/bm4015232",
# "10.1089/jamp.2015.1235",
# "10.1002/jps.21719",
# "10.1208/s12249-009-9315-1",
# "10.1021/mp4005029",
# "10.1007/s11095-022-03317-8",
# "10.1208/pt010317",
# "10.1007/s11095-018-2349-x",
# "10.1208/s12249-009-9284-4",
# "10.1049/iet-nbt.2017.0104",
# "10.1080/21645515.2015.1046660",
# "10.1208/s12249-009-9233-2",
# "10.1208/s12249-009-9287-1",
# "10.1208/pt050342",
# "10.1136/ejhpharm-2020-002534",
# "10.1007/s13346-020-00758-9",
# "10.1002/jps.22488",
# "10.1208/s12249-012-9762-y",
# "10.1208/pt070361",
# "10.1007/s11095-008-9626-z",
# "10.4161/hv.25639",
# "10.1208/pt060474",
# "10.1208/s12249-009-9257-7",
# "10.1208/s12249-010-9528-3",
# "10.1208/s12249-010-9440-x",
# "10.1208/s12249-009-9190-9",
# "10.3109/03639045.2012.763137",
# "10.1208/pt070244",
# "10.1002/adma.201804693",
# "10.1208/s12249-009-9234-1",
# "10.1208/s12249-014-0072-4",
# "10.1208/s12249-015-0366-1",
# "10.1208/s12249-009-9220-7",
# "10.1007/s11095-008-9594-3",
# "10.1208/s12249-011-9659-1",
# "10.1208/s12249-011-9672-4",
# "10.1208/pt070372",
# "10.3109/10717544.2014.923068",
# "10.1208/pt0801012",
# "10.1021/acs.molpharmaceut.8b00802",
# "10.1007/s11095-013-1252-8",
# "10.1208/s12249-009-9268-4",
# "10.1208/pt0802028",
# "10.1208/s12249-008-9131-z",
# "10.1208/s12249-009-9213-6",
# "10.1111/bph.13149",
# "10.1208/s12249-008-9082-4",
# "10.1124/jpet.118.254672",
# "10.1208/pt020310",
# "10.1208/s12249-014-0096-9",
# "10.1208/s12249-014-0103-1",
# "10.1007/s00270-018-1899-y",
# "10.1208/s12249-009-9306-2",
# "10.1208/s12249-013-9990-9",
# "10.1208/s12249-011-9742-7",
# "10.1208/s12249-009-9242-1",
# "10.1208/s12249-008-9053-9",
# "10.1049/iet-nbt.2019.0035",
# "10.1208/s12249-009-9286-2",
# "10.1208/s12249-008-9037-9",
# "10.1159/000522380",
# "10.1208/s12249-009-9340-0",
# "10.1177/0148607116640275",
# "10.1007/s42770-019-00203-1",
# "10.1124/jpet.118.252809",
# "10.1208/s12249-009-9192-7",
# "10.4103/ijp.ijp_370_23",
# "10.2147/DDDT.S103169",
# "10.1080/10837450.2019.1578372",
# "10.1208/aapsj0903041",
# "10.1208/pt0802042",
# "10.1128/aac.40.6.1467",
# "10.1159/000511443",
# "10.1208/s12249-014-0278-5",
# "10.17305/bjbms.2010.2697",
# "10.1208/s12249-015-0308-y",
# "10.1080/20415990.2024.2363136",
# "10.3109/1061186X.2015.1087529",
# "10.1208/s12249-009-9331-1",
# "10.1049/iet-nbt.2016.0116",
# "10.1208/s12249-015-0305-1",
# "10.1208/s12249-010-9457-1",
# "10.1208/s12249-018-1287-6",
# "10.1021/acsnano.9b07214",
# "10.1007/s11095-018-2391-8",
# "10.1631/jzus.B1600389",
# "10.3109/02652048.2013.814728",
# "10.1208/s12249-009-9186-5",
# "10.1152/ajpheart.00471.2017",
# "10.1007/s42770-019-00201-3",
# "10.1208/s12249-010-9507-8",
# "10.1021/mp3004379",
# "10.1049/iet-nbt.2017.0189",
# "10.1049/iet-nbt.2019.0148",
# "10.1208/aapsj070488",
# "10.1208/pt010432",
# "10.1007/s11095-008-9744-7",
# "10.1208/s12249-008-9080-6",
# "10.1021/acsnano.2c00199",
# "10.3791/53489",
# "10.1158/1535-7163.MCT-18-1046",
# "10.1208/s12249-011-9653-7",
# "10.3791/51874",
# "10.1208/s12249-014-0214-8",
# "10.1208/pt070127",
# "10.1080/20415990.2024.2363635",
# "10.1208/s12249-008-9070-8",
# "10.1208/s12248-013-9557-4",
# "10.1208/s12249-011-9661-7",
# "10.1208/s12248-012-9433-7",
# "10.2478/s11658-006-0037-z",
# "10.1208/s12249-009-9193-6",
# "10.1208/s12249-015-0354-5",
# "10.1208/s12249-010-9426-8"]
# # --- Helper Functions (Stateless) ---

# def get_pdf_link_unpaywall(doi):
#     """Strategy A: Ask Unpaywall for a free legal link."""
#     if not doi: return None
#     api_url = f"https://api.unpaywall.org/v2/{doi}?email={EMAIL_FOR_UNPAYWALL}"
#     try:
#         r = crequests.get(api_url, timeout=10)
#         if r.status_code == 200:
#             data = r.json()
#             if data.get('is_oa') and data.get('best_oa_location'):
#                 pdf_url = data['best_oa_location'].get('url_for_pdf')
#                 if pdf_url: return pdf_url
#     except Exception:
#         pass
#     return None

# def get_pdf_link_meta_tag(doi):
#     """Strategy B: Visit the page and scrape the <meta name="citation_pdf_url"> tag."""
#     if not doi: return None
#     url = f"https://doi.org/{doi}"
#     try:
#         response = crequests.get(url, impersonate="chrome120", allow_redirects=True, timeout=15)
#         if response.status_code == 200:
#             soup = BeautifulSoup(response.content, "html.parser")
            
#             # Standard academic meta tag
#             meta_tag = soup.find("meta", attrs={"name": "citation_pdf_url"})
#             if meta_tag and meta_tag.get("content"):
#                 return meta_tag.get("content")
                
#             # Fallback: simple PDF anchor check
#             for a in soup.find_all("a", href=True):
#                 href = a['href'].lower()
#                 if href.endswith(".pdf") and "suppl" not in href:
#                     if href.startswith("http"): return a['href']
#                     return response.url.rstrip("/") + "/" + a['href'].lstrip("/")
#     except Exception:
#         pass
#     return None

# def download_and_extract(pdf_url):
#     """Downloads PDF binary and extracts text."""
#     try:
#         r = crequests.get(pdf_url, impersonate="chrome120", timeout=30)
#         if r.status_code == 200 and r.content.startswith(b"%PDF"):
#             with io.BytesIO(r.content) as f:
#                 reader = PdfReader(f)
#                 text = []
#                 for page in reader.pages:
#                     extracted = page.extract_text()
#                     if extracted: text.append(extracted)
#                 return "\n".join(text)
#     except Exception:
#         pass
#     return None

# # --- New Worker Function for Concurrency ---

# def process_single_article(data):
#     """
#     Worker function to process ONE article.
#     Returns a tuple: (status, pmid, publisher, doi, content_or_error)
#     """
#     pmid, publisher, doi = data
    
#     # 1. Validation
#     if not doi or doi == "None":
#         return ("SKIP", pmid, publisher, doi, "No DOI")
    
#     # 2. Random Sleep (Politeness inside worker)
#     # Even in parallel, this helps stagger the hits slightly
#     time.sleep(random.uniform(1, 3)) 

#     # 3. Try Unpaywall
#     pdf_url = get_pdf_link_unpaywall(doi)
    
#     # 4. Try Meta Tag
#     if not pdf_url:
#         pdf_url = get_pdf_link_meta_tag(doi)

#     # 5. Download & Extract
#     if pdf_url:
#         content = download_and_extract(pdf_url)
#         if content:
#             return ("SUCCESS", pmid, publisher, doi, content)
    
#     return ("FAIL", pmid, publisher, doi, "Could not access/extract PDF")

# # --- Main Execution ---

# if __name__ == "__main__":
#     print(f"Starting Concurrent Scraping for {len(SOURCE_DATA)} articles...")
#     print(f"Batch Size (Max Workers): {BATCH_SIZE}")

#     success_count = 0
#     failed_articles = [] 

#     # We open the file once. The main thread will handle writing to avoid race conditions.
#     with open(OUTPUT_FILE, "w", encoding="utf-8") as f, \
#          concurrent.futures.ThreadPoolExecutor(max_workers=BATCH_SIZE) as executor:

#         # Submit all tasks
#         # future_to_doi keeps track of which task is which
#         future_to_article = {executor.submit(process_single_article, item): item for item in SOURCE_DATA}

#         # Process results as they complete
#         for future in concurrent.futures.as_completed(future_to_article):
#             status, pmid, publisher, doi, result_payload = future.result()

#             if status == "SUCCESS":
#                 # result_payload is the content string
#                 header = f"\n\n{'='*50}\nPMID: {pmid}\nDOI: {doi}\nPUBLISHER: {publisher}\n{'='*50}\n"
#                 f.write(header)
#                 f.write(result_payload)
#                 f.flush() # Ensure it's written to disk immediately
#                 print(f"    [SUCCESS] {doi}")
#                 success_count += 1
            
#             elif status == "FAIL":
#                 print(f"    [FAILED] {doi}")
#                 failed_articles.append((pmid, publisher, doi))
            
#             elif status == "SKIP":
#                 print(f"    [SKIPPED] PMID {pmid} (No DOI)")
#                 failed_articles.append((pmid, publisher, "No DOI"))

#     # --- Final Reporting ---
#     with open(FAILED_LOG_FILE, "w", encoding="utf-8") as log:
#         log.write("PMID, Publisher, DOI\n")
#         for item in failed_articles:
#             log.write(f"{item[0]}, {item[1]}, {item[2]}\n")

#     print("\n" + "="*30)
#     print(f"SCRAPING COMPLETE")
#     print(f"Total Processed: {len(SOURCE_DATA)}")
#     print(f"Successful:      {success_count}")
#     print(f"Failed:          {len(failed_articles)}")
#     print(f"Content File:    {OUTPUT_FILE}")
#     print(f"Failure Log:     {FAILED_LOG_FILE}")
#     print("="*30)



from curl_cffi import requests as crequests
from bs4 import BeautifulSoup
from pypdf import PdfReader
import io
import time
import random
import concurrent.futures

# --- Configuration ---
BATCH_SIZE = 5  # Concurrent workers
EMAIL_FOR_UNPAYWALL = "howard.kuo@vernus.ai"

# # --- Configuration ---
# BATCH_SIZE = 5 # How many articles to download at the same time
# OUTPUT_FILE = "withpmcidstillmissing_196_upayrwall.txt"
# FAILED_LOG_FILE = "withpmcidstillmissing_196_upayrwall.txt"
# EMAIL_FOR_UNPAYWALL = "howard.kuo@vernus.ai" 
# Output Files
CONTENT_FILE = "283_without_pmcid_still_missing_content.txt"
SUCCESS_LIST_FILE = "283_without_pmcid_still_missing_success_dois.txt"
FAILED_LIST_FILE = "283_without_pmcid_still_missing_failed_dois.txt"



# YOUR DOI LIST
# TARGET_DOIS = [
#   "10.1002/jps.22475",
# "10.1208/s12249-011-9721-z",
# "10.1208/s12249-013-9996-3",
# "10.1039/d3bm01765f",
# "10.1208/s12249-010-9455-3",
# "10.1208/s12249-014-0280-y",
# "10.1208/s12249-015-0370-5",
# "10.1007/s13346-017-0435-y",
# "10.1208/s12249-008-9178-x",
# "10.1208/s12249-010-9438-4",
# "10.1111/j.2042-7158.2011.01376.x",
# "10.1208/s12249-010-9432-x",
# "10.1007/s11095-014-1370-y",
# "10.1021/acsnano.5b01696",
# "10.1208/s12249-011-9675-1",
# "10.3109/02652048.2010.520093",
# "10.1208/pt010105",
# "10.1208/s12249-010-9486-9",
# "10.1208/s12249-012-9855-7",
# "10.1080/10837450.2020.1725893",
# "10.1007/s00280-011-1749-y",
# "10.1021/acsami.6b08153",
# "10.1089/jamp.2009.0766",
# "10.1049/iet-nbt.2018.5248",
# "10.1117/1.JBO.18.10.101312",
# "10.2217/nnm.14.4",
# "10.1208/s12249-011-9680-4",
# "10.1007/s13346-019-00619-0",
# "10.1208/pt070377",
# "10.1208/s12249-010-9445-5",
# "10.1208/s12249-014-0147-2",
# "10.1177/0884533617722759",
# "10.1208/pt0804116",
# "10.1208/pt020205",
# "10.1208/s12249-008-9089-x",
# "10.1208/pt030103",
# "10.1208/pt070489",
# "10.1208/s12249-008-9063-7",
# "10.1128/AEM.72.3.2280-2282.2006",
# "10.1002/jps.24053",
# "10.1007/s11095-018-2495-1",
# "10.1208/s12249-018-0973-8",
# "10.1080/17435889.2024.2386923",
# "10.1208/s12249-010-9453-5",
# "10.1208/s12249-014-0238-0",
# "10.1208/s12249-010-9510-0",
# "10.1002/mabi.201100107",
# "10.1007/s13346-024-01620-y",
# "10.1208/s12249-012-9847-7",
# "10.1208/s12249-012-9821-4",
# "10.1007/s11095-011-0474-x",
# "10.1021/mp300319m",
# "10.1007/BF02830623",
# "10.1208/pt040332",
# "10.1208/s12249-014-0258-9",
# "10.1208/s12249-010-9568-8",
# "10.1208/s12249-010-9478-9",
# "10.1208/s12249-007-9022-8",
# "10.1049/iet-nbt.2018.0006",
# "10.3109/10837450.2012.737806",
# "10.1128/aac.28.1.103",
# "10.1208/s12249-007-9016-6",
# "10.1208/s12249-011-9583-4",
# "10.1208/aapsj060326",
# "10.1208/s12249-011-9663-5",
# "10.1208/s12249-009-9235-0",
# "10.1208/s12249-009-9328-9",
# "10.1002/jps.23450",
# "10.1208/s12249-008-9183-0",
# "10.1208/s12249-008-9036-x",
# "10.1208/s12249-007-9023-7",
# "10.3748/wjg.v16.i27.3437",
# "10.1093/jbcr/irab118",
# "10.1208/s12249-008-9172-3",
# "10.1208/s12249-009-9218-1",
# "10.1208/s12249-014-0199-3",
# "10.1007/s00280-015-2851-3",
# "10.1208/s12249-021-02108-5",
# "10.1002/adhm.202101427",
# "10.1089/can.2022.0176",
# "10.1208/s12249-013-0048-9",
# "10.1073/pnas.1310214110",
# "10.1021/bm4015232",
# "10.1089/jamp.2015.1235",
# "10.1002/jps.21719",
# "10.1208/s12249-009-9315-1",
# "10.1021/mp4005029",
# "10.1007/s11095-022-03317-8",
# "10.1208/pt010317",
# "10.1007/s11095-018-2349-x",
# "10.1208/s12249-009-9284-4",
# "10.1049/iet-nbt.2017.0104",
# "10.1080/21645515.2015.1046660",
# "10.1208/s12249-009-9233-2",
# "10.1208/s12249-009-9287-1",
# "10.1208/pt050342",
# "10.1136/ejhpharm-2020-002534",
# "10.1007/s13346-020-00758-9",
# "10.1002/jps.22488",
# "10.1208/s12249-012-9762-y",
# "10.1208/pt070361",
# "10.1007/s11095-008-9626-z",
# "10.4161/hv.25639",
# "10.1208/pt060474",
# "10.1208/s12249-009-9257-7",
# "10.1208/s12249-010-9528-3",
# "10.1208/s12249-010-9440-x",
# "10.1208/s12249-009-9190-9",
# "10.3109/03639045.2012.763137",
# "10.1208/pt070244",
# "10.1002/adma.201804693",
# "10.1208/s12249-009-9234-1",
# "10.1208/s12249-014-0072-4",
# "10.1208/s12249-015-0366-1",
# "10.1208/s12249-009-9220-7",
# "10.1007/s11095-008-9594-3",
# "10.1208/s12249-011-9659-1",
# "10.1208/s12249-011-9672-4",
# "10.1208/pt070372",
# "10.3109/10717544.2014.923068",
# "10.1208/pt0801012",
# "10.1021/acs.molpharmaceut.8b00802",
# "10.1007/s11095-013-1252-8",
# "10.1208/s12249-009-9268-4",
# "10.1208/pt0802028",
# "10.1208/s12249-008-9131-z",
# "10.1208/s12249-009-9213-6",
# "10.1111/bph.13149",
# "10.1208/s12249-008-9082-4",
# "10.1124/jpet.118.254672",
# "10.1208/pt020310",
# "10.1208/s12249-014-0096-9",
# "10.1208/s12249-014-0103-1",
# "10.1007/s00270-018-1899-y",
# "10.1208/s12249-009-9306-2",
# "10.1208/s12249-013-9990-9",
# "10.1208/s12249-011-9742-7",
# "10.1208/s12249-009-9242-1",
# "10.1208/s12249-008-9053-9",
# "10.1049/iet-nbt.2019.0035",
# "10.1208/s12249-009-9286-2",
# "10.1208/s12249-008-9037-9",
# "10.1159/000522380",
# "10.1208/s12249-009-9340-0",
# "10.1177/0148607116640275",
# "10.1007/s42770-019-00203-1",
# "10.1124/jpet.118.252809",
# "10.1208/s12249-009-9192-7",
# "10.4103/ijp.ijp_370_23",
# "10.2147/DDDT.S103169",
# "10.1080/10837450.2019.1578372",
# "10.1208/aapsj0903041",
# "10.1208/pt0802042",
# "10.1128/aac.40.6.1467",
# "10.1159/000511443",
# "10.1208/s12249-014-0278-5",
# "10.17305/bjbms.2010.2697",
# "10.1208/s12249-015-0308-y",
# "10.1080/20415990.2024.2363136",
# "10.3109/1061186X.2015.1087529",
# "10.1208/s12249-009-9331-1",
# "10.1049/iet-nbt.2016.0116",
# "10.1208/s12249-015-0305-1",
# "10.1208/s12249-010-9457-1",
# "10.1208/s12249-018-1287-6",
# "10.1021/acsnano.9b07214",
# "10.1007/s11095-018-2391-8",
# "10.1631/jzus.B1600389",
# "10.3109/02652048.2013.814728",
# "10.1208/s12249-009-9186-5",
# "10.1152/ajpheart.00471.2017",
# "10.1007/s42770-019-00201-3",
# "10.1208/s12249-010-9507-8",
# "10.1021/mp3004379",
# "10.1049/iet-nbt.2017.0189",
# "10.1049/iet-nbt.2019.0148",
# "10.1208/aapsj070488",
# "10.1208/pt010432",
# "10.1007/s11095-008-9744-7",
# "10.1208/s12249-008-9080-6",
# "10.1021/acsnano.2c00199",
# "10.3791/53489",
# "10.1158/1535-7163.MCT-18-1046",
# "10.1208/s12249-011-9653-7",
# "10.3791/51874",
# "10.1208/s12249-014-0214-8",
# "10.1208/pt070127",
# "10.1080/20415990.2024.2363635",
# "10.1208/s12249-008-9070-8",
# "10.1208/s12248-013-9557-4",
# "10.1208/s12249-011-9661-7",
# "10.1208/s12248-012-9433-7",
# "10.2478/s11658-006-0037-z",
# "10.1208/s12249-009-9193-6",
# "10.1208/s12249-015-0354-5",
# "10.1208/s12249-010-9426-8"]

TARGET_DOIS = [                                                                   
    "10.1248/cpb.38.2797",
    "10.3109/21691401.2014.966192",
    "10.1080/03639045.2023.2183724",
    "10.1111/bcp.15875",
    "10.2133/dmpk.20.244",
    "10.1093/bja/56.6.617",
    "10.1248/bpb.b15-00110",
    "10.2478/v10007-007-0025-5",
    "10.18433/j3830g",
    "10.3109/10717544.2014.966925",
    "10.1248/bpb.22.1331",
    "10.1248/bpb.17.1526",
    "10.3109/10717544.2014.898713",
    "10.1080/21691401.2017.1324465",
    "10.3109/10717544.2013.878003",
    "10.5650/jos.ess17253",
    "10.1111/j.1365-2044.1996.tb12607.x",
    "10.62958/j.cjap.2024.016",
    "10.1248/cpb.c14-00231",
    "10.1271/bbb.67.1376",
    "10.3109/10717544.2014.916764",
    "10.1248/cpb.58.1332",
    "10.3109/21691401.2014.887018",
    "10.1248/bpb.34.1179",
    "10.5650/jos.ess20070",
    "10.20960/nh.04931",
    "10.3109/10717544.2014.893382",
    "10.5650/jos.ess14175",
    "10.2478/v10007-012-0022-1",
    "10.5650/jos.ess24118",
    "10.3109/10717544.2010.522613",
    "10.5650/jos.ess16018",
    "10.5650/jos.ess21265",
    "10.5650/jos.ess14177",
    "10.1080/10837450.2025.2537128",
    "10.3109/10717544.2014.898347",
    "10.1515/acph-2015-0009",
    "10.2478/v10007-007-0009-5",
    "10.1093/bja/57.8.736",
    "10.1248/bpb.26.994",
    "10.3109/10717544.2014.883117",
    "10.5582/ddt.2021.01004",
    "10.5582/ddt.2025.01000",
    "10.1080/10717540500455983",
    "10.1093/bja/68.2.193",
    "10.1248/cpb.56.1335",
    "10.1208/s12249-018-1215-9",
    "10.1248/cpb.58.639",
    "10.3177/jnsv.56.41",
    "10.3109/10717544.2011.589088",
    "10.1034/j.1600-6143.2002.020116.x",
    "10.1021/acs.jafc.0c06409",
    "10.2478/acph-2018-0035",
    "10.3109/10717544.2012.762434",
    "10.5301/JABFM.2012.10438",
    "10.5582/ddt.2017.01029",
    "10.1590/0001-3765202420220448",
    "10.1248/yakushi.130.103",
    "10.3109/10717544.2013.878857",
    "10.3109/10717544.2013.867382",
    "10.3109/10717544.2014.948643",
    "10.2478/acph-2020-0012",
    "10.1248/bpb.23.1341",
    "10.3109/10717544.2011.600784",
    "10.1080/10717540500313109",
    "10.1080/02652040701814140",
    "10.1080/10717540802481349",
    "10.1248/bpb.b17-00162",
    "10.3109/10717544.2016.1153747",
    "10.1248/cpb.59.321",
    "10.2133/dmpk.20.257",
    "10.1080/10717540802039089",
    "10.1039/c4nr05593d",
    "10.1080/10717544.2016.1223225",
    "10.1248/bpb.27.418",
    "10.3109/10717544.2014.885616",
    "10.1080/21691401.2017.1397002",
    "10.1248/cpb.c13-00051",
    "10.5650/jos.ess18209",
    "10.1248/cpb.c25-00382",
    "10.31083/j.fbl2812349",
    "10.1213/ANE.0000000000000558",
    "10.1093/bja/74.5.553",
    "10.1248/cpb.c16-00035",
    "10.1007/s13346-017-0390-7",
    "10.1023/a:1016001111731",
    "10.2478/v10007-011-0013-7",
    "10.1021/acs.molpharmaceut.8b00609",
    "10.1080/10717540802006864",
    "10.1080/21691401.2019.1581791",
    "10.1007/s10856-008-3666-0",
    "10.3109/10717544.2011.604686",
    "10.1023/a:1011009117586",
    "10.17219/acem/124439",
    "10.1080/21691401.2017.1337024",
    "10.3109/10717544.2011.595842",
    "10.1248/cpb.c18-00930",
    "10.7399/fh.10954",
    "10.1080/10717540600559478",
    "10.1248/cpb.58.16",
    "10.1080/21691401.2017.1301459",
    "10.1002/1873-3468.14936",
    "10.2133/dmpk.21.45",
    "10.1248/bpb.b17-00964",
    "10.1248/cpb.56.70",
    "10.1590/1519-6984.292718",
    "10.3109/10717544.2015.1088597",
    "10.1515/acph-2015-0012",
    "10.31083/j.fbe1603025",
    "10.18433/j3vp5h",
    "10.5650/jos.ess19250",
    "10.1016/j.ijpharm.2012.02.028",
    "10.1590/0001-3765201520130436",
    "10.3109/10717544.2014.923067",
    "10.5650/jos.59.395",
    "10.1248/cpb.41.599",
    "10.1248/bpb.31.118",
    "10.1021/acs.molpharmaceut.8b00097",
    "10.3109/10717544.2015.1054051",
    "10.1021/acsnano.5b02702",
    "10.1248/bpb.34.300",
    "10.5582/ddt.2020.03118",
    "10.1080/10717540590925726",
    "10.1007/s10856-013-4874-9",
    "10.1080/02652048.2023.2175924",
    "10.5650/jos.ess14194",
    "10.3109/10717540903431586",
    "10.1080/21691401.2016.1175444",
    "10.1248/cpb.56.156",
    "10.3109/10717544.2014.907842",
    "10.3109/21691401.2016.1161640",
    "10.1080/21691401.2016.1226178",
    "10.1515/acph-2017-0036",
    "10.3109/10717544.2010.483256",
    "10.1248/yakushi.128.595",
    "10.1248/cpb.c18-00614",
    "10.3109/10717544.2013.861659",
    "10.2478/v10007-008-0001-8",
    "10.2169/internalmedicine.44.149",
    "10.1080/10717540701606467",
    "10.3109/10717544.2013.879398",
    "10.1248/cpb.58.1015",
    "10.3109/21691401.2016.1161637",
    "10.3109/10717544.2013.859186",
    "10.1024/0300-9831.78.3.156",
    "10.1211/0022357021778736",
    "10.1271/bbb.67.1864",
    "10.1080/10717540601067786",
    "10.1248/cpb.58.11",
    "10.3109/10717544.2014.900154",
    "10.62958/j.cjap.2025.020",
    "10.1080/10717540802481646",
    "10.1248/cpb.47.492",
    "10.1080/10717540500313430",
    "10.3109/21691401.2016.1161639",
    "10.1080/21691401.2019.1683567",
    "10.1080/10717540802328599",
    "10.1248/bpb.31.673",
    "10.3109/10717544.2014.974001",
    "10.1080/10717540601067760",
    "10.1248/yakushi.131.1835",
    "10.20960/nh.252",
    "10.1248/cpb.50.87",
    "10.3109/10717544.2016.1145306",
    "10.1111/j.1525-1438.2006.00557.x",
    "10.3109/21691401.2015.1012261",
    "10.1080/21691401.2016.1196457",
    "10.2478/v10007-011-0022-6",
    "10.1515/acph-2015-0003",
    "10.1590/1519-6984.281236",
    "10.1248/bpb.b23-00066",
    "10.2133/dmpk.19.62",
    "10.2478/v10007-007-0034-4",
    "10.1080/10717540802481380",
    "10.1248/yakushi.15-00237",
    "10.2478/acph-2013-0013",
    "10.3109/21691401.2015.1042109",
    "10.3109/10717544.2014.903011",
    "10.3177/jnsv.65.S54",
    "10.3109/10717544.2014.920430",
    "10.3923/pjbs.2012.141.146",
    "10.1111/j.1365-2044.1987.tb03080.x",
    "10.1515/znc-2019-0229",
    "10.1248/cpb.c13-00599",
    "10.1080/09546634.2019.1668907",
    "10.4103/jcrt.jcrt_278_22",
    "10.2460/ajvr.2004.65.752",
    "10.1248/bpb.b19-00368",
    "10.3109/10717544.2012.704094",
    "10.3109/10717544.2015.1028603",
    "10.1248/yakushi.129.1559",
    "10.1080/713840366",
    "10.1093/bja/66.1.66",
    "10.1080/15227950290097633",
    "10.3109/10717544.2013.861883",
    "10.1080/10717544.2016.1183720",
    "10.1080/10717540701202960",
    "10.2133/dmpk.DMPK-11-RG-041",
    "10.1080/21691401.2017.1396996",
    "10.1080/21691401.2018.1477789",
    "10.3109/10717544.2014.893381",
    "10.2478/v10007-010-0022-y",
    "10.1046/j.1523-1755.1998.00194.x",
    "10.1248/yakushi.129.1537",
    "10.3109/10717544.2014.914601",
    "10.1248/cpb.c15-00516",
    "10.3109/10717544.2016.1141260",
    "10.1248/cpb.c15-00782",
    "10.5650/jos.ess15183",
    "10.1080/10717540500398092",
    "10.17219/acem/22636",
    "10.1248/cpb.55.800",
    "10.1111/j.1600-0625.2009.01001.x",
    "10.3109/10717544.2014.898109",
    "10.3109/10717544.2014.950768",
    "10.1080/21691401.2017.1313262",
    "10.1055/a-1699-3284",
    "10.3109/21691401.2016.1160915",
    "10.1248/bpb.b17-00026",
    "10.3109/10717544.2010.528068",
    "10.1248/bpb.29.508",
    "10.3109/10717544.2014.891273",
    "10.1590/0001-3765202420230373",
    "10.2298/vsp1304374m",
    "10.1080/10717540490494096",
    "10.1080/10717540500309172",
    "10.3109/10717544.2014.996833",
    "10.18433/jpps30097",
    "10.1248/bpb.26.1591",
    "10.1248/cpb.c16-00562",
    "10.1248/bpb.31.668",
    "10.1271/bbb.59.492",
    "10.1038/sj.jid.5700485",
    "10.1080/10717540802006377",
    "10.1248/bpb.31.939",
    "10.1248/cpb.53.1246",
    "10.1080/09546634.2022.2071823",
    "10.1080/14737167.2025.2556693",
    "10.1248/cpb.c12-00983",
    "10.3109/21691401.2014.984301",
    "10.1080/21691401.2018.1489826",
    "10.1080/10717540600740045",
    "10.1080/10717540500176829",
    "10.1111/j.1365-2044.1984.tb06425.x",
    "10.3109/10717544.2014.898715",
    "10.5650/jos.59.223",
    "10.3109/10717544.2014.920432",
    "10.1080/107175401750177061",
    "10.1248/cpb.c17-00542",
    "10.3109/10717544.2013.868557",
    "10.1080/21691401.2016.1260579",
    "10.1080/10717540701202937",
    "10.1055/a-2517-4967",
    "10.7314/apjcp.2015.16.18.8259",
    "10.1248/cpb.c14-00326",
    "10.1248/cpb.58.1455",
    "10.3109/10717544.2013.838716",
    "10.1248/bpb.31.662",
    "10.3109/10717544.2013.866992",
    "10.3109/10717544.2014.904021",
    "10.1248/cpb.c14-00696",
    "10.3109/13880209.2015.1021817",
    "10.1248/cpb.c12-00502",
    "10.2478/acph-2019-0054",
    "10.5650/jos.59.667",
    "10.3109/10717544.2015.1128496",
    "10.3109/10717544.2014.933284",
    "10.18433/j38p4v",
    "10.3109/21691401.2014.937869",
    "10.3109/10717544.2015.1077290",
    "10.1358/mf.2008.30.4.1185802",
    "10.2478/acph-2013-0019",
    "10.3109/21691401.2015.1111229",
    "10.1080/10717544.2016.1223210",
    "10.1248/cpb.c14-00110",
    "10.3109/10717544.2014.936987",
    "10.3109/21691401.2014.962741",
    "10.1080/02652040400026350",
    "10.3109/10717544.2014.891270",
    "10.3109/10717544.2013.835007",
    "10.1158/1535-7163.MCT-06-0289",
    "10.1111/anae.13625",
    "10.62958/j.cjap.2024.021",
]
# --- Helper Functions ---

def get_pdf_info_unpaywall(doi):
    """Returns (pdf_url, title)"""
    if not doi: return None, None
    api_url = f"https://api.unpaywall.org/v2/{doi}?email={EMAIL_FOR_UNPAYWALL}"
    try:
        r = crequests.get(api_url, timeout=10)
        if r.status_code == 200:
            data = r.json()
            title = data.get('title', '')
            if data.get('is_oa') and data.get('best_oa_location'):
                pdf_url = data['best_oa_location'].get('url_for_pdf')
                return pdf_url, title
            return None, title
    except Exception:
        pass
    return None, None

def get_pdf_info_scrape(doi):
    """Returns (pdf_url, title) by visiting the page"""
    if not doi: return None, None
    url = f"https://doi.org/{doi}"
    try:
        response = crequests.get(url, impersonate="chrome120", allow_redirects=True, timeout=15)
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, "html.parser")
            
            # Extract Title
            title = ""
            meta_title = soup.find("meta", attrs={"name": "citation_title"})
            if meta_title: 
                title = meta_title.get("content", "")
            if not title:
                if soup.title: title = soup.title.string.strip()

            # Extract PDF URL
            pdf_url = None
            meta_pdf = soup.find("meta", attrs={"name": "citation_pdf_url"})
            if meta_pdf and meta_pdf.get("content"):
                pdf_url = meta_pdf.get("content")
            
            # Fallback Anchor Check
            if not pdf_url:
                for a in soup.find_all("a", href=True):
                    href = a['href'].lower()
                    if href.endswith(".pdf") and "suppl" not in href:
                        if href.startswith("http"): 
                            pdf_url = a['href']
                        else:
                            pdf_url = response.url.rstrip("/") + "/" + a['href'].lstrip("/")
                        break
            
            return pdf_url, title
    except Exception:
        pass
    return None, None

def download_and_extract(pdf_url):
    try:
        r = crequests.get(pdf_url, impersonate="chrome120", timeout=30)
        if r.status_code == 200 and r.content.startswith(b"%PDF"):
            with io.BytesIO(r.content) as f:
                reader = PdfReader(f)
                text = []
                for page in reader.pages:
                    extracted = page.extract_text()
                    if extracted: text.append(extracted)
                return "\n".join(text)
    except Exception:
        pass
    return None

def process_single_article(doi):
    """Worker function for a single DOI."""
    if not doi: return ("FAIL", doi, "No DOI", None)
    
    time.sleep(random.uniform(1, 3)) # Politeness

    # 1. Try Unpaywall
    pdf_url, title = get_pdf_info_unpaywall(doi)
    
    # 2. Try Scrape if URL missing
    if not pdf_url:
        scrape_url, scrape_title = get_pdf_info_scrape(doi)
        if scrape_url: pdf_url = scrape_url
        if not title and scrape_title: title = scrape_title

    # Clean title for output
    if not title: title = "Title Not Found"
    title = title.replace('"', "'").replace('\n', ' ').strip()

    # 3. Download
    if pdf_url:
        content = download_and_extract(pdf_url)
        if content:
            return ("SUCCESS", doi, title, content)
    
    return ("FAIL", doi, title, None)

def format_list_output(items):
    """
    Formats list of tuples (doi, title) into:
    "doi", "title"
    """
    lines = []
    for doi, title in items:
        lines.append(f'"{doi}", "{title}"')
    return ",\n".join(lines)

# --- Main Execution ---

if __name__ == "__main__":
    print(f"Starting Scraping for {len(TARGET_DOIS)} DOIs...")
    
    successful_items = [] # Stores (doi, title)
    failed_items = []     # Stores (doi, title)

    with open(CONTENT_FILE, "w", encoding="utf-8") as f_content, \
         concurrent.futures.ThreadPoolExecutor(max_workers=BATCH_SIZE) as executor:

        future_to_doi = {executor.submit(process_single_article, doi): doi for doi in TARGET_DOIS}

        for future in concurrent.futures.as_completed(future_to_doi):
            status, doi, title, content = future.result()

            if status == "SUCCESS":
                print(f" [SUCCESS] {doi}")
                successful_items.append((doi, title))
                
                # Write content to file
                f_content.write(f"\n\n{'='*50}\nDOI: {doi}\nTITLE: {title}\n{'='*50}\n")
                f_content.write(content)
                f_content.flush()
            else:
                print(f" [FAILED]  {doi}")
                failed_items.append((doi, title))

    # --- Final Output ---
    success_output = format_list_output(successful_items)
    failed_output = format_list_output(failed_items)

    print("\n" + "="*40)
    print("FINAL RESULTS")
    print("="*40)
    
    print(f"\n✅ SUCCESS ({len(successful_items)}):")
    # print(success_output) # Optional: Don't print massive list to console
    
    print(f"\n❌ FAILED ({len(failed_items)}):")
    # print(failed_output)

    # Save to files
    with open(SUCCESS_LIST_FILE, "w", encoding="utf-8") as f: f.write(success_output)
    with open(FAILED_LIST_FILE, "w", encoding="utf-8") as f: f.write(failed_output)

    print(f"\nSaved SUCCESS list to: {SUCCESS_LIST_FILE}")
    print(f"Saved FAILED list to:  {FAILED_LIST_FILE}")
    print(f"Saved CONTENT to:      {CONTENT_FILE}")