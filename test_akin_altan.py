"""
Akın ALTAN Sesi ile Test
"""
from tts_engine import M1OptimizedTTS
import os

def test_akin_altan_voice():
    """Akın ALTAN'ın sesiyle metin okut"""
    
    print("\n" + "="*60)
    print("🎭 AKIN ALTAN SESİ KLONLAMA TESTİ")
    print("="*60)
    
    # Referans ses dosyası
    voice_sample = "voices/Dürüst Hırsız Dostoyevski sesli kitap tek parça seslendiren Akın ALTAN.wav"
    
    # Test metni
    test_text = """Her insanın bir hikâyesi vardır, doğumuyla başlar ölümüyle biter. Çokları zanneder ki kendi hikâyesi yalnız kendisine aittir ve yaşanıp bitecektir hiç kimseyle paylaşmadan, hiç kimse onun benzerini yaşamadan. Zannederler ki herkes aynı dünyada bambaşka bir hikâyeye sahiptir. Oysa ki hikâyeler aynı, farklı olan ise dünyalardır. Hele bazı insanlar vardır ki sembollerden ibaret, bambaşka bir dünyada yaşarlar. İşte bu kitap, o insanların hikâyesidir."""
    
    output_file = "output_akin_altan_clone.mp3"
    
    print(f"\n🎤 Referans Ses: Akın ALTAN (Dürüst Hırsız - Dostoyevski)")
    print(f"📝 Metin uzunluğu: {len(test_text)} karakter")
    print(f"💾 Çıktı: {output_file}")
    print("\n" + "-"*60)
    
    if not os.path.exists(voice_sample):
        print(f"\n❌ HATA: Ses dosyası bulunamadı: {voice_sample}")
        return
    
    try:
        # TTS motoru başlat
        print("\n🚀 TTS motoru başlatılıyor (Akın ALTAN sesi)...")
        engine = M1OptimizedTTS(voice_sample, use_progress_bar=False)
        
        print("\n🎙️  Metin Akın ALTAN'ın sesiyle seslendiriliyor...")
        print("   (Bu işlem birkaç dakika sürebilir)")
        
        # Cümlelere ayır ve seslendir
        from sentence_processor import SentenceProcessor
        processor = SentenceProcessor()
        sentences = processor.split_into_sentences(test_text)
        
        print(f"   📋 {len(sentences)} cümle tespit edildi")
        
        # Sesli kitap oluştur
        result = engine.generate_audiobook(sentences, output_file)
        
        print("\n" + "="*60)
        print("✅ BAŞARILI!")
        print("="*60)
        print(f"📁 Dosya oluşturuldu: {result}")
        print(f"\n🎧 Dinlemek için:")
        print(f"   open {result}")
        print("\n💡 Karşılaştırma:")
        print(f"   1. Orijinal: open '{voice_sample}'")
        print(f"   2. Klonlanan: open {result}")
        print("\n🎭 Akın ALTAN'ın sesine benzedi mi?")
        print("="*60)
        
    except Exception as e:
        print(f"\n❌ HATA: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    test_akin_altan_voice()




