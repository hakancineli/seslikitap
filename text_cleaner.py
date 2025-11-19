"""
Metin Temizleme - TTS için metin normalleştirme
"""
import unicodedata
import re
from typing import Dict


class TurkishTextPreprocessor:
    """Türkçe TTS için özel metin ön işleme"""
    
    # Türkçe kısaltmalar
    TURKISH_ABBREVIATIONS: Dict[str, str] = {
        'vb.': 've benzeri',
        'vs.': 've saire',
        'vd.': 've diğerleri',
        'Prof.': 'Profesör',
        'Dr.': 'Doktor',
        'Yrd.': 'Yardımcı',
        'Doç.': 'Doçent',
        'Av.': 'Avukat',
        'Muh.': 'Muhendis',
        'Ltd.': 'Limited',
        'Şti.': 'Şirketi',
        'A.Ş.': 'Anonim Şirket',
        'Hz.': 'Hazretleri',
        'Ö.': 'Ölümü',
        'D.': 'Doğumu',
        'No.': 'Numara',
        'Sok.': 'Sokak',
        'Cad.': 'Cadde',
        'Apt.': 'Apartman',
        'Tel.': 'Telefon',
        'Fax.': 'Faks',
        'Kat.': 'Kat',
        'S.': 'Sayfa',
        'bkz.': 'bakınız',
        'krş.': 'karşılaştırınız',
        'örn.': 'örneğin',
        'yak.': 'yaklaşık'
    }
    
    # Sayılar için Türkçe kelimeler
    ONES = ['', 'bir', 'iki', 'üç', 'dört', 'beş', 'altı', 'yedi', 'sekiz', 'dokuz']
    TENS = ['', 'on', 'yirmi', 'otuz', 'kırk', 'elli', 'altmış', 'yetmiş', 'seksen', 'doksan']
    HUNDREDS = ['', 'yüz', 'ikiyüz', 'üçyüz', 'dörtyüz', 'beşyüz', 'altıyüz', 'yediyüz', 'sekizyüz', 'dokuzyüz']
    
    @classmethod
    def expand_abbreviations(cls, text: str) -> str:
        """Kısaltmaları aç"""
        for abbr, expansion in cls.TURKISH_ABBREVIATIONS.items():
            # Case-insensitive replacement
            text = re.sub(re.escape(abbr), expansion, text, flags=re.IGNORECASE)
        return text
    
    @classmethod
    def number_to_words(cls, num: int) -> str:
        """
        Sayıyı Türkçe kelimeye çevir (0-999)
        
        Örnekler:
            123 → 'yüz yirmi üç'
            45 → 'kırk beş'
            7 → 'yedi'
        """
        if num == 0:
            return 'sıfır'
        
        if num < 0:
            return 'eksi ' + cls.number_to_words(abs(num))
        
        if num >= 1000:
            # Büyük sayılar için basit strateji
            return str(num)  # Veya daha kompleks bir çözüm eklenebilir
        
        result = []
        
        # Yüzler
        hundreds = num // 100
        if hundreds > 0:
            if hundreds == 1:
                result.append('yüz')
            else:
                result.append(cls.HUNDREDS[hundreds])
        
        # Onlar
        tens = (num % 100) // 10
        if tens > 0:
            result.append(cls.TENS[tens])
        
        # Birler
        ones = num % 10
        if ones > 0:
            result.append(cls.ONES[ones])
        
        return ' '.join(result)
    
    @classmethod
    def convert_numbers_to_words(cls, text: str) -> str:
        """Metindeki sayıları kelimelere çevir"""
        def replace_number(match):
            num_str = match.group(0)
            try:
                num = int(num_str)
                if 0 <= num < 1000:
                    return cls.number_to_words(num)
                else:
                    return num_str  # Büyük sayıları olduğu gibi bırak
            except ValueError:
                return num_str
        
        # Sadece tek başına duran sayıları değiştir
        text = re.sub(r'\b\d+\b', replace_number, text)
        return text
    
    @classmethod
    def preprocess_for_tts(cls, text: str, convert_numbers: bool = True) -> str:
        """
        Türkçe metni TTS için ön işle
        
        Args:
            text: Ham metin
            convert_numbers: Sayıları kelimelere çevir
            
        Returns:
            İşlenmiş metin
        """
        # 1. Kısaltmaları aç
        text = cls.expand_abbreviations(text)
        
        # 2. Sayıları kelimelere çevir (isteğe bağlı)
        if convert_numbers:
            text = cls.convert_numbers_to_words(text)
        
        return text


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
    def clean_text(text: str, verbose: bool = False, turkish_preprocess: bool = True) -> str:
        """
        Metni TTS için kapsamlı temizle
        
        Args:
            text: Ham metin
            verbose: Debug çıktısı göster
            turkish_preprocess: Türkçe ön işleme uygula
            
        Returns:
            Temizlenmiş metin
        """
        if verbose:
            print("\n" + "="*60)
            print("🧹 METİN TEMİZLEME")
            print("="*60)
            print(f"📝 Orijinal ({len(text)} karakter):")
            print(f"   {text[:200]}...")
        
        # 0. Türkçe ön işleme (kısaltmalar, sayılar)
        if turkish_preprocess:
            text = TurkishTextPreprocessor.preprocess_for_tts(text)
            if verbose:
                print(f"\n✓ Türkçe ön işleme tamamlandı")
        
        # 1. Diacritics (aksanlar) temizle
        text = TextCleaner.remove_diacritics(text)
        if verbose:
            print(f"✓ Aksanlar temizlendi")
        
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
        "Prof. Dr. Ali 25 yaşında vb.",  # Kısaltmalar ve sayılar
        "No. 123 Sok. Apt. 5 Kat",  # Kısaltmalar ve sayılar
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
    
    # Türkçe ön işleme testi
    print("\n" + "="*60)
    print("🧪 TÜRKÇE ÖN İŞLEME TESTİ")
    print("="*60)
    
    turkish_tests = [
        ("Prof. Dr. Ali", "Profesör Doktor Ali"),
        ("No. 5 vb.", "Numara beş ve benzeri"),
        ("123", "yüz yirmi üç"),
        ("45 yıl", "kırk beş yıl"),
    ]
    
    for i, (input_text, expected) in enumerate(turkish_tests, 1):
        processed = TurkishTextPreprocessor.preprocess_for_tts(input_text)
        print(f"\n{i}. Test:")
        print(f"   Girdi:    {input_text}")
        print(f"   Çıktı:    {processed}")
        print(f"   Beklenen: {expected}")
        print(f"   ✓" if processed.lower() == expected.lower() else "   ✗")
    
    print("\n" + "="*60)


if __name__ == "__main__":
    test_cleaner()



