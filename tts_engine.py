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
    # Model cache - Singleton pattern (Optimizasyon Seviye 3)
    _model_cache = None
    _cached_device = None
    
    def __init__(self, voice_sample_path: str, use_progress_bar: bool = True):
        """
        M1 Mac için optimize edilmiş TTS motoru
        
        Args:
            voice_sample_path: Klonlanacak sesin yolu (10-30 saniye, WAV format)
            use_progress_bar: Progress bar kullan (web arayüzünde False önerilir)
        """
        # GPU Desteği (Optimizasyon Seviye 1 - 5-10x Hızlanma!)
        import os
        os.environ['PYTORCH_ENABLE_MPS_FALLBACK'] = '1'
        
        if torch.backends.mps.is_available():
            self.device = "mps"  # M1/M2/M3 GPU
            self._safe_print("🚀 M1/M2/M3 GPU (MPS) kullanılıyor - 5-10x daha hızlı!")
        elif torch.cuda.is_available():
            self.device = "cuda"
            self._safe_print("🚀 NVIDIA GPU kullanılıyor!")
        else:
            self.device = "cpu"
            self._safe_print("⚠️  GPU bulunamadı, CPU kullanılıyor (yavaş olacak)")
        
        self.use_progress_bar = use_progress_bar
        self._safe_print(f"🖥️  Cihaz: {self.device.upper()}")
        
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
        
        # Model yükle (Cache kullan - Optimizasyon Seviye 3)
        if M1OptimizedTTS._model_cache is None or M1OptimizedTTS._cached_device != self.device:
            self._safe_print("📥 XTTS v2 modeli yükleniyor...")
            self._safe_print("   (İlk seferinde ~2GB indirecek, biraz sürebilir)")
            
            try:
                M1OptimizedTTS._model_cache = TTS("tts_models/multilingual/multi-dataset/xtts_v2").to(self.device)
                M1OptimizedTTS._cached_device = self.device
                self._safe_print("✅ Model yüklendi ve cache'lendi!")
            except Exception as e:
                self._safe_print(f"❌ Model yüklenirken hata: {e}")
                raise
        else:
            self._safe_print("✅ Model cache'den yüklendi (hızlı başlatma)!")
        
        self.tts = M1OptimizedTTS._model_cache
        
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
    
    def generate_single_sentence(self, text: str, output_path: str, show_progress: bool = True) -> bool:
        """Tek bir cümleyi seslendir"""
        try:
            if show_progress:
                self._safe_print(f"🎤 Seslendiriliyor: {text[:50]}...")
            
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
                if show_progress:
                    size_kb = os.path.getsize(output_path) / 1024
                    self._safe_print(f"   ✅ Başarılı: {size_kb:.1f} KB")
                return True
            else:
                self._safe_print(f"   ❌ Dosya oluşturulamadı: {output_path}")
                return False
                
        except Exception as e:
            self._safe_print(f"\n❌ HATA: {type(e).__name__}: {e}")
            self._safe_print(f"   Metin: {text[:100]}")
            import traceback
            traceback.print_exc()
            return False
    
    def generate_batch(self, texts: List[str], output_paths: List[str]) -> List[bool]:
        """
        Batch olarak birden fazla cümleyi işle (Optimizasyon Seviye 2)
        
        Args:
            texts: İşlenecek metinler
            output_paths: Çıktı dosya yolları
            
        Returns:
            Her cümle için başarı durumu (True/False)
        """
        results = []
        for text, output_path in zip(texts, output_paths):
            success = self.generate_single_sentence(text, output_path, show_progress=False)
            results.append(success)
        return results
    
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
        
        # Batch processing için ayar (Optimizasyon Seviye 2)
        BATCH_SIZE = 3 if self.device == "mps" or self.device == "cuda" else 1
        if BATCH_SIZE > 1:
            self._safe_print(f"🔄 Batch processing aktif: {BATCH_SIZE} cümle/batch")
        
        if start_from > 0:
            self._safe_print(f"🔄 {start_from}. cümleden devam ediliyor...")
        
        audio_chunks = []
        failed_sentences = []
        
        start_time = time.time()
        
        # Progress bar - Web arayüzünde tqdm devre dışı
        if self.use_progress_bar:
            try:
                iterator = tqdm(range(start_from, total, BATCH_SIZE), desc="🎤 Seslendirme", disable=False)
            except (BrokenPipeError, IOError):
                # tqdm başlatma hatası - normal range kullan
                iterator = range(start_from, total, BATCH_SIZE)
                self.use_progress_bar = False
        else:
            iterator = range(start_from, total, BATCH_SIZE)
        
        for i in iterator:
            batch_end = min(i + BATCH_SIZE, total)
            batch_sentences = sentences[i:batch_end]
            
            # Batch için metinler ve dosya yolları hazırla
            batch_texts = [s['text'] for s in batch_sentences]
            batch_paths = [os.path.join(self.temp_dir, f"chunk_{j:04d}.wav") 
                          for j in range(i, batch_end)]
            
            try:
                # Batch işle
                if BATCH_SIZE > 1:
                    self._safe_print(f"   🎤 Batch {i+1}-{batch_end}/{total} işleniyor...")
                    results = self.generate_batch(batch_texts, batch_paths)
                else:
                    # Tek cümle için
                    results = [self.generate_single_sentence(batch_texts[0], batch_paths[0])]
                
                # Her cümle için ses dosyalarını yükle
                for j, (success, sentence_data) in enumerate(zip(results, batch_sentences)):
                    sentence_idx = i + j
                    
                    if not success:
                        failed_sentences.append(sentence_idx)
                        continue
                    
                    chunk_path = batch_paths[j]
                    
                    # Ses dosyasını yükle
                    audio = AudioSegment.from_wav(chunk_path)
                    
                    # Normalize et
                    audio = audio.normalize()
                    
                    # Duraklama ekle
                    pause_ms = int(sentence_data['pause_after'] * 1000)
                    silence = AudioSegment.silent(duration=pause_ms)
                    
                    audio_chunks.append(audio + silence)
                
                # İlerleme göstergesi
                processed = i + len(batch_sentences)
                if processed % 15 == 0 or processed == total:
                    elapsed = time.time() - start_time
                    avg_time = elapsed / (processed - start_from)
                    remaining = avg_time * (total - processed)
                    self._safe_print(f"   💾 {processed}/{total} tamamlandı")
                    self._safe_print(f"   ⏱️  Kalan süre: ~{remaining/60:.1f} dakika")
                
                # Web arayüzü için ilerleme
                if not self.use_progress_bar and processed % 5 == 0:
                    progress_pct = ((processed - start_from) / (total - start_from)) * 100
                    self._safe_print(f"   ⏳ İlerleme: {processed}/{total} ({progress_pct:.1f}%)")
                
            except Exception as e:
                self._safe_print(f"\n⚠️  Hata (batch {i}-{batch_end}): {e}")
                for j in range(i, batch_end):
                    failed_sentences.append(j)
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
        """Tahmini süre hesapla (optimize edilmiş)"""
        # Optimizasyon sonrası hızlar
        if self.device == "mps" or self.device == "cuda":
            # GPU + Batch: 1-1.5 saniye/cümle
            seconds_per_sentence = 1.5
        else:
            # CPU: 15 saniye/cümle
            seconds_per_sentence = 15
        
        total_seconds = num_sentences * seconds_per_sentence
        hours = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60
        
        if hours > 0:
            return f"{hours}s {minutes}d"
        else:
            return f"~{minutes}d" if minutes > 0 else "< 1d"


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

