
import asyncio
import sys
import os
import argparse

# Add project root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../')))

from src.services.ingestion_service import IngestionService
from qdrant_client import models

async def search_sparse(query_text: str):
    print(f"--- Searching for: '{query_text}' (SPARSE / EXACT MATCH PRIORITY) ---")
    
    service = IngestionService()
    
    # 1. Generate Sparse Embedding ONLY (Dense is optional if just for ranking)
    print("Generating sparse embedding...")
    if not getattr(service, 'sparse_model', None):
        print("Error: Sparse model not initialized.")
        return

    sparse_vector = service.get_sparse_vector(query_text)

    # 2. Execute Search using SPARSE vector for ranking
    print("Querying Qdrant using 'sparse' vector...")
    
    search_result = service.qdrant.query_points(
        collection_name=service.collection_name,
        query=sparse_vector,
        using="sparse",
        limit=5,
        with_payload=True
    ).points
    
    print(f"\nFound {len(search_result)} results:\n")
    
    for i, point in enumerate(search_result):
        # Score here is BM25/Splade score (higher is better, can be > 1.0)
        print(f"Result {i+1} (Score: {point.score:.4f}):")
        print(f"  Source: {point.payload.get('source_file')}")
        print(f"  Content Preview: {point.payload.get('content')[:500]}...")
        print("-" * 50)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Search in Qdrant using Sparse Vectors")
    parser.add_argument("query", type=str, help="The question or text to search for")
    args = parser.parse_args()
    
    asyncio.run(search_sparse(args.query))
