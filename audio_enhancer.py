"""
Audio Enhancer - Ses Kalitesi İyileştirme
"""
import numpy as np
import soundfile as sf
from scipy import signal
from pydub import AudioSegment


class AudioEnhancer:
    """Ses kalitesi iyileştirme araçları"""
    
    @staticmethod
    def remove_noise(audio_path: str, output_path: str, noise_reduce_strength: float = 0.5):
        """
        Basit gürültü azaltma
        
        Args:
            audio_path: Giriş ses dosyası
            output_path: Çıkış ses dosyası
            noise_reduce_strength: Gürültü azaltma gücü (0-1)
        """
        data, sr = sf.read(audio_path)
        
        # Basit spectral gating (gerçek uygulamada noisereduce kütüphanesi kullanılabilir)
        # Düşük amplitude'ları bastır
        threshold = np.percentile(np.abs(data), 10) * (1 - noise_reduce_strength)
        data[np.abs(data) < threshold] *= 0.1
        
        sf.write(output_path, data, sr)
        return output_path
    
    @staticmethod
    def normalize_volume(audio_path: str, output_path: str, target_db: float = -20.0):
        """
        Ses seviyesini normalize et
        
        Args:
            audio_path: Giriş ses dosyası
            output_path: Çıkış ses dosyası
            target_db: Hedef dB seviyesi
        """
        audio = AudioSegment.from_file(audio_path)
        
        # Mevcut dB seviyesi
        current_db = audio.dBFS
        
        # dB farkı
        change_db = target_db - current_db
        
        # Uygula
        normalized = audio + change_db
        normalized.export(output_path, format="wav")
        
        return output_path
    
    @staticmethod
    def apply_compression(audio_path: str, output_path: str, threshold: float = -20.0, ratio: float = 4.0):
        """
        Audio compression (dinamik aralık sıkıştırma)
        
        Args:
            audio_path: Giriş ses dosyası
            output_path: Çıkış ses dosyası
            threshold: Threshold seviyesi (dB)
            ratio: Sıkıştırma oranı
        """
        audio = AudioSegment.from_file(audio_path)
        
        # Basit compression simülasyonu
        compressed = audio.compress_dynamic_range(
            threshold=threshold,
            ratio=ratio,
            attack=5.0,
            release=50.0
        )
        
        compressed.export(output_path, format="wav")
        return output_path
    
    @staticmethod
    def enhance_voice(audio_path: str, output_path: str):
        """
        Ses netleştirme (komple pipeline)
        
        Args:
            audio_path: Giriş ses dosyası
            output_path: Çıkış ses dosyası
        """
        # 1. Gürültü azaltma
        temp1 = output_path.replace('.wav', '_temp1.wav')
        AudioEnhancer.remove_noise(audio_path, temp1, noise_reduce_strength=0.3)
        
        # 2. Normalize
        temp2 = output_path.replace('.wav', '_temp2.wav')
        AudioEnhancer.normalize_volume(temp1, temp2, target_db=-18.0)
        
        # 3. Hafif compression
        AudioEnhancer.apply_compression(temp2, output_path, threshold=-20.0, ratio=3.0)
        
        # Temp dosyaları temizle
        import os
        if os.path.exists(temp1):
            os.remove(temp1)
        if os.path.exists(temp2):
            os.remove(temp2)
        
        print(f"✅ Ses iyileştirildi: {output_path}")
        return output_path

