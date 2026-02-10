import requests
import sys

BASE_URL = "http://127.0.0.1:8000"
API_PREFIX = "/api/v1"

def main():
    # 1. Register/Login
    email = "test@example.com"
    password = "password123"
    username = "testuser"
    
    print("1. Authenticating...")
    
    # Try to register (ignore if exists)
    try:
        requests.post(
            f"{BASE_URL}{API_PREFIX}/auth/register",
            json={"email": email, "password": password, "username": username, "role": "user"}
        )
    except:
        pass

    # Login
    response = requests.post(
        f"{BASE_URL}{API_PREFIX}/auth/token",
        data={"username": email, "password": password} # OAuth2 form uses 'username' field for email
    )
    
    if response.status_code != 200:
        print(f"Login failed: {response.text}")
        return

    token = response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    print(f"Auhtenticated. Token: {token[:10]}...")

    # 2. Call Chat Endpoint
    print("\n2. Calling /chat endpoint...")
    try:
        response = requests.post(
            f"{BASE_URL}{API_PREFIX}/chat",
            json={"message": "Hola, funciona con auth?"},
            headers=headers,
            timeout=30
        )
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
