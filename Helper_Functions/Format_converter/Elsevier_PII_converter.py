import requests

# Function to get PII from a 'j-style' DOI
def get_pii_from_doi(doi):
    url = f"https://doi.org/{doi}"
    # We follow the redirect to see the final ScienceDirect URL
    response = requests.head(url, allow_redirects=True)
    final_url = response.url
    
    # The final URL usually looks like: .../article/pii/S123456789...
    if "pii/" in final_url:
        return final_url.split("pii/")[-1]
    return None

# Example usage
doi_1 = "10.1016/j.actbio.2015.08.039"
print(get_pii_from_doi(doi_1)) 
# Output will be something like: S1742706115300665