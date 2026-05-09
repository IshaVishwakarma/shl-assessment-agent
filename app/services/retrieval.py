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
# DOMAIN BOOSTS
# -----------------------------

DOMAIN_KEYWORDS = {

    "software_engineering": [
        "java",
        "python",
        "spring",
        "docker",
        "aws",
        "backend",
        "frontend",
        "rest",
        "sql",
        "developer",
        "api",
        "coding"
    ],

    "leadership": [
        "leadership",
        "executive",
        "director",
        "cxo",
        "stakeholder"
    ],

    "graduate": [
        "graduate",
        "entry level",
        "trainee",
        "campus"
    ],

    "customer_service": [
        "customer",
        "contact center",
        "support",
        "call center",
        "retail"
    ],

    "safety": [
        "safety",
        "health",
        "workplace",
        "dependability"
    ],

    "finance": [
        "finance",
        "accounting",
        "statistics",
        "numerical"
    ]
}
# -----------------------------
# DETECT QUERY DOMAIN
# -----------------------------

def detect_domains(query):

    query = query.lower()

    detected = []

    for domain, keywords in DOMAIN_KEYWORDS.items():

        if any(
            keyword in query
            for keyword in keywords
        ):

            detected.append(domain)

    return detected

# -----------------------------
# EXACT KEYWORD OVERLAP
# -----------------------------

def keyword_overlap_score(
    query,
    document
):

    query_words = set(
        query.lower().split()
    )

    document_words = set(
        document.lower().split()
    )

    overlap = query_words.intersection(
        document_words
    )

    if len(query_words) == 0:
        return 0

    return len(overlap) / len(query_words)

# -----------------------------
# DOMAIN BOOST SCORE
# -----------------------------

def domain_boost_score(
    query_domains,
    metadata
):

    score = 0

    text = (
        str(metadata)
        .lower()
    )

    for domain in query_domains:

        keywords = DOMAIN_KEYWORDS[
            domain
        ]

        if any(
            keyword in text
            for keyword in keywords
        ):

            score += 1

    return score


# -----------------------------
# PERSONALITY TERMS
# -----------------------------

PERSONALITY_TERMS = [
    "stakeholder",
    "communication",
    "leadership",
    "behavior",
    "teamwork",
    "personality",
    "collaboration"
]


# -----------------------------
# TECH TERMS
# -----------------------------

TECH_TERMS = [
    "java",
    "developer",
    "backend",
    "frontend",
    "software",
    "api",
    "programming",
    ".net",
    "python",
    "react",
    "javascript"
]


# -----------------------------
# COGNITIVE TERMS
# -----------------------------

COGNITIVE_TERMS = [
    "cognitive",
    "aptitude",
    "reasoning",
    "problem solving",
    "logical thinking"
]


# -----------------------------
# HYBRID SEARCH
# -----------------------------

def hybrid_search(
    query,
    top_k=5
):

    # -------------------------
    # EMBEDDING
    # -------------------------

    response = co.embed(
        texts=[query],
        model="embed-english-v3.0",
        input_type="search_query"
    )

    query_embedding = (
        response.embeddings[0]
    )

    # -------------------------
    # CHROMA SEARCH
    # -------------------------

    results = collection.query(
        query_embeddings=[
            query_embedding
        ],
        n_results=25
    )

    documents = results["documents"][0]

    metadatas = results["metadatas"][0]

    distances = results["distances"][0]

    # -------------------------
    # DETECT DOMAINS
    # -------------------------

    query_domains = detect_domains(
        query
    )

    reranked = []

    # -------------------------
    # RERANKING
    # -------------------------

    for doc, meta, distance in zip(
        documents,
        metadatas,
        distances
    ):

        # ---------------------
        # SEMANTIC SCORE
        # ---------------------

        semantic_score = (
            1 - distance
        )

        # ---------------------
        # KEYWORD SCORE
        # ---------------------

        keyword_score = (
            keyword_overlap_score(
                query,
                doc
            )
        )

        # ---------------------
        # DOMAIN SCORE
        # ---------------------

        domain_score = (
            domain_boost_score(
                query_domains,
                meta
            )
        )

        # ---------------------
        # FINAL SCORE
        # ---------------------

        final_score = (
            (0.55 * semantic_score)
            +
            (0.30 * keyword_score)
            +
            (0.15 * domain_score)
        )

        reranked.append({

            "score": final_score,

            "metadata": meta,

            "document": doc
        })

    # -------------------------
    # SORT
    # -------------------------

    reranked = sorted(
        reranked,
        key=lambda x: x["score"],
        reverse=True
    )

    return reranked[:top_k]

    query_lower = query.lower()

    # -------------------------
    # QUERY EMBEDDING
    # -------------------------

    response = co.embed(
        texts=[query],
        model="embed-english-v3.0",
        input_type="search_query"
    )

    query_embedding = response.embeddings[0]

    # -------------------------
    # CHROMA SEARCH
    # -------------------------

    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=25
    )

    reranked = []

    # -------------------------
    # PROCESS RESULTS
    # -------------------------

    for i in range(len(results["documents"][0])):

        document = results["documents"][0][i].lower()

        metadata = results["metadatas"][0][i]

        distance = results["distances"][0][i]

        # ---------------------
        # BASE SEMANTIC SCORE
        # ---------------------

        semantic_score = max(
            0,
            1 / (1 + distance)
        )

        boost = 0

        # ---------------------
        # TECH BOOST
        # ---------------------

        tech_matches = sum(
            term in document
            for term in TECH_TERMS
            if term in query_lower
        )

        boost += tech_matches * 0.08

        # ---------------------
        # PERSONALITY BOOST
        # ---------------------

        personality_matches = sum(
            term in document
            for term in PERSONALITY_TERMS
            if term in query_lower
        )

        boost += personality_matches * 0.15

        # ---------------------
        # COGNITIVE BOOST
        # ---------------------

        cognitive_matches = sum(
            term in document
            for term in COGNITIVE_TERMS
            if term in query_lower
        )

        boost += cognitive_matches * 0.12

        # ---------------------
        # TEST TYPE BOOSTING
        # ---------------------

        test_type = metadata.get(
            "test_types",
            ""
        ).lower()

        # Personality weighting
        if any(
            term in query_lower
            for term in PERSONALITY_TERMS
        ):

            if (
                "personality" in test_type
                or "competencies" in test_type
            ):

                boost += 0.35

        # Cognitive weighting
        if any(
            term in query_lower
            for term in COGNITIVE_TERMS
        ):

            if (
                "ability" in test_type
                or "aptitude" in test_type
            ):

                boost += 0.30

        # Technical weighting
        if any(
            term in query_lower
            for term in TECH_TERMS
        ):

            if (
                "knowledge" in test_type
                or "skills" in test_type
                or "simulation" in test_type
            ):

                boost += 0.20

        # ---------------------
        # FINAL SCORE
        # ---------------------

        final_score = semantic_score + boost

        reranked.append({
            "score": round(final_score, 4),
            "metadata": metadata
        })

    # -------------------------
    # SORT RESULTS
    # -------------------------

    reranked = sorted(
        reranked,
        key=lambda x: x["score"],
        reverse=True
    )

    # -------------------------
    # REMOVE DUPLICATES
    # -------------------------

    unique_results = []

    seen = set()

    for item in reranked:

        name = item["metadata"]["name"]

        if name not in seen:

            unique_results.append(item)

            seen.add(name)

    return unique_results[:top_k]