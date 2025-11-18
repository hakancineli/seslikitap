# 🎤 Ses Yönetimi Rehberi

## 📋 İçindekiler

1. [Hazır Ses Dosyası Yükleme](#hazır-ses-dosyası-yükleme)
2. [Mikrofon ile Kayıt](#mikrofon-ile-kayıt)
3. [Ses Kütüphanesi Yönetimi](#ses-kütüphanesi-yönetimi)
4. [Ses Kalite Kontrolleri](#ses-kalite-kontrolleri)

---

## 📤 Hazır Ses Dosyası Yükleme

### Hızlı Başlangıç:

```bash
# Ses dosyası yükle ve sisteme kaydet
python upload_voice.py ~/Downloads/sesim.wav "Benim Sesim"

# İnteraktif mod
python upload_voice.py
```

### Desteklenen Formatlar:
- ✅ WAV (en iyi)
- ✅ MP3
- ✅ M4A
- ✅ AAC
- ✅ OGG
- ✅ FLAC

### Önerilen Ses Özellikleri:

```yaml
Süre: 30-60 saniye (ideal)
Minimum: 10 saniye
Maksimum: 120 saniye

Kalite:
  - Sample Rate: 22050 Hz (otomatik dönüştürülür)
  - Kanal: Mono (otomatik dönüştürülür)
  - Format: WAV
  - Bit Depth: 16-bit veya 32-bit float

İçerik:
  - Temiz, arka plan gürültüsü yok
  - Farklı tonlamalar (soru, ünlem, normal)
  - Doğal okuma temposu
  - Net telaffuz
```

### Örnek Kullanım:

```bash
# 1. Ses dosyasını yükle
python upload_voice.py ses_ornekleri/erkek_ses.wav "Profesyonel Erkek Ses"

# 2. Test et
python test_tts.py voices/Profesyonel_Erkek_Ses.wav

# 3. Kitap oluştur
python main.py pdfs/kitap.pdf voices/Profesyonel_Erkek_Ses.wav
```

---

## 🎙️ Mikrofon ile Kayıt

### İnteraktif Kayıt:

```bash
python voice_recorder.py
```

Adımlar:
1. Mikrofon cihazını seçin
2. Kayıt süresini girin (örn: 30 saniye)
3. Dosya adı girin
4. Kayıt başlar, konuşmaya başlayın
5. Otomatik durdurulur ve kaydedilir

### Programatik Kullanım:

```python
from voice_recorder import VoiceRecorder

recorder = VoiceRecorder()

# 30 saniyelik kayıt yap
output_path = recorder.record(
    duration=30,
    filename="sesim.wav",
    device=None  # Varsayılan mikrofon
)

# Doğrula
info = recorder.validate_audio(output_path)
print(info)
```

### Kayıt İpuçları:

✅ **YAPIN:**
- Sessiz bir ortam seçin
- Mikrofona 15-20 cm mesafeden konuşun
- Doğal tempoda okuyun
- Farklı cümle tipleri kullanın (soru, ünlem, normal)
- Net ve anlaşılır konuşun

❌ **YAPMAYIN:**
- Arka plan müziği olmasın
- Mikrofonun çok yakınında veya uzağında olmayın
- Monoton bir ses tonu kullanmayın
- Çok hızlı veya yavaş konuşmayın
- Mümkünse dış ortamda kayıt yapmayın

---

## 📚 Ses Kütüphanesi Yönetimi

### Ses Ekleme:

```bash
python voice_manager.py
# Seçenek 1: Ses ekle
```

Veya Python'da:

```python
from voice_manager import VoiceManager

manager = VoiceManager()

# Ses ekle
voice_id = manager.add_voice(
    audio_path="voices/sesim.wav",
    name="Benim Sesim",
    description="Kişisel sesli kitaplar için",
    gender="male",  # male/female/unknown
    language="tr",
    tags=["erkek", "genç", "enerji"]
)

print(f"Ses eklendi: {voice_id}")
```

### Sesleri Listeleme:

```bash
python voice_manager.py
# Seçenek 2: Sesleri listele
```

Veya Python'da:

```python
# Tüm sesler
voices = manager.list_voices()

# Filtreli
male_voices = manager.list_voices(gender="male")
turkish_voices = manager.list_voices(language="tr")
energetic_voices = manager.list_voices(tags=["enerji"])
```

### Ses Güncelleme:

```python
manager.update_voice(
    voice_id="abc123",
    name="Yeni Ad",
    description="Güncellenmiş açıklama",
    tags=["yeni", "etiket"]
)
```

### Ses Silme:

```bash
python voice_manager.py
# Seçenek 3: Ses sil
```

Veya Python'da:

```python
manager.delete_voice("abc123")
```

### Ses Kullanma:

```python
# Voice ID ile
voice_path = manager.get_voice_path("abc123")
print(voice_path)  # voices/abc123_sesim.wav

# Kullanım sayısını artır
manager.increment_usage("abc123")
```

---

## 🔍 Ses Kalite Kontrolleri

Sistem otomatik olarak şu kontrolleri yapar:

### ✅ Geçerlilik Kontrolleri:

1. **Süre Kontrolü:**
   - ⚠️ < 10 saniye: Çok kısa
   - ✅ 10-120 saniye: İdeal
   - ⚠️ > 120 saniye: Çok uzun

2. **Ses Seviyesi:**
   - ⚠️ RMS < 0.05: Çok sessiz
   - ✅ RMS 0.05-0.5: İdeal
   - ⚠️ RMS > 0.5: Çok yüksek (distortion riski)

3. **Sessizlik Oranı:**
   - ✅ < 30%: İyi
   - ⚠️ > 30%: Çok fazla sessizlik

4. **Sample Rate:**
   - ✅ 16000, 22050, 24000, 44100, 48000 Hz
   - ⚠️ Diğer: Alışılmadık, sorun çıkabilir

### Manuel Doğrulama:

```python
from voice_recorder import VoiceRecorder

recorder = VoiceRecorder()
info = recorder.validate_audio("voices/sesim.wav")

if info['valid']:
    print("✅ Geçerli ses dosyası")
    print(f"Süre: {info['duration']:.1f}s")
    print(f"Ses seviyesi: {info['rms_level']:.3f}")
    print(f"Sessizlik: {info['silence_percentage']:.1f}%")
    
    if info['warnings']:
        print("\n⚠️ Uyarılar:")
        for warning in info['warnings']:
            print(f"  - {warning}")
else:
    print(f"❌ Geçersiz: {info['error']}")
```

---

## 📖 Tam İş Akışı Örneği

### Senaryo 1: Hazır Ses Dosyası ile

```bash
# 1. Ses dosyasını yükle ve kaydet
python upload_voice.py ~/Downloads/sesim.wav "Anlatıcı Sesim"

# 2. Sisteme kayıt başarılı, ID aldınız: abc123

# 3. Test edin
python test_tts.py voices/Anlatıcı_Sesim.wav

# 4. Sesli kitap oluşturun
python main.py pdfs/kitap.pdf voices/Anlatıcı_Sesim.wav
```

### Senaryo 2: Mikrofon Kaydı ile

```bash
# 1. Mikrofon ile kayıt yap
python voice_recorder.py
# 30 saniye kayıt yapın

# 2. Kayıt: voices/voice_20251118_143022.wav

# 3. Sisteme kaydet
python upload_voice.py voices/voice_20251118_143022.wav "Canlı Kayıt"

# 4. Sesli kitap oluştur
python main.py pdfs/kitap.pdf voices/Canlı_Kayıt.wav
```

### Senaryo 3: Çoklu Ses Yönetimi

```python
from voice_manager import VoiceManager

manager = VoiceManager()

# Birden fazla ses ekle
voices = [
    ("voices/anlatici1.wav", "Anlatıcı 1", "male", ["ciddi", "derin"]),
    ("voices/anlatici2.wav", "Anlatıcı 2", "female", ["enerji", "genç"]),
    ("voices/anlatici3.wav", "Anlatıcı 3", "male", ["yaşlı", "bilge"])
]

for path, name, gender, tags in voices:
    voice_id = manager.add_voice(path, name, gender=gender, tags=tags)
    print(f"✅ {name}: {voice_id}")

# En çok kullanılan sesleri göster
popular = manager.list_voices()[:5]
for voice in popular:
    print(f"{voice['name']}: {voice['usage_count']} kullanım")
```

---

## 🎯 Sonraki Adımlar

1. ✅ Ses dosyalarınızı hazırlayın
2. ✅ Sisteme yükleyin/kaydedin
3. ✅ Kalite kontrolünden geçirin
4. ✅ Test edin
5. ✅ Sesli kitap oluşturun!

## 🆘 Sorun Giderme

### "Ses dosyası geçersiz" hatası:
- Dosya formatını kontrol edin (WAV önerilir)
- Dosya bozuk olabilir, yeniden kaydedin
- Farklı bir ses düzenleme programı deneyin

### "Ses seviyesi çok düşük":
- Ses kaydını yeniden yapın, mikrofona daha yakın olun
- Ses düzenleme programında normalize edin (Audacity vb.)

### "Çok fazla sessizlik":
- Kayıt öncesi ve sonrasındaki sessiz kısımları kesin
- Daha kompakt bir kayıt yapın

---

**🎉 Artık hazırsınız! Sesli kitap üretimine başlayabilirsiniz!**

