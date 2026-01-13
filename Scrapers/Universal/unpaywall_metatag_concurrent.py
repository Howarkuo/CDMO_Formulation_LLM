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
CONTENT_FILE = "withpmcidstillmissing_196_upayrwall_content.txt"
SUCCESS_LIST_FILE = "withpmcidstillmissing_196_upayrwall_success_dois.txt"
FAILED_LIST_FILE = "withpmcidstillmissing_196_upayrwall_failed_dois.txt"



# YOUR DOI LIST
TARGET_DOIS = [
  "10.1002/jps.22475",
"10.1208/s12249-011-9721-z",
"10.1208/s12249-013-9996-3",
"10.1039/d3bm01765f",
"10.1208/s12249-010-9455-3",
"10.1208/s12249-014-0280-y",
"10.1208/s12249-015-0370-5",
"10.1007/s13346-017-0435-y",
"10.1208/s12249-008-9178-x",
"10.1208/s12249-010-9438-4",
"10.1111/j.2042-7158.2011.01376.x",
"10.1208/s12249-010-9432-x",
"10.1007/s11095-014-1370-y",
"10.1021/acsnano.5b01696",
"10.1208/s12249-011-9675-1",
"10.3109/02652048.2010.520093",
"10.1208/pt010105",
"10.1208/s12249-010-9486-9",
"10.1208/s12249-012-9855-7",
"10.1080/10837450.2020.1725893",
"10.1007/s00280-011-1749-y",
"10.1021/acsami.6b08153",
"10.1089/jamp.2009.0766",
"10.1049/iet-nbt.2018.5248",
"10.1117/1.JBO.18.10.101312",
"10.2217/nnm.14.4",
"10.1208/s12249-011-9680-4",
"10.1007/s13346-019-00619-0",
"10.1208/pt070377",
"10.1208/s12249-010-9445-5",
"10.1208/s12249-014-0147-2",
"10.1177/0884533617722759",
"10.1208/pt0804116",
"10.1208/pt020205",
"10.1208/s12249-008-9089-x",
"10.1208/pt030103",
"10.1208/pt070489",
"10.1208/s12249-008-9063-7",
"10.1128/AEM.72.3.2280-2282.2006",
"10.1002/jps.24053",
"10.1007/s11095-018-2495-1",
"10.1208/s12249-018-0973-8",
"10.1080/17435889.2024.2386923",
"10.1208/s12249-010-9453-5",
"10.1208/s12249-014-0238-0",
"10.1208/s12249-010-9510-0",
"10.1002/mabi.201100107",
"10.1007/s13346-024-01620-y",
"10.1208/s12249-012-9847-7",
"10.1208/s12249-012-9821-4",
"10.1007/s11095-011-0474-x",
"10.1021/mp300319m",
"10.1007/BF02830623",
"10.1208/pt040332",
"10.1208/s12249-014-0258-9",
"10.1208/s12249-010-9568-8",
"10.1208/s12249-010-9478-9",
"10.1208/s12249-007-9022-8",
"10.1049/iet-nbt.2018.0006",
"10.3109/10837450.2012.737806",
"10.1128/aac.28.1.103",
"10.1208/s12249-007-9016-6",
"10.1208/s12249-011-9583-4",
"10.1208/aapsj060326",
"10.1208/s12249-011-9663-5",
"10.1208/s12249-009-9235-0",
"10.1208/s12249-009-9328-9",
"10.1002/jps.23450",
"10.1208/s12249-008-9183-0",
"10.1208/s12249-008-9036-x",
"10.1208/s12249-007-9023-7",
"10.3748/wjg.v16.i27.3437",
"10.1093/jbcr/irab118",
"10.1208/s12249-008-9172-3",
"10.1208/s12249-009-9218-1",
"10.1208/s12249-014-0199-3",
"10.1007/s00280-015-2851-3",
"10.1208/s12249-021-02108-5",
"10.1002/adhm.202101427",
"10.1089/can.2022.0176",
"10.1208/s12249-013-0048-9",
"10.1073/pnas.1310214110",
"10.1021/bm4015232",
"10.1089/jamp.2015.1235",
"10.1002/jps.21719",
"10.1208/s12249-009-9315-1",
"10.1021/mp4005029",
"10.1007/s11095-022-03317-8",
"10.1208/pt010317",
"10.1007/s11095-018-2349-x",
"10.1208/s12249-009-9284-4",
"10.1049/iet-nbt.2017.0104",
"10.1080/21645515.2015.1046660",
"10.1208/s12249-009-9233-2",
"10.1208/s12249-009-9287-1",
"10.1208/pt050342",
"10.1136/ejhpharm-2020-002534",
"10.1007/s13346-020-00758-9",
"10.1002/jps.22488",
"10.1208/s12249-012-9762-y",
"10.1208/pt070361",
"10.1007/s11095-008-9626-z",
"10.4161/hv.25639",
"10.1208/pt060474",
"10.1208/s12249-009-9257-7",
"10.1208/s12249-010-9528-3",
"10.1208/s12249-010-9440-x",
"10.1208/s12249-009-9190-9",
"10.3109/03639045.2012.763137",
"10.1208/pt070244",
"10.1002/adma.201804693",
"10.1208/s12249-009-9234-1",
"10.1208/s12249-014-0072-4",
"10.1208/s12249-015-0366-1",
"10.1208/s12249-009-9220-7",
"10.1007/s11095-008-9594-3",
"10.1208/s12249-011-9659-1",
"10.1208/s12249-011-9672-4",
"10.1208/pt070372",
"10.3109/10717544.2014.923068",
"10.1208/pt0801012",
"10.1021/acs.molpharmaceut.8b00802",
"10.1007/s11095-013-1252-8",
"10.1208/s12249-009-9268-4",
"10.1208/pt0802028",
"10.1208/s12249-008-9131-z",
"10.1208/s12249-009-9213-6",
"10.1111/bph.13149",
"10.1208/s12249-008-9082-4",
"10.1124/jpet.118.254672",
"10.1208/pt020310",
"10.1208/s12249-014-0096-9",
"10.1208/s12249-014-0103-1",
"10.1007/s00270-018-1899-y",
"10.1208/s12249-009-9306-2",
"10.1208/s12249-013-9990-9",
"10.1208/s12249-011-9742-7",
"10.1208/s12249-009-9242-1",
"10.1208/s12249-008-9053-9",
"10.1049/iet-nbt.2019.0035",
"10.1208/s12249-009-9286-2",
"10.1208/s12249-008-9037-9",
"10.1159/000522380",
"10.1208/s12249-009-9340-0",
"10.1177/0148607116640275",
"10.1007/s42770-019-00203-1",
"10.1124/jpet.118.252809",
"10.1208/s12249-009-9192-7",
"10.4103/ijp.ijp_370_23",
"10.2147/DDDT.S103169",
"10.1080/10837450.2019.1578372",
"10.1208/aapsj0903041",
"10.1208/pt0802042",
"10.1128/aac.40.6.1467",
"10.1159/000511443",
"10.1208/s12249-014-0278-5",
"10.17305/bjbms.2010.2697",
"10.1208/s12249-015-0308-y",
"10.1080/20415990.2024.2363136",
"10.3109/1061186X.2015.1087529",
"10.1208/s12249-009-9331-1",
"10.1049/iet-nbt.2016.0116",
"10.1208/s12249-015-0305-1",
"10.1208/s12249-010-9457-1",
"10.1208/s12249-018-1287-6",
"10.1021/acsnano.9b07214",
"10.1007/s11095-018-2391-8",
"10.1631/jzus.B1600389",
"10.3109/02652048.2013.814728",
"10.1208/s12249-009-9186-5",
"10.1152/ajpheart.00471.2017",
"10.1007/s42770-019-00201-3",
"10.1208/s12249-010-9507-8",
"10.1021/mp3004379",
"10.1049/iet-nbt.2017.0189",
"10.1049/iet-nbt.2019.0148",
"10.1208/aapsj070488",
"10.1208/pt010432",
"10.1007/s11095-008-9744-7",
"10.1208/s12249-008-9080-6",
"10.1021/acsnano.2c00199",
"10.3791/53489",
"10.1158/1535-7163.MCT-18-1046",
"10.1208/s12249-011-9653-7",
"10.3791/51874",
"10.1208/s12249-014-0214-8",
"10.1208/pt070127",
"10.1080/20415990.2024.2363635",
"10.1208/s12249-008-9070-8",
"10.1208/s12248-013-9557-4",
"10.1208/s12249-011-9661-7",
"10.1208/s12248-012-9433-7",
"10.2478/s11658-006-0037-z",
"10.1208/s12249-009-9193-6",
"10.1208/s12249-015-0354-5",
"10.1208/s12249-010-9426-8"]

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



