
from fastembed import SparseTextEmbedding

try:
    print("Supported Sparse Models:")
    for model in SparseTextEmbedding.list_supported_models():
        print(f"- {model['model']}")
except Exception as e:
    print(f"Error: {e}")
