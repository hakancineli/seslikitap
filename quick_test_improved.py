"""
Hızlı Test - İyileştirilmiş TTS ile
"""
from tts_engine import M1OptimizedTTS
import sys
import os

def quick_test(voice_sample_path):
    """Hızlı test - sadece 3 cümle"""
    
    print("\n" + "="*60)
    print("🧪 HIZLI TTS TESTİ (İYİLEŞTİRİLMİŞ PARAMETRELERİ)")
    print("="*60)
    
    # Test cümleleri - farklı tonlamalar
    test_sentences = [
        {
            'text': 'Merhaba! Bu iyileştirilmiş ses klonlama sistemidir.',
            'type': 'exclamation',
            'length': 6,
            'pause_after': 0.8
        },
        {
            'text': 'Sesin referans kaydınıza daha yakın mı?',
            'type': 'question',
            'length': 5,
            'pause_after': 0.8
        },
        {
            'text': 'Yeni parametreler daha doğal ve akıcı bir ses üretmelidir.',
            'type': 'statement',
            'length': 8,
            'pause_after': 0.5
        },
        {
            'text': 'Bir varmış bir yokmuş, evvel zaman içinde bir köyde yaşayan genç bir adam varmış.',
            'type': 'statement',
            'length': 13,
            'pause_after': 0.8
        }
    ]
    
    print(f"\n📁 Referans Ses: {voice_sample_path}")
    print(f"📋 Test Cümleleri: {len(test_sentences)} adet")
    print(f"💾 Çıktı: test_improved_output.mp3")
    print("\n" + "-"*60)
    
    try:
        # TTS engine'i başlat
        engine = M1OptimizedTTS(voice_sample_path)
        
        # Test sesli kitap oluştur
        output_path = "test_improved_output.mp3"
        result = engine.generate_audiobook(test_sentences, output_path)
        
        print("\n" + "="*60)
        print("✅ TEST TAMAMLANDI!")
        print("="*60)
        print(f"📁 Dosya: {result}")
        print(f"🎧 Dinlemek için:")
        print(f"   open {result}")
        print("\n💡 Karşılaştırma için:")
        print(f"   1. Referans sesinizi dinleyin: open {voice_sample_path}")
        print(f"   2. Üretilen sesi dinleyin: open {result}")
        print(f"   3. Farkı değerlendirin!")
        print("="*60)
        
    except Exception as e:
        print(f"\n❌ HATA: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("\n🎤 HIZLI TEST")
        print("-"*60)
        print("Kullanım:")
        print("  python quick_test_improved.py <ses_dosyası.wav>")
        print("\nÖrnek:")
        print("  python quick_test_improved.py voices/test_voice.wav")
        print("-"*60)
        sys.exit(1)
    
    voice_sample = sys.argv[1]
    
    if not os.path.exists(voice_sample):
        print(f"\n❌ Ses dosyası bulunamadı: {voice_sample}")
        sys.exit(1)
    
    quick_test(voice_sample)




