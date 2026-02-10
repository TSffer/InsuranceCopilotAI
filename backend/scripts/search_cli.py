
import asyncio
import sys
import os
import argparse

# Add project root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../')))

from src.services.ingestion_service import IngestionService
from qdrant_client import models

async def search(query_text: str):
    print(f"--- Searching for: '{query_text}' ---")
    
    service = IngestionService()
    
    # 1. Generate Embeddings
    print("Generating dense embedding...")
    dense_vector = await service.get_embedding(query_text)
    
    sparse_vector = None
    if getattr(service, 'sparse_model', None):
        print("Generating sparse embedding...")
        sparse_vector = service.get_sparse_vector(query_text)

    # 2. Execute Search
    print("Querying Qdrant...")
    
    # Hybrid Search logic (Prefetch for sparse, Rescore with dense)
    # This matches the advanced hybrid search pattern
    
    search_result = service.qdrant.query_points(
        collection_name=service.collection_name,
        prefetch=[
            models.Prefetch(
                query=sparse_vector,
                using="sparse",
                limit=20,
            )
        ],
        query=dense_vector,
        using="dense",
        limit=5,
        with_payload=True
    )
    
    print(f"\nFound {len(search_result.points)} results:\n")
    
    for i, point in enumerate(search_result.points):
        print(f"Result {i+1} (Score: {point.score:.4f}):")
        print(f"  Source: {point.payload.get('source_file')}")
        print(f"  Content Preview: {point.payload.get('content')[:150]}...")
        print("-" * 50)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Search in Qdrant")
    parser.add_argument("query", type=str, help="The question or text to search for")
    args = parser.parse_args()
    
    asyncio.run(search(args.query))
#python backend/scripts/search_cli.py "cobertura de robo total"