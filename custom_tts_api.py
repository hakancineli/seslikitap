"""
Özel TTS API Entegrasyonu
OpenAI-compatible endpoint ile hızlı ses üretimi
"""

import requests
import os
from typing import List, Dict
from pydub import AudioSegment
import time


class CustomTTSAPI:
    """
    Özel TTS API - OpenAI-compatible
    API: http://sk-5aa9382d8a504e31a0fa260817bc65fd@91.218.66.217:443
    """
    
    def __init__(self, api_url: str = None):
        """
        API başlat
        
        Args:
            api_url: Full API URL (format: http://API_KEY@HOST:PORT)
        """
        self.api_url = api_url or "http://sk-5aa9382d8a504e31a0fa260817bc65fd@91.218.66.217:443"
        
        # URL'yi parse et
        if "@" in self.api_url:
            # Format: http://API_KEY@HOST:PORT
            parts = self.api_url.split("@")
            self.api_key = parts[0].replace("http://", "").replace("https://", "")
            self.base_url = f"http://{parts[1]}"
        else:
            # Sadece URL verilmiş
            self.api_key = None
            self.base_url = self.api_url
        
        self._safe_print(f"⚡ Özel TTS API hazır!")
        self._safe_print(f"📡 Endpoint: {self.base_url}")
    
    def _safe_print(self, message: str):
        """Güvenli print - BrokenPipe hatası önlenir"""
        try:
            print(message)
        except (BrokenPipeError, IOError):
            pass
    
    def generate_speech(self, text: str, voice: str = "alloy", output_path: str = None) -> bytes:
        """
        Tek bir metni seslendirme
        
        Args:
            text: Seslendirilecek metin
            voice: Ses tipi (alloy, echo, fable, onyx, nova, shimmer)
            output_path: Kaydedilecek dosya yolu
            
        Returns:
            Audio bytes (MP3)
        """
        url = f"{self.base_url}/v1/audio/speech"
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": "tts-1-hd",  # Yüksek kalite
            "input": text,
            "voice": voice,
            "response_format": "mp3"
        }
        
        try:
            response = requests.post(url, json=data, headers=headers, timeout=30)
            
            if response.status_code == 200:
                audio_bytes = response.content
                
                if output_path:
                    with open(output_path, 'wb') as f:
                        f.write(audio_bytes)
                
                return audio_bytes
            else:
                raise Exception(f"API Hatası: {response.status_code} - {response.text}")
        
        except requests.exceptions.Timeout:
            raise Exception("API zaman aşımı - 30 saniye")
        except requests.exceptions.ConnectionError:
            raise Exception(f"API bağlantı hatası - {self.base_url}")
        except Exception as e:
            raise Exception(f"API hatası: {str(e)}")
    
    def generate_audiobook(
        self, 
        sentences: List[Dict], 
        voice: str = "alloy", 
        output_path: str = None
    ) -> str:
        """
        Tüm kitabı seslendir (ÇOK HIZLI!)
        
        Args:
            sentences: Cümle listesi (sentence_processor'dan gelen)
            voice: Ses tipi
            output_path: Çıktı dosyası
            
        Returns:
            Output MP3 dosya yolu
        """
        audio_chunks = []
        failed_sentences = []
        
        total = len(sentences)
        self._safe_print(f"\n{'='*60}")
        self._safe_print(f"⚡ ÖZEL TTS API - HIZLI SESLENDIRME")
        self._safe_print(f"{'='*60}")
        self._safe_print(f"📝 Cümle sayısı: {total}")
        self._safe_print(f"🎤 Ses tipi: {voice}")
        self._safe_print(f"⏱️  Tahmini süre: ~{total * 0.3 / 60:.1f} dakika")
        self._safe_print(f"🚀 Hız: ~0.3 saniye/cümle (XTTS'den 5x hızlı!)")
        self._safe_print(f"{'='*60}\n")
        
        start_time = time.time()
        
        # Geçici dosyalar klasörü
        temp_dir = "temp_chunks"
        os.makedirs(temp_dir, exist_ok=True)
        
        for i, sentence_data in enumerate(sentences):
            text = sentence_data['text']
            temp_path = os.path.join(temp_dir, f"api_chunk_{i:04d}.mp3")
            
            try:
                # API'den ses al (çok hızlı - ~0.3 saniye!)
                self.generate_speech(text, voice, temp_path)
                
                # Ses dosyasını yükle
                audio = AudioSegment.from_mp3(temp_path)
                
                # Normalize
                audio = audio.normalize()
                
                # Duraklama ekle
                pause_ms = int(sentence_data.get('pause_after', 0.5) * 1000)
                silence = AudioSegment.silent(duration=pause_ms)
                
                audio_chunks.append(audio + silence)
                
                # İlerleme göster
                if (i + 1) % 10 == 0 or (i + 1) == total:
                    elapsed = time.time() - start_time
                    avg_time = elapsed / (i + 1)
                    remaining = avg_time * (total - i - 1)
                    progress_pct = ((i + 1) / total) * 100
                    
                    self._safe_print(f"   ⏳ {i+1}/{total} ({progress_pct:.1f}%) - Kalan: ~{remaining/60:.1f}dk")
            
            except Exception as e:
                self._safe_print(f"   ⚠️  Hata (cümle {i}): {e}")
                failed_sentences.append(i)
                continue
        
        if not audio_chunks:
            raise Exception("❌ Hiç ses üretilemedi!")
        
        # Tüm chunk'ları birleştir
        self._safe_print("\n🔗 Ses dosyaları birleştiriliyor...")
        final_audio = sum(audio_chunks)
        
        # Normalize et
        self._safe_print("🎚️  Ses seviyesi ayarlanıyor...")
        final_audio = final_audio.normalize()
        
        # Kaydet
        if not output_path:
            output_path = f"outputs/audiobook_{int(time.time())}.mp3"
        
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        self._safe_print(f"💾 Kaydediliyor: {output_path}")
        final_audio.export(
            output_path, 
            format="mp3", 
            bitrate="192k",
            parameters=["-q:a", "2"]
        )
        
        # İstatistikler
        duration_minutes = len(final_audio) / 1000 / 60
        elapsed_minutes = (time.time() - start_time) / 60
        
        self._safe_print(f"\n{'='*60}")
        self._safe_print(f"✅ TAMAMLANDI!")
        self._safe_print(f"📁 Dosya: {output_path}")
        self._safe_print(f"🎵 Süre: {duration_minutes:.1f} dakika")
        self._safe_print(f"⏱️  İşlem süresi: {elapsed_minutes:.1f} dakika")
        self._safe_print(f"📊 Başarılı: {len(audio_chunks)}/{total} cümle")
        self._safe_print(f"⚡ Ortalama: {(elapsed_minutes * 60 / total):.2f} saniye/cümle")
        
        if failed_sentences:
            self._safe_print(f"⚠️  Başarısız: {len(failed_sentences)} cümle")
            self._safe_print(f"   Cümle numaraları: {failed_sentences[:10]}")
        
        self._safe_print(f"{'='*60}")
        
        # Geçici dosyaları temizle
        self._cleanup(temp_dir)
        
        return output_path
    
    def _cleanup(self, temp_dir: str):
        """Geçici dosyaları temizle"""
        import shutil
        if os.path.exists(temp_dir):
            try:
                shutil.rmtree(temp_dir)
                self._safe_print("🗑️  Geçici dosyalar temizlendi")
            except Exception as e:
                self._safe_print(f"⚠️  Geçici dosyalar silinemedi: {e}")


def test_api():
    """Test fonksiyonu"""
    print("\n🧪 Özel TTS API Test Başlıyor...\n")
    
    api = CustomTTSAPI()
    
    # Test cümleleri
    test_sentences = [
        {
            'text': 'Merhaba! Bu özel TTS API ile oluşturulmuş bir test sesidir.',
            'pause_after': 0.6
        },
        {
            'text': 'API çok hızlı çalışıyor. Cümle başına yaklaşık 0.3 saniye!',
            'pause_after': 0.6
        },
        {
            'text': 'XTTS sisteminden 5 kat daha hızlı.',
            'pause_after': 0.5
        }
    ]
    
    output = api.generate_audiobook(test_sentences, voice="alloy", output_path="test_api_output.mp3")
    print(f"\n✅ Test tamamlandı: {output}")


if __name__ == "__main__":
    test_api()

