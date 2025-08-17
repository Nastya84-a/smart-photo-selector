#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
АВТОМАТИЧЕСКИЙ АНАЛИЗ ВСЕХ ПАПОК
Анализирует все папки в директории fotos и создает структурированные результаты
"""

import os
import subprocess
import sys
from pathlib import Path

def get_all_folders():
    """Получает все папки для анализа"""
    fotos_dir = "fotos"
    if not os.path.exists(fotos_dir):
        print(f"❌ Директория '{fotos_dir}' не найдена!")
        return []
    
    folders = []
    for item in os.listdir(fotos_dir):
        item_path = os.path.join(fotos_dir, item)
        if os.path.isdir(item_path):
            # Проверяем наличие папки 'big'
            big_path = os.path.join(item_path, "big")
            if os.path.exists(big_path):
                folders.append(item)
    
    return sorted(folders, key=lambda x: int(x) if x.isdigit() else 0)

def analyze_folder(folder_number):
    """Анализирует конкретную папку"""
    folder_path = f"fotos/{folder_number}/big"
    
    print(f"\n{'='*60}")
    print(f"🔍 АНАЛИЗИРУЮ ПАПКУ {folder_number}")
    print(f"📁 Путь: {folder_path}")
    print(f"{'='*60}")
    
    try:
        # Запускаем анализ
        result = subprocess.run([
            sys.executable, "final_photo_selector.py", folder_path
        ], capture_output=True, text=True, encoding='utf-8')
        
        if result.returncode == 0:
            print("✅ Анализ завершен успешно!")
            
            # Показываем краткий результат
            output_lines = result.stdout.split('\n')
            for line in output_lines:
                if "Лучшие фотографии сохранены в:" in line:
                    print(f"📁 Результаты: {line}")
                    break
        else:
            print(f"❌ Ошибка при анализе: {result.stderr}")
            
    except Exception as e:
        print(f"❌ Ошибка: {e}")

def show_final_structure():
    """Показывает финальную структуру папок"""
    print(f"\n{'='*60}")
    print(f"📁 ФИНАЛЬНАЯ СТРУКТУРА РЕЗУЛЬТАТОВ")
    print(f"{'='*60}")
    
    # Показываем папки с номерами
    numbered_folders = [d for d in os.listdir('.') if d.startswith('selected_photos_')]
    numbered_folders.sort(key=lambda x: int(x.split('_')[-1]) if x.split('_')[-1].isdigit() else 0)
    
    if numbered_folders:
        print("📂 Папки с выбранными фотографиями:")
        for folder in numbered_folders:
            folder_num = folder.split('_')[-1]
            photo_count = len([f for f in os.listdir(folder) if f.lower().endswith(('.jpg', '.jpeg', '.png'))])
            print(f"   📁 {folder}/ - {photo_count} фото (папка {folder_num})")
    else:
        print("❌ Папки с результатами не найдены")
    
    # Показываем общую папку
    if os.path.exists("best_bag_photos_final"):
        total_files = len([f for f in os.listdir("best_bag_photos_final") if f.lower().endswith(('.jpg', '.jpeg', '.png'))])
        print(f"\n📂 Общая папка результатов:")
        print(f"   📁 best_bag_photos_final/ - {total_files} фото (все результаты)")

def main():
    """Главная функция"""
    print("🚀 АВТОМАТИЧЕСКИЙ АНАЛИЗ ВСЕХ ПАПОК")
    print("="*60)
    print("🎯 Цель: Проанализировать все папки в директории fotos")
    print("📁 Результат: Структурированные папки с выбранными фотографиями")
    print()
    
    # Получаем все папки для анализа
    folders = get_all_folders()
    
    if not folders:
        print("❌ Не найдено папок для анализа!")
        return
    
    print(f"🔍 Найдено {len(folders)} папок для анализа:")
    for folder in folders:
        print(f"   📁 Папка {folder}: fotos/{folder}/big/")
    
    print(f"\n⏳ Начинаю анализ...")
    
    # Анализируем каждую папку
    for folder in folders:
        analyze_folder(folder)
    
    # Показываем финальную структуру
    show_final_structure()
    
    print(f"\n🎉 АНАЛИЗ ВСЕХ ПАПОК ЗАВЕРШЕН!")
    print(f"📁 Результаты сохранены в структурированных папках")
    print(f"🏆 Каждая папка имеет свой номер для удобства")

if __name__ == "__main__":
    main()
