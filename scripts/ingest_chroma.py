import json
import chromadb
import cohere

from app.core.config import COHERE_API_KEY


# -----------------------------
# INGEST FUNCTION
# -----------------------------

def ingest_data():

    # -------------------------
    # LOAD DATA
    # -------------------------

    with open(
        "db/catalog_enriched.json",
        "r",
        encoding="utf-8"
    ) as f:

        catalog = json.load(f)

    # -------------------------
    # INIT CLIENTS
    # -------------------------

    co = cohere.Client(
        COHERE_API_KEY
    )

    client = chromadb.PersistentClient(
        path="./db/chroma"
    )

    # -------------------------
    # SAFE COLLECTION INIT
    # -------------------------

    try:

        collection = client.get_collection(
            name="shl_catalog"
        )

    except Exception:

        collection = client.create_collection(
            name="shl_catalog"
        )

    # -------------------------
    # SKIP IF ALREADY POPULATED
    # -------------------------

    existing = collection.count()

    if existing > 0:

        print(
            "Collection already populated."
        )

        return

    # -------------------------
    # PREPARE DOCUMENTS
    # -------------------------

    documents = []
    metadatas = []
    ids = []

    for item in catalog:

        documents.append(
            item["retrieval_text"]
        )

        metadatas.append({

            "name": item["name"],

            "url": item["url"],

            "test_types": ", ".join(
                item["test_types"]
            ),

            "remote": item["remote"],

            "adaptive": item["adaptive"],

            "job_levels": ", ".join(
                item["job_levels"]
            )
        })

        ids.append(item["id"])

    # -------------------------
    # GENERATE EMBEDDINGS
    # -------------------------

    print("\nGenerating embeddings...\n")

    response = co.embed(
        texts=documents,
        model="embed-english-v3.0",
        input_type="search_document"
    )

    embeddings = response.embeddings

    # -------------------------
    # INSERT INTO CHROMA
    # -------------------------

    collection.add(
        documents=documents,
        embeddings=embeddings,
        metadatas=metadatas,
        ids=ids
    )

    print("\nChroma ingestion complete.")
    print(
        f"Inserted records: {len(ids)}"
    )


# -----------------------------
# MAIN
# -----------------------------

if __name__ == "__main__":

    ingest_data()