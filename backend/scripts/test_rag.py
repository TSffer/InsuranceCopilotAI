
import asyncio
import sys
import os

# Add project root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../')))

from src.services.rag_service import RAGService

async def test_rag():
    print("Initializing RAG Service...")
    rag = RAGService()
    
    query = "EXCLUSIONES ESPECÍFICAS"
    print(f"\n--- Testing Query: '{query}' ---")
    
    # Test Retrieval directly
    print("Retrieving documents...")
    queries = await rag.expand_query(query)
    print(f"Expanded Queries: {queries}")
    
    docs = await rag.retrieve_documents(queries)
    print(f"\nRetrieved {len(docs)} documents.")
    for i, d in enumerate(docs):
        print(f"[{i+1}] Score: {d['score']:.4f} - Source: {d['metadata'].get('source_file')}")
        print(f"    Preview: {d['content'][:100]}...")

    # Test Full Answer
    print("\nGenerating Answer...")
    answer = await rag.answer_legal_query(query)
    print("\n--- FINAL ANSWER ---")
    print(answer)

if __name__ == "__main__":
    asyncio.run(test_rag())
