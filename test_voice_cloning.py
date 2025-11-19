"""
Ses Klonlama Test Scripti - Doğrudan test
"""
from tts_engine import M1OptimizedTTS
import os

def test_voice_cloning():
    """Ses klonlamayı test et"""
    
    print("\n" + "="*60)
    print("🧪 SES KLONLAMA TESTİ")
    print("="*60)
    
    # Referans ses dosyası
    voice_sample = "voices/test_voice.wav"
    
    if not os.path.exists(voice_sample):
        print(f"\n❌ HATA: Ses dosyası bulunamadı: {voice_sample}")
        print("Lütfen önce bir ses dosyası kaydedin.")
        return
    
    # Test cümlesi
    test_text = "Merhaba, ben senin sesini klonladım. Bu test cümlesi senin sesinle okunuyor mu?"
    output_file = "test_cloning_output.wav"
    
    print(f"\n📝 Test Metni: {test_text}")
    print(f"🎤 Referans Ses: {voice_sample}")
    print(f"💾 Çıktı: {output_file}")
    print("\n" + "-"*60)
    
    try:
        # TTS motoru başlat - Progress bar KAPALI
        print("\n🚀 TTS motoru başlatılıyor...")
        engine = M1OptimizedTTS(voice_sample, use_progress_bar=False)
        
        print("\n🎙️  Ses üretiliyor...")
        print(f"   Referans sesiniz kullanılıyor: {voice_sample}")
        
        # Tek cümle üret
        success = engine.generate_single_sentence(test_text, output_file)
        
        if success:
            print("\n" + "="*60)
            print("✅ TEST BAŞARILI!")
            print("="*60)
            print(f"📁 Dosya oluşturuldu: {output_file}")
            print(f"\n🎧 Dinlemek için:")
            print(f"   open {output_file}")
            print("\n💡 ÖNEMLİ:")
            print(f"   1. Referans sesinizi dinleyin: open {voice_sample}")
            print(f"   2. Üretilen sesi dinleyin: open {output_file}")
            print(f"   3. Sesler benziyor mu kontrol edin!")
            print("\n" + "="*60)
            
            # Ses dosyası bilgileri
            import soundfile as sf
            data, sr = sf.read(output_file)
            duration = len(data) / sr
            print(f"\n📊 Üretilen Ses Bilgileri:")
            print(f"   Süre: {duration:.1f} saniye")
            print(f"   Sample Rate: {sr} Hz")
            print("="*60)
            
        else:
            print("\n❌ TEST BAŞARISIZ: Ses üretilemedi")
            
    except Exception as e:
        print(f"\n❌ HATA: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    test_voice_cloning()




