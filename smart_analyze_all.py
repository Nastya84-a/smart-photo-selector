#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
УМНЫЙ АНАЛИЗ ВСЕХ ПАПОК
Автоматически анализирует все папки в директории fotos
Использует умный селектор с автоматическими правилами
"""

import os
import sys
from smart_photo_selector import SmartPhotoSelector

def get_all_folders():
    """Получает все папки для анализа"""
    fotos_dir = "fotos"
    if not os.path.exists(fotos_dir):
        print(f"Директория '{fotos_dir}' не найдена!")
        return []
    
    folders = []
    for item in os.listdir(fotos_dir):
        item_path = os.path.join(fotos_dir, item)
        if os.path.isdir(item_path):
            # Проверяем наличие папки 'big'
            big_path = os.path.join(item_path, "big")
            if os.path.exists(big_path):
                folders.append(item)
    
    return sorted(folders, key=lambda x: int(x))

def analyze_folder(folder_number):
    """Анализирует одну папку"""
    print(f"\n{'='*60}")
    print(f"🧠 АНАЛИЗ ПАПКИ {folder_number}")
    print(f"{'='*60}")
    
    # Путь к папке big
    folder_path = f"fotos/{folder_number}/big"
    
    if not os.path.exists(folder_path):
        print(f"❌ Папка '{folder_path}' не найдена!")
        return False
    
    try:
        # Создаем умный селектор
        selector = SmartPhotoSelector()
        
        # Запускаем анализ
        best_photos = selector.select_best_photos(folder_path, 2)
        
        if best_photos:
            print(f"\n✅ Папка {folder_number} проанализирована успешно!")
            print(f"📁 Результаты сохранены в: smart_photos_results/folder_{folder_number}/")
            return True
        else:
            print(f"\n❌ Анализ папки {folder_number} не удался!")
            return False
            
    except Exception as e:
        print(f"❌ Ошибка при анализе папки {folder_number}: {e}")
        return False

def main():
    """Главная функция"""
    print("🧠 УМНЫЙ АНАЛИЗ ВСЕХ ПАПОК С АВТОМАТИЧЕСКИМИ ПРАВИЛАМИ")
    print("="*70)
    print("🤖 AI модель: ConvNeXt Large + умные правила")
    print("🎯 Автоматические правила: работает с любыми папками!")
    print("📁 Анализируем все папки в директории fotos")
    print("🏆 Каждая папка получает свою папку с результатами!")
    print()
    
    # Получаем все папки
    folders = get_all_folders()
    
    if not folders:
        print("❌ Папки для анализа не найдены!")
        print("Убедитесь, что существует директория 'fotos' с пронумерованными папками")
        return
    
    print(f"🔍 Найдено {len(folders)} папок для анализа:")
    for folder in folders:
        print(f"   📁 Папка {folder}: fotos/{folder}/big")
    print()
    
    # Анализируем каждую папку
    successful = 0
    failed = 0
    
    for folder in folders:
        if analyze_folder(folder):
            successful += 1
        else:
            failed += 1
    
    # Итоговый отчет
    print(f"\n{'='*70}")
    print("📊 ИТОГОВЫЙ ОТЧЕТ")
    print(f"{'='*70}")
    print(f"✅ Успешно проанализировано: {successful} папок")
    print(f"❌ Ошибок: {failed} папок")
    print(f"📁 Всего папок: {len(folders)}")
    
    if successful > 0:
        print(f"\n🎉 Результаты сохранены в общей папке:")
        print(f"   📁 smart_photos_results/ - общая папка результатов")
        for folder in folders:
            print(f"      📁 folder_{folder}/ - результаты папки {folder}")
        
        print(f"\n🧠 Автоматические правила работают идеально!")
        print("✅ Система готова к работе с новыми папками!")
    
    if failed > 0:
        print(f"\n⚠️ Обратите внимание на папки с ошибками")
        print("Проверьте наличие файлов и доступность")

if __name__ == "__main__":
    main()
