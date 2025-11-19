"""
Türkçe Açık Kaynak Ses Örnekleri İndirme
"""
import os
import requests
from pathlib import Path
from tqdm import tqdm


class TurkishVoiceDownloader:
    """Türkçe açık kaynak ses örnekleri"""
    
    # Açık kaynak Türkçe ses örnekleri
    VOICE_SAMPLES = [
        {
            "name": "Mozilla Common Voice - Türkçe Kadın 1",
            "url": "https://commonvoice.mozilla.org/tr/datasets",
            "filename": "mozilla_tr_female_1.wav",
            "gender": "female",
            "description": "Mozilla Common Voice Türkçe kadın sesi",
            "license": "CC0",
            "manual_download": True,
            "instructions": """
            1. https://commonvoice.mozilla.org/tr/datasets adresine git
            2. Hesap oluştur (ücretsiz)
            3. Türkçe veri setini indir
            4. validated.tsv dosyasından örnek ses seç
            5. voices/ klasörüne kopyala
            """
        },
        {
            "name": "Coqui TTS Örnek Sesler",
            "url": "https://github.com/coqui-ai/TTS",
            "filename": "coqui_sample.wav",
            "gender": "mixed",
            "description": "Coqui TTS demo sesleri",
            "license": "MPL-2.0",
            "manual_download": True,
            "instructions": """
            1. TTS modeli yüklendiğinde örnek sesler gelir
            2. ~/.local/share/tts/ klasörüne bakın
            """
        },
        {
            "name": "YouTube Ses Örnekleri (Telif Hakkı Uyumlu)",
            "url": "https://www.youtube.com",
            "filename": "youtube_sample.wav",
            "gender": "mixed",
            "description": "Creative Commons lisanslı YouTube videoları",
            "license": "CC-BY",
            "manual_download": True,
            "instructions": """
            1. YouTube'da "türkçe sesli kitap creative commons" ara
            2. CC lisanslı video bul
            3. youtube-dl veya yt-dlp ile ses indir:
               yt-dlp -x --audio-format wav [VIDEO_URL]
            4. voices/ klasörüne taşı
            """
        },
        {
            "name": "LibriVox Türkçe",
            "url": "https://librivox.org/search?primary_key=0&search_category=language&search_page=1&search_form=get_results&search_language=Turkish",
            "filename": "librivox_sample.wav",
            "gender": "mixed",
            "description": "Kamu malı sesli kitaplar",
            "license": "Public Domain",
            "manual_download": True,
            "instructions": """
            1. https://librivox.org/ adresine git
            2. "Turkish" dilini seç
            3. Bir sesli kitap seç
            4. MP3'ü indir ve WAV'a dönüştür:
               ffmpeg -i input.mp3 -ar 24000 output.wav
            5. voices/ klasörüne kopyala
            """
        },
        {
            "name": "Ses Kaydı Yap (Kendi Sesin)",
            "url": None,
            "filename": "my_voice_sample.wav",
            "gender": "custom",
            "description": "Kendi sesini kaydet - En iyi sonuç!",
            "license": "Your Own",
            "manual_download": True,
            "instructions": """
            WEB ARAYÜZÜNDE:
            1. "Ses Kaydı" sekmesine git
            2. 30-60 saniye kayıt yap
            3. Farklı tonlamalar kullan
            4. Otomatik olarak voices/ klasörüne kaydedilecek
            
            VEYA PYTHON İLE:
            python voice_recorder.py
            """
        }
    ]
    
    def __init__(self, voices_dir: str = "voices"):
        self.voices_dir = Path(voices_dir)
        self.voices_dir.mkdir(exist_ok=True)
    
    def print_sources(self):
        """Mevcut ses kaynaklarını yazdır"""
        print("\n" + "="*70)
        print("🎤 TÜRKÇE SES KAYNAKLARI")
        print("="*70)
        
        for i, voice in enumerate(self.VOICE_SAMPLES, 1):
            print(f"\n{i}. {voice['name']}")
            print(f"   👤 Cinsiyet: {voice['gender']}")
            print(f"   📜 Lisans: {voice['license']}")
            print(f"   📝 {voice['description']}")
            
            if voice['manual_download']:
                print(f"   📥 Manuel İndirme Gerekli")
                if voice['url']:
                    print(f"   🔗 {voice['url']}")
                print(f"\n   📋 Talimatlar:")
                for line in voice['instructions'].strip().split('\n'):
                    if line.strip():
                        print(f"      {line.strip()}")
        
        print("\n" + "="*70)
        print("💡 ÖNERİ: En iyi sonuç için kendi sesini kaydet!")
        print("   Web arayüzünde 'Ses Kaydı' sekmesini kullan")
        print("="*70)
    
    def download_sample_with_tts(self):
        """TTS modeli ile örnek ses üret"""
        print("\n🎙️  TTS Modeli ile Örnek Ses Oluşturuluyor...")
        print("="*70)
        
        try:
            from TTS.api import TTS
            
            # Mevcut ses dosyalarını kontrol et
            existing_voices = list(self.voices_dir.glob("*.wav"))
            
            if not existing_voices:
                print("❌ voices/ klasöründe referans ses bulunamadı!")
                print("💡 Önce bir ses kaydı yapmanız gerekiyor:")
                print("   1. Web arayüzünde 'Ses Kaydı' sekmesini kullan")
                print("   2. Veya python voice_recorder.py komutunu çalıştır")
                return
            
            # İlk bulduğumuz sesi referans olarak kullan
            reference_voice = existing_voices[0]
            print(f"📌 Referans ses: {reference_voice.name}")
            
            # XTTS v2 modeli
            print("📥 XTTS v2 modeli yükleniyor...")
            tts = TTS("tts_models/multilingual/multi-dataset/xtts_v2").to("cpu")
            
            # Örnek metinler
            sample_texts = {
                "kadın": "Merhaba, ben bir yapay zeka sesiyle konuşuyorum. Bu Türkçe kadın sesidir.",
                "erkek": "Merhaba, ben bir yapay zeka sesiyle konuşuyorum. Bu Türkçe erkek sesidir.",
                "genç": "Selam! Ben daha genç bir sesle konuşuyorum. Türkçe ses klonlama harika!",
            }
            
            # Her biri için örnek üret
            for voice_type, text in sample_texts.items():
                output_path = self.voices_dir / f"tts_sample_{voice_type}.wav"
                
                print(f"\n   Oluşturuluyor: {voice_type} sesi...")
                
                # Referans sesi kullanarak klon
                tts.tts_to_file(
                    text=text,
                    speaker_wav=str(reference_voice),  # Referans ses eklendi
                    language="tr",
                    file_path=str(output_path)
                )
                
                print(f"   ✅ Kaydedildi: {output_path}")
            
            print("\n✅ TTS örnek sesleri oluşturuldu!")
            print(f"📁 Konum: voices/tts_sample_*.wav")
            print(f"🎤 Referans: {reference_voice.name}")
            
        except Exception as e:
            print(f"❌ Hata: {e}")
            print("💡 Not: Bu özellik için TTS modeli ve referans ses gerekli")
    
    def create_download_guide(self):
        """Markdown rehber oluştur"""
        guide_path = Path("VOICE_SOURCES.md")
        
        content = """# 🎤 Türkçe Ses Kaynakları Rehberi

Bu dokümanda Türkçe ses klonlama için kullanabileceğiniz açık kaynak ses örneklerini bulabilirsiniz.

## ⭐ En İyi Yöntem: Kendi Sesini Kaydet

**Neden?**
- En iyi klonlama kalitesi
- Telif hakkı sorunu yok
- Tam kontrol

**Nasıl?**
1. Web arayüzünde "Ses Kaydı" sekmesine git
2. 30-60 saniye süre seç
3. Farklı tonlamalarla konuş (soru, ünlem, normal)
4. Kaydet - otomatik olarak `voices/` klasörüne kaydedilecek

---

## 📚 Açık Kaynak Ses Kaynakları

"""
        
        for i, voice in enumerate(self.VOICE_SAMPLES, 1):
            content += f"\n### {i}. {voice['name']}\n\n"
            content += f"- **Cinsiyet:** {voice['gender']}\n"
            content += f"- **Lisans:** {voice['license']}\n"
            content += f"- **Açıklama:** {voice['description']}\n"
            
            if voice['url']:
                content += f"- **Link:** [{voice['url']}]({voice['url']})\n"
            
            content += f"\n**İndirme Talimatları:**\n```\n{voice['instructions'].strip()}\n```\n\n"
        
        content += """
---

## 🎯 Ses Kalitesi İpuçları

### Kayıt İçin:
- ✅ Sessiz ortam
- ✅ 30-60 saniye süre
- ✅ Farklı tonlamalar (soru, ünlem, normal)
- ✅ Mikrofona 15-20 cm mesafe
- ✅ Net ve anlaşılır konuşma

### Hazır Ses İçin:
- ✅ Minimum 10 saniye
- ✅ Temiz kayıt (gürültüsüz)
- ✅ 22050 Hz veya 24000 Hz sample rate
- ✅ WAV formatı (tercih edilen)
- ✅ Mono kanal

---

## 📋 İndirdikten Sonra

1. Ses dosyasını `voices/` klasörüne kopyala
2. Terminalde çalıştır:
```bash
python voice_catalog.py
```
3. Otomatik olarak kataloglanacak!
4. Web arayüzünde "Hazır Sesler" dropdown'ında görünecek

---

## ⚖️ Telif Hakkı Uyarısı

- Sadece açık lisanslı sesler kullanın
- Creative Commons, Public Domain, CC0 lisansları güvenli
- Telif hakkı olan içerikleri izinsiz kullanmayın
- Kendi sesini kaydetmek en güvenli yöntemdir

---

**💡 Soru?** README.md dosyasına bakın veya GitHub'da issue açın.
"""
        
        with open(guide_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"\n✅ Rehber oluşturuldu: {guide_path}")


def main():
    """Ana fonksiyon"""
    downloader = TurkishVoiceDownloader()
    
    print("\n" + "="*70)
    print("🎙️  TÜRKÇE SES İNDİRME ARACI")
    print("="*70)
    
    print("\n1. Ses kaynaklarını göster")
    print("2. TTS ile örnek sesler oluştur")
    print("3. İndirme rehberi oluştur (VOICE_SOURCES.md)")
    print("4. Hepsini yap")
    
    choice = input("\nSeçim (1-4): ").strip()
    
    if choice == "1":
        downloader.print_sources()
    elif choice == "2":
        downloader.download_sample_with_tts()
    elif choice == "3":
        downloader.create_download_guide()
    elif choice == "4":
        downloader.print_sources()
        print("\n")
        downloader.create_download_guide()
        print("\n")
        
        create_samples = input("TTS ile örnek sesler oluşturulsun mu? (e/h): ")
        if create_samples.lower() in ['e', 'evet', 'y', 'yes']:
            downloader.download_sample_with_tts()
    else:
        print("❌ Geçersiz seçim")


if __name__ == "__main__":
    main()

