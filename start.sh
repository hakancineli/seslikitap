#!/bin/bash

# 🎙️ Sesli Kitap Sunucusu - Hızlı Başlatma
# Tüm kontrolleri yapar ve sunucuyu başlatır

clear
echo "════════════════════════════════════════════════════════════"
echo "🎙️  SESLİ KİTAP ÜRETİM SİSTEMİ - BAŞLATILIYOR"
echo "════════════════════════════════════════════════════════════"
echo ""

cd "$(dirname "$0")"

# 1. Virtual Environment Kontrolü
echo "📦 [1/5] Virtual environment kontrol ediliyor..."
if [ ! -d "venv" ]; then
    echo "   ⚠️  venv bulunamadı, oluşturuluyor..."
    python3 -m venv venv
    echo "   ✅ venv oluşturuldu"
else
    echo "   ✅ venv mevcut"
fi

# 2. Bağımlılık Kontrolü ve Kurulumu
echo ""
echo "📥 [2/5] Bağımlılıklar kontrol ediliyor..."
./venv/bin/pip install -q --upgrade pip 2>/dev/null

# Kritik paketleri kontrol et
PACKAGES_OK=true
for pkg in gradio TTS transformers torch soundfile; do
    if ! ./venv/bin/python -c "import $pkg" 2>/dev/null; then
        PACKAGES_OK=false
        break
    fi
done

if [ "$PACKAGES_OK" = false ]; then
    echo "   ⚠️  Eksik paketler bulundu, kuruluyor..."
    ./venv/bin/pip install -q gradio soundfile sounddevice pydub pymupdf spacy requests
    ./venv/bin/pip uninstall -y transformers torch torchaudio 2>/dev/null
    ./venv/bin/pip install -q transformers==4.33.0
    ./venv/bin/pip install -q torch==2.3.0 torchaudio==2.3.0
    ./venv/bin/pip install -q TTS
    echo "   ✅ Tüm bağımlılıklar kuruldu"
else
    echo "   ✅ Tüm bağımlılıklar mevcut"
fi

# 3. Eski Sunucu Process'lerini Temizle
echo ""
echo "🧹 [3/5] Eski process'ler temizleniyor..."
pkill -9 -f "python.*app.py" 2>/dev/null
sleep 2
if lsof -i :3000 2>/dev/null | grep -q LISTEN; then
    echo "   ⚠️  Port 3000 hala meşgul, zorla kapatılıyor..."
    lsof -ti :3000 | xargs kill -9 2>/dev/null
    sleep 1
fi
echo "   ✅ Temizlik tamamlandı"

# 4. Ses Dosyaları Kontrolü
echo ""
echo "🎤 [4/5] Ses dosyaları kontrol ediliyor..."
VOICE_COUNT=$(ls -1 voices/*.wav 2>/dev/null | wc -l | xargs)
if [ "$VOICE_COUNT" -gt 0 ]; then
    echo "   ✅ $VOICE_COUNT ses dosyası bulundu"
else
    echo "   ⚠️  Ses dosyası bulunamadı, devam ediliyor..."
fi

# 5. Sunucuyu Başlat
echo ""
echo "🚀 [5/5] Sunucu başlatılıyor..."
echo ""
./venv/bin/python app.py 2>&1 | while IFS= read -r line; do
    echo "$line"
    if echo "$line" | grep -q "http://127.0.0.1:3000"; then
        echo ""
        echo "════════════════════════════════════════════════════════════"
        echo "✅ SUNUCU BAŞARIYLA BAŞLATILDI!"
        echo "════════════════════════════════════════════════════════════"
        echo "🌐 URL: http://localhost:3000"
        echo "💡 Durdurmak için: Ctrl+C"
        echo "════════════════════════════════════════════════════════════"
        echo ""
    fi
done

