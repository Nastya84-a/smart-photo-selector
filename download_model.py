#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
СКАЧИВАНИЕ МОДЕЛИ ConvNeXt Large ПОЛНОСТЬЮ ЛОКАЛЬНО
Скачивает модель в папку models/ проекта для автономной работы
"""

import os
import shutil
from transformers import ConvNextForImageClassification, ConvNextImageProcessor, pipeline
from transformers import AutoFeatureExtractor
import json

class ModelDownloader:
    """Скачивает модель ConvNeXt Large локально"""
    
    def __init__(self):
        self.model_name = "facebook/convnext-large-224"
        self.local_path = "./models/convnext-large-224"
        self.backup_path = "./models/convnext-large-224-backup"
        
    def create_directories(self):
        """Создает необходимые папки"""
        print("📁 Создаю папки для модели...")
        
        if not os.path.exists("./models"):
            os.makedirs("./models")
            print("   ✅ Создана папка: ./models")
        
        if not os.path.exists(self.local_path):
            os.makedirs(self.local_path)
            print("   ✅ Создана папка: ./models/convnext-large-224")
        
        print("   📁 Структура папок готова!")
    
    def download_model(self):
        """Скачивает модель и процессор"""
        print(f"\n🚀 Скачиваю модель: {self.model_name}")
        print("   ⏳ Это может занять несколько минут...")
        print("   📊 Размер модели: ~1.7 ГБ")
        
        try:
            # Скачиваем модель
            print("   🔄 Скачиваю модель...")
            model = ConvNextForImageClassification.from_pretrained(self.model_name)
            
            # Скачиваем процессор
            print("   🔄 Скачиваю процессор...")
            processor = ConvNextImageProcessor.from_pretrained(self.model_name)
            
            # Скачиваем feature extractor (если нужен)
            print("   🔄 Скачиваю feature extractor...")
            feature_extractor = AutoFeatureExtractor.from_pretrained(self.model_name)
            
            print("   ✅ Все компоненты скачаны успешно!")
            return model, processor, feature_extractor
            
        except Exception as e:
            print(f"   ❌ Ошибка при скачивании: {e}")
            return None, None, None
    
    def save_model_locally(self, model, processor, feature_extractor):
        """Сохраняет модель локально"""
        print(f"\n💾 Сохраняю модель в: {self.local_path}")
        
        try:
            # Сохраняем модель
            print("   💾 Сохраняю модель...")
            model.save_pretrained(self.local_path)
            
            # Сохраняем процессор
            print("   💾 Сохраняю процессор...")
            processor.save_pretrained(self.local_path)
            
            # Сохраняем feature extractor
            print("   💾 Сохраняю feature extractor...")
            feature_extractor.save_pretrained(self.local_path)
            
            print("   ✅ Модель сохранена локально!")
            return True
            
        except Exception as e:
            print(f"   ❌ Ошибка при сохранении: {e}")
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
            }
        }
        
        info_path = os.path.join(self.local_path, "model_info.json")
        with open(info_path, 'w', encoding='utf-8') as f:
            json.dump(model_info, f, ensure_ascii=False, indent=2)
        
        print("   ✅ Информация о модели создана!")
    
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
    
    def create_backup(self):
        """Создает резервную копию модели"""
        print(f"\n💾 Создаю резервную копию...")
        
        try:
            if os.path.exists(self.backup_path):
                shutil.rmtree(self.backup_path)
            
            shutil.copytree(self.local_path, self.backup_path)
            print("   ✅ Резервная копия создана!")
            return True
            
        except Exception as e:
            print(f"   ❌ Ошибка при создании резервной копии: {e}")
            return False
    
    def update_scripts(self):
        """Обновляет скрипты для использования локальной модели"""
        print(f"\n📝 Обновляю скрипты...")
        
        try:
            # Обновляем final_photo_selector.py
            self.update_script("final_photo_selector.py")
            
            # Обновляем batch_photo_selector.py
            self.update_script("batch_photo_selector.py")
            
            print("   ✅ Скрипты обновлены!")
            return True
            
        except Exception as e:
            print(f"   ❌ Ошибка при обновлении скриптов: {e}")
            return False
    
    def update_script(self, script_name):
        """Обновляет конкретный скрипт"""
        if not os.path.exists(script_name):
            print(f"   ⚠️ Скрипт {script_name} не найден, пропускаю")
            return
        
        print(f"   📝 Обновляю {script_name}...")
        
        # Читаем файл
        with open(script_name, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Заменяем ссылку на модель
        old_model = "facebook/convnext-large-224"
        new_model = "./models/convnext-large-224"
        
        if old_model in content:
            content = content.replace(old_model, new_model)
            
            # Записываем обновленный файл
            with open(script_name, 'w', encoding='utf-8') as f:
                f.write(content)
            
            print(f"      ✅ {script_name} обновлен!")
        else:
            print(f"      ⚠️ Ссылка на модель в {script_name} не найдена")
    
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
            print(f"✅ Статус: ГОТОВА К ИСПОЛЬЗОВАНИЮ!")
        
        print(f"\n🎯 Теперь можете использовать модель БЕЗ интернета!")
        print(f"📝 Скрипты обновлены для работы с локальной моделью")
    
    def run_download(self):
        """Запускает полный процесс скачивания"""
        print("🏆 СКАЧИВАНИЕ МОДЕЛИ ConvNeXt Large")
        print("="*50)
        print("🎯 Цель: Полностью локальная модель")
        print("📁 Место: ./models/convnext-large-224")
        print("💾 Размер: ~1.7 ГБ")
        print()
        
        # Создаем папки
        self.create_directories()
        
        # Скачиваем модель
        model, processor, feature_extractor = self.download_model()
        if not model:
            print("❌ Скачивание не удалось!")
            return False
        
        # Сохраняем локально
        if not self.save_model_locally(model, processor, feature_extractor):
            print("❌ Сохранение не удалось!")
            return False
        
        # Создаем информацию о модели
        self.create_model_info()
        
        # Тестируем модель
        if not self.test_local_model():
            print("❌ Тестирование не удалось!")
            return False
        
        # Создаем резервную копию
        self.create_backup()
        
        # Обновляем скрипты
        if not self.update_scripts():
            print("⚠️ Обновление скриптов не удалось!")
        
        # Показываем результат
        self.show_final_structure()
        
        print(f"\n🎉 СКАЧИВАНИЕ ЗАВЕРШЕНО УСПЕШНО!")
        print(f"🏆 Теперь у вас есть ПОЛНОСТЬЮ ЛОКАЛЬНАЯ AI модель!")
        
        return True

def main():
    """Главная функция"""
    downloader = ModelDownloader()
    success = downloader.run_download()
    
    if success:
        print(f"\n🚀 Модель готова к использованию!")
        print(f"📝 Запустите: python final_photo_selector.py")
    else:
        print(f"\n❌ Скачивание не удалось!")

if __name__ == "__main__":
    main()
