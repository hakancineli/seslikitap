# 🎤 Türkçe Ses Kaynakları Rehberi

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


### 1. Mozilla Common Voice - Türkçe Kadın 1

- **Cinsiyet:** female
- **Lisans:** CC0
- **Açıklama:** Mozilla Common Voice Türkçe kadın sesi
- **Link:** [https://commonvoice.mozilla.org/tr/datasets](https://commonvoice.mozilla.org/tr/datasets)

**İndirme Talimatları:**
```
1. https://commonvoice.mozilla.org/tr/datasets adresine git
            2. Hesap oluştur (ücretsiz)
            3. Türkçe veri setini indir
            4. validated.tsv dosyasından örnek ses seç
            5. voices/ klasörüne kopyala
```


### 2. Coqui TTS Örnek Sesler

- **Cinsiyet:** mixed
- **Lisans:** MPL-2.0
- **Açıklama:** Coqui TTS demo sesleri
- **Link:** [https://github.com/coqui-ai/TTS](https://github.com/coqui-ai/TTS)

**İndirme Talimatları:**
```
1. TTS modeli yüklendiğinde örnek sesler gelir
            2. ~/.local/share/tts/ klasörüne bakın
```


### 3. YouTube Ses Örnekleri (Telif Hakkı Uyumlu)

- **Cinsiyet:** mixed
- **Lisans:** CC-BY
- **Açıklama:** Creative Commons lisanslı YouTube videoları
- **Link:** [https://www.youtube.com](https://www.youtube.com)

**İndirme Talimatları:**
```
1. YouTube'da "türkçe sesli kitap creative commons" ara
            2. CC lisanslı video bul
            3. youtube-dl veya yt-dlp ile ses indir:
               yt-dlp -x --audio-format wav [VIDEO_URL]
            4. voices/ klasörüne taşı
```


### 4. LibriVox Türkçe

- **Cinsiyet:** mixed
- **Lisans:** Public Domain
- **Açıklama:** Kamu malı sesli kitaplar
- **Link:** [https://librivox.org/search?primary_key=0&search_category=language&search_page=1&search_form=get_results&search_language=Turkish](https://librivox.org/search?primary_key=0&search_category=language&search_page=1&search_form=get_results&search_language=Turkish)

**İndirme Talimatları:**
```
1. https://librivox.org/ adresine git
            2. "Turkish" dilini seç
            3. Bir sesli kitap seç
            4. MP3'ü indir ve WAV'a dönüştür:
               ffmpeg -i input.mp3 -ar 24000 output.wav
            5. voices/ klasörüne kopyala
```


### 5. Ses Kaydı Yap (Kendi Sesin)

- **Cinsiyet:** custom
- **Lisans:** Your Own
- **Açıklama:** Kendi sesini kaydet - En iyi sonuç!

**İndirme Talimatları:**
```
WEB ARAYÜZÜNDE:
            1. "Ses Kaydı" sekmesine git
            2. 30-60 saniye kayıt yap
            3. Farklı tonlamalar kullan
            4. Otomatik olarak voices/ klasörüne kaydedilecek
            
            VEYA PYTHON İLE:
            python voice_recorder.py
```


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
