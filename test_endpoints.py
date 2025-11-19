import requests

API_KEY = "sk-5aa9382d8a504e31a0fa260817bc65fd"
BASE_URL = "http://91.218.66.217:443"

# Test edilecek endpoint'ler
endpoints = [
    "/tts",
    "/api/tts",
    "/v1/tts",
    "/generate",
    "/api/generate",
    "/synthesize",
    "/api/synthesize"
]

print("🔍 Endpoint taraması...")
print()

for endpoint in endpoints:
    url = f"{BASE_URL}{endpoint}"
    try:
        # GET dene
        resp_get = requests.get(url, timeout=2)
        if resp_get.status_code != 404:
            print(f"✅ {endpoint} - GET {resp_get.status_code}")
        
        # POST dene
        resp_post = requests.post(url, json={"text": "test"}, timeout=2)
        if resp_post.status_code != 404:
            print(f"✅ {endpoint} - POST {resp_post.status_code}")
    except:
        pass

print("\n💡 API sağlayıcınızdan doğru endpoint'i öğrenin")
