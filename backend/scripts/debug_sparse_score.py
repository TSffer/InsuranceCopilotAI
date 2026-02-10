
import sys
import os
from fastembed import SparseTextEmbedding

# Add project root
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../')))

def debug_sparse():
    print("Loading model Qdrant/bm42-all-minilm-l6-v2-attentions...")
    model = SparseTextEmbedding(model_name="Qdrant/bm42-all-minilm-l6-v2-attentions")
    
    query = "EXCLUSIONES ESPECÍFICAS"
    print(f"\nAnalyzing Query: '{query}'")
    
    # Generate embedding
    vector = list(model.embed([query]))[0]
    
    print(f"Indices: {vector.indices}")
    print(f"Values: {vector.values}")
    
    print("\n--- Interpretation ---")
    print(f"Number of active tokens: {len(vector.values)}")
    print(f"Max weight: {max(vector.values, default=0)}")
    print(f"Sum of weights (approx max score): {sum(vector.values)}")

if __name__ == "__main__":
    debug_sparse()
