"""
ElevenLabs TTS API Entegrasyonu
Türkçe sesler için optimize edilmiş ElevenLabs entegrasyon modülü
"""

import requests
import os
from pathlib import Path
from typing import Optional, Dict, Any
import json


class ElevenLabsTTS:
    """ElevenLabs API ile TTS entegrasyonu"""
    
    # Resmi Türkçe Sesler (Voice ID'ler ElevenLabs'den alınmalı)
    TURKISH_VOICES = {
        "ada": {
            "voice_id": "XB0fDUnXU5powFXDhCwa",  # Örnek ID
            "name": "Ada",
            "gender": "female",
            "age": "young",
            "description": "Kadın, genç, net - Edebi metinler için ideal"
        },
        "emre": {
            "voice_id": "VR6AewLTigWG4xSOukaG",  # Örnek ID
            "name": "Emre",
            "gender": "male",
            "age": "middle",
            "description": "Erkek, orta yaş, sıcak - Profesyonel sunum"
        },
        "aylin": {
            "voice_id": "pNInz6obpgDQGcFmaJgB",  # Örnek ID
            "name": "Aylin",
            "gender": "female",
            "age": "mature",
            "description": "Kadın, olgun, otoriter - Haber sunumu"
        },
        "burak": {
            "voice_id": "yoZ06aMxZJJ28mfd3POQ",  # Örnek ID
            "name": "Burak",
            "gender": "male",
            "age": "young",
            "description": "Erkek, genç, enerjik - Reklam ve tanıtım"
        }
    }
    
    # Türkçe İçin Ses Profilleri
    VOICE_PROFILES = {
        "story_teller_male": {
            "voice_id": "emre",
            "settings": {"stability": 0.4, "similarity_boost": 0.8},
            "description": "Sıcak, hikaye anlatıcı erkek sesi",
            "category": "Edebiyat"
        },
        "story_teller_female": {
            "voice_id": "ada",
            "settings": {"stability": 0.3, "similarity_boost": 0.85},
            "description": "Yumuşak, duygusal kadın sesi",
            "category": "Edebiyat"
        },
        "educator_male": {
            "voice_id": "burak",
            "settings": {"stability": 0.6, "similarity_boost": 0.7},
            "description": "Net, anlaşılır eğitim sesi",
            "category": "Eğitim"
        },
        "news_anchor_female": {
            "voice_id": "aylin",
            "settings": {"stability": 0.7, "similarity_boost": 0.9},
            "description": "Otoriter, haber sunucusu sesi",
            "category": "Profesyonel"
        },
        "wise_elder": {
            "voice_id": "emre",
            "settings": {"stability": 0.2, "similarity_boost": 0.6},
            "description": "Bilge, yaşlı karakter sesi",
            "category": "Karakter"
        },
        "young_hero": {
            "voice_id": "burak",
            "settings": {"stability": 0.5, "similarity_boost": 0.8},
            "description": "Genç, enerjik kahraman sesi",
            "category": "Karakter"
        }
    }
    
    def __init__(self, api_key: Optional[str] = None):
        """
        ElevenLabs TTS'yi başlat
        
        Args:
            api_key: ElevenLabs API anahtarı (None ise çevre değişkeninden alınır)
        """
        self.api_key = api_key or os.getenv("ELEVENLABS_API_KEY")
        self.base_url = "https://api.elevenlabs.io/v1"
        
        if not self.api_key:
            print("⚠️  UYARI: ElevenLabs API anahtarı bulunamadı!")
            print("   ELEVENLABS_API_KEY çevre değişkenini ayarlayın veya")
            print("   config.json dosyasına API anahtarınızı ekleyin.")
    
    def _safe_print(self, message: str):
        """Güvenli print (BrokenPipeError önleme)"""
        try:
            print(message)
        except (BrokenPipeError, IOError):
            pass
    
    def generate_speech(
        self, 
        text: str, 
        voice_name: str = "ada",
        output_path: Optional[str] = None,
        stability: float = 0.5,
        similarity_boost: float = 0.75,
        style: float = 0.0,
        use_speaker_boost: bool = True
    ) -> Optional[bytes]:
        """
        Metni seslendir
        
        Args:
            text: Seslendirilecek metin
            voice_name: Ses adı (ada, emre, aylin, burak)
            output_path: Kaydedilecek dosya yolu (None ise byte döndürür)
            stability: Ses kararlılığı (0-1)
            similarity_boost: Ses benzerliği (0-1)
            style: Stil yoğunluğu (0-1)
            use_speaker_boost: Konuşmacı güçlendirme
            
        Returns:
            Audio bytes veya None (hata durumunda)
        """
        if not self.api_key:
            self._safe_print("❌ API anahtarı bulunamadı!")
            return None
        
        # Ses ID'sini al
        voice_info = self.TURKISH_VOICES.get(voice_name.lower())
        if not voice_info:
            self._safe_print(f"❌ Bilinmeyen ses: {voice_name}")
            return None
        
        voice_id = voice_info["voice_id"]
        url = f"{self.base_url}/text-to-speech/{voice_id}"
        
        headers = {
            "Accept": "audio/mpeg",
            "Content-Type": "application/json",
            "xi-api-key": self.api_key
        }
        
        data = {
            "text": text,
            "model_id": "eleven_multilingual_v2",  # Türkçe için ÇOK ÖNEMLİ!
            "voice_settings": {
                "stability": stability,
                "similarity_boost": similarity_boost,
                "style": style,
                "use_speaker_boost": use_speaker_boost
            }
        }
        
        try:
            self._safe_print(f"🎙️  ElevenLabs ile seslendiriliyor ({voice_info['name']})...")
            response = requests.post(url, json=data, headers=headers, timeout=60)
            
            if response.status_code == 200:
                audio_data = response.content
                
                if output_path:
                    # MP3 olarak kaydet
                    output_path = Path(output_path)
                    output_path.parent.mkdir(parents=True, exist_ok=True)
                    
                    with open(output_path, "wb") as f:
                        f.write(audio_data)
                    
                    self._safe_print(f"   ✅ Kaydedildi: {output_path}")
                
                return audio_data
            else:
                error_msg = response.json().get("detail", {}).get("message", "Bilinmeyen hata")
                self._safe_print(f"❌ API Hatası ({response.status_code}): {error_msg}")
                return None
                
        except requests.exceptions.Timeout:
            self._safe_print("❌ İstek zaman aşımına uğradı (60 saniye)")
            return None
        except Exception as e:
            self._safe_print(f"❌ Hata: {e}")
            return None
    
    def generate_with_profile(
        self,
        text: str,
        profile_name: str,
        output_path: Optional[str] = None
    ) -> Optional[bytes]:
        """
        Önceden tanımlı profil ile seslendir
        
        Args:
            text: Seslendirilecek metin
            profile_name: Profil adı (örn: story_teller_male)
            output_path: Kaydedilecek dosya yolu
            
        Returns:
            Audio bytes veya None
        """
        profile = self.VOICE_PROFILES.get(profile_name)
        if not profile:
            self._safe_print(f"❌ Bilinmeyen profil: {profile_name}")
            return None
        
        voice_name = profile["voice_id"]
        settings = profile["settings"]
        
        self._safe_print(f"📝 Profil: {profile['description']}")
        
        return self.generate_speech(
            text=text,
            voice_name=voice_name,
            output_path=output_path,
            stability=settings["stability"],
            similarity_boost=settings["similarity_boost"]
        )
    
    def get_available_voices(self) -> Dict[str, Any]:
        """Mevcut Türkçe sesleri listele"""
        return self.TURKISH_VOICES
    
    def get_available_profiles(self, category: Optional[str] = None) -> Dict[str, Any]:
        """
        Mevcut ses profillerini listele
        
        Args:
            category: Kategori filtresi (Edebiyat, Eğitim, vb.)
            
        Returns:
            Profil sözlüğü
        """
        if category:
            return {
                name: profile 
                for name, profile in self.VOICE_PROFILES.items() 
                if profile["category"] == category
            }
        return self.VOICE_PROFILES
    
    def list_voices(self):
        """Mevcut sesleri güzel formatta yazdır"""
        print("\n" + "="*70)
        print("🎙️  ElevenLabs Türkçe Sesler")
        print("="*70)
        
        for voice_key, voice_info in self.TURKISH_VOICES.items():
            print(f"\n🔹 {voice_info['name']} ({voice_key})")
            print(f"   👤 {voice_info['gender'].title()}, {voice_info['age']}")
            print(f"   📝 {voice_info['description']}")
        
        print("\n" + "="*70)
        print("🎭 Ses Profilleri")
        print("="*70)
        
        categories = {}
        for profile_name, profile_info in self.VOICE_PROFILES.items():
            cat = profile_info["category"]
            if cat not in categories:
                categories[cat] = []
            categories[cat].append((profile_name, profile_info))
        
        for category, profiles in categories.items():
            print(f"\n📂 {category}:")
            for profile_name, profile_info in profiles:
                print(f"   • {profile_name}: {profile_info['description']}")
        
        print("\n" + "="*70)


class ElevenLabsConfig:
    """ElevenLabs API key yönetimi"""
    
    CONFIG_FILE = Path("config.json")
    
    @classmethod
    def save_api_key(cls, api_key: str):
        """API anahtarını config.json'a kaydet"""
        config = {}
        
        if cls.CONFIG_FILE.exists():
            with open(cls.CONFIG_FILE, "r") as f:
                config = json.load(f)
        
        config["elevenlabs_api_key"] = api_key
        
        with open(cls.CONFIG_FILE, "w") as f:
            json.dump(config, f, indent=2)
        
        print(f"✅ API anahtarı kaydedildi: {cls.CONFIG_FILE}")
    
    @classmethod
    def load_api_key(cls) -> Optional[str]:
        """config.json'dan API anahtarını yükle"""
        if not cls.CONFIG_FILE.exists():
            return None
        
        try:
            with open(cls.CONFIG_FILE, "r") as f:
                config = json.load(f)
            return config.get("elevenlabs_api_key")
        except Exception:
            return None


def test_elevenlabs():
    """ElevenLabs entegrasyonunu test et"""
    print("\n" + "="*70)
    print("🧪 ElevenLabs Entegrasyon Testi")
    print("="*70)
    
    # API key kontrolü
    tts = ElevenLabsTTS()
    
    if not tts.api_key:
        print("\n❌ Test başarısız: API anahtarı bulunamadı!")
        print("\n💡 Çözüm:")
        print("   1. https://elevenlabs.io/sign-up adresinden hesap oluştur")
        print("   2. API anahtarını al")
        print("   3. Terminal'de şunu çalıştır:")
        print("      export ELEVENLABS_API_KEY='your-api-key-here'")
        print("   VEYA")
        print("   4. Python ile:")
        print("      from elevenlabs_integration import ElevenLabsConfig")
        print("      ElevenLabsConfig.save_api_key('your-api-key-here')")
        return
    
    # Sesleri listele
    tts.list_voices()
    
    # Test metni
    test_text = "Merhaba! Ben ElevenLabs Türkçe ses sentezi sistemi. Sesimi beğendiniz mi?"
    
    print("\n🎤 Test metni:")
    print(f"   '{test_text}'")
    print("\n📁 Test dosyası: test_elevenlabs.mp3")
    
    # Test seslendirmesi
    result = tts.generate_speech(
        text=test_text,
        voice_name="ada",
        output_path="test_elevenlabs.mp3"
    )
    
    if result:
        print("\n✅ Test başarılı!")
    else:
        print("\n❌ Test başarısız!")


if __name__ == "__main__":
    test_elevenlabs()

