"""
Metin Temizleme - TTS için metin normalleştirme
"""
import unicodedata
import re


class TextCleaner:
    """Metni TTS için temizle ve normalize et"""
    
    @staticmethod
    def remove_diacritics(text: str) -> str:
        """
        Diacritics (aksanlar, özel işaretler) kaldır
        Örnek: ẕ → z, á → a, ñ → n
        
        ANCAK Türkçe karakterleri koru: ş, ğ, ü, ö, ç, ı
        """
        # Türkçe karakterleri geçici olarak koru
        turkish_chars = {
            'ş': '___TURKISH_S___',
            'Ş': '___TURKISH_S_UPPER___',
            'ğ': '___TURKISH_G___',
            'Ğ': '___TURKISH_G_UPPER___',
            'ü': '___TURKISH_U___',
            'Ü': '___TURKISH_U_UPPER___',
            'ö': '___TURKISH_O___',
            'Ö': '___TURKISH_O_UPPER___',
            'ç': '___TURKISH_C___',
            'Ç': '___TURKISH_C_UPPER___',
            'ı': '___TURKISH_I___',
            'İ': '___TURKISH_I_UPPER___',
        }
        
        # Türkçe karakterleri değiştir
        for char, placeholder in turkish_chars.items():
            text = text.replace(char, placeholder)
        
        # NFD decomposition - aksanları ayır
        text = unicodedata.normalize('NFD', text)
        
        # Combining characters'ları (aksanları) kaldır
        text = ''.join(char for char in text if unicodedata.category(char) != 'Mn')
        
        # NFC composition - tekrar birleştir
        text = unicodedata.normalize('NFC', text)
        
        # Türkçe karakterleri geri getir
        for char, placeholder in turkish_chars.items():
            text = text.replace(placeholder, char)
        
        return text
    
    @staticmethod
    def normalize_whitespace(text: str) -> str:
        """Boşlukları normalize et"""
        # Birden fazla boşluğu tek boşluğa çevir
        text = re.sub(r'\s+', ' ', text)
        # Başta ve sonda boşluk kaldır
        text = text.strip()
        return text
    
    @staticmethod
    def remove_special_characters(text: str) -> str:
        """
        TTS için sorunlu özel karakterleri kaldır
        Ama noktalama işaretlerini koru (. , ! ? : ; - ...)
        """
        # İzin verilen karakterler: harfler, sayılar, temel noktalama
        # Türkçe karakterler de dahil
        allowed_pattern = r'[^a-zA-ZşğüöçıİŞĞÜÖÇ0-9\s.,!?:;\-—–\'\"()\[\]…]'
        text = re.sub(allowed_pattern, '', text)
        return text
    
    @staticmethod
    def fix_common_issues(text: str) -> str:
        """Yaygın sorunları düzelt"""
        # Birden fazla nokta işaretini üç noktaya çevir
        text = re.sub(r'\.{4,}', '...', text)
        
        # Noktalama işaretlerinden önce boşluk kaldır
        text = re.sub(r'\s+([.,!?:;])', r'\1', text)
        
        # Noktalama işaretlerinden sonra boşluk ekle (yoksa)
        text = re.sub(r'([.,!?:;])([^\s])', r'\1 \2', text)
        
        return text
    
    @staticmethod
    def clean_text(text: str, verbose: bool = False) -> str:
        """
        Metni TTS için kapsamlı temizle
        
        Args:
            text: Ham metin
            verbose: Debug çıktısı göster
            
        Returns:
            Temizlenmiş metin
        """
        if verbose:
            print("\n" + "="*60)
            print("🧹 METİN TEMİZLEME")
            print("="*60)
            print(f"📝 Orijinal ({len(text)} karakter):")
            print(f"   {text[:200]}...")
        
        # 1. Diacritics (aksanlar) temizle
        text = TextCleaner.remove_diacritics(text)
        if verbose:
            print(f"\n✓ Aksanlar temizlendi")
        
        # 2. Özel karakterleri temizle
        text = TextCleaner.remove_special_characters(text)
        if verbose:
            print(f"✓ Özel karakterler kaldırıldı")
        
        # 3. Boşlukları normalize et
        text = TextCleaner.normalize_whitespace(text)
        if verbose:
            print(f"✓ Boşluklar normalize edildi")
        
        # 4. Yaygın sorunları düzelt
        text = TextCleaner.fix_common_issues(text)
        if verbose:
            print(f"✓ Yaygın sorunlar düzeltildi")
        
        if verbose:
            print(f"\n📝 Temizlenmiş ({len(text)} karakter):")
            print(f"   {text[:200]}...")
            print("="*60)
        
        return text


def test_cleaner():
    """Test fonksiyonu"""
    test_texts = [
        "Her insanın bir hikâyesi vardır",  # Normal
        "Bazı kelimeler ẕ harfi ile yazılmış",  # z̄ problemi
        "Çok    fazla       boşluk",  # Boşluk problemi
        "Türkçe karakterler: şğüöçıİ",  # Türkçe karakterler korunmalı
        "Özel@#$%karakterler&*() burada",  # Özel karakterler
    ]
    
    print("\n" + "="*60)
    print("🧪 METİN TEMİZLEME TESTİ")
    print("="*60)
    
    for i, text in enumerate(test_texts, 1):
        print(f"\n{i}. Test:")
        print(f"   Önce:  {text}")
        cleaned = TextCleaner.clean_text(text)
        print(f"   Sonra: {cleaned}")
    
    print("\n" + "="*60)


if __name__ == "__main__":
    test_cleaner()



