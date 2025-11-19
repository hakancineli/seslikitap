"""
Voice Catalog - Hazır Ses Klonları Kataloğu
"""
import os
from pathlib import Path
from typing import List, Dict, Optional
import json
import soundfile as sf


class VoiceCatalog:
    """Hazır ses klonları yönetimi"""
    
    def __init__(self, voices_dir: str = "voices"):
        self.voices_dir = Path(voices_dir)
        self.catalog_file = self.voices_dir / "catalog.json"
        self.catalog = self._load_catalog()
    
    def _load_catalog(self) -> Dict:
        """Katalog dosyasını yükle"""
        if self.catalog_file.exists():
            with open(self.catalog_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {"voices": []}
    
    def _save_catalog(self):
        """Katalog dosyasını kaydet"""
        with open(self.catalog_file, 'w', encoding='utf-8') as f:
            json.dump(self.catalog, f, indent=2, ensure_ascii=False)
    
    def scan_voices(self):
        """Voices klasöründeki tüm sesleri tara ve katalogla"""
        print("\n🔍 Ses klasörü taranıyor...")
        
        # WAV dosyalarını bul
        wav_files = list(self.voices_dir.glob("*.wav"))
        
        existing_files = {v['file_name'] for v in self.catalog['voices']}
        new_voices = []
        
        for wav_file in wav_files:
            if wav_file.name in existing_files:
                continue
            
            try:
                # Ses bilgilerini oku
                data, sr = sf.read(str(wav_file))
                duration = len(data) / sr
                
                # Otomatik kategori ve isim çıkar
                name = wav_file.stem
                
                # Sanatçı/eser bilgisi varsa ayır
                artist = "Bilinmiyor"
                work = name
                
                if "OKAN BAYÜLGEN" in name.upper():
                    artist = "Okan Bayülgen"
                    work = name.replace("OKAN BAYÜLGENİN SESİYLE", "").replace("OKAN BAYÜLGEN", "").strip()
                elif "AKIN ALTAN" in name.upper():
                    artist = "Akın Altan"
                    work = name.replace("seslendiren Akın ALTAN", "").strip()
                
                # Kategorize et
                if duration < 60:
                    category = "short_sample"
                    category_tr = "Kısa Örnek"
                elif duration < 300:
                    category = "voice_sample"
                    category_tr = "Ses Örneği"
                else:
                    category = "audiobook"
                    category_tr = "Sesli Kitap"
                
                voice_info = {
                    "id": len(self.catalog['voices']) + len(new_voices) + 1,
                    "file_name": wav_file.name,
                    "file_path": str(wav_file),
                    "display_name": work,
                    "artist": artist,
                    "category": category,
                    "category_tr": category_tr,
                    "duration_seconds": round(duration, 1),
                    "sample_rate": sr,
                    "language": "tr",
                    "gender": "male",  # Varsayılan
                    "quality": "high" if duration > 30 else "medium"
                }
                
                new_voices.append(voice_info)
                print(f"  ✅ {voice_info['display_name']} - {voice_info['artist']}")
                
            except Exception as e:
                print(f"  ⚠️  {wav_file.name}: {e}")
        
        # Yeni sesleri kataloga ekle
        if new_voices:
            self.catalog['voices'].extend(new_voices)
            self._save_catalog()
            print(f"\n✅ {len(new_voices)} yeni ses kataloğa eklendi!")
        else:
            print("\n📝 Yeni ses bulunamadı (tümü zaten katalogda)")
    
    def get_voices_by_category(self, category: Optional[str] = None) -> List[Dict]:
        """Kategoriye göre sesleri getir"""
        voices = self.catalog['voices']
        
        if category:
            voices = [v for v in voices if v['category'] == category]
        
        return sorted(voices, key=lambda x: x['display_name'])
    
    def get_voice_by_id(self, voice_id: int) -> Optional[Dict]:
        """ID'ye göre ses bilgisi getir"""
        for voice in self.catalog['voices']:
            if voice['id'] == voice_id:
                return voice
        return None
    
    def get_voice_choices(self) -> List[tuple]:
        """Gradio dropdown için ses seçenekleri"""
        choices = []
        for voice in self.catalog['voices']:
            label = f"{voice['display_name']} - {voice['artist']} ({voice['duration_seconds']}s)"
            choices.append((label, voice['file_path']))
        return sorted(choices)
    
    def print_catalog(self):
        """Kataloğu güzelce yazdır"""
        print("\n" + "="*60)
        print("🎤 SES KATALOĞU")
        print("="*60)
        
        # Kategorilere göre grupla
        categories = {}
        for voice in self.catalog['voices']:
            cat = voice['category_tr']
            if cat not in categories:
                categories[cat] = []
            categories[cat].append(voice)
        
        for category, voices in categories.items():
            print(f"\n📁 {category} ({len(voices)} ses)")
            print("-"*60)
            for voice in voices:
                print(f"  {voice['id']:2d}. {voice['display_name']}")
                print(f"      🎭 {voice['artist']}")
                print(f"      ⏱️  {voice['duration_seconds']:.1f}s | 🔊 {voice['sample_rate']}Hz")
                print(f"      📁 {voice['file_name']}")
        
        print("\n" + "="*60)
        print(f"Toplam: {len(self.catalog['voices'])} ses")
        print("="*60)


class TurkishTTSModels:
    """Türkçe TTS modelleri listesi"""
    
    MODELS = [
        {
            "id": "xtts_v2",
            "name": "XTTS v2 (Çok Dilli)",
            "description": "Coqui TTS - En iyi ses klonlama",
            "engine": "coqui",
            "languages": ["tr", "en", "es", "fr", "de", "it", "pt", "pl", "uk", "cs", "ar", "zh", "ja", "hu", "ko", "hi"],
            "features": ["voice_cloning", "multi_speaker", "multi_lingual"],
            "quality": "high",
            "speed": "medium",
            "model_path": "tts_models/multilingual/multi-dataset/xtts_v2",
            "recommended": True
        },
        {
            "id": "vits_tr",
            "name": "VITS Türkçe",
            "description": "Türkçe için optimize edilmiş VITS",
            "engine": "coqui",
            "languages": ["tr"],
            "features": ["fast", "quality"],
            "quality": "medium",
            "speed": "fast",
            "model_path": "tts_models/tr/common-voice/glow-tts",
            "recommended": False
        },
        {
            "id": "tacotron2_tr",
            "name": "Tacotron2 Türkçe",
            "description": "Klasik Tacotron2 modeli",
            "engine": "coqui",
            "languages": ["tr"],
            "features": ["stable"],
            "quality": "medium",
            "speed": "slow",
            "model_path": "tts_models/tr/common-voice/tacotron2-DDC",
            "recommended": False
        },
        {
            "id": "fairseq_tr",
            "name": "Fairseq Türkçe",
            "description": "Facebook Fairseq modeli",
            "engine": "fairseq",
            "languages": ["tr"],
            "features": ["research"],
            "quality": "medium",
            "speed": "medium",
            "model_path": "facebook/fastspeech2-tr",
            "recommended": False
        }
    ]
    
    @classmethod
    def get_recommended_model(cls) -> Dict:
        """Önerilen modeli getir"""
        return next(m for m in cls.MODELS if m['recommended'])
    
    @classmethod
    def get_model_by_id(cls, model_id: str) -> Optional[Dict]:
        """ID'ye göre model getir"""
        return next((m for m in cls.MODELS if m['id'] == model_id), None)
    
    @classmethod
    def list_models(cls, language: str = "tr") -> List[Dict]:
        """Dile göre modelleri listele"""
        return [m for m in cls.MODELS if language in m['languages']]
    
    @classmethod
    def print_models(cls):
        """Modelleri güzelce yazdır"""
        print("\n" + "="*60)
        print("🤖 TÜRKÇE TTS MODELLERİ")
        print("="*60)
        
        for model in cls.MODELS:
            print(f"\n📌 {model['name']}")
            if model['recommended']:
                print("   ⭐ ÖNERİLİR")
            print(f"   📝 {model['description']}")
            print(f"   🌍 Diller: {', '.join(model['languages'][:5])}")
            print(f"   ✨ Özellikler: {', '.join(model['features'])}")
            print(f"   📊 Kalite: {model['quality']} | Hız: {model['speed']}")
            print(f"   🔗 {model['model_path']}")
        
        print("\n" + "="*60)


def initialize_catalog():
    """Kataloğu başlat ve tara"""
    catalog = VoiceCatalog()
    catalog.scan_voices()
    catalog.print_catalog()
    
    print("\n")
    TurkishTTSModels.print_models()
    
    return catalog


if __name__ == "__main__":
    initialize_catalog()

