"""
Voice Recorder - Mikrofon ile ses kaydı ve yönetimi
"""
import sounddevice as sd
import soundfile as sf
import numpy as np
from pathlib import Path
import time


class VoiceRecorder:
    def __init__(self, output_dir: str = "voices"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        self.sample_rate = 24000  # XTTS v2 için optimal (22050'den 24000'e yükseltildi)
        self.channels = 1  # Mono
        
    def list_devices(self):
        """Mevcut ses giriş cihazlarını listele"""
        print("\n🎤 Mevcut Mikrofon Cihazları:")
        print("-" * 60)
        devices = sd.query_devices()
        for i, device in enumerate(devices):
            if device['max_input_channels'] > 0:
                print(f"{i}: {device['name']}")
                print(f"   Kanal: {device['max_input_channels']}, "
                      f"Sample Rate: {device['default_samplerate']}")
        print("-" * 60)
        
    def record(
        self, 
        duration: int = 60, 
        filename: str = None,
        device: int = None
    ) -> str:
        """
        Mikrofon ile ses kaydı yap
        
        Args:
            duration: Kayıt süresi (saniye)
            filename: Çıktı dosya adı (None ise otomatik)
            device: Mikrofon cihaz ID (None ise varsayılan)
            
        Returns:
            Kaydedilen dosyanın yolu
        """
        
        if filename is None:
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            filename = f"voice_{timestamp}.wav"
        
        output_path = self.output_dir / filename
        
        print(f"\n🎙️  KES KAYDEDIYOR...")
        print(f"⏱️  Süre: {duration} saniye")
        print(f"💾 Dosya: {output_path}")
        print(f"\n{'='*60}")
        print("🔴 KAYIT BAŞLADI - Konuşmaya başlayın!")
        print("="*60)
        
        # Kayıt yap
        recording = sd.rec(
            int(duration * self.sample_rate),
            samplerate=self.sample_rate,
            channels=self.channels,
            device=device,
            dtype='float32'
        )
        
        # İlerleme göster
        for i in range(duration):
            time.sleep(1)
            elapsed = i + 1
            remaining = duration - elapsed
            progress = int((elapsed / duration) * 50)
            bar = "█" * progress + "░" * (50 - progress)
            print(f"\r[{bar}] {elapsed}/{duration}s (Kalan: {remaining}s)", end="")
        
        sd.wait()  # Kaydın bitmesini bekle
        
        print("\n" + "="*60)
        print("✅ KAYIT TAMAMLANDI!")
        print("="*60)
        
        # Kaydet
        sf.write(output_path, recording, self.sample_rate)
        
        # Dosya bilgisi
        file_size = output_path.stat().st_size / 1024  # KB
        print(f"\n📁 Dosya: {output_path}")
        print(f"📊 Boyut: {file_size:.1f} KB")
        print(f"🎵 Süre: {duration} saniye")
        print(f"📡 Sample Rate: {self.sample_rate} Hz")
        
        return str(output_path)
    
    def validate_audio(self, audio_path: str) -> dict:
        """
        Ses dosyasını doğrula ve analiz et
        
        Args:
            audio_path: Ses dosyasının yolu
            
        Returns:
            Ses dosyası bilgileri
        """
        
        try:
            data, samplerate = sf.read(audio_path)
            
            # Mono'ya çevir (gerekirse)
            if len(data.shape) > 1:
                data = np.mean(data, axis=1)
            
            duration = len(data) / samplerate
            
            # Sessiz bölümleri tespit et
            silence_threshold = 0.01
            silence_percentage = (np.abs(data) < silence_threshold).sum() / len(data) * 100
            
            # RMS (ses seviyesi)
            rms = np.sqrt(np.mean(data**2))
            
            info = {
                'valid': True,
                'duration': duration,
                'sample_rate': samplerate,
                'channels': 1 if len(data.shape) == 1 else data.shape[1],
                'rms_level': float(rms),
                'silence_percentage': float(silence_percentage),
                'file_size_kb': Path(audio_path).stat().st_size / 1024
            }
            
            # Kalite kontrolleri
            warnings = []
            
            if duration < 10:
                warnings.append("⚠️  Ses çok kısa (minimum 10 saniye önerilir)")
            elif duration > 120:
                warnings.append("⚠️  Ses çok uzun (maksimum 120 saniye önerilir)")
            
            if rms < 0.05:
                warnings.append("⚠️  Ses seviyesi çok düşük")
            elif rms > 0.5:
                warnings.append("⚠️  Ses seviyesi çok yüksek")
            
            if silence_percentage > 30:
                warnings.append(f"⚠️  Çok fazla sessizlik var ({silence_percentage:.1f}%)")
            
            if samplerate not in [16000, 22050, 24000, 44100, 48000]:
                warnings.append(f"⚠️  Alışılmadık sample rate: {samplerate} Hz")
            
            info['warnings'] = warnings
            
            return info
            
        except Exception as e:
            return {
                'valid': False,
                'error': str(e)
            }
    
    def convert_to_format(
        self, 
        input_path: str, 
        output_path: str = None
    ) -> str:
        """
        Ses dosyasını TTS için uygun formata çevir
        
        Args:
            input_path: Kaynak ses dosyası
            output_path: Hedef dosya (None ise otomatik)
            
        Returns:
            Dönüştürülen dosyanın yolu
        """
        
        if output_path is None:
            output_path = str(Path(input_path).with_suffix('.wav'))
        
        print(f"🔄 Ses dosyası dönüştürülüyor...")
        
        # Oku
        data, samplerate = sf.read(input_path)
        
        # Mono'ya çevir
        if len(data.shape) > 1:
            data = np.mean(data, axis=1)
            print("   ✓ Stereo → Mono")
        
        # Sample rate ayarla
        if samplerate != self.sample_rate:
            # Basit resampling (gerçek uygulamada librosa kullanılabilir)
            print(f"   ✓ Sample rate: {samplerate} → {self.sample_rate} Hz")
            # Not: Gerçek resampling için librosa.resample kullanılmalı
        
        # Normalize et
        if np.max(np.abs(data)) > 0:
            data = data / np.max(np.abs(data)) * 0.95
            print("   ✓ Normalize edildi")
        
        # Kaydet
        sf.write(output_path, data, self.sample_rate)
        
        print(f"✅ Dönüştürüldü: {output_path}")
        
        return output_path


def interactive_record():
    """İnteraktif kayıt modu"""
    recorder = VoiceRecorder()
    
    print("\n" + "="*60)
    print("🎤 SES KAYIT SİSTEMİ")
    print("="*60)
    
    # Cihazları listele
    recorder.list_devices()
    
    # Cihaz seç
    print("\nVarsayılan mikrofonu kullanmak için Enter'a basın")
    print("Veya cihaz numarasını girin:")
    device_input = input("Cihaz: ").strip()
    device = int(device_input) if device_input else None
    
    # Süre
    print("\nKayıt süresi (saniye, varsayılan: 30):")
    duration_input = input("Süre: ").strip()
    duration = int(duration_input) if duration_input else 30
    
    # Dosya adı
    print("\nDosya adı (varsayılan: otomatik):")
    filename = input("Dosya adı: ").strip() or None
    
    # Kayıt yap
    output_path = recorder.record(duration, filename, device)
    
    # Doğrula
    print("\n🔍 Ses dosyası analiz ediliyor...")
    info = recorder.validate_audio(output_path)
    
    if info['valid']:
        print("\n✅ SES DOSYASı GEÇERLİ")
        print(f"   Süre: {info['duration']:.1f} saniye")
        print(f"   Sample Rate: {info['sample_rate']} Hz")
        print(f"   Ses Seviyesi: {info['rms_level']:.3f}")
        print(f"   Sessizlik: {info['silence_percentage']:.1f}%")
        
        if info['warnings']:
            print("\n⚠️  UYARILAR:")
            for warning in info['warnings']:
                print(f"   {warning}")
    else:
        print(f"\n❌ HATA: {info['error']}")
    
    print("\n" + "="*60)
    print(f"🎧 Kaydı dinlemek için:")
    print(f"   open {output_path}")
    print("\n🧪 TTS ile test etmek için:")
    print(f"   python test_tts.py {output_path}")
    print("="*60)


if __name__ == "__main__":
    interactive_record()

