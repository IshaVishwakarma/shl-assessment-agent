import requests
from bs4 import BeautifulSoup

URL = "https://tcp-us-prod-rnd.shl.com/voiceRater/shl-ai-hiring/shl_product_catalog.json"


headers = {
    "User-Agent": "Mozilla/5.0"
}

response = requests.get(URL, headers=headers)

print(response.status_code)

soup = BeautifulSoup(response.text, "lxml")

print(soup.title)