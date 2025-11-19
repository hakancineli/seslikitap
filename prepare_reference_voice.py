"""
Referans Ses Hazırlama - İlk 45 saniyeyi çıkar ve optimize et
"""
import soundfile as sf
import numpy as np
from scipy import signal

def prepare_reference_voice(input_file, output_file, duration_seconds=45):
    """
    Referans ses dosyasını XTTS v2 için optimize et
    - İlk X saniyeyi al
    - 24000 Hz'e dönüştür
    - Normalize et
    - Mono yap
    """
    
    print("\n" + "="*60)
    print("🎤 REFERANS SES OPTİMİZASYONU")
    print("="*60)
    
    # Ses dosyasını oku
    print(f"\n📂 Orijinal dosya okunuyor: {input_file}")
    data, sr = sf.read(input_file)
    
    print(f"   Sample Rate: {sr} Hz")
    print(f"   Toplam Süre: {len(data)/sr:.1f} saniye")
    
    # Mono'ya çevir
    if len(data.shape) > 1:
        print(f"   Stereo → Mono dönüştürülüyor...")
        data = np.mean(data, axis=1)
    
    # İlk X saniyeyi al
    target_samples = int(duration_seconds * sr)
    if len(data) > target_samples:
        print(f"   İlk {duration_seconds} saniye alınıyor...")
        data = data[:target_samples]
    
    # 24000 Hz'e resample (XTTS v2 için optimal)
    if sr != 24000:
        print(f"   Sample Rate dönüştürülüyor: {sr} Hz → 24000 Hz")
        # Resample oranını hesapla
        num_samples = int(len(data) * 24000 / sr)
        data = signal.resample(data, num_samples)
        sr = 24000
    
    # Normalize et (0.95 peak)
    print(f"   Normalize ediliyor...")
    max_val = np.max(np.abs(data))
    if max_val > 0:
        data = data / max_val * 0.95
    
    # RMS hesapla
    rms = np.sqrt(np.mean(data**2))
    
    # Kaydet
    print(f"\n💾 Optimize edilmiş ses kaydediliyor: {output_file}")
    sf.write(output_file, data, sr)
    
    # Sonuç
    final_duration = len(data) / sr
    file_size = len(data) * 2 / (1024*1024)  # MB (16-bit = 2 bytes)
    
    print("\n" + "="*60)
    print("✅ OPTİMİZASYON TAMAMLANDI!")
    print("="*60)
    print(f"📁 Çıktı: {output_file}")
    print(f"⏱️  Süre: {final_duration:.1f} saniye")
    print(f"🔊 Sample Rate: {sr} Hz")
    print(f"📊 RMS Seviyesi: {rms:.4f}")
    print(f"💾 Dosya Boyutu: ~{file_size:.1f} MB")
    print("="*60)
    print("\n💡 Bu optimize edilmiş ses artık XTTS v2 için ideal!")
    print("="*60)
    
    return output_file


if __name__ == "__main__":
    input_file = "voices/Dürüst Hırsız Dostoyevski sesli kitap tek parça seslendiren Akın ALTAN.wav"
    output_file = "voices/akin_altan_optimized.wav"
    
    prepare_reference_voice(input_file, output_file, duration_seconds=45)




