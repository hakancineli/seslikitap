"""
Sentence Processor - Akıllı cümle bölme ve tonlama analizi
"""
import re
from typing import List, Dict


class SentenceProcessor:
    def __init__(self):
        # Türkçe kısaltmalar (yanlış bölünmeyi engellemek için)
        self.abbreviations = [
            'Dr', 'Prof', 'vs', 'vb', 'örn', 'sayfa', 'no', 'ör',
            'Doç', 'Yrd', 'Yrd.Doç', 'Uz', 'Müh', 'Mim', 'Av',
            'Ltd', 'Şti', 'A.Ş', 'Ltd.Şti'
        ]
    
    def split_into_sentences(self, text: str) -> List[Dict]:
        """Metni anlamlı cümlelere böl ve analiz et"""
        
        # Önce paragraf bazında işle
        paragraphs = text.split('\n\n')
        all_sentences = []
        
        for para in paragraphs:
            if not para.strip():
                continue
            
            # Cümlelere böl
            sentences = self._split_paragraph_to_sentences(para)
            
            for sentence in sentences:
                if sentence.strip():
                    all_sentences.append({
                        'text': sentence.strip(),
                        'type': self.classify_sentence(sentence),
                        'length': len(sentence.split()),
                        'pause_after': self.calculate_pause(sentence)
                    })
        
        return all_sentences
    
    def _split_paragraph_to_sentences(self, paragraph: str) -> List[str]:
        """Paragrafı cümlelere böl"""
        # Noktalama işaretlerine göre böl
        pattern = r'([.!?…]+[\s]*)'
        parts = re.split(pattern, paragraph)
        
        sentences = []
        current = ""
        
        for i, part in enumerate(parts):
            current += part
            
            # Cümle sonu işareti mi?
            if re.match(pattern, part):
                # Kısaltma kontrolü
                if not self._is_abbreviation_end(current):
                    sentences.append(current.strip())
                    current = ""
        
        # Kalan metni ekle
        if current.strip():
            sentences.append(current.strip())
        
        return sentences
    
    def _is_abbreviation_end(self, text: str) -> bool:
        """Cümle sonu kısaltma mı?"""
        words = text.strip().split()
        if not words:
            return False
        
        last_word = words[-1].rstrip('.!?')
        
        # Tek harf veya kısaltma listesinde mi?
        if len(last_word) <= 2 or last_word in self.abbreviations:
            return True
        
        return False
    
    def classify_sentence(self, sentence: str) -> str:
        """Cümle tipini belirle"""
        sentence = sentence.strip()
        
        if sentence.endswith('?'):
            return 'question'
        elif sentence.endswith('!'):
            return 'exclamation'
        elif '"' in sentence or '"' in sentence or '"' in sentence:
            return 'dialogue'
        elif '—' in sentence or '–' in sentence:
            return 'dialogue'
        else:
            return 'statement'
    
    def calculate_pause(self, sentence: str) -> float:
        """Cümle sonrası duraklama süresi (saniye)"""
        sentence = sentence.rstrip()
        
        if sentence.endswith('...') or sentence.endswith('…'):
            return 0.8
        elif sentence.endswith('.'):
            return 0.5
        elif sentence.endswith('!'):
            return 0.6
        elif sentence.endswith('?'):
            return 0.6
        elif sentence.endswith(','):
            return 0.2
        elif sentence.endswith(';'):
            return 0.4
        elif sentence.endswith(':'):
            return 0.3
        else:
            return 0.3


def test_sentence_processor():
    """Test fonksiyonu"""
    test_text = """
    Merhaba! Bu bir test metnidir. Ses klonlama sistemi çalışıyor mu? 
    Evet, çok iyi çalışıyor... Dr. Ahmet'in söylediği gibi. 
    "Bu harika bir sistem," dedi Ayşe. İşte böyle!
    """
    
    processor = SentenceProcessor()
    sentences = processor.split_into_sentences(test_text)
    
    print(f"\n✅ {len(sentences)} cümle tespit edildi:\n")
    
    for i, sent in enumerate(sentences, 1):
        print(f"{i}. [{sent['type']}] {sent['text']}")
        print(f"   → Duraklama: {sent['pause_after']}s, Kelime: {sent['length']}\n")


if __name__ == "__main__":
    test_sentence_processor()

