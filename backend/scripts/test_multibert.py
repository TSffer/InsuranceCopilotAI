
from flashrank import Ranker
import sys

model_name = "ms-marco-MultiBERT-L-12"
print(f"Attempting to load {model_name} with FlashRank...")

try:
    ranker = Ranker(model_name=model_name, cache_dir="/tmp/flashrank")
    print("Success! Model loaded.")
except Exception as e:
    print(f"Error loading {model_name}: {e}")
