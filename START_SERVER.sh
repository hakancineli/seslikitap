#!/bin/bash

# Sesli Kitap Sunucusunu Başlat

echo "🚀 Sesli Kitap Sunucusu Başlatılıyor..."
echo ""

cd "$(dirname "$0")"

# Virtual environment'ı aktifleştir
source venv/bin/activate

# Eski sunucuyu kapat
pkill -f "python app.py" 2>/dev/null

# Sunucuyu başlat
echo "📡 Sunucu başlatılıyor: http://localhost:3000"
echo "💡 Durdurmak için: Ctrl+C"
echo ""

python app.py

