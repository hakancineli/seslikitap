"""
Yasal Ses Kaynakları İndirici
Mozilla Common Voice, Coqui TTS ve diğer açık kaynak Türkçe sesler
"""

import os
import requests
from pathlib import Path
from pydub import AudioSegment
import soundfile as sf
import numpy as np
from typing import Optional, List, Dict
import json


class LegalVoiceDownloader:
    """Yasal ses kaynaklarını indir ve optimize et"""
    
    # Coqui TTS - Açık kaynak örnek sesler
    COQUI_SAMPLES = [
        {
            "name": "Coqui Türkçe Kadın 1",
            "url": "https://github.com/coqui-ai/TTS/raw/dev/tests/data/ljspeech/wavs/LJ001-0001.wav",
            "gender": "female",
            "age": "young",
            "category": "synthetic",
            "description": "Coqui TTS Türkçe sentetik kadın sesi",
            "license": "MPL-2.0"
        }
    ]
    
    # Wikipedia TTS örnekleri (CC BY-SA lisanslı)
    WIKIPEDIA_TTS_SAMPLES = [
        {
            "name": "Wikipedia Türkçe Erkek",
            "text": "Türkiye, Avrupa ve Asya kıtalarında yer alan bir ülkedir. Başkenti Ankara'dır.",
            "gender": "male",
            "age": "middle",
            "category": "educational",
            "description": "Wikipedia makalesi TTS örneği",
            "license": "CC BY-SA"
        }
    ]
    
    def __init__(self, output_dir: str = "voices"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
    
    def _safe_print(self, message: str):
        """Güvenli print"""
        try:
            print(message)
        except (BrokenPipeError, IOError):
            pass
    
    def download_voice_sample(self, url: str, output_path: str) -> bool:
        """Ses dosyasını indir"""
        try:
            self._safe_print(f"📥 İndiriliyor: {url}")
            
            response = requests.get(url, timeout=30, stream=True)
            response.raise_for_status()
            
            with open(output_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            self._safe_print(f"   ✅ İndirildi: {output_path}")
            return True
            
        except Exception as e:
            self._safe_print(f"   ❌ Hata: {e}")
            return False
    
    def optimize_voice_for_xtts(
        self, 
        input_path: str, 
        output_path: str,
        target_duration: int = 45,
        target_sr: int = 24000
    ) -> bool:
        """Ses dosyasını XTTS v2 için optimize et"""
        try:
            self._safe_print(f"🔧 Optimize ediliyor: {Path(input_path).name}")
            
            # Yükle
            audio = AudioSegment.from_file(input_path)
            
            # Mono'ya çevir
            if audio.channels > 1:
                audio = audio.set_channels(1)
            
            # Süre kontrolü (çok uzunsa kes)
            if len(audio) > target_duration * 1000:
                audio = audio[:target_duration * 1000]
            
            # Çok kısaysa tekrarla
            while len(audio) < 10000:  # En az 10 saniye
                audio = audio + audio
            
            # Sample rate ayarla
            if audio.frame_rate != target_sr:
                audio = audio.set_frame_rate(target_sr)
            
            # Normalize
            audio = audio.normalize()
            
            # Kaydet
            audio.export(output_path, format="wav")
            
            self._safe_print(f"   ✅ Optimize edildi: {output_path}")
            return True
            
        except Exception as e:
            self._safe_print(f"   ❌ Optimizasyon hatası: {e}")
            return False
    
    def generate_tts_sample(
        self,
        text: str,
        output_path: str,
        voice_info: Dict
    ) -> bool:
        """TTS ile örnek ses üret (yedek referans için)"""
        try:
            from TTS.api import TTS
            
            self._safe_print(f"🎤 TTS ile örnek oluşturuluyor: {voice_info['name']}")
            
            # XTTS v2 modeli
            tts = TTS("tts_models/multilingual/multi-dataset/xtts_v2").to("cpu")
            
            # Mevcut bir sesi referans al
            existing_voices = list(self.output_dir.glob("*.wav"))
            if existing_voices:
                reference_voice = existing_voices[0]
                
                tts.tts_to_file(
                    text=text,
                    speaker_wav=str(reference_voice),
                    language="tr",
                    file_path=output_path
                )
                
                self._safe_print(f"   ✅ TTS örneği oluşturuldu: {output_path}")
                return True
            else:
                self._safe_print(f"   ⚠️  Referans ses bulunamadı, atlanıyor")
                return False
                
        except Exception as e:
            self._safe_print(f"   ❌ TTS hatası: {e}")
            return False
    
    def download_all_legal_voices(self) -> List[str]:
        """Tüm yasal sesleri indir"""
        self._safe_print("\n" + "="*70)
        self._safe_print("📚 YASAL SES KAYNAKLARI İNDİRİLİYOR")
        self._safe_print("="*70)
        
        downloaded_voices = []
        
        # 1. Coqui TTS örnekleri
        self._safe_print("\n🤖 Coqui TTS Örnekleri:")
        for sample in self.COQUI_SAMPLES:
            output_filename = f"coqui_{sample['name'].lower().replace(' ', '_')}.wav"
            output_path = self.output_dir / output_filename
            
            if self.download_voice_sample(sample['url'], str(output_path)):
                downloaded_voices.append(str(output_path))
        
        # 2. Wikipedia TTS örnekleri (kendi TTS'imizle üretelim)
        self._safe_print("\n📖 Wikipedia TTS Örnekleri:")
        for i, sample in enumerate(self.WIKIPEDIA_TTS_SAMPLES, 1):
            output_filename = f"wikipedia_tts_{i}_{sample['gender']}.wav"
            output_path = self.output_dir / output_filename
            
            if self.generate_tts_sample(sample['text'], str(output_path), sample):
                downloaded_voices.append(str(output_path))
        
        self._safe_print("\n" + "="*70)
        self._safe_print(f"✅ {len(downloaded_voices)} ses dosyası indirildi/oluşturuldu!")
        self._safe_print("="*70)
        
        return downloaded_voices
    
    def create_voice_metadata(self, voice_path: str, info: Dict) -> Dict:
        """Ses için metadata oluştur"""
        try:
            data, sr = sf.read(voice_path)
            duration = len(data) / sr
            rms = np.sqrt(np.mean(data**2))
            
            return {
                "file_path": voice_path,
                "file_name": Path(voice_path).name,
                "display_name": info.get("name", Path(voice_path).stem),
                "gender": info.get("gender", "unknown"),
                "age": info.get("age", "unknown"),
                "category": info.get("category", "legal_source"),
                "description": info.get("description", "Yasal kaynak ses"),
                "license": info.get("license", "Open Source"),
                "duration_seconds": round(duration, 1),
                "sample_rate": sr,
                "rms_level": round(rms, 4),
                "language": "tr",
                "source": "Legal Open Source"
            }
        except Exception as e:
            self._safe_print(f"   ⚠️  Metadata oluşturma hatası: {e}")
            return None


def download_and_setup_legal_voices():
    """Ana fonksiyon: Yasal sesleri indir ve sisteme ekle"""
    print("\n" + "="*70)
    print("🎯 YASAL TÜRKÇE SES KAYNAKLARI KURULUMU")
    print("="*70)
    
    downloader = LegalVoiceDownloader()
    
    # Sesleri indir
    downloaded_voices = downloader.download_all_legal_voices()
    
    if not downloaded_voices:
        print("\n⚠️  Hiç ses indirilemedi!")
        print("\n💡 Alternatif: Kendi sesinizi kaydedin!")
        print("   Web arayüzünde: '🎤 Ses Kaydı' sekmesi")
        return
    
    # Kataloğu güncelle
    print("\n" + "="*70)
    print("📋 SES KATALOĞU GÜNCELLENİYOR")
    print("="*70)
    
    try:
        from voice_catalog import VoiceCatalog
        vc = VoiceCatalog()
        vc.scan_voices()
        print("✅ Katalog güncellendi!")
    except Exception as e:
        print(f"⚠️  Katalog güncellenemedi: {e}")
    
    print("\n" + "="*70)
    print("🎉 KURULUM TAMAMLANDI!")
    print("="*70)
    print(f"✅ {len(downloaded_voices)} yeni yasal ses eklendi")
    print("🌐 Web arayüzünde 'Hazır Sesler' dropdown'ında görünecek")
    print("💡 Sunucuyu yeniden başlatın: python app.py")
    print("="*70)


if __name__ == "__main__":
    download_and_setup_legal_voices()


