"""
Sesli Kitap Üretim Sistemi - Web Arayüzü
"""
import gradio as gr
import os
from pathlib import Path
import time
from pdf_parser import PDFParser
from sentence_processor import SentenceProcessor
from tts_engine import M1OptimizedTTS
from voice_manager import VoiceManager
from voice_recorder import VoiceRecorder
from text_cleaner import TextCleaner
from advanced_tts import AdvancedTTS
from voice_catalog import VoiceCatalog, TurkishTTSModels


# Global değişkenler
voice_manager = VoiceManager()
voice_recorder = VoiceRecorder()
voice_catalog = VoiceCatalog()

# Kataloğu tara (ilk başlatmada)
voice_catalog.scan_voices()


def analyze_pdf(pdf_file):
    """PDF'i analiz et"""
    if pdf_file is None:
        return "❌ PDF dosyası yükleyin"
    
    try:
        parser = PDFParser(pdf_file.name)
        content = parser.extract_text_with_structure()
        
        info = f"""
## 📊 PDF Analizi

- **Sayfa Sayısı:** {content['total_pages']}
- **Kelime Sayısı:** {content['word_count']:,}
- **Tahmini Sesli Kitap Süresi:** {content['estimated_duration_minutes']:.0f} dakika
- **Tahmini İşlem Süresi (M1):** ~{content['word_count'] / 150 * 4 / 60:.0f} dakika

### 📝 İlk Paragraf Önizlemesi:
{content['full_text'][:500]}...
        """
        
        return info
        
    except Exception as e:
        return f"❌ Hata: {str(e)}"


def analyze_text(text_input):
    """Metni analiz et"""
    if not text_input.strip():
        return "❌ Metin girin"
    
    try:
        # Metni temizle
        cleaned_text = TextCleaner.clean_text(text_input)
        
        word_count = len(cleaned_text.split())
        char_count = len(cleaned_text)
        paragraph_count = len([p for p in cleaned_text.split('\n\n') if p.strip()])
        estimated_duration = word_count / 150  # dakika
        estimated_processing = word_count / 150 * 4 / 60  # dakika
        
        info = f"""
## 📊 Metin Analizi

- **Kelime Sayısı:** {word_count:,}
- **Karakter Sayısı:** {char_count:,}
- **Paragraf Sayısı:** {paragraph_count}
- **Tahmini Sesli Kitap Süresi:** {estimated_duration:.0f} dakika
- **Tahmini İşlem Süresi (M1):** ~{estimated_processing:.0f} dakika

### 📝 Temizlenmiş Metin (İlk 500 Karakter):
{cleaned_text[:500]}...

✅ Özel karakterler otomatik olarak düzeltildi
        """
        
        return info
        
    except Exception as e:
        return f"❌ Hata: {str(e)}"


def validate_voice_file(audio_file):
    """Ses dosyasını doğrula"""
    if audio_file is None:
        return "❌ Ses dosyası yükleyin"
    
    try:
        info = voice_recorder.validate_audio(audio_file.name)
        
        if not info['valid']:
            return f"❌ Geçersiz ses dosyası: {info['error']}"
        
        warnings_text = ""
        if info['warnings']:
            warnings_text = "\n\n### ⚠️ Uyarılar:\n" + "\n".join(f"- {w}" for w in info['warnings'])
        
        result = f"""
## ✅ Ses Dosyası Geçerli

- **Süre:** {info['duration']:.1f} saniye
- **Sample Rate:** {info['sample_rate']} Hz
- **Kanal:** {info['channels']} (Mono)
- **Ses Seviyesi:** {info['rms_level']:.3f}
- **Sessizlik Oranı:** {info['silence_percentage']:.1f}%
- **Dosya Boyutu:** {info['file_size_kb']:.1f} KB
{warnings_text}
        """
        
        return result
        
    except Exception as e:
        return f"❌ Hata: {str(e)}"


def record_voice_interface(duration):
    """Mikrofon ile ses kaydı (arayüz için)"""
    try:
        output_path = voice_recorder.record(duration=int(duration))
        
        # Analiz
        info = voice_recorder.validate_audio(output_path)
        
        analysis = f"""
## ✅ Kayıt Tamamlandı!

- **Dosya:** {output_path}
- **Süre:** {info['duration']:.1f} saniye
- **Ses Seviyesi:** {info['rms_level']:.3f}
        """
        
        return output_path, analysis
        
    except Exception as e:
        return None, f"❌ Hata: {str(e)}"


def generate_audiobook(pdf_file, text_input, voice_dropdown_selected, voice_file, speed_control, pitch_control, progress=gr.Progress()):
    """Sesli kitap oluştur"""
    
    # Metin veya PDF kontrolü
    if pdf_file is None and not text_input.strip():
        return None, "❌ PDF dosyası yükleyin veya metin girin"
    
    # Ses dosyası: Hazır seslerden VEYA yüklenmiş
    selected_voice = voice_dropdown_selected or voice_file
    
    if selected_voice is None:
        return None, "❌ Hazır seslerden seçin VEYA ses dosyası yükleyin"
    
    try:
        # Metin kaynağını belirle
        if text_input.strip():
            # Direkt metin girilmiş
            progress(0, desc="📝 Metin işleniyor...")
            
            # METİN TEMİZLEME - Özel karakterleri düzelt
            print("\n🧹 Metin temizleniyor (özel karakterler düzeltiliyor)...")
            full_text = TextCleaner.clean_text(text_input, verbose=True)
            
            page_count = len(full_text.split('\n\n'))  # Paragraf sayısı
            word_count = len(full_text.split())
            
        else:
            # PDF yüklenmiş
            progress(0, desc="📖 PDF okunuyor...")
            
            # PDF Parse
            parser = PDFParser(pdf_file.name)
            content = parser.extract_text_with_structure()
            
            full_text = content['full_text']
            page_count = content['total_pages']
            word_count = content['word_count']
        
        progress(0.2, desc="✂️ Cümleler analiz ediliyor...")
        
        # Cümlelere ayır
        processor = SentenceProcessor()
        sentences = processor.split_into_sentences(full_text)
        
        if len(sentences) > 500:
            return None, f"❌ Çok uzun metin! ({len(sentences)} cümle). Maksimum 500 cümle destekleniyor. Daha kısa bir PDF deneyin."
        
        progress(0.3, desc="🎙️ TTS motoru hazırlanıyor...")
        
        # Ses dosyası formatını kontrol et ve gerekirse dönüştür
        # Öncelik: Dropdown seçimi > Yüklenen dosya
        if voice_dropdown_selected:
            voice_path = voice_dropdown_selected
            print(f"📚 Hazır ses kullanılıyor: {voice_path}")
        else:
            voice_path = voice_file.name if hasattr(voice_file, 'name') else voice_file
            print(f"📤 Yüklenen ses kullanılıyor: {voice_path}")
        
        print(f"\n{'='*60}")
        print(f"🎤 REFERANS SES DOSYASI KONTROL EDİLİYOR")
        print(f"{'='*60}")
        print(f"📁 Alınan dosya: {voice_path}")
        print(f"📂 Dosya türü: {type(voice_file)}")
        
        # MP3 veya diğer formatları WAV'a dönüştür
        if not voice_path.lower().endswith('.wav'):
            progress(0.35, desc="🔄 Ses dosyası WAV formatına dönüştürülüyor...")
            from pathlib import Path
            temp_wav_path = f"temp_chunks/voice_converted_{int(time.time())}.wav"
            os.makedirs("temp_chunks", exist_ok=True)
            
            try:
                voice_path = voice_recorder.convert_to_format(voice_path, temp_wav_path)
                print(f"✅ Ses dönüştürüldü: {voice_path}")
            except Exception as e:
                return None, f"❌ Ses dosyası dönüştürme hatası: {str(e)}"
        
        print(f"✅ Kullanılacak ses dosyası: {voice_path}")
        print(f"{'='*60}\n")
        
        # TTS Engine - SES KLONLAMA BURADA BAŞLIYOR
        print(f"🚀 TTS motoru başlatılıyor - REFERANS SES: {voice_path}")
        print(f"⚡ Hız: {speed_control}x")
        print(f"🎵 Ton: {pitch_control:+d}")
        
        # Gelişmiş özellikler varsa AdvancedTTS kullan
        if speed_control != 1.0 or pitch_control != 0:
            engine = AdvancedTTS(voice_path)
            use_advanced = True
        else:
            engine = M1OptimizedTTS(voice_path, use_progress_bar=False)
            use_advanced = False
        
        # Output path
        output_path = f"outputs/audiobook_{int(time.time())}.mp3"
        os.makedirs("outputs", exist_ok=True)
        
        progress(0.4, desc=f"🎤 {len(sentences)} cümle seslendiriliyor...")
        
        # Üret (gelişmiş özelliklerle veya normal)
        if use_advanced:
            # Gelişmiş özelliklerle üret
            print("🎭 Gelişmiş özellikler kullanılıyor...")
            audio_chunks = []
            for i, sentence_data in enumerate(sentences):
                chunk_path = f"temp_chunks/chunk_{i:04d}.wav"
                os.makedirs("temp_chunks", exist_ok=True)
                
                success = engine.generate_with_style(
                    sentence_data['text'],
                    chunk_path,
                    speed=speed_control,
                    pitch_shift=pitch_control
                )
                
                if success:
                    audio = AudioSegment.from_wav(chunk_path)
                    pause_ms = int(sentence_data['pause_after'] * 1000)
                    silence = AudioSegment.silent(duration=pause_ms)
                    audio_chunks.append(audio + silence)
            
            # Birleştir ve kaydet
            if audio_chunks:
                from pydub import AudioSegment
                final_audio = sum(audio_chunks)
                final_audio = final_audio.normalize()
                final_audio.export(output_path, format="mp3", bitrate="192k")
                audiobook_path = output_path
            else:
                return None, "❌ Ses üretilemedi"
        else:
            # Normal üretim
            audiobook_path = engine.generate_audiobook(sentences, output_path)
        
        progress(1.0, desc="✅ Tamamlandı!")
        
        info = f"""
## 🎉 Sesli Kitap Oluşturuldu!

- **Dosya:** {audiobook_path}
- **Cümle Sayısı:** {len(sentences)}
- **Sayfa/Paragraf Sayısı:** {page_count}
- **Kelime Sayısı:** {word_count}

🎧 Aşağıdan dinleyebilir veya indirebilirsiniz!
        """
        
        return audiobook_path, info
        
    except Exception as e:
        import traceback
        error_detail = traceback.format_exc()
        return None, f"❌ Hata: {str(e)}\n\n```\n{error_detail}\n```"


def list_saved_voices():
    """Kayıtlı sesleri listele"""
    voices = voice_manager.list_voices()
    
    if not voices:
        return "📭 Henüz kayıtlı ses yok"
    
    result = "## 🎤 Kayıtlı Sesler\n\n"
    
    for voice in voices:
        result += f"""
### 📌 {voice['name']}
- **ID:** {voice['id']}
- **Cinsiyet:** {voice['gender']}
- **Kullanım:** {voice['usage_count']} kez
- **Dosya:** {voice['file_name']}

---
        """
    
    return result


# Gradio Arayüzü
with gr.Blocks(title="🎙️ Sesli Kitap Üretim Sistemi", theme=gr.themes.Soft()) as app:
    
    gr.Markdown("""
    # 🎙️ Sesli Kitap Üretim Sistemi
    
    **Kendi sesinizi klonlayın ve PDF'lerinizi sesli kitaba dönüştürün!**
    
    M1 Mac için optimize edilmiş, XTTS v2 ses klonlama ile güçlendirilmiş sistem.
    """)
    
    with gr.Tabs():
        
        # TAB 1: Sesli Kitap Oluştur
        with gr.Tab("📚 Sesli Kitap Oluştur"):
            
            # Metin Girişi - En üstte, çok görünür
            gr.Markdown("# ✍️ Metin Yazın (Buraya!)")
            text_input = gr.Textbox(
                label="📝 Metin İçeriği",
                placeholder="Buraya seslendirilmesini istediğiniz metni yazın veya yapıştırın...\n\nÖrnek:\nBir varmış bir yokmuş, evvel zaman içinde...\n\nVeya kendi hikayenizi, makalenizi yazın.",
                lines=8,
                max_lines=15,
                show_label=True
            )
            
            with gr.Row():
                text_analyze_btn = gr.Button("🔍 Metni Analiz Et", variant="secondary", scale=1)
                text_clear_btn = gr.Button("🗑️ Temizle", variant="secondary", scale=1)
            
            text_info = gr.Markdown("Metin girdikten sonra analiz butonuna tıklayın")
            
            gr.Markdown("---")
            gr.Markdown("# 📄 veya PDF Yükleyin")
            
            with gr.Row():
                with gr.Column():
                    pdf_input = gr.File(
                        label="📄 PDF Dosyası",
                        file_types=[".pdf"],
                        type="filepath"
                    )
                    
                    pdf_analyze_btn = gr.Button("🔍 PDF'i Analiz Et", variant="secondary")
                    pdf_info = gr.Markdown("PDF yükledikten sonra analiz edin")
                
                with gr.Column():
                    gr.Markdown("### 🎭 Ses Seçimi")
                    
                    # Hazır seslerden seç VEYA yeni yükle
                    with gr.Tab("📚 Hazır Sesler"):
                        voice_dropdown = gr.Dropdown(
                            choices=voice_catalog.get_voice_choices(),
                            label="Hazır Ses Klonlarından Seç",
                            info="Profesyonel sesli kitap sanatçıları"
                        )
                        
                        # TTS Modeli seçimi
                        model_choices = [(m['name'], m['id']) for m in TurkishTTSModels.MODELS]
                        tts_model_dropdown = gr.Dropdown(
                            choices=model_choices,
                            value="xtts_v2",
                            label="🤖 TTS Modeli",
                            info="⭐ XTTS v2 önerilir (en iyi klonlama)"
                        )
                    
                    with gr.Tab("📤 Ses Yükle"):
                        voice_input = gr.Audio(
                            label="🎤 Kendi Sesinizi Yükle (WAV, MP3, M4A)",
                            type="filepath",
                            sources=["upload", "microphone"]
                        )
                        
                        voice_validate_btn = gr.Button("✅ Sesi Doğrula", variant="secondary")
                        voice_info = gr.Markdown("Ses yükledikten sonra doğrulayın")
            
            # Gelişmiş Kontroller
            gr.Markdown("---")
            gr.Markdown("### 🎛️ Gelişmiş Kontroller (Opsiyonel)")
            
            with gr.Row():
                speed_control = gr.Slider(
                    minimum=0.5,
                    maximum=2.0,
                    value=1.0,
                    step=0.1,
                    label="⚡ Konuşma Hızı (0.5=Yavaş, 1.0=Normal, 2.0=Hızlı)",
                    info="Sesi daha yavaş veya hızlı okut"
                )
                
                pitch_control = gr.Slider(
                    minimum=-5,
                    maximum=5,
                    value=0,
                    step=1,
                    label="🎵 Ses Tonu (-5=Alçak, 0=Normal, +5=Yüksek)",
                    info="Sesin tonunu değiştir"
                )
            
            generate_btn = gr.Button("🎬 Sesli Kitap Oluştur", variant="primary", size="lg")
            
            with gr.Row():
                with gr.Column():
                    audiobook_output = gr.Audio(
                        label="🎧 Sesli Kitap",
                        type="filepath"
                    )
                
                with gr.Column():
                    generation_info = gr.Markdown("Sesli kitap burada görünecek")
            
            # Event handlers
            text_analyze_btn.click(
                fn=analyze_text,
                inputs=[text_input],
                outputs=[text_info]
            )
            
            text_clear_btn.click(
                fn=lambda: ("", "Metin temizlendi"),
                outputs=[text_input, text_info]
            )
            
            pdf_analyze_btn.click(
                fn=analyze_pdf,
                inputs=[pdf_input],
                outputs=[pdf_info]
            )
            
            voice_validate_btn.click(
                fn=validate_voice_file,
                inputs=[voice_input],
                outputs=[voice_info]
            )
            
            generate_btn.click(
                fn=generate_audiobook,
                inputs=[pdf_input, text_input, voice_dropdown, voice_input, speed_control, pitch_control],
                outputs=[audiobook_output, generation_info]
            )
        
        # TAB 2: Ses Kaydı
        with gr.Tab("🎤 Ses Kaydı"):
            gr.Markdown("""
            ## Mikrofon ile Ses Kaydı
            
            30-60 saniyelik temiz bir ses kaydı yapın. Farklı tonlamalar kullanın:
            - Normal cümleler
            - Soru cümleleri (?)
            - Ünlem cümleleri (!)
            - Yavaş ve hızlı okuma
            """)
            
            record_duration = gr.Slider(
                minimum=10,
                maximum=120,
                value=30,
                step=5,
                label="⏱️ Kayıt Süresi (saniye)"
            )
            
            record_btn = gr.Button("🔴 Kaydı Başlat", variant="primary", size="lg")
            
            with gr.Row():
                recorded_audio = gr.Audio(
                    label="🎧 Kaydedilen Ses",
                    type="filepath"
                )
                
                record_info = gr.Markdown("Kayıt bilgileri burada görünecek")
            
            record_btn.click(
                fn=record_voice_interface,
                inputs=[record_duration],
                outputs=[recorded_audio, record_info]
            )
            
            gr.Markdown("""
            ### 📝 Örnek Okuma Metni:
            
            ```
            Merhaba! Ben [İsminiz], ve bu ses kaydı yapay zeka tarafından 
            klonlanacak. Sesli kitaplar için kullanılacak. 
            
            Farklı tonlamalarda konuşuyorum: Bu bir soru mu? Evet, bu bir soru! 
            Ve bu bir ünlem cümlesi. Normal bir anlatım cümlesi. 
            
            Yavaşça söylenen bir cümle... Hızlıca söylenen bir cümle. 
            Mutlu bir ton ile konuşuyorum. Üzgün bir ton ile konuşuyorum.
            
            Teşekkür ederim!
            ```
            """)
        
        # TAB 3: Ses Kütüphanesi
        with gr.Tab("📚 Ses Kütüphanesi"):
            gr.Markdown("## Kayıtlı Sesleriniz")
            
            refresh_btn = gr.Button("🔄 Listeyi Yenile", variant="secondary")
            voices_list = gr.Markdown("Kayıtlı sesler yüklenecek...")
            
            refresh_btn.click(
                fn=list_saved_voices,
                outputs=[voices_list]
            )
            
            # İlk yüklemede göster
            app.load(fn=list_saved_voices, outputs=[voices_list])
        
        # TAB 4: Yardım
        with gr.Tab("❓ Yardım"):
            gr.Markdown("""
            ## 📖 Kullanım Kılavuzu
            
            ### 1️⃣ Ses Hazırlığı
            
            **Seçenek A: Hazır Ses Dosyası Yükleme**
            - "Sesli Kitap Oluştur" sekmesinde "Ses Dosyası Yükle" butonuna tıklayın
            - WAV, MP3, M4A formatlarını destekler
            - 30-60 saniye uzunluğunda olmalı
            
            **Seçenek B: Mikrofon ile Kayıt**
            - "Ses Kaydı" sekmesine gidin
            - Kayıt süresini ayarlayın (30 saniye önerilir)
            - "Kaydı Başlat" butonuna tıklayın
            - Örnek metni okuyun
            
            ### 2️⃣ Metin Hazırlama
            
            **Seçenek A: Direkt Metin Girişi**
            - "Sesli Kitap Oluştur" sekmesinde metin kutusuna yazın/yapıştırın
            - Hikayeler, makaleler, blog yazıları için ideal
            - "Metni Analiz Et" ile ön bilgi alın
            
            **Seçenek B: PDF Yükleme**
            - "Sesli Kitap Oluştur" sekmesinde PDF yükleyin
            - "PDF'i Analiz Et" ile ön bilgi alın
            - Küçük PDF'lerle (10-20 sayfa) test edin
            
            ### 3️⃣ Sesli Kitap Oluşturma
            
            - Hem PDF hem ses yüklendiğinde "Sesli Kitap Oluştur" butonuna tıklayın
            - İşlem süresi cümle sayısına bağlıdır (M1'de ~3-5 saniye/cümle)
            - Tamamlandığında dinleyebilir veya indirebilirsiniz
            
            ### ⚙️ Sistem Gereksinimleri
            
            - **Cihaz:** macOS M1/M2/M3
            - **RAM:** 8GB+ önerilir
            - **Disk:** 5GB+ boş alan
            - **İnternet:** İlk model indirme için gerekli (~2GB)
            
            ### 💡 İpuçları
            
            - ✅ İlk testinizi 5-10 sayfalık küçük PDF ile yapın
            - ✅ Sessiz ortamda temiz ses kaydı yapın
            - ✅ Farklı tonlamalar kullanın (soru, ünlem, normal)
            - ✅ Net ve anlaşılır konuşun
            - ❌ Arka plan gürültüsü olmasın
            - ❌ Çok hızlı veya yavaş konuşmayın
            
            ### 🔧 Sorun Giderme
            
            **"Ses dosyası geçersiz" hatası:**
            - Ses formatını kontrol edin (WAV önerilir)
            - En az 10 saniye olmalı
            - Ses seviyesi çok düşükse yeniden kaydedin
            
            **"İşlem çok yavaş":**
            - MPS (M1 GPU) aktif mi kontrol edin
            - Arka plan uygulamalarını kapatın
            - Daha küçük PDF'lerle test edin
            
            **"Model yüklenemedi":**
            - İnternet bağlantınızı kontrol edin
            - Terminal'de `python test_tts.py` çalıştırın
            - Model indirmesi birkaç dakika sürebilir
            
            ### 📞 Destek
            
            Sorunlarınız için:
            - README.md dosyasına bakın
            - VOICE_GUIDE.md'de detaylı bilgi var
            - Terminal'den `python test_tts.py` ile test edin
            
            ---
            
            **🎉 Artık hazırsınız! Sesli kitap üretmeye başlayın!**
            """)
    
    gr.Markdown("""
    ---
    💻 **Sesli Kitap Üretim Sistemi v1.0** | M1 Optimize | XTTS v2 Ses Klonlama
    """)


if __name__ == "__main__":
    print("\n" + "="*60)
    print("🎙️ SESLİ KİTAP ÜRETİM SİSTEMİ - WEB ARAYÜZÜ")
    print("="*60)
    print("\n🚀 Arayüz başlatılıyor...")
    print("📡 Tarayıcınızda otomatik olarak açılacak")
    print("🌐 URL: http://localhost:3000")
    print("\n💡 Durdurmak için: Ctrl+C")
    print("="*60 + "\n")
    
    app.launch(
        server_name="127.0.0.1",
        server_port=3000,
        share=False,
        inbrowser=True
    )

