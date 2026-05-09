import requests
import json
import re

URL = "https://tcp-us-prod-rnd.shl.com/voiceRater/shl-ai-hiring/shl_product_catalog.json"


def clean_text(text):
    if not text:
        return ""

    text = re.sub(r'[\x00-\x1F\x7F]', '', text)
    text = re.sub(r'\s+', ' ', text)

    return text.strip()


response = requests.get(URL)

raw_text = response.text

clean_json = re.sub(
    r'[\x00-\x1F\x7F]',
    '',
    raw_text
)

data = json.loads(clean_json)

normalized = []

for item in data:

    name = clean_text(item.get("name"))

    description = clean_text(item.get("description"))

    url = item.get("link", "")

    duration = clean_text(item.get("duration"))

    remote = item.get("remote", "")

    adaptive = item.get("adaptive", "")

    job_levels = item.get("job_levels", [])

    test_types = item.get("keys", [])

    combined_text = f"""
    {name}

    {description}

    {' '.join(job_levels)}

    {' '.join(test_types)}
    """

    normalized_item = {
        "id": item.get("entity_id"),
        "name": name,
        "url": url,
        "description": description,
        "duration": duration,
        "remote": remote,
        "adaptive": adaptive,
        "job_levels": job_levels,
        "test_types": test_types,
        "search_text": clean_text(combined_text)
    }

    normalized.append(normalized_item)

print(f"Normalized records: {len(normalized)}")

print("\nSample:\n")
print(json.dumps(normalized[0], indent=2))

with open("db/catalog.json", "w", encoding="utf-8") as f:
    json.dump(normalized, f, indent=2, ensure_ascii=False)

print("\nSaved normalized catalog to db/catalog.json")