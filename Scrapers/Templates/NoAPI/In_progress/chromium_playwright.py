

from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
import json
import re

SEARCH_URL = "https://www.mdpi.com/search?q=formulation+excipients+emulsifying&journal=pharmaceutics"
ARTICLE_URL = "https://www.mdpi.com/1999-4923/17/9/1166"

def scrape_search_page(page, url):
    print(f"--- Scraping Search Page: {url} ---")
    page.goto(url)
    page.wait_for_selector('div.article-content')  # wait for first article to load
    html = page.content()
    soup = BeautifulSoup(html, 'html.parser')

    results = {}
    article_content = soup.find('div', class_='article-content')
    if article_content:
        # Title
        title_tag = article_content.find('a', class_='title-link')
        results['title'] = title_tag.get_text(strip=True) if title_tag else 'Not Found'

        # Authors
        authors_div = article_content.find('div', class_='authors')
        if authors_div:
            authors_text = authors_div.get_text(separator=', ', strip=True)
            cleaned_authors = re.sub(r'by\s*', '', authors_text)
            results['authors'] = cleaned_authors.strip()
        else:
            results['authors'] = 'Not Found'

        # PDF link
        pdf_tag = article_content.find('a', class_='UD_Listings_ArticlePDF')
        results['pdf_link'] = f"https://www.mdpi.com{pdf_tag['href']}" if pdf_tag and 'href' in pdf_tag.attrs else 'Not Found'

    return results

def scrape_article_page(page, url):
    print(f"\n--- Scraping Article Page: {url} ---")
    page.goto(url)
    page.wait_for_selector('div.html-p')  # wait for first paragraph to render
    html = page.content()
    soup = BeautifulSoup(html, 'html.parser')

    results = {}

    # Meta title
    title_meta = soup.find('meta', attrs={'name': 'title'})
    results['meta_title'] = title_meta['content'] if title_meta else 'Not Found'

    # Meta abstract
    abstract_meta = soup.find('meta', attrs={'name': 'dc.description'})
    results['meta_abstract'] = abstract_meta['content'] if abstract_meta else 'Not Found'

    # First paragraph under Introduction
    intro_heading = soup.find('h2', string=re.compile(r'\s*1\. Introduction'))
    first_paragraph_div = None
    if intro_heading:
        # The first following div with class "html-p" after the Introduction heading
        sibling = intro_heading.find_next_sibling()
        while sibling:
            if sibling.name == 'div' and 'html-p' in sibling.get('class', []):
                first_paragraph_div = sibling
                break
            sibling = sibling.find_next_sibling()

    if first_paragraph_div:
        paragraph_text = first_paragraph_div.get_text(separator=' ', strip=True)
        cleaned_paragraph = re.sub(r'\[\d+.*?\]', '', paragraph_text).strip()
        results['first_paragraph'] = cleaned_paragraph
    else:
        results['first_paragraph'] = 'Not Found'

    return results

def main():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        # Scrape search page
        search_results = scrape_search_page(page, SEARCH_URL)

        # Scrape specific article page
        article_results = scrape_article_page(page, ARTICLE_URL)

        browser.close()

    final_output = {
        "Search_Result_First_Article": search_results,
        "Specific_Article_Content": article_results
    }

    print("\n" + "="*50)
    print("FINAL SCRAPING RESULTS")
    print("="*50)
    print(json.dumps(final_output, indent=4))

if __name__ == "__main__":
    main()
