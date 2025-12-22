import requests
import json

url = "http://127.0.0.1:8000/api/candidates/search"

payload = {
  "skill": "java",
  "experience": 3
}

print("[INFO] Sending request to API...")

try:
    response = requests.post(url, json=payload)
    print(f"[INFO] Status Code: {response.status_code}")
    print("\nAPI RESPONSE:")
    print(json.dumps(response.json(), indent=4))

except Exception as e:
    print(f"[ERROR] {e}")