"""
OpenAI TTS API Entegrasyonu (Direkt)
Daha hızlı ve güvenilir TTS için OpenAI API
"""

import requests
import os
from typing import List, Dict
from pydub import AudioSegment
import time


class OpenAITTSAPI:
    """
    OpenAI TTS API - Direkt Bağlantı
    https://platform.openai.com/docs/guides/text-to-speech
    """
    
    def __init__(self, api_key: str = None):
        """
        Args:
            api_key: OpenAI API Key (sk-...)
        """
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.base_url = "https://api.openai.com/v1"
        
        if not self.api_key:
            raise ValueError("OpenAI API key gerekli! OPENAI_API_KEY ortam değişkenini ayarlayın.")
        
        self._safe_print(f"⚡ OpenAI TTS API hazır!")
    
    def _safe_print(self, message: str):
        """Güvenli print"""
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
        url = f"{self.base_url}/audio/speech"
        
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
        
        response = requests.post(url, json=data, headers=headers, timeout=30)
        
        if response.status_code == 200:
            audio_bytes = response.content
            
            if output_path:
                with open(output_path, 'wb') as f:
                    f.write(audio_bytes)
            
            return audio_bytes
        else:
            raise Exception(f"OpenAI API Hatası: {response.status_code} - {response.text}")
    
    def generate_audiobook(
        self, 
        sentences: List[Dict], 
        voice: str = "alloy", 
        output_path: str = None
    ) -> str:
        """
        Tüm kitabı seslendir
        
        Args:
            sentences: Cümle listesi
            voice: Ses tipi
            output_path: Çıktı dosyası
            
        Returns:
            Output MP3 dosya yolu
        """
        audio_chunks = []
        failed_sentences = []
        
        total = len(sentences)
        self._safe_print(f"\n{'='*60}")
        self._safe_print(f"⚡ OPENAI TTS API - HIZLI SESLENDIRME")
        self._safe_print(f"{'='*60}")
        self._safe_print(f"📝 Cümle sayısı: {total}")
        self._safe_print(f"🎤 Ses tipi: {voice}")
        self._safe_print(f"⏱️  Tahmini süre: ~{total * 0.3 / 60:.1f} dakika")
        self._safe_print(f"{'='*60}\n")
        
        start_time = time.time()
        
        temp_dir = "temp_chunks"
        os.makedirs(temp_dir, exist_ok=True)
        
        for i, sentence_data in enumerate(sentences):
            text = sentence_data['text']
            temp_path = os.path.join(temp_dir, f"openai_chunk_{i:04d}.mp3")
            
            try:
                self.generate_speech(text, voice, temp_path)
                
                audio = AudioSegment.from_mp3(temp_path)
                audio = audio.normalize()
                
                pause_ms = int(sentence_data.get('pause_after', 0.5) * 1000)
                silence = AudioSegment.silent(duration=pause_ms)
                
                audio_chunks.append(audio + silence)
                
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
        
        self._safe_print("\n🔗 Ses dosyaları birleştiriliyor...")
        final_audio = sum(audio_chunks)
        final_audio = final_audio.normalize()
        
        if not output_path:
            output_path = f"outputs/audiobook_{int(time.time())}.mp3"
        
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        self._safe_print(f"💾 Kaydediliyor: {output_path}")
        final_audio.export(output_path, format="mp3", bitrate="192k", parameters=["-q:a", "2"])
        
        elapsed_minutes = (time.time() - start_time) / 60
        
        self._safe_print(f"\n{'='*60}")
        self._safe_print(f"✅ TAMAMLANDI!")
        self._safe_print(f"📁 Dosya: {output_path}")
        self._safe_print(f"⏱️  Süre: {elapsed_minutes:.1f} dakika")
        self._safe_print(f"📊 Başarılı: {len(audio_chunks)}/{total} cümle")
        self._safe_print(f"{'='*60}")
        
        # Temizlik
        import shutil
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)
        
        return output_path


# Test
if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("❌ OpenAI API key gerekli!")
        print("Kullanım: python openai_tts_api.py YOUR_API_KEY")
        print()
        print("API Key alma:")
        print("1. https://platform.openai.com/api-keys")
        print("2. 'Create new secret key' tıklayın")
        print("3. Key'i kopyalayın (sk-...)")
        sys.exit(1)
    
    api_key = sys.argv[1]
    
    print("\n🧪 OpenAI TTS API Test...")
    
    try:
        api = OpenAITTSAPI(api_key)
        
        test_sentences = [
            {'text': 'Merhaba! Bu OpenAI TTS API ile oluşturulmuş bir test sesidir.', 'pause_after': 0.6},
            {'text': 'Ses kalitesi çok yüksek ve hızlı çalışıyor.', 'pause_after': 0.5}
        ]
        
        output = api.generate_audiobook(test_sentences, voice="alloy", output_path="test_openai.mp3")
        print(f"\n✅ Test başarılı: {output}")
        
    except Exception as e:
        print(f"\n❌ Test başarısız: {e}")

