"""
TTS Engine - M1 Optimize Ses Üretim Motoru
"""
import torch
from TTS.api import TTS
from pydub import AudioSegment
import os
from tqdm import tqdm
from typing import List, Dict
import time
import sys


class M1OptimizedTTS:
    def __init__(self, voice_sample_path: str, use_progress_bar: bool = True):
        """
        M1 Mac için optimize edilmiş TTS motoru
        
        Args:
            voice_sample_path: Klonlanacak sesin yolu (10-30 saniye, WAV format)
            use_progress_bar: Progress bar kullan (web arayüzünde False önerilir)
        """
        # XTTS v2 MPS ile FFT sorunu yaşıyor, CPU kullanıyoruz
        # TODO: PyTorch ve TTS güncellendiğinde MPS'e geç
        self.device = "cpu"
        self.use_progress_bar = use_progress_bar
        self._safe_print(f"🖥️  Cihaz: {self.device}")
        self._safe_print("ℹ️  XTTS v2 şu an MPS'i tam desteklemiyor, CPU kullanılıyor")
        
        # MPS fallback için environment variable
        import os
        os.environ['PYTORCH_ENABLE_MPS_FALLBACK'] = '1'
        
        # Ses örneği kontrol
        if not os.path.exists(voice_sample_path):
            raise FileNotFoundError(f"Ses örneği bulunamadı: {voice_sample_path}")
        
        # Ses dosyası bilgilerini göster
        import soundfile as sf
        try:
            audio_data, sample_rate = sf.read(voice_sample_path)
            duration = len(audio_data) / sample_rate
            self._safe_print(f"\n{'='*60}")
            self._safe_print(f"🎵 REFERANS SES BİLGİLERİ (SES KLONLAMA İÇİN)")
            self._safe_print(f"{'='*60}")
            self._safe_print(f"📁 Dosya: {voice_sample_path}")
            self._safe_print(f"⏱️  Süre: {duration:.1f} saniye")
            self._safe_print(f"🔊 Sample Rate: {sample_rate} Hz")
            self._safe_print(f"📊 Boyut: {len(audio_data)} sample")
            
            if duration < 3:
                self._safe_print(f"⚠️  UYARI: Ses çok kısa ({duration:.1f}s). En az 10-30 saniye önerilir!")
            elif duration < 10:
                self._safe_print(f"⚠️  UYARI: Ses biraz kısa ({duration:.1f}s). 10-30 saniye önerilir.")
            elif duration > 60:
                self._safe_print(f"⚠️  UYARI: Ses çok uzun ({duration:.1f}s). 10-30 saniye arası önerilir!")
            else:
                self._safe_print(f"✅ Ses süresi uygun!")
            self._safe_print(f"{'='*60}\n")
        except Exception as e:
            self._safe_print(f"❌ HATA: Ses dosyası okunamadı: {e}")
            raise
        
        self.voice_sample = voice_sample_path
        
        # Model yükle
        self._safe_print("📥 XTTS v2 modeli yükleniyor...")
        self._safe_print("   (İlk seferinde ~2GB indirecek, biraz sürebilir)")
        
        try:
            self.tts = TTS("tts_models/multilingual/multi-dataset/xtts_v2").to(self.device)
            self._safe_print("✅ Model yüklendi!")
        except Exception as e:
            self._safe_print(f"❌ Model yüklenirken hata: {e}")
            raise
        
        # Geçici dosyalar için klasör
        self.temp_dir = "temp_chunks"
        os.makedirs(self.temp_dir, exist_ok=True)
    
    def _safe_print(self, message: str):
        """Güvenli print - BrokenPipe hatası önlenir"""
        try:
            print(message)
            sys.stdout.flush()
        except (BrokenPipeError, IOError):
            # Web arayüzünde pipe bozulabilir, sessizce devam et
            pass
    
    def generate_single_sentence(self, text: str, output_path: str) -> bool:
        """Tek bir cümleyi seslendir"""
        try:
            self._safe_print(f"🎤 Seslendiriliyor: {text[:50]}...")
            self._safe_print(f"   Ses örneği: {self.voice_sample}")
            self._safe_print(f"   Hedef: {output_path}")
            
            # TTS çağrısını yap - SES KLONLAMA İÇİN OPTİMİZE
            # NOT: XTTS v2'de fazla parametre ses klonlamayı bozuyor!
            # Sadece temel parametreleri kullanıyoruz
            self.tts.tts_to_file(
                text=text,
                speaker_wav=self.voice_sample,  # REFERANS SES - ÖNEMLİ!
                language="tr",
                file_path=output_path
            )
            
            # Dosya oluşturuldu mu kontrol et
            if os.path.exists(output_path) and os.path.getsize(output_path) > 0:
                size_kb = os.path.getsize(output_path) / 1024
                self._safe_print(f"   ✅ Başarılı: {size_kb:.1f} KB")
                return True
            else:
                self._safe_print(f"   ❌ Dosya oluşturulamadı: {output_path}")
                return False
                
        except Exception as e:
            self._safe_print(f"\n❌ HATA: {type(e).__name__}: {e}")
            self._safe_print(f"   Metin: {text[:100]}")
            self._safe_print(f"   Ses: {self.voice_sample}")
            import traceback
            traceback.print_exc()
            return False
    
    def generate_audiobook(
        self, 
        sentences: List[Dict],
        output_path: str = "audiobook.mp3",
        start_from: int = 0
    ) -> str:
        """
        Tüm kitabı seslendir
        
        Args:
            sentences: Cümle listesi (sentence_processor'dan gelen)
            output_path: Çıktı dosyası yolu
            start_from: Hangi cümleden başlanacak (hata durumunda devam için)
        """
        
        total = len(sentences)
        self._safe_print(f"\n🎙️  {total} cümle seslendiriliyor...")
        self._safe_print(f"⏱️  Tahmini süre: {self.estimate_time(total)}")
        
        if start_from > 0:
            self._safe_print(f"🔄 {start_from}. cümleden devam ediliyor...")
        
        audio_chunks = []
        failed_sentences = []
        
        start_time = time.time()
        
        # Progress bar - Web arayüzünde tqdm devre dışı
        if self.use_progress_bar:
            try:
                iterator = tqdm(range(start_from, total), desc="🎤 Seslendirme", disable=False)
            except (BrokenPipeError, IOError):
                # tqdm başlatma hatası - normal range kullan
                iterator = range(start_from, total)
                self.use_progress_bar = False
        else:
            iterator = range(start_from, total)
        
        for i in iterator:
            sentence_data = sentences[i]
            
            try:
                # Ses dosyası yolu
                chunk_path = os.path.join(self.temp_dir, f"chunk_{i:04d}.wav")
                
                # TTS
                success = self.generate_single_sentence(
                    sentence_data['text'],
                    chunk_path
                )
                
                if not success:
                    failed_sentences.append(i)
                    continue
                
                # Ses dosyasını yükle
                audio = AudioSegment.from_wav(chunk_path)
                
                # Normalize et
                audio = audio.normalize()
                
                # Duraklama ekle
                pause_ms = int(sentence_data['pause_after'] * 1000)
                silence = AudioSegment.silent(duration=pause_ms)
                
                audio_chunks.append(audio + silence)
                
                # Her 50 cümlede bir ara kayıt (güvenlik için)
                if (i + 1) % 50 == 0:
                    elapsed = time.time() - start_time
                    avg_time = elapsed / (i - start_from + 1)
                    remaining = avg_time * (total - i - 1)
                    self._safe_print(f"\n   💾 {i+1}/{total} tamamlandı")
                    self._safe_print(f"   ⏱️  Kalan süre: ~{remaining/60:.1f} dakika")
                
                # Web arayüzü için her 5 cümlede bir ilerleme göster
                if not self.use_progress_bar and (i + 1) % 5 == 0:
                    progress_pct = ((i + 1 - start_from) / (total - start_from)) * 100
                    self._safe_print(f"   ⏳ İlerleme: {i+1}/{total} ({progress_pct:.1f}%)")
                
            except Exception as e:
                self._safe_print(f"\n⚠️  Hata (cümle {i}): {e}")
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
        
        # Dışa aktar
        self._safe_print(f"💾 Kaydediliyor: {output_path}")
        final_audio.export(
            output_path, 
            format="mp3", 
            bitrate="192k",
            parameters=["-q:a", "2"]  # Yüksek kalite
        )
        
        # İstatistikler
        duration_minutes = len(final_audio) / 1000 / 60
        elapsed_minutes = (time.time() - start_time) / 60
        
        self._safe_print(f"\n" + "="*60)
        self._safe_print(f"✅ TAMAMLANDI!")
        self._safe_print(f"📁 Dosya: {output_path}")
        self._safe_print(f"🎵 Süre: {duration_minutes:.1f} dakika")
        self._safe_print(f"⏱️  İşlem süresi: {elapsed_minutes:.1f} dakika")
        self._safe_print(f"📊 Başarılı: {len(audio_chunks)}/{total} cümle")
        
        if failed_sentences:
            self._safe_print(f"⚠️  Başarısız: {len(failed_sentences)} cümle")
            self._safe_print(f"   Cümle numaraları: {failed_sentences[:10]}")
        
        self._safe_print("="*60)
        
        # Geçici dosyaları temizle
        self.cleanup()
        
        return output_path
    
    def cleanup(self):
        """Geçici dosyaları sil"""
        import shutil
        if os.path.exists(self.temp_dir):
            try:
                shutil.rmtree(self.temp_dir)
                self._safe_print("🗑️  Geçici dosyalar temizlendi")
            except Exception as e:
                self._safe_print(f"⚠️  Geçici dosyalar silinemedi: {e}")
    
    def estimate_time(self, num_sentences: int) -> str:
        """Tahmini süre hesapla"""
        # M1'de ortalama 3-5 saniye/cümle
        if self.device == "mps":
            seconds_per_sentence = 4
        else:
            seconds_per_sentence = 15
        
        total_seconds = num_sentences * seconds_per_sentence
        hours = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60
        
        if hours > 0:
            return f"{hours}s {minutes}d"
        else:
            return f"{minutes}d"


def test_tts_engine():
    """Test fonksiyonu"""
    import sys
    
    if len(sys.argv) < 2:
        print("Kullanım: python tts_engine.py <voice_sample.wav>")
        sys.exit(1)
    
    voice_sample = sys.argv[1]
    
    # Test cümleleri
    test_sentences = [
        {
            'text': 'Merhaba! Bu bir test cümlesidir.',
            'type': 'exclamation',
            'length': 5,
            'pause_after': 0.6
        },
        {
            'text': 'Ses klonlama sistemi çalışıyor mu?',
            'type': 'question',
            'length': 5,
            'pause_after': 0.6
        },
        {
            'text': 'Evet, çok iyi çalışıyor.',
            'type': 'statement',
            'length': 4,
            'pause_after': 0.5
        }
    ]
    
    print("\n🧪 TTS Motor Test Başlıyor...")
    
    engine = M1OptimizedTTS(voice_sample)
    output = engine.generate_audiobook(test_sentences, "test_output.mp3")
    
    print(f"\n✅ Test tamamlandı: {output}")


if __name__ == "__main__":
    test_tts_engine()

