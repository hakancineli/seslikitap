"""
Gelişmiş TTS Özellikleri
- Konuşma stili uyarlama (hız, ton, vurgu)
- Gelişmiş kontroller
- Ses karıştırma
"""
from TTS.api import TTS
import torch
from pydub import AudioSegment
import os
import numpy as np
import soundfile as sf


class AdvancedTTS:
    """Gelişmiş TTS özellikleri"""
    
    def __init__(self, voice_sample_path: str):
        self.device = "cpu"
        self.voice_sample = voice_sample_path
        
        print("📥 XTTS v2 modeli yükleniyor (Gelişmiş Özellikler)...")
        self.tts = TTS("tts_models/multilingual/multi-dataset/xtts_v2").to(self.device)
        print("✅ Model yüklendi!")
    
    def generate_with_style(
        self,
        text: str,
        output_path: str,
        speed: float = 1.0,
        emotion: str = "neutral",
        pitch_shift: int = 0
    ) -> bool:
        """
        Gelişmiş stil kontrolü ile ses üretimi
        
        Args:
            text: Metin
            output_path: Çıktı dosyası
            speed: Konuşma hızı (0.5-2.0, 1.0=normal)
            emotion: Duygu tonu (neutral, happy, sad, excited)
            pitch_shift: Ses tonu kaydırma (-5 to +5)
        """
        
        try:
            print(f"\n🎭 Gelişmiş Üretim:")
            print(f"   📝 Metin: {text[:50]}...")
            print(f"   ⚡ Hız: {speed}x")
            print(f"   🎭 Duygu: {emotion}")
            print(f"   🎵 Ton: {pitch_shift:+d}")
            
            # Temel TTS üretimi
            temp_output = output_path.replace('.wav', '_temp.wav')
            
            self.tts.tts_to_file(
                text=text,
                speaker_wav=self.voice_sample,
                language="tr",
                file_path=temp_output
            )
            
            # Ses dosyasını yükle
            audio = AudioSegment.from_wav(temp_output)
            
            # HIZ AYARI
            if speed != 1.0:
                print(f"   ⚡ Hız ayarlanıyor: {speed}x")
                # Hızı değiştir (frame rate manipülasyonu)
                new_sample_rate = int(audio.frame_rate * speed)
                audio = audio._spawn(audio.raw_data, overrides={
                    "frame_rate": new_sample_rate
                }).set_frame_rate(audio.frame_rate)
            
            # TON AYARI (Pitch Shift)
            if pitch_shift != 0:
                print(f"   🎵 Ton kaydırılıyor: {pitch_shift:+d}")
                # Octave değişimi (her +1 = yarım oktav yukarı)
                octaves = pitch_shift * 0.1  # Daha hassas kontrol
                new_sample_rate = int(audio.frame_rate * (2.0 ** octaves))
                audio = audio._spawn(audio.raw_data, overrides={
                    "frame_rate": new_sample_rate
                }).set_frame_rate(audio.frame_rate)
            
            # DUYGU TONU (basit amplitüd manipülasyonu)
            if emotion == "excited":
                print(f"   🎭 Heyecanlı ton ekleniyor...")
                audio = audio + 2  # Biraz daha yüksek ses
            elif emotion == "sad":
                print(f"   🎭 Üzgün ton ekleniyor...")
                audio = audio - 2  # Biraz daha düşük ses
            elif emotion == "happy":
                print(f"   🎭 Mutlu ton ekleniyor...")
                audio = audio + 1
            
            # Normalize et
            audio = audio.normalize()
            
            # Kaydet
            audio.export(output_path, format="wav")
            
            # Temp dosyayı sil
            if os.path.exists(temp_output):
                os.remove(temp_output)
            
            print(f"   ✅ Başarılı: {output_path}")
            return True
            
        except Exception as e:
            print(f"   ❌ Hata: {e}")
            return False
    
    @staticmethod
    def blend_voices(
        voice1_path: str,
        voice2_path: str,
        output_path: str,
        blend_ratio: float = 0.5
    ) -> str:
        """
        İki sesi karıştır (Voice Blending)
        
        Args:
            voice1_path: İlk ses dosyası
            voice2_path: İkinci ses dosyası
            output_path: Çıktı dosyası
            blend_ratio: Karışım oranı (0.0=sadece voice1, 1.0=sadece voice2, 0.5=eşit)
        
        Returns:
            Çıktı dosya yolu
        """
        
        print(f"\n🎨 SES KARIŞTIRMA:")
        print(f"   🎤 Ses 1: {voice1_path}")
        print(f"   🎤 Ses 2: {voice2_path}")
        print(f"   🎚️  Oran: {blend_ratio:.1%} (Ses 2)")
        
        # Ses dosyalarını yükle
        data1, sr1 = sf.read(voice1_path)
        data2, sr2 = sf.read(voice2_path)
        
        # Sample rate eşitle
        if sr1 != sr2:
            print(f"   ⚠️  Sample rate eşitleniyor: {sr1} vs {sr2}")
            # Basitleştirilmiş: daha kısa olanı kullan
            sr_target = min(sr1, sr2)
            if sr1 != sr_target:
                # Resample data1
                ratio = sr_target / sr1
                new_length = int(len(data1) * ratio)
                data1 = np.interp(
                    np.linspace(0, len(data1), new_length),
                    np.arange(len(data1)),
                    data1
                )
                sr1 = sr_target
            if sr2 != sr_target:
                # Resample data2
                ratio = sr_target / sr2
                new_length = int(len(data2) * ratio)
                data2 = np.interp(
                    np.linspace(0, len(data2), new_length),
                    np.arange(len(data2)),
                    data2
                )
                sr2 = sr_target
        
        # Uzunlukları eşitle (daha kısa olanı kullan)
        min_length = min(len(data1), len(data2))
        data1 = data1[:min_length]
        data2 = data2[:min_length]
        
        # Karıştır
        blended = data1 * (1 - blend_ratio) + data2 * blend_ratio
        
        # Normalize
        blended = blended / np.max(np.abs(blended)) * 0.95
        
        # Kaydet
        sf.write(output_path, blended, sr1)
        
        print(f"   ✅ Karışık ses oluşturuldu: {output_path}")
        print(f"   ⏱️  Süre: {len(blended)/sr1:.1f} saniye")
        
        return output_path


def test_advanced_features():
    """Gelişmiş özellikleri test et"""
    
    print("\n" + "="*60)
    print("🧪 GELİŞMİŞ ÖZELLİKLER TESTİ")
    print("="*60)
    
    voice_sample = "voices/akin_altan_optimized.wav"
    
    if not os.path.exists(voice_sample):
        print(f"❌ Referans ses bulunamadı: {voice_sample}")
        return
    
    tts = AdvancedTTS(voice_sample)
    
    # Test 1: Normal hız
    print("\n--- Test 1: Normal Hız ---")
    tts.generate_with_style(
        "Bu normal hızda bir cümledir.",
        "test_normal.wav",
        speed=1.0
    )
    
    # Test 2: Yavaş
    print("\n--- Test 2: Yavaş Konuşma ---")
    tts.generate_with_style(
        "Bu yavaş bir cümledir.",
        "test_slow.wav",
        speed=0.7
    )
    
    # Test 3: Hızlı
    print("\n--- Test 3: Hızlı Konuşma ---")
    tts.generate_with_style(
        "Bu hızlı bir cümledir.",
        "test_fast.wav",
        speed=1.3
    )
    
    # Test 4: Yüksek ton
    print("\n--- Test 4: Yüksek Ton ---")
    tts.generate_with_style(
        "Bu yüksek tonlu bir cümledir.",
        "test_high_pitch.wav",
        speed=1.0,
        pitch_shift=3
    )
    
    # Test 5: Düşük ton
    print("\n--- Test 5: Düşük Ton ---")
    tts.generate_with_style(
        "Bu düşük tonlu bir cümledir.",
        "test_low_pitch.wav",
        speed=1.0,
        pitch_shift=-3
    )
    
    print("\n" + "="*60)
    print("✅ TESTLER TAMAMLANDI!")
    print("="*60)
    print("\n🎧 Dinlemek için:")
    print("   open test_normal.wav")
    print("   open test_slow.wav")
    print("   open test_fast.wav")
    print("   open test_high_pitch.wav")
    print("   open test_low_pitch.wav")
    print("="*60)


def test_voice_blending():
    """Ses karıştırmayı test et"""
    
    print("\n" + "="*60)
    print("🧪 SES KARIŞTIRMA TESTİ")
    print("="*60)
    
    voice1 = "voices/akin_altan_optimized.wav"
    voice2 = "voices/benim_sesim.wav"
    
    if not os.path.exists(voice1) or not os.path.exists(voice2):
        print("❌ Ses dosyaları bulunamadı!")
        print(f"   Voice 1: {voice1}")
        print(f"   Voice 2: {voice2}")
        return
    
    # %25 voice2, %75 voice1
    AdvancedTTS.blend_voices(voice1, voice2, "blended_25.wav", 0.25)
    
    # %50-%50
    AdvancedTTS.blend_voices(voice1, voice2, "blended_50.wav", 0.5)
    
    # %75 voice2, %25 voice1
    AdvancedTTS.blend_voices(voice1, voice2, "blended_75.wav", 0.75)
    
    print("\n" + "="*60)
    print("✅ KARIŞIK SESLER OLUŞTURULDU!")
    print("="*60)
    print("\n🎧 Dinlemek için:")
    print("   open blended_25.wav  # %75 Akın ALTAN + %25 Senin Sesin")
    print("   open blended_50.wav  # %50-%50 Karışık")
    print("   open blended_75.wav  # %25 Akın ALTAN + %75 Senin Sesin")
    print("="*60)


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "blend":
        test_voice_blending()
    else:
        test_advanced_features()



