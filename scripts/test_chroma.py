import chromadb

client = chromadb.PersistentClient(
    path="./db/chroma"
)

collection = client.get_or_create_collection(
    name="shl_catalog"
)

print("ChromaDB working successfully")