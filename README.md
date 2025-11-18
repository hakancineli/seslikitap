# 🎙️ Sesli Kitap Üretim Sistemi

MacOS M1 için optimize edilmiş, ses klonlama ve uzun metin okutma sistemi.

## 🌟 Özellikler

- ✅ PDF'den otomatik metin çıkarma
- ✅ Ses klonlama (XTTS v2)
- ✅ Akıllı cümle bölme ve tonlama
- ✅ M1 GPU (MPS) desteği
- ✅ Türkçe dil desteği
- ✅ Yüksek kaliteli MP3 çıktısı

## 📋 Gereksinimler

- macOS (M1/M2/M3)
- Python 3.10+
- FFmpeg
- 8GB+ RAM
- İnternet (ilk model indirme için)

## 🚀 Kurulum

### 1. Bağımlılıkları Yükle

```bash
# Homebrew varsa güncelle
brew update

# FFmpeg kur
brew install ffmpeg

# Python 3.10 kur (yoksa)
brew install python@3.10

# Virtual environment oluştur
cd sesli-kitap-uretim
python3.10 -m venv venv
source venv/bin/activate

# Python paketlerini yükle
pip install --upgrade pip
pip install -r requirements.txt

# Türkçe NLP modeli
python -m spacy download tr_core_news_lg
```

### 2. Hızlı Test

```bash
# Ortam kontrolü ve basit TTS testi
python test_tts.py

# Ses klonlama ile test
python test_tts.py voices/voice_sample.wav
```

## 🎤 Ses Örneği Hazırlama

### Kaliteli Ses Kaydı İçin:

1. **QuickTime Player** ile kayıt:
   - File > New Audio Recording
   - Kırmızı butona bas, başla
   - 30-60 saniye doğal okuma yap
   - Durdur ve `voices/voice_sample.wav` olarak kaydet

2. **Okuma İpuçları:**
   - Sessiz bir ortam seçin
   - Doğal tempoda okuyun
   - Farklı tonlamalar kullanın (soru, ünlem, normal)
   - Net telaffuz yapın
   - Arka plan gürültüsü olmasın

3. **Örnek Metin:**
```
Merhaba! Ben [İsminiz], ve bu ses kaydı yapay zeka tarafından 
klonlanacak. Sesli kitaplar için kullanılacak. Farklı tonlamalarda 
konuşuyorum: Bu bir soru mu? Evet, bu bir soru! Ve bu bir ünlem 
cümlesi. Normal bir anlatım cümlesi. Yavaşça söylenen bir cümle... 
Hızlıca söylenen bir cümle.
```

## 📖 Kullanım

### Temel Kullanım:

```bash
# Tam sesli kitap üretimi
python main.py pdfs/kitap.pdf voices/sesim.wav

# Özel çıktı dosyası ile
python main.py pdfs/kitap.pdf voices/sesim.wav outputs/kitabim.mp3
```

### Modüler Kullanım:

```bash
# Sadece PDF analizi
python pdf_parser.py pdfs/kitap.pdf

# Sadece cümle işleme testi
python sentence_processor.py

# Sadece TTS testi
python tts_engine.py voices/sesim.wav
```

## 📊 Performans

### M1 Mac (MPS):
- **Cümle başına:** ~3-5 saniye
- **150 sayfa kitap:** ~3-4 saat işlem süresi
- **Çıktı kalitesi:** 192kbps MP3

### CPU Modu:
- **Cümle başına:** ~15-20 saniye
- **150 sayfa kitap:** ~12-15 saat işlem süresi

## 🗂️ Klasör Yapısı

```
sesli-kitap-uretim/
├── voices/              # Ses örnekleri (.wav)
├── pdfs/               # PDF dosyaları
├── outputs/            # Üretilen sesli kitaplar (.mp3)
├── temp_chunks/        # Geçici ses parçaları (otomatik temizlenir)
├── pdf_parser.py       # PDF işleme
├── sentence_processor.py # Cümle analizi
├── tts_engine.py       # TTS motoru
├── test_tts.py         # Hızlı test
├── main.py             # Ana program
└── requirements.txt    # Python bağımlılıkları
```

## 🔧 Sorun Giderme

### MPS (M1 GPU) çalışmıyor:

```bash
# PyTorch'u yeniden yükle
pip uninstall torch
pip install torch torchvision torchaudio
```

### Ses kalitesi düşük:

`tts_engine.py` dosyasında bitrate'i artırın:
```python
final_audio.export(output_path, format="mp3", bitrate="256k")
```

### İşlem çok yavaş:

- MPS'nin aktif olduğundan emin olun
- Arka plan uygulamalarını kapatın
- Daha küçük PDF ile test edin

### Model indirme hatası:

```bash
# Manuel model indirme
python -c "from TTS.api import TTS; TTS('tts_models/multilingual/multi-dataset/xtts_v2')"
```

## 💡 İpuçları

1. **İlk Test:** 5-10 sayfalık küçük PDF ile başlayın
2. **Gece İşleme:** Uzun kitapları gece işletin
3. **Ses Örneği:** 30-60 saniyelik temiz kayıt en iyi sonucu verir
4. **PDF Kalitesi:** OCR taranmış PDF'ler daha az doğru olabilir
5. **Geçici Dosyalar:** `temp_chunks/` otomatik temizlenir, yer sıkıntısı olmaz

## 📈 Gelecek Özellikler

- [ ] Bölüm tespiti ve chapter marks
- [ ] Çoklu ses desteği (farklı karakterler için)
- [ ] Web arayüzü
- [ ] Batch işleme
- [ ] İlerleme kaydetme/devam ettirme
- [ ] Duygu analizi bazlı tonlama

## 🤝 Katkıda Bulunma

Bu bir prototip projedir. Önerileriniz için issue açabilirsiniz.

## 📄 Lisans

MIT License - Kişisel ve ticari kullanım için ücretsizdir.

## ⚠️ Uyarılar

- Ses klonlama sadece kendi sesiniz veya izinli sesler için kullanın
- Telif hakkı olan PDF'leri sadece kişisel kullanım için işleyin
- Ticari kullanım için yasal izinleri alın

## 📞 Destek

Sorularınız için:
- GitHub Issues
- [Email]
- [Discord/Telegram]

---

**Yapımcı:** Sesli Kitap Üretim Ekibi
**Versiyon:** 1.0.0
**Son Güncelleme:** 2025-11-18

