from app.services.retrieval import hybrid_search


query = "Java backend developer with stakeholder communication"

results = hybrid_search(query)


print("\nTop Results:\n")


for i, result in enumerate(results):

    metadata = result["metadata"]

    print(f"{i+1}. {metadata['name']}")
    print(f"Score: {result['score']:.4f}")
    print(f"URL: {metadata['url']}")
    print(f"Type: {metadata['test_types']}")
    print()