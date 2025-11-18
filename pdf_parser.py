"""
PDF Parser - PDF'den yapılandırılmış metin çıkarma
"""
import pymupdf
from typing import List, Dict
import re


class PDFParser:
    def __init__(self, pdf_path: str):
        self.pdf_path = pdf_path
    
    def extract_text_with_structure(self) -> Dict:
        """PDF'den yapılandırılmış metin çıkar"""
        doc = pymupdf.open(self.pdf_path)
        
        structured_content = []
        full_text = ""
        
        print(f"📖 PDF okunuyor: {self.pdf_path}")
        
        for page_num, page in enumerate(doc, 1):
            text = page.get_text()
            
            # Sayfa numaralarını ve gereksiz boşlukları temizle
            text = self.clean_text(text)
            
            if text.strip():
                structured_content.append({
                    'page': page_num,
                    'text': text,
                    'paragraphs': self.split_into_paragraphs(text)
                })
                full_text += text + "\n\n"
        
        doc.close()
        
        word_count = len(full_text.split())
        
        return {
            'structured': structured_content,
            'full_text': full_text,
            'total_pages': len(structured_content),
            'word_count': word_count,
            'estimated_duration_minutes': word_count / 150  # Ortalama okuma hızı
        }
    
    def clean_text(self, text: str) -> str:
        """Metni temizle"""
        # Çoklu boşlukları düzelt
        text = re.sub(r' +', ' ', text)
        
        # Çoklu satır sonlarını düzelt
        text = re.sub(r'\n\s*\n\s*\n+', '\n\n', text)
        
        # Tire ile bölünmüş kelimeleri birleştir
        text = re.sub(r'(\w+)-\n(\w+)', r'\1\2', text)
        
        return text.strip()
    
    def split_into_paragraphs(self, text: str) -> List[str]:
        """Metni paragraflara ayır"""
        paragraphs = text.split('\n\n')
        return [p.strip() for p in paragraphs if p.strip()]


def test_pdf_parser():
    """Test fonksiyonu"""
    import sys
    
    if len(sys.argv) < 2:
        print("Kullanım: python pdf_parser.py <pdf_dosyası>")
        sys.exit(1)
    
    parser = PDFParser(sys.argv[1])
    content = parser.extract_text_with_structure()
    
    print(f"\n✅ Analiz Tamamlandı:")
    print(f"   📄 Toplam sayfa: {content['total_pages']}")
    print(f"   📝 Toplam kelime: {content['word_count']}")
    print(f"   ⏱️  Tahmini süre: {content['estimated_duration_minutes']:.1f} dakika")
    print(f"\nİlk 200 karakter:")
    print(content['full_text'][:200])


if __name__ == "__main__":
    test_pdf_parser()

