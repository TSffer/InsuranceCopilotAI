
from flashrank import Ranker
import sys

model_name = "mmarco-mMiniLMv2-L12-H384-v1"
print(f"Attempting to load {model_name} with FlashRank...")

try:
    ranker = Ranker(model_name=model_name, cache_dir="/tmp/flashrank")
    print("Success! Model loaded.")
except Exception as e:
    print(f"Error loading {model_name}: {e}")
    
    # Try another one
    model_name_2 = "ms-marco-MiniLM-L-12-v2"
    print(f"\nAttempting to load default {model_name_2}...")
    try:
        ranker = Ranker(model_name=model_name_2, cache_dir="/tmp/flashrank")
        print("Success! Default model loaded.")
    except Exception as e:
        print(f"Error loading {model_name_2}: {e}")
