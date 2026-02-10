
import sys
import os
import json

# Add project root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../')))

from qdrant_client import QdrantClient
from src.core.config import settings

def inspect():
    client = QdrantClient(
        url=settings.QDRANT_URL,
        api_key=settings.QDRANT_API_KEY
    )
    collection_name = settings.QDRANT_COLLECTION_NAME

    print(f"--- Inspecting Collection: {collection_name} ---")
    
    # 1. Get Collection Stats
    try:
        info = client.get_collection(collection_name)
        print(f"Status: {info.status}")
        print(f"Points Count: {info.points_count}")
        print(f"Vectors Config: {info.config.params.vectors}")
        print(f"Sparse Vectors Config: {info.config.params.sparse_vectors}")
    except Exception as e:
        print(f"Error getting collection info: {e}")
        return

    # 2. Scroll (Browse) Points
    print("\n--- Sample Points (First 3) ---")
    response, _ = client.scroll(
        collection_name=collection_name,
        limit=3,
        with_payload=True,
        with_vectors=True 
    )

    for point in response:
        print(f"\nID: {point.id}")
        print(f"Payload (Metadata): {json.dumps(point.payload, indent=2, ensure_ascii=False)}")
        
        # Analyze Vectors
        if point.vector:
            print("Vectors:")
            if 'dense' in point.vector:
                dense_len = len(point.vector['dense'])
                print(f"  - Dense Vector: [Present] Length: {dense_len} (First 5 vals: {point.vector['dense'][:5]}...)")
            
            if 'sparse' in point.vector:
                sparse = point.vector['sparse']
                print(f"  - Sparse Vector: [Present] Indices Count: {len(sparse.indices)}, Values Count: {len(sparse.values)}")
                print(f"    Sample Indices: {sparse.indices[:5]}")
                print(f"    Sample Values: {sparse.values[:5]}")

if __name__ == "__main__":
    inspect()
