import sys
import json
import requests
from prettytable import PrettyTable

# Documentation: https://www.uniprot.org/help/api
WEBSITE_API = "https://rest.uniprot.org/"

# Documentation: https://www.ebi.ac.uk/proteins/api/doc/
PROTEINS_API = "https://www.ebi.ac.uk/proteins/api"

# Helper function to download data
def get_url(url, **kwargs):
  response = requests.get(url, **kwargs);

  if not response.ok:
    print(response.text)
    response.raise_for_status()
    sys.exit()

  return response


# all of the entry
r = get_url(f"{WEBSITE_API}/uniprotkb/P00533")
data = r.json()
print(json.dumps(data, indent=2))

#dict  →  list  →  dict  →  list  →  dict

# 1.data is a dict (the outermost JSON object).

# 2.data["comments"] is a list (iterable object;  *Observed from for clause --for iterable object)).

# 3.item is a dict (an element from data["comments"]).

# 4.1 "commentType" is a key in the item dict.

# 4.2 item["commentType"] gives the value associated with the "commentType" key in that dict.


# Extract all commentType values
comment_types = []

# Sometimes "comments" are inside data['comments'], or under another key depending on API version
if "comments" in data:
    for item in data["comments"]:
        if "commentType" in item:
            comment_types.append(item["commentType"])



# Remove duplicates (optional)
# comment_types = list(set(comment_types))

print("---")
print("All extracted commentType for eGFR：")
print(comment_types)




features_list = []

for item in data.get("features", []):
    # extract the 'type' and convert to lowercase (optional)
    if "type" in item:
        features_list.append(item["type"].lower())

features_list = list(dict.fromkeys(features_list))

print(f'All extracted features for eGFR： : {features_list}')