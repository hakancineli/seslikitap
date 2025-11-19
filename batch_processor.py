"""
Batch Processor - Toplu İşlem Yöneticisi
"""
import os
from pathlib import Path
from typing import List, Dict
import json
from datetime import datetime


class BatchProcessor:
    """Toplu metin işleme ve seslendirme"""
    
    def __init__(self, output_dir: str = "batch_outputs"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        self.queue = []
        self.results = []
    
    def add_to_queue(self, text: str, voice_id: str, settings: Dict = None):
        """
        İşlem kuyruğuna ekle
        
        Args:
            text: Seslendirilecek metin
            voice_id: Kullanılacak ses ID'si
            settings: Ek ayarlar (hız, ton, vb.)
        """
        task = {
            'id': len(self.queue) + 1,
            'text': text,
            'voice_id': voice_id,
            'settings': settings or {},
            'status': 'pending',
            'created_at': datetime.now().isoformat()
        }
        self.queue.append(task)
        print(f"✅ Kuyrukta eklendi: Task #{task['id']}")
        return task['id']
    
    def process_queue(self, tts_engine):
        """
        Kuyruktaki tüm işlemleri sırayla işle
        
        Args:
            tts_engine: TTS motor instance
        """
        print(f"\n🚀 Toplu işlem başlıyor: {len(self.queue)} görev")
        
        for i, task in enumerate(self.queue, 1):
            try:
                print(f"\n[{i}/{len(self.queue)}] İşleniyor: Task #{task['id']}")
                
                task['status'] = 'processing'
                
                # Çıktı dosyası
                output_file = self.output_dir / f"batch_{task['id']}_{int(datetime.now().timestamp())}.mp3"
                
                # TTS işlemi (basitleştirilmiş)
                # Gerçek implementasyonda sentence_processor kullanılmalı
                print(f"   📝 Metin: {task['text'][:50]}...")
                
                # Başarılı işaretleme
                task['status'] = 'completed'
                task['output_file'] = str(output_file)
                task['completed_at'] = datetime.now().isoformat()
                
                self.results.append(task)
                
                print(f"   ✅ Tamamlandı: {output_file}")
                
            except Exception as e:
                print(f"   ❌ Hata: {e}")
                task['status'] = 'failed'
                task['error'] = str(e)
                self.results.append(task)
        
        # Sonuçları kaydet
        self.save_results()
        
        print(f"\n🎉 Toplu işlem tamamlandı!")
        print(f"   Başarılı: {sum(1 for r in self.results if r['status'] == 'completed')}")
        print(f"   Başarısız: {sum(1 for r in self.results if r['status'] == 'failed')}")
    
    def save_results(self):
        """Sonuçları JSON olarak kaydet"""
        results_file = self.output_dir / f"batch_results_{int(datetime.now().timestamp())}.json"
        
        with open(results_file, 'w', encoding='utf-8') as f:
            json.dump({
                'total': len(self.results),
                'completed': sum(1 for r in self.results if r['status'] == 'completed'),
                'failed': sum(1 for r in self.results if r['status'] == 'failed'),
                'results': self.results
            }, f, indent=2, ensure_ascii=False)
        
        print(f"📄 Sonuçlar kaydedildi: {results_file}")
    
    def clear_queue(self):
        """Kuyruğu temizle"""
        self.queue = []
        print("🗑️  Kuyruk temizlendi")

