
from fastembed import SparseTextEmbedding

model_name = "Qdrant/bm42-all-minilm-l6-v2-attentions"
try:
    print(f"Attempting to load {model_name}...")
    model = SparseTextEmbedding(model_name=model_name)
    print("Success! Model loaded.")
    
    # Test embedding
    embeddings = list(model.embed(["Hola mundo, prueba de embedding sparse."]))
    print(f"Embedding generated.")
    print(f"Indices: {embeddings[0].indices}")
    print(f"Values: {embeddings[0].values}")

except Exception as e:
    print(f"Error loading model: {e}")
