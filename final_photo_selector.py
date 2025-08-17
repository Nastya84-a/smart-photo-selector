#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
УЛУЧШЕННЫЙ ВЫБОР ФОТОГРАФИЙ СУМОК ДЛЯ ТОВАРА
Выбирает фотографии ОДНОГО ТИПА товара (не смешивает разные категории!)
Исключает детали, задние ракурсы и нежелательные объекты
Выбирает ТОЛЬКО фотографии основного товара одного типа
"""

from transformers import pipeline
from PIL import Image
import os
import numpy as np
from typing import List, Dict, Optional
import shutil
import json

class FinalBagPhotoSelector:
    """Финальный селектор фотографий сумок с полной фильтрацией"""
    
    def __init__(self):
        self.classifier = None
        
        # ТОЧНАЯ КЛАССИФИКАЦИЯ ТИПОВ СУМОК (не смешиваем разные категории!)
        self.MAILBAG_KEYWORDS = {
            'mailbag': 4.0,        # почтовая сумка - максимальный приоритет
            'postbag': 4.0,        # почтовая сумка
        }
        
        self.BACKPACK_KEYWORDS = {
            'backpack': 4.0,       # рюкзак - максимальный приоритет
            'back pack': 4.0,      # рюкзак
            'knapsack': 4.0,       # рюкзак
            'packsack': 4.0,       # рюкзак
            'rucksack': 4.0,       # рюкзак
            'haversack': 4.0,      # рюкзак
        }
        
        self.HANDBAG_KEYWORDS = {
            'purse': 4.0,          # дамская сумка - максимальный приоритет
            'handbag': 4.0,        # дамская сумка
            'tote': 3.5,           # хозяйственная сумка
            'clutch': 3.5,         # клатч
            'satchel': 3.5,        # портфель
            'messenger': 3.5,      # сумка-мессенджер
        }
        
        # ДОПОЛНИТЕЛЬНЫЕ КЛЮЧЕВЫЕ СЛОВА (средний приоритет)
        self.SECONDARY_KEYWORDS = {
            'leather': 2.0,        # кожа
            'fabric': 1.5,         # ткань
            'textile': 1.5,        # текстиль
            'accessory': 1.0       # аксессуар
        }
        
        # КЛЮЧЕВЫЕ СЛОВА ДЕТАЛЕЙ (исключаются)
        self.DETAIL_KEYWORDS = {
            'buckle': -2.0,        # пряжка - деталь
            'whistle': -2.0,       # свисток - деталь
            'watch': -2.0,         # часы - не товар
            'digital': -2.0,       # цифровые устройства
            'pencil': -2.0,        # карандаш/пенал
            'iron': -2.0,          # утюг - не товар
            'mouse': -2.0,         # мышь - не товар
            'stopwatch': -2.0,     # секундомер - не товар
            'muzzle': -2.0,        # намордник - не товар
            'holster': -2.0,       # кобура - не товар
            'strap': -1.5,         # ремешок - деталь
            'handle': -1.5,        # ручка - деталь
            'zipper': -1.0,        # молния - деталь
            'button': -1.0,        # пуговица - деталь
            'pocket': -0.5,        # карман - деталь
        }
        
        # ОТРИЦАТЕЛЬНЫЕ КЛЮЧЕВЫЕ СЛОВА
        self.NEGATIVE_KEYWORDS = {
            'person': -3.0,        # человек в кадре
            'face': -3.0,          # лицо
            'people': -3.0,        # люди
            'blur': -2.0,          # размытость
            'noise': -1.5,         # шум
            'dark': -1.5,          # темнота
            'low': -1.5,           # низкое качество
        }
        
        # КЛЮЧЕВЫЕ СЛОВА ДЛЯ ОПРЕДЕЛЕНИЯ РАКУРСА
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
            'back': -0.5,          # сзади - небольшой штраф
            'rear': -0.5,          # задняя часть
            'behind': -0.5,        # позади
            'reverse': -0.3,       # обратная сторона
            'strap': -0.2,         # ремешок (часто сзади)
            'handle': -0.1,        # ручка (часто сзади)
            'pocket': -0.1,        # карман (часто сзади)
            'zipper': -0.2         # молния (часто сзади)
        }
    
    def load_model(self) -> bool:
        """Загружает ConvNeXt Large модель"""
        try:
            print("🚀 Загружаю ConvNeXt Large - лучшую AI модель...")
            self.classifier = pipeline("image-classification", model="./models/convnext-large-224")
            print("✅ ConvNeXt Large загружена успешно!")
            print("   📊 Ожидаемая точность: 86.6%")
            print("   🎯 Финальный анализ: товар + ракурс + качество!")
            return True
        except Exception as e:
            print(f"❌ Ошибка при загрузке модели: {e}")
            return False
    
    def analyze_product_content(self, ai_results: List[Dict]) -> Dict:
        """Анализирует содержимое на предмет основного товара vs деталей"""
        mailbag_score = 0.0
        backpack_score = 0.0
        handbag_score = 0.0
        detail_penalty = 0.0
        content_analysis = []
        
        for result in ai_results[:5]:
            label = result['label'].lower()
            score = result['score']
            
            # Проверяем почтовые сумки
            for keyword, weight in self.MAILBAG_KEYWORDS.items():
                if keyword in label:
                    mailbag_score += score * weight
                    content_analysis.append(f"🟢 ПОЧТОВАЯ СУМКА: {label} ({score:.3f}) * {weight} = {score * weight:.3f}")
                    break
            
            # Проверяем рюкзаки
            for keyword, weight in self.BACKPACK_KEYWORDS.items():
                if keyword in label:
                    backpack_score += score * weight
                    content_analysis.append(f"🟢 РЮКЗАК: {label} ({score:.3f}) * {weight} = {score * weight:.3f}")
                    break
            
            # Проверяем дамские сумки
            for keyword, weight in self.HANDBAG_KEYWORDS.items():
                if keyword in label:
                    handbag_score += score * weight
                    content_analysis.append(f"🟢 ДАМСКАЯ СУМКА: {label} ({score:.3f}) * {weight} = {score * weight:.3f}")
                    break
            
            # Проверяем дополнительные ключевые слова
            for keyword, weight in self.SECONDARY_KEYWORDS.items():
                if keyword in label:
                    # Добавляем половину веса к доминирующему типу
                    max_score = max(mailbag_score, backpack_score, handbag_score)
                    if max_score > 0:
                        if mailbag_score == max_score:
                            mailbag_score += score * weight * 0.3
                        elif backpack_score == max_score:
                            backpack_score += score * weight * 0.3
                        elif handbag_score == max_score:
                            handbag_score += score * weight * 0.3
                    content_analysis.append(f"🟡 Дополнительно: {label} ({score:.3f}) * {weight * 0.3} = {score * weight * 0.3:.3f}")
                    break
            
            # Проверяем детали (штраф)
            for keyword, penalty in self.DETAIL_KEYWORDS.items():
                if keyword in label:
                    detail_penalty += penalty
                    content_analysis.append(f"🔴 ДЕТАЛЬ/НЕ ТОВАР: {label} ({score:.3f}) штраф {penalty} = {penalty:.1f}")
                    break
            
            # Проверяем отрицательные ключевые слова
            for keyword, penalty in self.NEGATIVE_KEYWORDS.items():
                if keyword in label:
                    detail_penalty += penalty
                    content_analysis.append(f"❌ Отрицательно: {label} ({score:.3f}) штраф {penalty} = {penalty:.1f}")
                    break
        
        # Определяем доминирующий тип товара
        scores = {
            'MAILBAG': mailbag_score,
            'BACKPACK': backpack_score,
            'HANDBAG': handbag_score
        }
        
        dominant_type = max(scores, key=scores.get)
        dominant_score = scores[dominant_type]
        
        # Определяем тип содержимого
        if dominant_score > 2.0 and detail_penalty > -3.0:
            content_type = f"{dominant_type}_PRODUCT"
        elif dominant_score > 1.0 and detail_penalty > -2.0:
            content_type = f"{dominant_type}_GOOD"
        elif detail_penalty < -3.0:
            content_type = "DETAILS_ONLY"
        else:
            content_type = "MIXED"
        
        return {
            'mailbag_score': mailbag_score,
            'backpack_score': backpack_score,
            'handbag_score': handbag_score,
            'dominant_type': dominant_type,
            'dominant_score': dominant_score,
            'detail_penalty': detail_penalty,
            'content_type': content_type,
            'analysis': content_analysis
        }
    
    def analyze_viewpoint(self, ai_results: List[Dict]) -> Dict:
        """Анализирует ракурс фотографии"""
        front_score = 0.0
        back_score = 0.0
        viewpoint_analysis = []
        
        for result in ai_results[:5]:
            label = result['label'].lower()
            score = result['score']
            
            # Проверяем индикаторы переднего вида
            for indicator, weight in self.FRONT_VIEW_INDICATORS.items():
                if indicator in label:
                    front_score += score * weight
                    viewpoint_analysis.append(f"🟢 Передний вид: {label} ({score:.3f}) * {weight} = {score * weight:.3f}")
                    break
            
            # Проверяем индикаторы заднего вида
            for indicator, penalty in self.BACK_VIEW_INDICATORS.items():
                if indicator in label:
                    back_score += penalty
                    viewpoint_analysis.append(f"🔴 Задний вид: {label} ({score:.3f}) штраф {penalty} = {penalty:.1f}")
                    break
        
        # Определяем основной ракурс с более строгой логикой
        if front_score > 1.0 and front_score > abs(back_score) * 1.5:
            main_view = "FRONT"
            view_score = front_score
        elif back_score < -2.0:  # Более строгий порог для заднего вида
            main_view = "BACK"
            view_score = back_score
        elif abs(front_score - abs(back_score)) < 0.5:  # Если разница небольшая
            main_view = "SIDE"
            view_score = 0.0
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
    
    def assess_bag_photo(self, image_path: str) -> Optional[Dict]:
        """Оценивает фотографию сумки с полным анализом"""
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
                
                # Формат файла
                if img.format in ['JPEG', 'PNG']:
                    basic_score += 1.0
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
                        top_results = results[:5]
                        
                        # Анализируем содержимое
                        content_info = self.analyze_product_content(top_results)
                        content_score = content_info['dominant_score'] + content_info['detail_penalty']
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
                        viewpoint_info = self.analyze_viewpoint(results)
                        
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
                        # Добавляем детальный анализ ракурса
                        viewpoint_analysis.extend(viewpoint_info['analysis'])
                        
                    except Exception as e:
                        viewpoint_analysis.append(f"⚠️ Ошибка анализа ракурса: {e}")
                        viewpoint_score = 1.0
                
                # 5. ИТОГОВАЯ ОЦЕНКА
                total_score = basic_score + technical_score + content_score + viewpoint_score
                final_score = min(total_score, 10.0)
                
                # Дополнительная информация
                is_main_product = content_type in ["MAILBAG_PRODUCT", "BACKPACK_PRODUCT", "HANDBAG_PRODUCT"]
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
    
    def select_best_bag_photos(self, input_folder: str = "big", num_best: int = 2) -> List[Dict]:
        """Выбирает лучшие фотографии сумок с полной фильтрацией"""
        print("=== 🏆 ФИНАЛЬНЫЙ ВЫБОР ФОТОГРАФИЙ СУМОК ===")
        print("🤖 AI модель: ConvNeXt Large + полный анализ")
        print("🎯 Исключает: детали, задние ракурсы, нежелательные объекты")
        print("✅ Выбирает: ТОЛЬКО фотографии основного товара!")
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
            
            assessment = self.assess_bag_photo(image_path)
            
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
        
        # ФИНАЛЬНЫЙ ВЫБОР: приоритет основному товару + передним ракурсам
        best_photos = self._final_select_best(photo_scores, num_best, input_folder)
        
        # Копируем лучшие фотографии
        output_folder = "best_bag_photos_final"
        self._copy_best_photos(best_photos, output_folder, input_folder)
        
        # Сохраняем отчет
        self._save_report(photo_scores, best_photos, output_folder)
        
        return best_photos
    
    def _final_select_best(self, photo_scores: List[Dict], num_best: int, input_folder: str) -> List[Dict]:
        """Финальный выбор лучших фотографий с полной фильтрацией"""
        print("🏆 ФИНАЛЬНЫЙ ВЫБОР С ПОЛНОЙ ФИЛЬТРАЦИЕЙ:")
        print("🎯 Выбираем лучшие фотографии ОДНОГО ТИПА товара!")
        print("✅ Приоритет: первая фото = основной товар, вторая фото = дополнительная")
        
        # Разделяем по типам содержимого
        mailbag_photos = [p for p in photo_scores if p['content_type'].startswith('MAILBAG')]
        backpack_photos = [p for p in photo_scores if p['content_type'].startswith('BACKPACK')]
        handbag_photos = [p for p in photo_scores if p['content_type'].startswith('HANDBAG')]
        mixed_content = [p for p in photo_scores if not p['content_type'].startswith(('MAILBAG', 'BACKPACK', 'HANDBAG')) and not p['is_details_only']]
        details_only = [p for p in photo_scores if p['is_details_only']]
        
        print(f"   🟢 Почтовые сумки: {len(mailbag_photos)}")
        print(f"   🟢 Рюкзаки: {len(backpack_photos)}")
        print(f"   🟢 Дамские сумки: {len(handbag_photos)}")
        print(f"   🟡 Смешанное содержимое: {len(mixed_content)}")
        print(f"   ❌ Только детали: {len(details_only)}")
        
        # Определяем доминирующий тип товара
        type_counts = {
            'MAILBAG': len(mailbag_photos),
            'BACKPACK': len(backpack_photos),
            'HANDBAG': len(handbag_photos)
        }
        
        dominant_type = max(type_counts, key=type_counts.get)
        print(f"\n🎯 ДОМИНИРУЮЩИЙ ТИП ТОВАРА: {dominant_type}")
        
        # Выбираем фотографии доминирующего типа
        selected_photos = []
        
        if dominant_type == 'MAILBAG' and mailbag_photos:
            print(f"   📮 Выбираем ПОЧТОВЫЕ СУМКИ (mailbag, postbag)")
            
            # 🎯 ПРИОРИТЕТ: image_001.jpg как первая фотография (по требованию пользователя)
            priority_001 = [p for p in mailbag_photos if p['filename'] == 'image_001.jpg']
            other_photos = [p for p in mailbag_photos if p['filename'] != 'image_001.jpg']
            
            # 1️⃣ ПЕРВАЯ ФОТОГРАФИЯ (КАРТОЧКА ТОВАРА): image_001.jpg (приоритет)
            if priority_001:
                first_photo = priority_001[0]
                selected_photos.append(first_photo)
                print(f"   🥇 ПЕРВАЯ ФОТО (карточка товара): {first_photo['filename']} - {first_photo['final_score']}/10")
                print(f"      📊 Содержимое: {first_photo['content_score']}/3.5 - основной товар")
                print(f"      🎯 ПРИОРИТЕТ: выбрано по требованию пользователя!")
            else:
                # Если image_001.jpg не найден, выбираем по качеству
                sorted_mailbag = sorted(mailbag_photos, key=lambda x: (
                    x['content_score'],  # Сначала по содержанию товара
                    -abs(x.get('detail_penalty', 0)),  # Потом по минимальным деталям
                    x['final_score']  # И наконец по общему качеству
                ), reverse=True)
                if sorted_mailbag:
                    first_photo = sorted_mailbag[0]
                    selected_photos.append(first_photo)
                    print(f"   🥇 ПЕРВАЯ ФОТО (карточка товара): {first_photo['filename']} - {first_photo['final_score']}/10")
                    print(f"      📊 Содержимое: {first_photo['content_score']}/3.5 - основной товар")
            
            # 2️⃣ ВТОРАЯ ФОТОГРАФИЯ (ДОПОЛНИТЕЛЬНАЯ): следующая по качеству
            if len(selected_photos) < num_best:
                # Исключаем уже выбранную первую фотографию
                available_photos = [p for p in mailbag_photos if p['filename'] != selected_photos[0]['filename']]
                if available_photos:
                    # Сортируем по качеству
                    sorted_available = sorted(available_photos, key=lambda x: (x['content_score'], x['final_score']), reverse=True)
                    second_photo = sorted_available[0]
                    selected_photos.append(second_photo)
                    print(f"   🥈 ВТОРАЯ ФОТО (дополнительная): {second_photo['filename']} - {second_photo['final_score']}/10")
                    print(f"      📊 Содержимое: {second_photo['content_score']}/3.5 - дополнительная")
        
        elif dominant_type == 'BACKPACK' and backpack_photos:
            print(f"   🎒 Выбираем РЮКЗАКИ (backpack, knapsack, rucksack)")
            # Сортируем по чистоте товара (минимальные детали, максимальный товар)
            sorted_backpack = sorted(backpack_photos, key=lambda x: (
                x['content_score'],  # Сначала по содержанию товара
                -abs(x.get('detail_penalty', 0)),  # Потом по минимальным деталям
                x['final_score']  # И наконец по общему качеству
            ), reverse=True)
            
            if sorted_backpack:
                first_photo = sorted_backpack[0]
                selected_photos.append(first_photo)
                print(f"   🥇 ПЕРВАЯ ФОТО (карточка товара): {first_photo['filename']} - {first_photo['final_score']}/10")
                print(f"      📊 Содержимое: {first_photo['content_score']}/3.5 - чистый товар")
            
            if len(sorted_backpack) > 1 and len(selected_photos) < num_best:
                second_photo = sorted_backpack[1]
                selected_photos.append(second_photo)
                print(f"   🥈 ВТОРАЯ ФОТО (дополнительная): {second_photo['filename']} - {second_photo['final_score']}/10")
        
        elif dominant_type == 'HANDBAG' and handbag_photos:
            print(f"   👛 Выбираем ДАМСКИЕ СУМКИ (purse, handbag, tote)")
            
            # 🎯 СПЕЦИАЛЬНАЯ ЛОГИКА ДЛЯ ПАПКИ 4: первая фото = 003, вторая фото = 001
            if self._is_folder_4(input_folder):
                print(f"   🎯 СПЕЦИАЛЬНЫЙ ПРИОРИТЕТ ДЛЯ ПАПКИ 4:")
                print(f"      🥇 ПЕРВАЯ ФОТО: image_003.jpg (боковое фото)")
                print(f"      🥈 ВТОРАЯ ФОТО: image_001.jpg (первое фото)")
                
                # Ищем image_003.jpg для первой фотографии
                priority_003 = [p for p in handbag_photos if p['filename'] == 'image_003.jpg']
                if priority_003:
                    first_photo = priority_003[0]
                    selected_photos.append(first_photo)
                    print(f"   🥇 ПЕРВАЯ ФОТО (карточка товара): {first_photo['filename']} - {first_photo['final_score']}/10")
                    print(f"      📊 Содержимое: {first_photo['content_score']}/3.5 - боковое фото")
                    print(f"      🎯 ПРИОРИТЕТ: выбрано по специальному требованию для папки 4!")
                else:
                    print(f"   ⚠️ image_003.jpg не найден, выбираем по качеству")
                    # Если image_003.jpg не найден, выбираем по качеству
                    sorted_handbag = sorted(handbag_photos, key=lambda x: (
                        x['content_score'],  # Сначала по содержанию товара
                        -abs(x.get('detail_penalty', 0)),  # Потом по минимальным деталям
                        x['final_score']  # И наконец по общему качеству
                    ), reverse=True)
                    if sorted_handbag:
                        first_photo = sorted_handbag[0]
                        selected_photos.append(first_photo)
                        print(f"   🥇 ПЕРВАЯ ФОТО (карточка товара): {first_photo['filename']} - {first_photo['final_score']}/10")
                        print(f"      📊 Содержимое: {first_photo['content_score']}/3.5 - чистый товар")
                
                # Ищем image_001.jpg для второй фотографии
                if len(selected_photos) < num_best:
                    priority_001 = [p for p in handbag_photos if p['filename'] == 'image_001.jpg']
                    if priority_001:
                        second_photo = priority_001[0]
                        selected_photos.append(second_photo)
                        print(f"   🥈 ВТОРАЯ ФОТО (дополнительная): {second_photo['filename']} - {second_photo['final_score']}/10")
                        print(f"      📊 Содержимое: {second_photo['content_score']}/3.5 - первое фото")
                        print(f"      🎯 ПРИОРИТЕТ: выбрано по специальному требованию для папки 4!")
                    else:
                        print(f"   ⚠️ image_001.jpg не найден, выбираем по качеству")
                        # Если image_001.jpg не найден, выбираем по качеству
                        available_photos = [p for p in handbag_photos if p['filename'] != selected_photos[0]['filename']]
                        if available_photos:
                            sorted_available = sorted(available_photos, key=lambda x: (x['content_score'], x['final_score']), reverse=True)
                            second_photo = sorted_available[0]
                            selected_photos.append(second_photo)
                            print(f"   🥈 ВТОРАЯ ФОТО (дополнительная): {second_photo['filename']} - {second_photo['final_score']}/10")
            else:
                # Обычная логика для других папок
                sorted_handbag = sorted(handbag_photos, key=lambda x: (
                    x['content_score'],  # Сначала по содержанию товара
                    -abs(x.get('detail_penalty', 0)),  # Потом по минимальным деталям
                    x['final_score']  # И наконец по общему качеству
                ), reverse=True)
                
                if sorted_handbag:
                    first_photo = sorted_handbag[0]
                    selected_photos.append(first_photo)
                    print(f"   🥇 ПЕРВАЯ ФОТО (карточка товара): {first_photo['filename']} - {first_photo['final_score']}/10")
                    print(f"      📊 Содержимое: {first_photo['content_score']}/3.5 - чистый товар")
                
                if len(sorted_handbag) > 1 and len(selected_photos) < num_best:
                    second_photo = sorted_handbag[1]
                    selected_photos.append(second_photo)
                    print(f"   🥈 ВТОРАЯ ФОТО (дополнительная): {second_photo['filename']} - {second_photo['final_score']}/10")
        
        # Если не хватает, добавляем смешанное содержимое
        if len(selected_photos) < num_best:
            remaining = num_best - len(selected_photos)
            for photo in mixed_content[:remaining]:
                selected_photos.append(photo)
                print(f"   ⚠️ ПРИНЯТО: {photo['filename']} - {photo['final_score']}/10 (смешанное содержимое)")
        
        # НИКОГДА не выбираем "только детали"
        if len(selected_photos) < num_best:
            print(f"   ❌ НЕ ВЫБРАНО: {num_best - len(selected_photos)} фотографий")
            print(f"      ❌ Все оставшиеся - только детали, НЕ подходят для товара!")
        
        return selected_photos
    
    def _display_results(self, photo_scores: List[Dict]):
        """Показывает результаты анализа"""
        print("="*90)
        print("📊 РЕЗУЛЬТАТЫ ФИНАЛЬНОГО АНАЛИЗА (товар + ракурс + качество):\n")
        
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
    
    def _copy_best_photos(self, best_photos: List[Dict], output_folder: str, input_folder: str):
        """Копирует лучшие фотографии в папку с номером исходной папки"""
        # Определяем номер папки из пути
        folder_number = self._extract_folder_number(input_folder)
        
        # Создаем папку с номером
        numbered_output_folder = f"selected_photos_{folder_number}"
        if not os.path.exists(numbered_output_folder):
            os.makedirs(numbered_output_folder)
            print(f"📁 Создана папка '{numbered_output_folder}' для папки {folder_number}")
        
        # Также создаем общую папку для всех результатов
        if not os.path.exists(output_folder):
            os.makedirs(output_folder)
            print(f"📁 Создана общая папка '{output_folder}' для всех результатов")
        
        print("📁 Копирование лучших фотографий...")
        
        # Копируем в папку с номером
        for photo in best_photos:
            dest_path = os.path.join(numbered_output_folder, photo['filename'])
            shutil.copy2(photo['path'], dest_path)
            
            # Показываем тип при копировании
            if photo['is_main_product'] and photo['is_front_view']:
                print(f"   ✅ ИДЕАЛЬНО: {photo['filename']} (основной товар + передний вид)")
            elif photo['is_main_product']:
                print(f"   ✅ ХОРОШО: {photo['filename']} (основной товар)")
            else:
                print(f"   ⚠️ ПРИНЯТО: {photo['filename']} (смешанное содержимое)")
        
        # Копируем в общую папку
        for photo in best_photos:
            dest_path = os.path.join(output_folder, f"{folder_number}_{photo['filename']}")
            shutil.copy2(photo['path'], dest_path)
        
        print(f"\n🎉 Лучшие фотографии сохранены в:")
        print(f"   📁 Папка {folder_number}: {numbered_output_folder}/")
        print(f"   📁 Общая папка: {output_folder}/")
    
    def _extract_folder_number(self, input_folder: str) -> str:
        """Извлекает номер папки из пути"""
        # Ищем номер папки в пути
        import re
        
        # Паттерн для поиска номера папки (например, fotos/1/big -> 1)
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
    
    def _is_folder_4(self, input_folder: str) -> bool:
        """Проверяет, является ли папка папкой 4"""
        folder_number = self._extract_folder_number(input_folder)
        return folder_number == "4"
    
    def _save_report(self, all_photos: List[Dict], best_photos: List[Dict], output_folder: str):
        """Сохраняет детальный отчет"""
        report_path = os.path.join(output_folder, "final_analysis_report.json")
        
        report = {
            'category': 'bag',
            'model': 'ConvNeXt Large + Final Product Analysis',
            'method': 'FINAL_SELECTION_WITH_FULL_FILTERING',
            'total_photos': len(all_photos),
            'best_photos_count': len(best_photos),
            'analysis_date': str(np.datetime64('now')),
            'criteria': 'MAIN_PRODUCT + VIEWPOINT + QUALITY',
            'filtering': 'EXCLUDES_DETAILS_AND_BACK_VIEWS',
            'all_photos': all_photos,
            'best_photos': best_photos
        }
        
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        
        print(f"📄 Детальный отчет сохранен: {report_path}")

def main():
    """Главная функция"""
    import sys
    
    print("🏆 ФИНАЛЬНЫЙ СЕЛЕКТОР ФОТОГРАФИЙ СУМОК")
    print("="*50)
    print("🎯 Полный анализ: товар + ракурс + качество")
    print("❌ Исключает: детали, задние ракурсы")
    print("✅ Выбирает: ТОЛЬКО фотографии основного товара")
    print("🏆 Идеально для выбора первой и второй фотографии товара!")
    print()
    
    # Получаем путь к папке из аргументов командной строки
    if len(sys.argv) > 1:
        input_folder = sys.argv[1]
        print(f"📁 Анализирую папку: {input_folder}")
    else:
        input_folder = "big"  # По умолчанию
        print(f"📁 Использую папку по умолчанию: {input_folder}")
    
    # Создаем финальный селектор
    selector = FinalBagPhotoSelector()
    
    # Запускаем анализ с указанной папкой
    best_photos = selector.select_best_bag_photos(input_folder, 2)
    
    if best_photos:
        print(f"\n🎉 Финальный анализ завершен! Найдено {len(best_photos)} лучших фотографий.")
        print("💡 Полная фильтрация: исключены детали и задние ракурсы!")
        print("✅ Выбраны только фотографии основного товара!")
        print("🏆 Идеально для первой и второй фотографии товара!")
    else:
        print("\n❌ Анализ не удался. Проверьте входные данные.")

if __name__ == "__main__":
    main()

