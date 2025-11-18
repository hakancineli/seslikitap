"""
Ana Program - PDF'den Sesli Kitap Üretimi
"""
from pdf_parser import PDFParser
from sentence_processor import SentenceProcessor
from tts_engine import M1OptimizedTTS
import sys
import os
import time


def print_header():
    """Başlık yazdır"""
    print("\n" + "="*60)
    print("🎬 SESLİ KİTAP ÜRETİM SİSTEMİ")
    print("="*60)


def validate_inputs(pdf_path: str, voice_sample: str) -> bool:
    """Giriş dosyalarını kontrol et"""
    errors = []
    
    if not os.path.exists(pdf_path):
        errors.append(f"❌ PDF bulunamadı: {pdf_path}")
    
    if not os.path.exists(voice_sample):
        errors.append(f"❌ Ses örneği bulunamadı: {voice_sample}")
    
    if errors:
        for error in errors:
            print(error)
        return False
    
    return True


def get_user_confirmation(content: dict, num_sentences: int) -> bool:
    """Kullanıcıdan onay al"""
    print("\n" + "-"*60)
    print("📊 ÖZETİ:")
    print(f"   📄 Sayfa sayısı: {content['total_pages']}")
    print(f"   📝 Kelime sayısı: {content['word_count']}")
    print(f"   📋 Cümle sayısı: {num_sentences}")
    print(f"   🎵 Tahmini sesli kitap süresi: {content['estimated_duration_minutes']:.0f} dakika")
    print("-"*60)
    
    response = input("\n▶️  Devam etmek istiyor musunuz? (e/h): ")
    return response.lower() in ['e', 'evet', 'y', 'yes']


def main(pdf_path: str, voice_sample: str, output_path: str = None):
    """Ana pipeline"""
    
    start_time = time.time()
    
    print_header()
    
    # Giriş kontrolü
    if not validate_inputs(pdf_path, voice_sample):
        print("\n❌ Giriş dosyaları kontrol edilemedi.")
        sys.exit(1)
    
    # Çıktı dosya adı
    if output_path is None:
        base_name = os.path.splitext(os.path.basename(pdf_path))[0]
        output_path = os.path.join("outputs", f"{base_name}_sesli.mp3")
    
    # Output klasörünü oluştur
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    try:
        # ADIM 1: PDF Okuma
        print("\n📖 ADIM 1: PDF Okunuyor...")
        print("-"*60)
        parser = PDFParser(pdf_path)
        content = parser.extract_text_with_structure()
        print(f"✅ {content['total_pages']} sayfa okundu")
        print(f"✅ {content['word_count']} kelime tespit edildi")
        
        # İlk 200 karakteri göster
        print(f"\n📝 İlk paragraf önizlemesi:")
        print(f"   {content['full_text'][:200]}...")
        
        # ADIM 2: Cümlelere Ayırma
        print("\n✂️  ADIM 2: Cümleler Analiz Ediliyor...")
        print("-"*60)
        processor = SentenceProcessor()
        sentences = processor.split_into_sentences(content['full_text'])
        print(f"✅ {len(sentences)} cümle tespit edildi")
        
        # Cümle tiplerini özetle
        types = {}
        for sent in sentences:
            types[sent['type']] = types.get(sent['type'], 0) + 1
        
        print(f"   📊 Cümle dağılımı:")
        for stype, count in types.items():
            print(f"      - {stype}: {count}")
        
        # ADIM 3: Kullanıcı Onayı
        if not get_user_confirmation(content, len(sentences)):
            print("\n❌ İptal edildi.")
            sys.exit(0)
        
        # ADIM 4: Ses Üretimi
        print("\n🎙️  ADIM 3: Ses Üretiliyor...")
        print("-"*60)
        engine = M1OptimizedTTS(voice_sample)
        print(f"⏱️  Tahmini işlem süresi: {engine.estimate_time(len(sentences))}")
        print(f"💾 Çıktı dosyası: {output_path}")
        
        # Üretimi başlat
        audiobook_path = engine.generate_audiobook(sentences, output_path)
        
        # Toplam süre
        elapsed_time = time.time() - start_time
        elapsed_minutes = elapsed_time / 60
        
        # BAŞARI
        print("\n" + "="*60)
        print("🎉 BAŞARIYLA TAMAMLANDI!")
        print("="*60)
        print(f"📁 Dosya: {audiobook_path}")
        print(f"⏱️  Toplam işlem süresi: {elapsed_minutes:.1f} dakika")
        print(f"🎧 Şimdi {audiobook_path} dosyasını dinleyebilirsiniz!")
        print("="*60)
        
    except KeyboardInterrupt:
        print("\n\n⚠️  İşlem kullanıcı tarafından durduruldu.")
        print("💡 Devam etmek için start_from parametresi kullanabilirsiniz.")
        sys.exit(1)
        
    except Exception as e:
        print(f"\n❌ HATA: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


def print_usage():
    """Kullanım bilgisi"""
    print("\n🎤 SESLİ KİTAP ÜRETİM SİSTEMİ")
    print("-"*60)
    print("Kullanım:")
    print("  python main.py <pdf_dosyası> <ses_örneği> [çıktı_dosyası]")
    print("\nÖrnekler:")
    print("  python main.py pdfs/kitap.pdf voices/sesim.wav")
    print("  python main.py pdfs/kitap.pdf voices/sesim.wav outputs/kitap.mp3")
    print("\nGerekenler:")
    print("  - PDF dosyası (pdfs/ klasöründe)")
    print("  - Ses örneği (voices/ klasöründe, 30-60 saniye, WAV)")
    print("-"*60)


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print_usage()
        sys.exit(1)
    
    pdf = sys.argv[1]
    voice = sys.argv[2]
    output = sys.argv[3] if len(sys.argv) > 3 else None
    
    main(pdf, voice, output)

