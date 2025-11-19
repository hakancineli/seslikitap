# 🎙️ Sesli Kitap Üretim Sistemi

**XTTS v2 ile Profesyonel Ses Klonlama ve Metin Seslendirme**

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Gradio](https://img.shields.io/badge/Gradio-Web%20UI-orange)](https://gradio.app/)

## 🌟 Özellikler

### ✅ Temel Özellikler
- **Ses Klonlama**: Herhangi bir sesi 30-60 saniyelik örnekle klonlama
- **PDF Seslendirme**: PDF dosyalarından otomatik sesli kitap üretimi
- **Metin Seslendirme**: Direkt metin girişi ile hızlı seslendirme
- **Çoklu Format Desteği**: WAV, MP3, M4A ses dosyası desteği
- **Türkçe Optimizasyonu**: Türkçe ses sentezi için özel olarak optimize edilmiş

### 🎛️ Gelişmiş Kontroller
- **Konuşma Hızı**: 0.5x (yavaş) - 2.0x (hızlı) ayarlanabilir hız
- **Ses Tonu**: -5 (alçak) to +5 (yüksek) ton kontrolü
- **Metin Temizleme**: Otomatik özel karakter düzeltme
- **Ses İyileştirme**: Gürültü azaltma, normalize, compression
- **Toplu İşlem**: Birden fazla metni kuyruğa alıp toplu işleme

### 🎨 Ses Karıştırma
- İki farklı sesi birleştirme
- Özelleştirilebilir karışım oranı
- Yeni hibrit sesler oluşturma

## 📦 Kurulum

### Gereksinimler
- Python 3.10+
- macOS (M1/M2/M3 optimize edilmiş)
- 8GB+ RAM
- 5GB+ disk alanı

### Adım 1: Repository'yi Klonlayın
```bash
git clone https://github.com/hakancineli/seslikitap.git
cd seslikitap
```

### Adım 2: Virtual Environment Oluşturun
```bash
python3 -m venv venv
source venv/bin/activate
```

### Adım 3: Bağımlılıkları Yükleyin
```bash
pip install -r requirements.txt
```

## 🚀 Kullanım

### Web Arayüzü (Önerilen)
```bash
python app.py
```
Tarayıcınızda açılır: `http://localhost:3000`

### Komut Satırı
```bash
# Basit test
python test_tts.py voices/your_voice.wav

# PDF'den sesli kitap
python main.py pdfs/book.pdf voices/your_voice.wav

# Gelişmiş özelliklerle test
python advanced_tts.py

# Ses karıştırma
python advanced_tts.py blend
```

## 📚 Modül Yapısı

### Core Modüller
```
├── app.py                  # Web arayüzü (Gradio)
├── tts_engine.py          # Temel TTS motoru (M1 optimize)
├── advanced_tts.py        # Gelişmiş TTS özellikleri
├── pdf_parser.py          # PDF metin çıkarma
├── sentence_processor.py  # Cümle analizi ve işleme
├── text_cleaner.py        # Metin normalleştirme
└── voice_manager.py       # Ses kütüphanesi yönetimi
```

### Yardımcı Modüller
```
├── voice_recorder.py      # Mikrofon ile ses kaydı
├── audio_enhancer.py      # Ses kalitesi iyileştirme
├── batch_processor.py     # Toplu işlem yönetimi
└── prepare_reference_voice.py  # Referans ses optimizasyonu
```

## 🎯 Kullanım Senaryoları

### 1. Hızlı Ses Klonlama
```python
from tts_engine import M1OptimizedTTS

# Referans ses ile motor oluştur
engine = M1OptimizedTTS("voices/my_voice.wav")

# Metin seslendir
engine.generate_single_sentence(
    "Merhaba dünya!",
    "output.wav"
)
```

### 2. Gelişmiş Stil Kontrolü
```python
from advanced_tts import AdvancedTTS

engine = AdvancedTTS("voices/my_voice.wav")

# Hız ve ton kontrolü ile
engine.generate_with_style(
    text="Bu hızlı ve yüksek tonlu bir cümle",
    output_path="output.wav",
    speed=1.3,      # %30 daha hızlı
    pitch_shift=+3  # 3 kademe yüksek ton
)
```

### 3. Ses Karıştırma
```python
from advanced_tts import AdvancedTTS

# %50 voice1 + %50 voice2
AdvancedTTS.blend_voices(
    "voices/voice1.wav",
    "voices/voice2.wav",
    "blended_voice.wav",
    blend_ratio=0.5
)
```

### 4. Toplu İşlem
```python
from batch_processor import BatchProcessor

batch = BatchProcessor()

# Kuyruğa ekle
batch.add_to_queue("Metin 1", "voice_id_1")
batch.add_to_queue("Metin 2", "voice_id_2")

# İşle
batch.process_queue(tts_engine)
```

## 🎛️ Web Arayüzü Özellikleri

### Sesli Kitap Oluştur Sekmesi
- ✍️ **Metin Girişi**: Direkt metin yaz veya yapıştır
- 📄 **PDF Yükleme**: PDF dosyasından otomatik metin çıkarma
- 🎤 **Ses Yükleme**: WAV/MP3/M4A formatında referans ses
- ⚡ **Hız Kontrolü**: Slider ile 0.5x - 2.0x arası
- 🎵 **Ton Kontrolü**: Slider ile -5 to +5 arası
- 🎬 **Anlık Üretim**: Progress bar ile canlı ilerleme

### Ses Kaydı Sekmesi
- 🔴 **Mikrofon Kaydı**: 10-120 saniye arası kayıt
- 📊 **Kalite Analizi**: Otomatik ses kalitesi kontrolü
- 💡 **Örnek Metin**: Rehber okuma metni
- 💾 **Kaydetme**: Otomatik voices/ klasörüne kayıt

### Ses Kütüphanesi Sekmesi
- 📚 **Kayıtlı Sesler**: Tüm seslerinizi görüntüleme
- 🔍 **Filtreleme**: Cinsiyet, dil, etiket bazlı arama
- 📈 **İstatistikler**: Kullanım sayıları ve meta data

## 🔧 Yapılandırma

### TTS Motor Ayarları (`tts_engine.py`)
```python
# Cihaz seçimi
self.device = "cpu"  # veya "mps" (M1/M2/M3 için)

# Sample rate
self.sample_rate = 24000  # XTTS v2 için optimal
```

### Ses Kalitesi Ayarları
```python
# Referans ses gereksinimleri
- Süre: 30-60 saniye (optimal)
- Format: WAV (tercih edilen)
- Sample Rate: 24000 Hz
- Kanallar: Mono
- Ses Seviyesi: 0.1-0.3 RMS
```

## 📊 Performans

### İşlem Süreleri (Apple M1)
| İşlem | CPU | MPS (GPU) |
|-------|-----|-----------|
| 1 cümle | ~15 saniye | ~4 saniye |
| 10 cümle | ~2.5 dakika | ~40 saniye |
| 100 cümle | ~25 dakika | ~7 dakika |

### Bellek Kullanımı
- Model yükleme: ~2GB
- Aktif işlem: +500MB-1GB
- Önbellek: +200MB

## 🐛 Sorun Giderme

### "Model yüklenemiyor"
```bash
# XTTS v2 modelini manuel indir
python -c "from TTS.api import TTS; TTS('tts_models/multilingual/multi-dataset/xtts_v2')"
```

### "BrokenPipeError"
- Web arayüzünde otomatik düzeltilmiş
- `use_progress_bar=False` parametresi kullanılıyor

### "Ses klonlama çalışmıyor"
- Referans sesinizin 30+ saniye olduğundan emin olun
- Optimize edilmiş ses kullanın: `python prepare_reference_voice.py`
- Sessiz ortamda kaydedilmiş temiz ses kullanın

### "İlk cümleler sorunlu"
- `akin_altan_optimized.wav` gibi optimize edilmiş referans ses kullanın
- 45 saniyelik temiz ses optimal

## 📖 Dokümantasyon

- [VOICE_GUIDE.md](VOICE_GUIDE.md) - Ses kaydı rehberi
- [IYILESTIRME_REHBERI.md](IYILESTIRME_REHBERI.md) - İyileştirme önerileri
- [TEST_BU.md](TEST_BU.md) - Test senaryoları

## 🤝 Katkıda Bulunma

Pull request'ler memnuniyetle karşılanır!

1. Fork edin
2. Feature branch oluşturun (`git checkout -b feature/amazing-feature`)
3. Commit edin (`git commit -m 'Add amazing feature'`)
4. Push edin (`git push origin feature/amazing-feature`)
5. Pull Request açın

## 📝 Lisans

MIT License - detaylar için [LICENSE](LICENSE) dosyasına bakın.

## 👏 Teşekkürler

- [Coqui TTS](https://github.com/coqui-ai/TTS) - XTTS v2 modeli
- [Gradio](https://gradio.app/) - Web arayüzü
- [PyDub](https://github.com/jiaaro/pydub) - Ses işleme

## 📧 İletişim

Hakan Cineli - [@hakancineli](https://github.com/hakancineli)

Project Link: [https://github.com/hakancineli/seslikitap](https://github.com/hakancineli/seslikitap)

---

**⭐ Projeyi beğendiyseniz yıldızlamayı unutmayın!**

