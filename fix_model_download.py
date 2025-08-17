#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ИСПРАВЛЕНИЕ СКАЧИВАНИЯ МОДЕЛИ ConvNeXt Large
Полностью перескачивает и сохраняет модель локально
"""

import os
import shutil
from transformers import pipeline, AutoModelForImageClassification, AutoImageProcessor
import json

class ModelFixer:
    """Исправляет скачивание модели"""
    
    def __init__(self):
        self.model_name = "facebook/convnext-large-224"
        self.local_path = "./models/convnext-large-224"
        self.backup_path = "./models/convnext-large-224-backup"
        
    def clean_directories(self):
        """Очищает старые папки"""
        print("🧹 Очищаю старые папки...")
        
        if os.path.exists(self.local_path):
            shutil.rmtree(self.local_path)
            print("   ✅ Удалена старая папка модели")
        
        if os.path.exists(self.backup_path):
            shutil.rmtree(self.backup_path)
            print("   ✅ Удалена старая резервная копия")
        
        # Создаем заново
        os.makedirs(self.local_path, exist_ok=True)
        print("   ✅ Создана новая папка для модели")
    
    def download_and_save_model(self):
        """Скачивает и сохраняет модель правильно"""
        print(f"\n🚀 Скачиваю модель: {self.model_name}")
        print("   ⏳ Это может занять несколько минут...")
        
        try:
            # Скачиваем модель напрямую
            print("   🔄 Скачиваю модель...")
            model = AutoModelForImageClassification.from_pretrained(self.model_name)
            
            # Скачиваем процессор напрямую
            print("   🔄 Скачиваю процессор...")
            processor = AutoImageProcessor.from_pretrained(self.model_name)
            
            print("   ✅ Модель и процессор получены!")
            
            # Сохраняем модель
            print("   💾 Сохраняю модель...")
            model.save_pretrained(self.local_path)
            
            # Сохраняем процессор
            print("   💾 Сохраняю процессор...")
            processor.save_pretrained(self.local_path)
            
            print("   ✅ Модель сохранена локально!")
            return True
            
        except Exception as e:
            print(f"   ❌ Ошибка при скачивании: {e}")
            return False
    
    def test_local_model(self):
        """Тестирует локальную модель"""
        print(f"\n🧪 Тестирую локальную модель...")
        
        try:
            # Создаем pipeline с локальной моделью
            local_pipeline = pipeline("image-classification", model=self.local_path)
            
            print("   ✅ Локальная модель работает!")
            print("   🎯 Модель готова к использованию!")
            return True
            
        except Exception as e:
            print(f"   ❌ Ошибка при тестировании: {e}")
            return False
    
    def create_model_info(self):
        """Создает информацию о модели"""
        print("\n📄 Создаю информацию о модели...")
        
        model_info = {
            "model_name": "ConvNeXt Large",
            "version": "224x224",
            "source": "facebook/convnext-large-224",
            "local_path": self.local_path,
            "description": "ConvNeXt Large модель для классификации изображений",
            "accuracy": "86.6%",
            "download_date": "2024",
            "usage": "Выбор лучших фотографий товара",
            "requirements": {
                "input_size": "224x224",
                "format": "RGB",
                "normalization": "ImageNet"
            },
            "status": "FULLY_DOWNLOADED"
        }
        
        info_path = os.path.join(self.local_path, "model_info.json")
        with open(info_path, 'w', encoding='utf-8') as f:
            json.dump(model_info, f, ensure_ascii=False, indent=2)
        
        print("   ✅ Информация о модели создана!")
    
    def create_backup(self):
        """Создает резервную копию модели"""
        print(f"\n💾 Создаю резервную копию...")
        
        try:
            shutil.copytree(self.local_path, self.backup_path)
            print("   ✅ Резервная копия создана!")
            return True
            
        except Exception as e:
            print(f"   ❌ Ошибка при создании резервной копии: {e}")
            return False
    
    def show_final_structure(self):
        """Показывает финальную структуру"""
        print(f"\n📁 ФИНАЛЬНАЯ СТРУКТУРА ПРОЕКТА:")
        print("="*50)
        
        if os.path.exists(self.local_path):
            total_size = 0
            file_count = 0
            
            for root, dirs, files in os.walk(self.local_path):
                for file in files:
                    file_path = os.path.join(root, file)
                    total_size += os.path.getsize(file_path)
                    file_count += 1
            
            size_mb = total_size / (1024 * 1024)
            size_gb = size_mb / 1024
            
            print(f"📊 Модель: {self.local_path}")
            print(f"📁 Файлов: {file_count}")
            print(f"💾 Размер: {size_mb:.1f} МБ ({size_gb:.2f} ГБ)")
            print(f"✅ Статус: ПОЛНОСТЬЮ ГОТОВА!")
        
        print(f"\n🎯 Теперь можете использовать модель БЕЗ интернета!")
    
    def run_fix(self):
        """Запускает исправление"""
        print("🔧 ИСПРАВЛЕНИЕ СКАЧИВАНИЯ МОДЕЛИ ConvNeXt Large")
        print("="*50)
        print("🎯 Цель: Полностью рабочая локальная модель")
        print("📁 Место: ./models/convnext-large-224")
        print()
        
        # Очищаем старые папки
        self.clean_directories()
        
        # Скачиваем и сохраняем модель
        if not self.download_and_save_model():
            print("❌ Скачивание не удалось!")
            return False
        
        # Создаем информацию о модели
        self.create_model_info()
        
        # Тестируем модель
        if not self.test_local_model():
            print("❌ Тестирование не удалось!")
            return False
        
        # Создаем резервную копию
        self.create_backup()
        
        # Показываем результат
        self.show_final_structure()
        
        print(f"\n🎉 ИСПРАВЛЕНИЕ ЗАВЕРШЕНО УСПЕШНО!")
        print(f"🏆 Теперь у вас есть ПОЛНОСТЬЮ РАБОЧАЯ локальная модель!")
        
        return True

def main():
    """Главная функция"""
    fixer = ModelFixer()
    success = fixer.run_fix()
    
    if success:
        print(f"\n🚀 Модель исправлена и готова к использованию!")
        print(f"📝 Теперь можете запустить: python final_photo_selector.py")
    else:
        print(f"\n❌ Исправление не удалось!")

if __name__ == "__main__":
    main()
