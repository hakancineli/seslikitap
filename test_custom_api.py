"""
Özel TTS API Test Script
"""

import requests

# API bilgileri
API_KEY = "sk-5aa9382d8a504e31a0fa260817bc65fd"
BASE_URL = "http://91.218.66.217:443"

def test_api_connection():
    """API bağlantısını test et"""
    print("="*60)
    print("🧪 ÖZEL TTS API TEST")
    print("="*60)
    print(f"📡 Base URL: {BASE_URL}")
    print(f"🔑 API Key: {API_KEY[:20]}...")
    print()
    
    # Test 1: Basit health check
    print("1️⃣ API erişilebilir mi?")
    try:
        response = requests.get(f"{BASE_URL}/", timeout=5)
        print(f"   ✅ HTTP {response.status_code}")
    except requests.exceptions.ConnectionError:
        print(f"   ❌ Bağlantı hatası - API'ye ulaşılamıyor")
        print(f"   💡 Proxy ayarları gerekebilir veya API offline olabilir")
        return False
    except Exception as e:
        print(f"   ⚠️  Hata: {e}")
    
    print()
    
    # Test 2: TTS endpoint
    print("2️⃣ TTS endpoint test ediliyor...")
    url = f"{BASE_URL}/v1/audio/speech"
    
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    
    data = {
        "model": "tts-1-hd",
        "input": "Merhaba, bu bir test mesajıdır.",
        "voice": "alloy",
        "response_format": "mp3"
    }
    
    try:
        print(f"   📤 POST {url}")
        response = requests.post(url, json=data, headers=headers, timeout=30)
        
        print(f"   📥 HTTP {response.status_code}")
        
        if response.status_code == 200:
            print(f"   ✅ Başarılı! Audio alındı ({len(response.content)} bytes)")
            
            # Test dosyası kaydet
            with open("test_api_output.mp3", "wb") as f:
                f.write(response.content)
            print(f"   💾 test_api_output.mp3 kaydedildi")
            return True
        else:
            print(f"   ❌ Hata: {response.text}")
            return False
            
    except requests.exceptions.Timeout:
        print(f"   ❌ Timeout - API 30 saniyede cevap vermedi")
        return False
    except requests.exceptions.ConnectionError as e:
        print(f"   ❌ Bağlantı hatası: {e}")
        print(f"   💡 API offline veya ağ sorunu olabilir")
        return False
    except Exception as e:
        print(f"   ❌ Beklenmeyen hata: {e}")
        return False

if __name__ == "__main__":
    success = test_api_connection()
    print()
    print("="*60)
    if success:
        print("✅ API çalışıyor!")
    else:
        print("❌ API ile bağlantı kurulamadı")
        print()
        print("🔍 Olası Nedenler:")
        print("   1. API offline")
        print("   2. Port 443 erişilebilir değil")
        print("   3. API key yanlış")
        print("   4. Firewall/Proxy sorunu")
    print("="*60)

