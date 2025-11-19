# 🌐 ElevenLabs Kurulum Rehberi

## 📝 ElevenLabs Nedir?

ElevenLabs, profesyonel kalitede yapay zeka destekli ses sentezi sunan bir platformdur. Türkçe dahil 29 dilde doğal ve gerçekçi sesler üretebilir.

## ⭐ Özellikler

- **Profesyonel Kalite**: Stüdyo kalitesinde ses çıktısı
- **Türkçe Destek**: 4 özel Türkçe ses (Ada, Emre, Aylin, Burak)
- **Hızlı**: ~1 saniye/cümle (XTTS v2'den 4x daha hızlı)
- **API Entegrasyonu**: Otomatik entegrasyon

## 🆚 XTTS v2 vs ElevenLabs

| Özellik | XTTS v2 (Yerel) | ElevenLabs (Cloud) |
|---------|-----------------|---------------------|
| **Kalite** | ⭐⭐⭐⭐ Çok İyi | ⭐⭐⭐⭐⭐ Mükemmel |
| **Hız** | ~4s/cümle | ~1s/cümle |
| **Maliyet** | **Ücretsiz** 💚 | $0-99/ay |
| **İnternet** | İlk indirme | Her kullanım |
| **Ses Klonlama** | Evet (referans gerekli) | Hazır sesler |
| **Gizlilik** | 100% Yerel | Cloud tabanlı |

## 🚀 Kurulum (3 Adım)

### 1️⃣ ElevenLabs Hesabı Oluştur

1. **Üye ol**: https://elevenlabs.io/sign-up
2. **Ücretsiz plan**: 10,000 karakter/ay (yaklaşık 8-10 sayfa)
3. **E-posta doğrula**

### 2️⃣ API Anahtarı Al

1. **Giriş yap**: https://elevenlabs.io/app
2. **Ayarlara git**: Profile Icon → Settings
3. **API Keys**: https://elevenlabs.io/app/settings/api-keys
4. **Create API Key** butonuna tıkla
5. **İzinler**: 
   - ✅ **Text to Speech** (zorunlu)
   - ✅ **Metinden Konuşmaya** aktif olmalı
6. **Anahtarı kopyala**: Başında `a6c...` gibi uzun bir string

### 3️⃣ Uygulamaya Ekle

**Yöntem 1: Web Arayüzü (Kolay)**

1. Uygulamayı başlat: `python app.py`
2. "🌐 ElevenLabs TTS" sekmesine git
3. API anahtarını yapıştır
4. "💾 API Anahtarını Kaydet" butonuna tıkla

**Yöntem 2: Terminal**

```bash
export ELEVENLABS_API_KEY='your-api-key-here'
```

**Yöntem 3: config.json Dosyası**

```bash
cp config.json.example config.json
# config.json dosyasını düzenle ve API anahtarını ekle
```

## 🎤 Türkçe Sesler

### 1. **Ada** 👩 (Kadın, Genç, Net)
- **Kullanım**: Edebi metinler, hikayeler, romanlar
- **Ton**: Genç, net, duygusal
- **Profil**: `story_teller_female`

### 2. **Emre** 👨 (Erkek, Orta Yaş, Sıcak)
- **Kullanım**: Profesyonel sunumlar, eğitim içerikleri
- **Ton**: Sıcak, güvenilir, profesyonel
- **Profil**: `story_teller_male`, `wise_elder`

### 3. **Aylin** 👩 (Kadın, Olgun, Otoriter)
- **Kullanım**: Haber sunumu, kurumsal içerikler
- **Ton**: Otoriter, ciddi, profesyonel
- **Profil**: `news_anchor_female`

### 4. **Burak** 👨 (Erkek, Genç, Enerjik)
- **Kullanım**: Reklam, tanıtım, dinamik içerikler
- **Ton**: Enerjik, hızlı, çekici
- **Profil**: `young_hero`, `educator_male`

## 🎭 Ses Profilleri

Hazır profiller, belirli kullanım senaryoları için optimize edilmiştir:

```python
# Hikaye Anlatıcı (Erkek)
profile = "story_teller_male"
# Stability: 0.4, Similarity: 0.8
# Duygusal, hikaye anlatımı için ideal

# Eğitmen
profile = "educator_male"  
# Stability: 0.6, Similarity: 0.7
# Net, anlaşılır, eğitim içerikleri için

# Haber Sunucusu
profile = "news_anchor_female"
# Stability: 0.7, Similarity: 0.9
# Profesyonel, ciddi, haber için
```

## 💰 Fiyatlandırma

### Ücretsiz Plan
- **10,000 karakter/ay**
- Tüm sesler
- API erişimi
- **Yeterli mi?** ~8-10 sayfa metin

### Starter ($5/ay)
- **30,000 karakter/ay**
- ~25-30 sayfa

### Creator ($22/ay)
- **100,000 karakter/ay**
- ~80-100 sayfa
- Ses klonlama

### Pro ($99/ay)
- **500,000 karakter/ay**
- ~400-500 sayfa
- Ticari kullanım

## 🧪 Test

```bash
# Terminal'de test
python -c "
from elevenlabs_integration import ElevenLabsTTS
tts = ElevenLabsTTS('your-api-key')
tts.generate_speech(
    text='Merhaba! ElevenLabs Türkçe TTS testi.',
    voice_name='ada',
    output_path='test.mp3'
)
"
```

**Web arayüzünde test:**
1. "🌐 ElevenLabs TTS" sekmesine git
2. Metin yaz
3. Ses seç (Ada, Emre, Aylin, Burak)
4. "🎬 Ses Üret" butonuna tıkla

## 🔧 Sorun Giderme

### ❌ "401 Unauthorized"
- **Neden**: API anahtarı geçersiz veya yanlış
- **Çözüm**: Yeni API anahtarı oluştur

### ❌ "Missing permission text_to_speech"
- **Neden**: API anahtarında "Text to Speech" izni yok
- **Çözüm**: 
  1. Settings → API Keys'e git
  2. Anahtarı düzenle
  3. "Text to Speech" iznini aktif et

### ❌ "Quota exceeded"
- **Neden**: Aylık karakter limitini aştınız
- **Çözüm**: 
  - Sonraki ay başını bekle
  - Veya plan yükselt

### ❌ "Network error"
- **Neden**: İnternet bağlantısı yok
- **Çözüm**: İnternet bağlantınızı kontrol edin

## 💡 İpuçları

### Karakter Tasarrufu
- Kısa cümleler kullanın
- Gereksiz boşlukları kaldırın
- Test için XTTS v2 kullanın (ücretsiz)

### Kalite İyileştirme
- **Stability (Kararlılık)**:
  - Düşük (0.3): Daha ifadeli, değişken
  - Yüksek (0.7): Daha tutarlı, kararlı
  
- **Similarity (Benzerlik)**:
  - Düşük (0.5): Daha yaratıcı
  - Yüksek (0.9): Orijinal sese daha sadık

### Ne Zaman Hangisi?

**XTTS v2 Kullan:**
- ✅ Ücretsiz olmalı
- ✅ Uzun metinler (100+ sayfa)
- ✅ Gizlilik önemli
- ✅ İnternet yok

**ElevenLabs Kullan:**
- ✅ Maksimum kalite gerekli
- ✅ Hızlı üretim (deadline var)
- ✅ Profesyonel proje
- ✅ Kısa metinler (10-50 sayfa)

## 📚 Kaynaklar

- **Resmi Site**: https://elevenlabs.io
- **Dokümantasyon**: https://docs.elevenlabs.io
- **API Referans**: https://elevenlabs.io/docs/api-reference
- **Destek**: https://elevenlabs.io/support

## 🎓 Örnek Kullanım

```python
from elevenlabs_integration import ElevenLabsTTS

# API ile başlat
tts = ElevenLabsTTS('your-api-key')

# Basit kullanım
tts.generate_speech(
    text="Merhaba dünya!",
    voice_name="ada",
    output_path="output.mp3"
)

# Profil ile kullanım
tts.generate_with_profile(
    text="Bir varmış, bir yokmuş...",
    profile_name="story_teller_female",
    output_path="hikaye.mp3"
)

# Manuel ayarlarla
tts.generate_speech(
    text="Haber bülteni başlıyor",
    voice_name="aylin",
    output_path="haber.mp3",
    stability=0.8,
    similarity_boost=0.9
)
```

---

**Sorularınız için**: Discord veya GitHub Issues kullanabilirsiniz! 🚀

