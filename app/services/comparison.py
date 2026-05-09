import chromadb
import cohere

from app.core.config import COHERE_API_KEY


# -----------------------------
# INIT CLIENTS
# -----------------------------

co = cohere.Client(COHERE_API_KEY)

client = chromadb.PersistentClient(
    path="./db/chroma"
)

collection = client.get_collection(
    name="shl_catalog"
)


# -----------------------------
# FIND CLOSEST ASSESSMENT
# -----------------------------

def find_assessment(query):

    response = co.embed(
        texts=[query],
        model="embed-english-v3.0",
        input_type="search_query"
    )

    embedding = response.embeddings[0]

    results = collection.query(
        query_embeddings=[embedding],
        n_results=1
    )

    metadata = results["metadatas"][0][0]

    document = results["documents"][0][0]

    return {
        "metadata": metadata,
        "document": document
    }


# -----------------------------
# COMPARE ASSESSMENTS
# -----------------------------

def compare_assessments(query):

    query_lower = query.lower()

    # -------------------------
    # CLEAN QUERY
    # -------------------------

    cleaned_query = (
        query_lower
        .replace("compare", "")
        .replace("difference between", "")
        .strip()
    )

    # -------------------------
    # ENTITY SPLITTING
    # -------------------------

    separators = [
        " vs ",
        " versus ",
        " and "
    ]

    parts = None

    for separator in separators:

        if separator in cleaned_query:

            parts = cleaned_query.split(separator)
            break

    # -------------------------
    # VALIDATION
    # -------------------------

    if not parts or len(parts) < 2:

        return {
            "reply": (
                "Please specify two assessments "
                "to compare."
            )
        }

    left_query = parts[0].strip()
    right_query = parts[1].strip()

    # -------------------------
    # FIND ASSESSMENTS
    # -------------------------

    left = find_assessment(left_query)

    right = find_assessment(right_query)

    left_meta = left["metadata"]
    right_meta = right["metadata"]

    # -------------------------
    # SAFE METADATA EXTRACTION
    # -------------------------

    left_name = left_meta.get(
        "name",
        "Unknown Assessment"
    )

    right_name = right_meta.get(
        "name",
        "Unknown Assessment"
    )

    left_test_type = left_meta.get(
        "test_types",
        "Not Available"
    )

    right_test_type = right_meta.get(
        "test_types",
        "Not Available"
    )

    left_remote = left_meta.get(
        "remote",
        "Unknown"
    )

    right_remote = right_meta.get(
        "remote",
        "Unknown"
    )

    left_adaptive = left_meta.get(
        "adaptive",
        "Unknown"
    )

    right_adaptive = right_meta.get(
        "adaptive",
        "Unknown"
    )

    left_levels = left_meta.get(
        "job_levels",
        "Not Available"
    )

    right_levels = right_meta.get(
        "job_levels",
        "Not Available"
    )

    # -------------------------
    # BUILD RESPONSE
    # -------------------------

    reply = f"""
Comparison between {left_name} and {right_name}:

1. Test Type:
- {left_name}: {left_test_type}
- {right_name}: {right_test_type}

2. Remote Support:
- {left_name}: {left_remote}
- {right_name}: {right_remote}

3. Adaptive Testing:
- {left_name}: {left_adaptive}
- {right_name}: {right_adaptive}

4. Recommended Usage:
- {left_name} is suited for:
  {left_levels}

- {right_name} is suited for:
  {right_levels}
"""

    return {
        "reply": reply.strip()
    }