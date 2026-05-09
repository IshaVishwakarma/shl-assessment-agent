import requests
import json
import re

URL = "https://tcp-us-prod-rnd.shl.com/voiceRater/shl-ai-hiring/shl_product_catalog.json"

response = requests.get(URL)

print("Status Code:", response.status_code)

# Raw text
raw_text = response.text

# Remove invalid control characters
clean_text = re.sub(
    r'[\x00-\x1F\x7F]',
    '',
    raw_text
)

# Parse cleaned JSON
data = json.loads(clean_text)

print("\nType of data:")
print(type(data))

print("\nTotal records:")
print(len(data))

print("\nFirst item:")
print(json.dumps(data[0], indent=2)[:3000])