
import sys
import os

# Add project root to sys.path to allow importing from src
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../')))

from qdrant_client import QdrantClient
from src.core.config import settings

client = QdrantClient(
    url=settings.QDRANT_URL,
    api_key=settings.QDRANT_API_KEY
)

collection_name = settings.QDRANT_COLLECTION_NAME

try:
    print(f"Checking collection '{collection_name}'...")
    # Check if collection exists by trying to get it
    try:
        collection_info = client.get_collection(collection_name)
        print(f"Collection '{collection_name}' found.")
        print(f"Current Config: {collection_info.config.params}")
        
        # Delete collection to force recreation with new schema
        print(f"Deleting collection '{collection_name}' to fix schema mismatch...")
        client.delete_collection(collection_name)
        print("Collection deleted successfully.")
    except Exception as e:
        # If get_collection fails, it might not exist or connection error
        print(f"Collection might not exist or error retrieving it: {e}")
        # Try deleting anyway just in case
        try:
            client.delete_collection(collection_name)
            print("Delete command sent (just in case).")
        except:
            pass
    
except Exception as e:
    print(f"Critical Error: {e}")
