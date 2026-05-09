import json
import chromadb
import cohere

from app.core.config import COHERE_API_KEY


def ingest_data():


# -----------------------------
# LOAD ENRICHED CATALOG
# -----------------------------

with open(
    "db/catalog_enriched.json",
    "r",
    encoding="utf-8"
) as f:

    catalog = json.load(f)


# -----------------------------
# INIT COHERE
# -----------------------------

co = cohere.Client(COHERE_API_KEY)


# -----------------------------
# INIT CHROMADB
# -----------------------------

client = chromadb.PersistentClient(
    path="./db/chroma"
)

collection = client.get_or_create_collection(
    name="shl_catalog"
)


# -----------------------------
# CLEAR OLD DATA
# -----------------------------

existing = collection.get()

if existing["ids"]:
    collection.delete(ids=existing["ids"])


# -----------------------------
# PREPARE DOCUMENTS
# -----------------------------

documents = []
metadatas = []
ids = []


for item in catalog:

    documents.append(item["retrieval_text"])

    metadatas.append({
        "name": item["name"],
        "url": item["url"],
        "duration": item["duration"],
        "remote": item["remote"],
        "adaptive": item["adaptive"],
        "job_levels": ", ".join(item["job_levels"]),
        "test_types": ", ".join(item["test_types"])
    })

    ids.append(str(item["id"]))


# -----------------------------
# GENERATE EMBEDDINGS
# -----------------------------

print("\nGenerating embeddings...\n")

embeddings_response = co.embed(
    texts=documents,
    model="embed-english-v3.0",
    input_type="search_document"
)

embeddings = embeddings_response.embeddings


# -----------------------------
# INSERT INTO CHROMADB
# -----------------------------

collection.add(
    documents=documents,
    embeddings=embeddings,
    metadatas=metadatas,
    ids=ids
)


print("\nChroma ingestion complete.")
print(f"Inserted records: {len(ids)}")

if __name__ == "__main__":

    ingest_data()