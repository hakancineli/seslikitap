"""
Voice Manager - Ses yönetimi ve kütüphanesi
"""
from pathlib import Path
from typing import List, Dict, Optional
import json
import hashlib
from datetime import datetime
import shutil


class VoiceManager:
    def __init__(self, voices_dir: str = "voices"):
        self.voices_dir = Path(voices_dir)
        self.voices_dir.mkdir(exist_ok=True)
        
        # Metadata dosyası
        self.metadata_file = self.voices_dir / "voices_metadata.json"
        self.metadata = self._load_metadata()
    
    def _load_metadata(self) -> dict:
        """Metadata dosyasını yükle"""
        if self.metadata_file.exists():
            with open(self.metadata_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {}
    
    def _save_metadata(self):
        """Metadata dosyasını kaydet"""
        with open(self.metadata_file, 'w', encoding='utf-8') as f:
            json.dump(self.metadata, f, indent=2, ensure_ascii=False)
    
    def add_voice(
        self,
        audio_path: str,
        name: str,
        description: str = "",
        gender: str = "unknown",
        language: str = "tr",
        tags: List[str] = None
    ) -> str:
        """
        Yeni ses ekle
        
        Args:
            audio_path: Ses dosyasının yolu
            name: Ses adı
            description: Açıklama
            gender: Cinsiyet (male/female/unknown)
            language: Dil kodu
            tags: Etiketler
            
        Returns:
            Voice ID
        """
        
        # Ses dosyasını kopyala
        audio_path = Path(audio_path)
        if not audio_path.exists():
            raise FileNotFoundError(f"Ses dosyası bulunamadı: {audio_path}")
        
        # Unique ID oluştur
        voice_id = hashlib.md5(
            f"{name}_{datetime.now().isoformat()}".encode()
        ).hexdigest()[:12]
        
        # Dosya adı
        new_filename = f"{voice_id}_{audio_path.name}"
        new_path = self.voices_dir / new_filename
        
        # Kopyala
        shutil.copy2(audio_path, new_path)
        
        # Metadata kaydet
        self.metadata[voice_id] = {
            'id': voice_id,
            'name': name,
            'description': description,
            'gender': gender,
            'language': language,
            'tags': tags or [],
            'file_path': str(new_path),
            'file_name': new_filename,
            'created_at': datetime.now().isoformat(),
            'updated_at': datetime.now().isoformat(),
            'usage_count': 0
        }
        
        self._save_metadata()
        
        print(f"✅ Ses eklendi: {name} (ID: {voice_id})")
        
        return voice_id
    
    def get_voice(self, voice_id: str) -> Optional[Dict]:
        """Ses bilgilerini getir"""
        return self.metadata.get(voice_id)
    
    def list_voices(
        self,
        gender: str = None,
        language: str = None,
        tags: List[str] = None
    ) -> List[Dict]:
        """
        Sesleri listele (filtreli)
        
        Args:
            gender: Cinsiyet filtresi
            language: Dil filtresi
            tags: Etiket filtresi
            
        Returns:
            Ses listesi
        """
        
        voices = list(self.metadata.values())
        
        # Filtrele
        if gender:
            voices = [v for v in voices if v['gender'] == gender]
        
        if language:
            voices = [v for v in voices if v['language'] == language]
        
        if tags:
            voices = [
                v for v in voices 
                if any(tag in v['tags'] for tag in tags)
            ]
        
        # Kullanım sayısına göre sırala
        voices.sort(key=lambda x: x['usage_count'], reverse=True)
        
        return voices
    
    def update_voice(self, voice_id: str, **kwargs):
        """Ses bilgilerini güncelle"""
        if voice_id not in self.metadata:
            raise ValueError(f"Ses bulunamadı: {voice_id}")
        
        # Güncellenebilir alanlar
        updatable = ['name', 'description', 'gender', 'language', 'tags']
        
        for key, value in kwargs.items():
            if key in updatable:
                self.metadata[voice_id][key] = value
        
        self.metadata[voice_id]['updated_at'] = datetime.now().isoformat()
        self._save_metadata()
        
        print(f"✅ Ses güncellendi: {voice_id}")
    
    def delete_voice(self, voice_id: str):
        """Ses sil"""
        if voice_id not in self.metadata:
            raise ValueError(f"Ses bulunamadı: {voice_id}")
        
        # Dosyayı sil
        file_path = Path(self.metadata[voice_id]['file_path'])
        if file_path.exists():
            file_path.unlink()
        
        # Metadata'dan sil
        del self.metadata[voice_id]
        self._save_metadata()
        
        print(f"🗑️  Ses silindi: {voice_id}")
    
    def increment_usage(self, voice_id: str):
        """Kullanım sayısını artır"""
        if voice_id in self.metadata:
            self.metadata[voice_id]['usage_count'] += 1
            self._save_metadata()
    
    def get_voice_path(self, voice_id: str) -> Optional[str]:
        """Ses dosyası yolunu getir"""
        voice = self.get_voice(voice_id)
        return voice['file_path'] if voice else None
    
    def print_voices(self):
        """Sesleri güzel formatla yazdır"""
        voices = self.list_voices()
        
        if not voices:
            print("\n📭 Henüz ses eklenmemiş")
            return
        
        print("\n" + "="*60)
        print("🎤 SES KÜTÜPHANESİ")
        print("="*60)
        
        for voice in voices:
            print(f"\n📌 {voice['name']}")
            print(f"   ID: {voice['id']}")
            print(f"   Cinsiyet: {voice['gender']}")
            print(f"   Dil: {voice['language']}")
            print(f"   Kullanım: {voice['usage_count']} kez")
            if voice['description']:
                print(f"   Açıklama: {voice['description']}")
            if voice['tags']:
                print(f"   Etiketler: {', '.join(voice['tags'])}")
            print(f"   Dosya: {voice['file_name']}")
        
        print("\n" + "="*60)


def demo_usage():
    """Örnek kullanım"""
    manager = VoiceManager()
    
    print("\n🎤 SES YÖNETİCİSİ - DEMO")
    print("="*60)
    
    # Kullanıcı seçenekleri
    print("\n1. Ses ekle")
    print("2. Sesleri listele")
    print("3. Ses sil")
    print("4. Çıkış")
    
    choice = input("\nSeçiminiz: ").strip()
    
    if choice == "1":
        # Ses ekle
        print("\n📁 Ses dosyası yolu:")
        audio_path = input("Yol: ").strip()
        
        print("📝 Ses adı:")
        name = input("Ad: ").strip()
        
        print("📄 Açıklama (opsiyonel):")
        description = input("Açıklama: ").strip()
        
        print("⚥ Cinsiyet (male/female/unknown):")
        gender = input("Cinsiyet: ").strip() or "unknown"
        
        print("🌍 Dil (varsayılan: tr):")
        language = input("Dil: ").strip() or "tr"
        
        print("🏷️  Etiketler (virgülle ayırın):")
        tags_input = input("Etiketler: ").strip()
        tags = [t.strip() for t in tags_input.split(",")] if tags_input else []
        
        try:
            voice_id = manager.add_voice(
                audio_path, name, description, gender, language, tags
            )
            print(f"\n✅ Ses başarıyla eklendi!")
            print(f"   ID: {voice_id}")
        except Exception as e:
            print(f"\n❌ Hata: {e}")
    
    elif choice == "2":
        # Sesleri listele
        manager.print_voices()
    
    elif choice == "3":
        # Ses sil
        manager.print_voices()
        print("\n🗑️  Silmek istediğiniz ses ID'si:")
        voice_id = input("ID: ").strip()
        
        try:
            manager.delete_voice(voice_id)
        except Exception as e:
            print(f"\n❌ Hata: {e}")
    
    print("\n" + "="*60)


if __name__ == "__main__":
    demo_usage()

