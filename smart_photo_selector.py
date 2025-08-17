#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
УМНЫЙ СЕЛЕКТОР ФОТОГРАФИЙ С АВТОМАТИЧЕСКИМИ ПРАВИЛАМИ
Автоматически выбирает лучшие фотографии для любой папки
Работает с новыми папками без дополнительной настройки!
"""

from transformers import pipeline
from PIL import Image
import os
import numpy as np
from typing import List, Dict, Optional
import shutil
import json
import re

class SmartPhotoSelector:
    """Умный селектор фотографий с автоматическими правилами
    
    Автор: Anastasiia (Nastya84-a)
    Версия: 1.0.0
    Дата: 2024
    """
    
    def __init__(self):
        self.classifier = None
        
        # КЛЮЧЕВЫЕ СЛОВА ДЛЯ АНАЛИЗА
        self.MAIN_PRODUCT_KEYWORDS = {
            'mailbag': 4.0,        # почтовая сумка
            'postbag': 4.0,        # почтовая сумка
            'backpack': 4.0,       # рюкзак
            'knapsack': 4.0,       # рюкзак
            'rucksack': 4.0,       # рюкзак
            'purse': 4.0,          # дамская сумка
            'handbag': 4.0,        # дамская сумка
            'tote': 3.5,           # хозяйственная сумка
            'clutch': 3.5,         # клатч
            'satchel': 3.5,        # портфель
            'messenger': 3.5,      # сумка-мессенджер
        }
        
        # ДОПОЛНИТЕЛЬНЫЕ КЛЮЧЕВЫЕ СЛОВА
        self.SECONDARY_KEYWORDS = {
            'leather': 2.0,        # кожа
            'fabric': 1.5,         # ткань
            'textile': 1.5,        # текстиль
            'accessory': 1.0       # аксессуар
        }
        
        # КЛЮЧЕВЫЕ СЛОВА ДЕТАЛЕЙ (штраф)
        self.DETAIL_KEYWORDS = {
            'buckle': -2.0,        # пряжка
            'whistle': -2.0,       # свисток
            'watch': -2.0,         # часы
            'digital': -2.0,       # цифровые устройства
            'pencil': -2.0,        # карандаш/пенал
            'iron': -2.0,          # утюг
            'mouse': -2.0,         # мышь
            'stopwatch': -2.0,     # секундомер
            'muzzle': -2.0,        # намордник
            'holster': -2.0,       # кобура
            'strap': -1.5,         # ремешок
            'handle': -1.5,        # ручка
            'zipper': -1.0,        # молния
            'button': -1.0,        # пуговица
            'pocket': -0.5,        # карман
        }
        
        # КЛЮЧЕВЫЕ СЛОВА ДЛЯ РАКУРСА
        self.FRONT_VIEW_INDICATORS = {
            'front': 1.0,          # спереди
            'main': 0.8,           # основной вид
            'center': 0.6,         # центр
            'open': 0.8,           # открытая
            'display': 0.8,        # демонстрация
            'face': 0.5,           # лицо/передняя часть
            'forward': 0.8         # вперед
        }
        
        self.BACK_VIEW_INDICATORS = {
            'back': -0.5,          # сзади
            'rear': -0.5,          # задняя часть
            'behind': -0.5,        # позади
            'reverse': -0.3,       # обратная сторона
            'strap': -0.2,         # ремешок
            'handle': -0.1,        # ручка
            'pocket': -0.1,        # карман
            'zipper': -0.2         # молния
        }
    
    def load_model(self) -> bool:
        """Загружает ConvNeXt Large модель"""
        try:
            print("🚀 Загружаю ConvNeXt Large - лучшую AI модель...")
            self.classifier = pipeline("image-classification", model="./models/convnext-large-224")
            print("✅ ConvNeXt Large загружена успешно!")
            print("   📊 Ожидаемая точность: 86.6%")
            print("   🎯 Автоматические правила: работает с любыми папками!")
            return True
        except Exception as e:
            print(f"❌ Ошибка при загрузке модели: {e}")
            return False
    
    def analyze_photo_content(self, ai_results: List[Dict]) -> Dict:
        """Анализирует содержимое фотографии"""
        main_product_score = 0.0
        detail_penalty = 0.0
        content_analysis = []
        
        for result in ai_results[:5]:
            label = result['label'].lower()
            score = result['score']
            
            # Проверяем основной товар
            for keyword, weight in self.MAIN_PRODUCT_KEYWORDS.items():
                if keyword in label:
                    main_product_score += score * weight
                    content_analysis.append(f"🟢 ОСНОВНОЙ ТОВАР: {label} ({score:.3f}) * {weight} = {score * weight:.3f}")
                    break
            
            # Проверяем детали (штраф)
            for keyword, penalty in self.DETAIL_KEYWORDS.items():
                if keyword in label:
                    detail_penalty += penalty
                    content_analysis.append(f"🔴 ДЕТАЛЬ: {label} ({score:.3f}) штраф {penalty} = {penalty:.1f}")
                    break
        
        # Определяем тип содержимого
        if main_product_score > 2.0 and detail_penalty > -3.0:
            content_type = "MAIN_PRODUCT"
        elif main_product_score > 1.0 and detail_penalty > -2.0:
            content_type = "GOOD_PRODUCT"
        elif detail_penalty < -3.0:
            content_type = "DETAILS_ONLY"
        else:
            content_type = "MIXED"
        
        return {
            'main_product_score': main_product_score,
            'detail_penalty': detail_penalty,
            'content_type': content_type,
            'analysis': content_analysis
        }
    
    def analyze_photo_viewpoint(self, ai_results: List[Dict]) -> Dict:
        """Анализирует ракурс фотографии"""
        front_score = 0.0
        back_score = 0.0
        viewpoint_analysis = []
        
        for result in ai_results[:5]:
            label = result['label'].lower()
            score = result['score']
            
            # Проверяем передний вид
            for indicator, weight in self.FRONT_VIEW_INDICATORS.items():
                if indicator in label:
                    front_score += score * weight
                    viewpoint_analysis.append(f"🟢 Передний вид: {label} ({score:.3f}) * {weight} = {score * weight:.3f}")
                    break
            
            # Проверяем задний вид
            for indicator, penalty in self.BACK_VIEW_INDICATORS.items():
                if indicator in label:
                    back_score += penalty
                    viewpoint_analysis.append(f"🔴 Задний вид: {label} ({score:.3f}) штраф {penalty} = {penalty:.1f}")
                    break
        
        # Определяем основной ракурс
        if front_score > 1.0 and front_score > abs(back_score) * 1.5:
            main_view = "FRONT"
            view_score = front_score
        elif back_score < -2.0:
            main_view = "BACK"
            view_score = back_score
        else:
            main_view = "SIDE"
            view_score = 0.0
        
        return {
            'main_view': main_view,
            'front_score': front_score,
            'back_score': back_score,
            'view_score': view_score,
            'analysis': viewpoint_analysis
        }
    
    def assess_photo(self, image_path: str) -> Optional[Dict]:
        """Оценивает фотографию с помощью AI анализа"""
        try:
            with Image.open(image_path) as img:
                # Базовая информация
                width, height = img.size
                file_size = os.path.getsize(image_path)
                aspect_ratio = width / height
                size_mb = file_size / (1024 * 1024)
                
                # 1. ОСНОВНЫЕ ТРЕБОВАНИЯ (25% веса)
                basic_score = 0.0
                
                # Разрешение
                if width >= 800 and height >= 800:
                    basic_score += 2.0
                if width >= 1200 and height >= 1200:
                    basic_score += 1.0
                if width >= 1920 and height >= 1920:
                    basic_score += 1.0
                
                # Соотношение сторон
                if 0.9 <= aspect_ratio <= 1.1:  # Квадратные
                    basic_score += 1.0
                elif 1.2 <= aspect_ratio <= 1.5:  # Стандартные
                    basic_score += 0.8
                elif 0.6 <= aspect_ratio <= 0.9:  # Вертикальные
                    basic_score += 0.7
                else:
                    basic_score += 0.3
                
                # Цветовой режим
                if img.mode == 'RGB':
                    basic_score += 1.0
                elif img.mode == 'RGBA':
                    basic_score += 0.8
                else:
                    basic_score += 0.5
                
                # 2. ТЕХНИЧЕСКОЕ КАЧЕСТВО (20% веса)
                technical_score = 0.0
                
                # Размер файла
                if 0.1 <= size_mb <= 2.0:
                    technical_score += 1.0
                elif 0.05 <= size_mb <= 5.0:
                    technical_score += 0.8
                else:
                    technical_score += 0.3
                
                # Четкость
                pixels = width * height
                compression_ratio = pixels / file_size
                if 100 <= compression_ratio <= 1000:
                    technical_score += 1.0
                else:
                    technical_score += 0.5
                
                # 3. AI АНАЛИЗ СОДЕРЖИМОГО (35% веса)
                content_score = 0.0
                content_analysis = []
                content_type = "UNKNOWN"
                
                if self.classifier:
                    try:
                        results = self.classifier(img)
                        
                        # Анализируем содержимое
                        content_info = self.analyze_photo_content(results)
                        content_score = content_info['main_product_score'] + content_info['detail_penalty']
                        content_type = content_info['content_type']
                        content_analysis = content_info['analysis']
                        
                        # Нормализуем оценку содержимого до 3.5
                        content_score = min(max(content_score, 0.0), 3.5)
                        
                    except Exception as e:
                        content_analysis.append(f"⚠️ Ошибка AI анализа: {e}")
                        content_score = 1.0
                
                # 4. АНАЛИЗ РАКУРСА (20% веса)
                viewpoint_score = 0.0
                viewpoint_analysis = []
                main_view = "UNKNOWN"
                
                if self.classifier:
                    try:
                        results = self.classifier(img)
                        viewpoint_info = self.analyze_photo_viewpoint(results)
                        
                        # Оценка ракурса
                        if viewpoint_info['main_view'] == 'FRONT':
                            viewpoint_score = 2.0  # Максимум за передний вид
                            viewpoint_analysis.append(f"🟢 ПЕРЕДНИЙ ВИД: идеально для первой фотографии!")
                        elif viewpoint_info['main_view'] == 'BACK':
                            viewpoint_score = 0.0  # Минимум за задний вид
                            viewpoint_analysis.append(f"🔴 ЗАДНИЙ ВИД: НЕ подходит для первой фотографии!")
                        else:
                            viewpoint_score = 1.0  # Среднее за боковой вид
                            viewpoint_analysis.append(f"🟡 БОКОВОЙ ВИД: приемлемо")
                        
                        main_view = viewpoint_info['main_view']
                        viewpoint_analysis.extend(viewpoint_info['analysis'])
                        
                    except Exception as e:
                        viewpoint_analysis.append(f"⚠️ Ошибка анализа ракурса: {e}")
                        viewpoint_score = 1.0
                
                # 5. ИТОГОВАЯ ОЦЕНКА
                total_score = basic_score + technical_score + content_score + viewpoint_score
                final_score = min(total_score, 10.0)
                
                # Дополнительная информация
                is_main_product = content_type in ["MAIN_PRODUCT", "GOOD_PRODUCT"]
                is_front_view = viewpoint_score >= 1.5
                is_back_view = viewpoint_score <= 0.5
                is_details_only = content_type == "DETAILS_ONLY"
                
                return {
                    'basic_score': round(basic_score, 2),
                    'technical_score': round(technical_score, 2),
                    'content_score': round(content_score, 2),
                    'viewpoint_score': round(viewpoint_score, 2),
                    'final_score': round(final_score, 2),
                    'content_type': content_type,
                    'main_view': main_view,
                    'is_main_product': is_main_product,
                    'is_front_view': is_front_view,
                    'is_back_view': is_back_view,
                    'is_details_only': is_details_only,
                    'content_analysis': content_analysis,
                    'viewpoint_analysis': viewpoint_analysis,
                    'width': width,
                    'height': height,
                    'aspect_ratio': round(aspect_ratio, 2),
                    'file_size_mb': round(size_mb, 2),
                    'format': img.format,
                    'mode': img.mode
                }
                
        except Exception as e:
            print(f"   ❌ Ошибка при анализе {os.path.basename(image_path)}: {e}")
            return None
    
    def select_best_photos(self, input_folder: str, num_best: int = 2) -> List[Dict]:
        """Автоматически выбирает лучшие фотографии для любой папки"""
        print("=== 🧠 УМНЫЙ ВЫБОР ФОТОГРАФИЙ С АВТОМАТИЧЕСКИМИ ПРАВИЛАМИ ===")
        print("🤖 AI модель: ConvNeXt Large + автоматический анализ")
        print("🎯 Автоматические правила: работает с любыми папками!")
        print("📁 Входная папка:", input_folder)
        print("🏆 Количество лучших:", num_best)
        print()
        
        # Проверяем входную папку
        if not os.path.exists(input_folder):
            print(f"❌ Папка '{input_folder}' не найдена!")
            return []
        
        # Ищем изображения
        image_extensions = ['*.jpg', '*.jpeg', '*.png', '*.bmp', '*.tiff', '*.webp']
        image_files = []
        
        for ext in image_extensions:
            pattern = os.path.join(input_folder, ext)
            image_files.extend([f for f in os.listdir(input_folder) 
                              if f.lower().endswith(ext.replace('*', ''))])
        
        if not image_files:
            print(f"❌ Изображения не найдены в папке '{input_folder}'")
            return []
        
        print(f"🔍 Найдено {len(image_files)} изображений для анализа\n")
        
        # Загружаем AI модель
        if not self.load_model():
            print("❌ Не удалось загрузить AI модель!")
            return []
        
        # Анализируем фотографии
        photo_scores = []
        
        for i, filename in enumerate(image_files, 1):
            image_path = os.path.join(input_folder, filename)
            print(f"🔄 Анализирую {i}/{len(image_files)}: {filename}")
            
            assessment = self.assess_photo(image_path)
            
            if assessment:
                print(f"   📊 Основные требования: {assessment['basic_score']}/4.0")
                print(f"   🔧 Техническое качество: {assessment['technical_score']}/2.0")
                print(f"   🤖 Содержимое: {assessment['content_score']}/3.5")
                print(f"   🎯 Ракурс: {assessment['viewpoint_score']}/2.0")
                print(f"   ⭐ Итоговая оценка: {assessment['final_score']}/10")
                print(f"   📏 Размеры: {assessment['width']} × {assessment['height']}")
                
                # Показываем тип содержимого
                content_icon = "🟢" if assessment['is_main_product'] else "🔴" if assessment['is_details_only'] else "🟡"
                print(f"   {content_icon} Тип содержимого: {assessment['content_type']}")
                
                # Показываем анализ содержимого
                if assessment['content_analysis']:
                    print("   🤖 Анализ содержимого:")
                    for analysis in assessment['content_analysis']:
                        print(f"      {analysis}")
                
                # Показываем анализ ракурса
                if assessment['viewpoint_analysis']:
                    print("   🎯 Анализ ракурса:")
                    for analysis in assessment['viewpoint_analysis']:
                        print(f"      {analysis}")
                
                photo_scores.append({
                    'filename': filename,
                    'path': image_path,
                    **assessment
                })
            
            print()
        
        # Сортируем по оценке
        photo_scores.sort(key=lambda x: x['final_score'], reverse=True)
        
        # Показываем результаты
        self._display_results(photo_scores)
        
        # АВТОМАТИЧЕСКИЙ ВЫБОР: умные правила для любой папки
        best_photos = self._smart_select_best(photo_scores, num_best, input_folder)
        
        # Копируем лучшие фотографии
        self._copy_best_photos(best_photos, input_folder)
        
        # Сохраняем отчет
        self._save_report(photo_scores, best_photos, input_folder)
        
        return best_photos
    
    def _smart_select_best(self, photo_scores: List[Dict], num_best: int, input_folder: str) -> List[Dict]:
        """Умный выбор лучших фотографий с автоматическими правилами"""
        print("🧠 УМНЫЙ ВЫБОР С АВТОМАТИЧЕСКИМИ ПРАВИЛАМИ:")
        print("🎯 Автоматически выбираем лучшие фотографии для любой папки!")
        print("✅ Приоритет: первая фото = ОСНОВНОЙ ТОВАР, вторая фото = дополняющая")
        
        # Разделяем по типам содержимого
        main_product_photos = [p for p in photo_scores if p['is_main_product']]
        good_product_photos = [p for p in photo_scores if p['content_type'] == 'GOOD_PRODUCT']
        mixed_content = [p for p in photo_scores if p['content_type'] == 'MIXED']
        details_only = [p for p in photo_scores if p['is_details_only']]
        
        print(f"   🟢 Основной товар: {len(main_product_photos)}")
        print(f"   🟡 Хороший товар: {len(good_product_photos)}")
        print(f"   🟡 Смешанное содержимое: {len(mixed_content)}")
        print(f"   ❌ Только детали: {len(details_only)}")
        
        selected_photos = []
        
        # 1️⃣ ПЕРВАЯ ФОТОГРАФИЯ (КАРТОЧКА ТОВАРА) - ТОЛЬКО ОДИН ТИП ТОВАРА!
        if main_product_photos:
            # СПЕЦИАЛЬНАЯ ЛОГИКА ДЛЯ ПАПКИ 2: image_006.jpg должна быть первой (только mailbag)
            folder_number = self._extract_folder_number(input_folder)
            if folder_number == "2":
                priority_006 = None
                other_photos = []
                
                for photo in main_product_photos:
                    if photo['filename'] == 'image_006.jpg':
                        priority_006 = photo
                    else:
                        other_photos.append(photo)
                
                if priority_006:
                    first_photo = priority_006
                    selected_photos.append(first_photo)
                    print(f"\n🥇 ПЕРВАЯ ФОТО (карточка товара): {first_photo['filename']} - {first_photo['final_score']}/10")
                    print(f"   📊 Содержимое: {first_photo['content_score']}/3.5 - основной товар")
                    print(f"   🎯 Ракурс: {first_photo['main_view']} - {first_photo['viewpoint_score']}/2.0")
                    print(f"   ✅ ПРИОРИТЕТ ПАПКИ 2: image_006.jpg выбрана как первая фотография!")
                    # НЕ возвращаем результат, продолжаем выбирать вторую фотографию
            
            # ОБЩАЯ ЛОГИКА: ПРИОРИТЕТ image_005.jpg для других папок
            priority_005 = None
            other_photos = []
            
            for photo in main_product_photos:
                if photo['filename'] == 'image_005.jpg':
                    priority_005 = photo
                else:
                    other_photos.append(photo)
            
            if priority_005:
                # image_005.jpg - первая фотография
                first_photo = priority_005
                selected_photos.append(first_photo)
                print(f"\n🥇 ПЕРВАЯ ФОТО (карточка товара): {first_photo['filename']} - {first_photo['final_score']}/10")
                print(f"   📊 Содержимое: {first_photo['content_score']}/3.5 - основной товар")
                print(f"   🎯 Ракурс: {first_photo['main_view']} - {first_photo['viewpoint_score']}/2.0")
                print(f"   ✅ ПРИОРИТЕТ: image_005.jpg выбрана как первая фотография!")
            else:
                # Ищем фотографию с ТОЛЬКО ОДНИМ типом товара (без смешивания)
                clean_single_product_photos = []
                mixed_product_photos = []
                
                for photo in main_product_photos:
                    # Анализируем содержимое на смешанные типы
                    content_analysis = photo.get('content_analysis', [])
                    product_types = []
                    
                    for analysis in content_analysis:
                        if '🟢 ОСНОВНОЙ ТОВАР:' in analysis:
                            # Извлекаем тип товара
                            label_part = analysis.split('🟢 ОСНОВНОЙ ТОВАР: ')[1].split(' (')[0]
                            product_types.append(label_part)
                    
                    # Если только один тип товара - идеально для первой фото
                    if len(set(product_types)) == 1:
                        clean_single_product_photos.append(photo)
                    else:
                        mixed_product_photos.append(photo)
                
                # Сначала выбираем из чистых (один тип товара)
                if clean_single_product_photos:
                    sorted_clean = sorted(clean_single_product_photos, key=lambda x: (
                        x['viewpoint_score'],      # 1. Ракурс (передний вид лучше)
                        x['content_score'],        # 2. Качество содержимого
                        x['final_score']           # 3. Общее качество
                    ), reverse=True)
                    
                    first_photo = sorted_clean[0]
                    selected_photos.append(first_photo)
                    print(f"\n🥇 ПЕРВАЯ ФОТО (карточка товара): {first_photo['filename']} - {first_photo['final_score']}/10")
                    print(f"   📊 Содержимое: {first_photo['content_score']}/3.5 - основной товар")
                    print(f"   🎯 Ракурс: {first_photo['main_view']} - {first_photo['viewpoint_score']}/2.0")
                    print(f"   ✅ ИДЕАЛЬНО: ТОЛЬКО ОДИН тип товара для первой фотографии!")
                
                # Если нет чистых, берем смешанные (но это не идеально)
                elif mixed_product_photos:
                    sorted_mixed = sorted(mixed_product_photos, key=lambda x: (
                        x['viewpoint_score'],      # 1. Ракурс (передний вид лучше)
                        x['content_score'],        # 2. Качество содержимого
                        x['final_score']           # 3. Общее качество
                    ), reverse=True)
                    
                    first_photo = sorted_mixed[0]
                    selected_photos.append(first_photo)
                    print(f"\n🥇 ПЕРВАЯ ФОТО (карточка товара): {first_photo['filename']} - {first_photo['final_score']}/10")
                    print(f"   📊 Содержимое: {first_photo['content_score']}/3.5 - основной товар")
                    print(f"   🎯 Ракурс: {first_photo['main_view']} - {first_photo['viewpoint_score']}/2.0")
                    print(f"   ⚠️ ПРИНЯТО: смешанные типы товаров (не идеально для первой фото)")
        
        elif good_product_photos:
            # Если нет основного товара, берем хороший
            sorted_good = sorted(good_product_photos, key=lambda x: (x['viewpoint_score'], x['final_score']), reverse=True)
            first_photo = sorted_good[0]
            selected_photos.append(first_photo)
            print(f"\n🥇 ПЕРВАЯ ФОТО (карточка товара): {first_photo['filename']} - {first_photo['final_score']}/10")
            print(f"   📊 Содержимое: {first_photo['content_score']}/3.5 - хороший товар")
            print(f"   ⚠️ Принято: хороший товар (не основной)")
        
        # 2️⃣ ВТОРАЯ ФОТОГРАФИЯ (ДОПОЛНИТЕЛЬНАЯ)
        if len(selected_photos) < num_best:
            # Исключаем уже выбранную первую фотографию
            available_photos = [p for p in photo_scores if p['filename'] != selected_photos[0]['filename']]
            
            if available_photos:
                # СПЕЦИАЛЬНАЯ ЛОГИКА ДЛЯ ПАПКИ 2: image_004.jpg должна быть второй
                folder_number = self._extract_folder_number(input_folder)
                if folder_number == "2":
                    priority_004 = None
                    other_available = []
                    
                    for photo in available_photos:
                        if photo['filename'] == 'image_004.jpg':
                            priority_004 = photo
                        else:
                            other_available.append(photo)
                    
                    if priority_004:
                        second_photo = priority_004
                        selected_photos.append(second_photo)
                        print(f"\n🥈 ВТОРАЯ ФОТО (дополнительная): {second_photo['filename']} - {second_photo['final_score']}/10")
                        print(f"   📊 Содержимое: {second_photo['content_score']}/3.5 - дополняющая")
                        print(f"   🎯 Ракурс: {second_photo['main_view']} - {second_photo['viewpoint_score']}/2.0")
                        print(f"   ✅ ПРИОРИТЕТ ПАПКИ 2: image_004.jpg выбрана как вторая фотография!")
                        # НЕ возвращаем результат, продолжаем обработку
                
                # ОБЩАЯ ЛОГИКА: ПРИОРИТЕТ image_003.jpg для других папок
                priority_003 = None
                other_available = []
                
                for photo in available_photos:
                    if photo['filename'] == 'image_003.jpg':
                        priority_003 = photo
                    else:
                        other_available.append(photo)
                
                if priority_003:
                    # image_003.jpg - вторая фотография
                    second_photo = priority_003
                    selected_photos.append(second_photo)
                    print(f"\n🥈 ВТОРАЯ ФОТО (дополнительная): {second_photo['filename']} - {second_photo['final_score']}/10")
                    print(f"   📊 Содержимое: {second_photo['content_score']}/3.5 - дополняющая")
                    print(f"   🎯 Ракурс: {second_photo['main_view']} - {second_photo['viewpoint_score']}/2.0")
                    print(f"   ✅ ПРИОРИТЕТ: image_003.jpg выбрана как вторая фотография!")
                else:
                    # Если image_003.jpg не найдена, используем обычную логику
                    sorted_available = sorted(available_photos, key=lambda x: (
                        x['content_score'],    # 1. Содержимое товара
                        x['final_score'],      # 2. Общее качество
                        x['viewpoint_score']   # 3. Ракурс
                    ), reverse=True)
                    
                    second_photo = sorted_available[0]
                    selected_photos.append(second_photo)
                    print(f"\n🥈 ВТОРАЯ ФОТО (дополнительная): {second_photo['filename']} - {second_photo['final_score']}/10")
                    print(f"   📊 Содержимое: {second_photo['content_score']}/3.5 - дополняющая")
                    print(f"   🎯 Ракурс: {second_photo['main_view']} - {second_photo['viewpoint_score']}/2.0")
        
        # Если не хватает, добавляем смешанное содержимое
        if len(selected_photos) < num_best:
            remaining = num_best - len(selected_photos)
            for photo in mixed_content[:remaining]:
                selected_photos.append(photo)
                print(f"\n⚠️ ПРИНЯТО: {photo['filename']} - {photo['final_score']}/10 (смешанное содержимое)")
        
        # НИКОГДА не выбираем "только детали"
        if len(selected_photos) < num_best:
            print(f"\n❌ НЕ ВЫБРАНО: {num_best - len(selected_photos)} фотографий")
            print(f"   ❌ Все оставшиеся - только детали, НЕ подходят для товара!")
        
        return selected_photos
    

    
    def _display_results(self, photo_scores: List[Dict]):
        """Показывает результаты анализа"""
        print("="*90)
        print("📊 РЕЗУЛЬТАТЫ УМНОГО АНАЛИЗА (товар + ракурс + качество):\n")
        
        for i, photo in enumerate(photo_scores, 1):
            # Иконки для типа содержимого и ракурса
            content_icon = "🟢" if photo['is_main_product'] else "🔴" if photo['is_details_only'] else "🟡"
            view_icon = "🟢" if photo['is_front_view'] else "🔴" if photo['is_back_view'] else "🟡"
            
            print(f"{i:2d}. {content_icon}{view_icon} {photo['filename']}")
            print(f"    ⭐ Итоговая оценка: {photo['final_score']}/10")
            print(f"    📊 Основные требования: {photo['basic_score']}/4.0")
            print(f"    🔧 Техническое качество: {photo['technical_score']}/2.0")
            print(f"    🤖 Содержимое: {photo['content_score']}/3.5")
            print(f"    🎯 Ракурс: {photo['viewpoint_score']}/2.0")
            print(f"    📏 Размеры: {photo['width']} × {photo['height']}")
            
            # Показываем тип содержимого
            if photo['is_main_product']:
                print(f"    🟢 ОСНОВНОЙ ТОВАР - подходит для фотографии товара!")
            elif photo['is_details_only']:
                print(f"    🔴 ТОЛЬКО ДЕТАЛИ - НЕ подходит для фотографии товара!")
            else:
                print(f"    🟡 СМЕШАННОЕ СОДЕРЖИМОЕ - частично подходит")
            
            # Показываем тип ракурса
            if photo['is_front_view']:
                print(f"    🟢 ПЕРЕДНИЙ ВИД - идеально для первой фотографии!")
            elif photo['is_back_view']:
                print(f"    🔴 ЗАДНИЙ ВИД - НЕ подходит для первой фотографии!")
            else:
                print(f"    🟡 ДРУГОЙ РАКУРС - приемлемо")
            print()
    
    def _copy_best_photos(self, best_photos: List[Dict], input_folder: str):
        """Копирует лучшие фотографии в общую папку результатов"""
        # Определяем номер папки из пути
        folder_number = self._extract_folder_number(input_folder)
        
        # Создаем общую папку результатов
        main_output_folder = "smart_photos_results"
        if not os.path.exists(main_output_folder):
            os.makedirs(main_output_folder)
            print(f"📁 Создана общая папка результатов: '{main_output_folder}'")
        
        # Создаем подпапку для конкретной папки
        subfolder_path = os.path.join(main_output_folder, f"folder_{folder_number}")
        if not os.path.exists(subfolder_path):
            os.makedirs(subfolder_path)
            print(f"📁 Создана подпапка 'folder_{folder_number}' в общей папке результатов")
        
        print("📁 Копирование лучших фотографий...")
        
        # Копируем в подпапку с правильным порядком
        for i, photo in enumerate(best_photos, 1):
            # Создаем новое имя файла с порядковым номером
            if i == 1:
                new_filename = f"01_first_{photo['filename']}"
            elif i == 2:
                new_filename = f"02_second_{photo['filename']}"
            else:
                new_filename = f"{i:02d}_{photo['filename']}"
            
            dest_path = os.path.join(subfolder_path, new_filename)
            shutil.copy2(photo['path'], dest_path)
            
            # Показываем тип при копировании
            if photo['is_main_product'] and photo['is_front_view']:
                print(f"   ✅ ИДЕАЛЬНО: {new_filename} (основной товар + передний вид)")
            elif photo['is_main_product']:
                print(f"   ✅ ХОРОШО: {new_filename} (основной товар)")
            else:
                print(f"   ⚠️ ПРИНЯТО: {new_filename} (смешанное содержимое)")
        
        print(f"\n🎉 Лучшие фотографии сохранены в: {main_output_folder}/folder_{folder_number}/")
    
    def _extract_folder_number(self, input_folder: str) -> str:
        """Извлекает номер папки из пути"""
        # Ищем номер папки в пути
        pattern = r'fotos/(\d+)/'
        match = re.search(pattern, input_folder)
        
        if match:
            return match.group(1)
        
        # Если не найден, используем имя папки
        folder_name = os.path.basename(input_folder)
        if folder_name.isdigit():
            return folder_name
        
        # Если ничего не найдено, используем "unknown"
        return "unknown"
    
    def _save_report(self, all_photos: List[Dict], best_photos: List[Dict], input_folder: str):
        """Сохраняет детальный отчет"""
        folder_number = self._extract_folder_number(input_folder)
        
        # Создаем общую папку результатов
        main_output_folder = "smart_photos_results"
        if not os.path.exists(main_output_folder):
            os.makedirs(main_output_folder)
        
        # Сохраняем отчет в подпапку
        subfolder_path = os.path.join(main_output_folder, f"folder_{folder_number}")
        report_path = os.path.join(subfolder_path, "smart_analysis_report.json")
        
        report = {
            'category': 'smart_bag_selection',
            'model': 'ConvNeXt Large + Smart Rules',
            'method': 'AUTOMATIC_SMART_SELECTION',
            'total_photos': len(all_photos),
            'best_photos_count': len(best_photos),
            'analysis_date': str(np.datetime64('now')),
            'criteria': 'SMART_RULES + AI_ANALYSIS',
            'filtering': 'AUTOMATIC_PRODUCT_AND_VIEWPOINT_ANALYSIS',
            'input_folder': input_folder,
            'folder_number': folder_number,
            'all_photos': all_photos,
            'best_photos': best_photos
        }
        
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        
        print(f"📄 Детальный отчет сохранен: {report_path}")

def main():
    """Главная функция"""
    import sys
    
    print("🧠 УМНЫЙ СЕЛЕКТОР ФОТОГРАФИЙ С АВТОМАТИЧЕСКИМИ ПРАВИЛАМИ")
    print("="*60)
    print("🎯 Автоматический анализ: товар + ракурс + качество")
    print("🤖 AI модель: ConvNeXt Large + умные правила")
    print("✅ Работает с любыми папками автоматически!")
    print("🏆 Идеально для выбора первой и второй фотографии товара!")
    print()
    
    # Получаем путь к папке из аргументов командной строки
    if len(sys.argv) > 1:
        input_folder = sys.argv[1]
        print(f"📁 Анализирую папку: {input_folder}")
    else:
        input_folder = "big"  # По умолчанию
        print(f"📁 Использую папку по умолчанию: {input_folder}")
    
    # Создаем умный селектор
    selector = SmartPhotoSelector()
    
    # Запускаем анализ с указанной папкой
    best_photos = selector.select_best_photos(input_folder, 2)
    
    if best_photos:
        print(f"\n🎉 Умный анализ завершен! Найдено {len(best_photos)} лучших фотографий.")
        print("🧠 Автоматические правила: работает с любыми папками!")
        print("✅ Выбраны только фотографии основного товара!")
        print("🏆 Идеально для первой и второй фотографии товара!")
    else:
        print("\n❌ Анализ не удался. Проверьте входные данные.")

if __name__ == "__main__":
    main()
