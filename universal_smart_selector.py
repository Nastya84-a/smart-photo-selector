#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Универсальный умный селектор фотографий товаров
Автоматически определяет категорию товара и применяет соответствующие правила
"""

import os
import json
import shutil
from pathlib import Path
from typing import List, Dict, Tuple, Optional
from PIL import Image
import numpy as np

try:
    from transformers import pipeline
    from smart_photo_selector import SmartPhotoSelector
except ImportError:
    print("❌ Ошибка: Не удалось импортировать необходимые модули")
    print("Установите зависимости: pip install -r requirements.txt")
    exit(1)


class UniversalSmartSelector:
    """Универсальный умный селектор для любых категорий товаров"""
    
    def __init__(self):
        """Инициализация с AI моделью и категориями товаров"""
        print("🧠 Инициализация универсального селектора...")
        
        # Загружаем базовый селектор
        self.base_selector = SmartPhotoSelector()
        
        # Определяем категории товаров и их ключевые слова
        self.product_categories = {
            'bags': {
                'keywords': ['mailbag', 'postbag', 'backpack', 'purse', 'handbag', 'bag', 'tote', 'satchel'],
                'details': ['buckle', 'wallet', 'zipper', 'pocket', 'strap', 'handle'],
                'description': 'Сумки, рюкзаки, кошельки',
                'priority_rules': {
                    'first_photo': 'Только основной товар, без деталей',
                    'second_photo': 'Дополняющая, может содержать детали'
                }
            },
            'clothing': {
                'keywords': ['shirt', 'dress', 'pants', 'jacket', 'blouse', 'skirt', 'coat', 'sweater', 't-shirt'],
                'details': ['button', 'zipper', 'fabric', 'pattern', 'collar', 'sleeve', 'pocket'],
                'description': 'Одежда, текстиль',
                'priority_rules': {
                    'first_photo': 'Полный вид товара, хороший ракурс',
                    'second_photo': 'Детали или альтернативный ракурс'
                }
            },
            'electronics': {
                'keywords': ['phone', 'laptop', 'computer', 'camera', 'tablet', 'device', 'gadget', 'smartphone'],
                'details': ['screen', 'button', 'cable', 'charger', 'port', 'antenna'],
                'description': 'Электроника, гаджеты',
                'priority_rules': {
                    'first_photo': 'Основной товар в фокусе',
                    'second_photo': 'Технические детали или использование'
                }
            },
            'jewelry': {
                'keywords': ['ring', 'necklace', 'earring', 'bracelet', 'watch', 'pendant', 'brooch'],
                'details': ['stone', 'metal', 'clasp', 'chain', 'gem', 'diamond'],
                'description': 'Украшения, драгоценности',
                'priority_rules': {
                    'first_photo': 'Четкий вид украшения',
                    'second_photo': 'Детали или на модели'
                }
            },
            'shoes': {
                'keywords': ['shoe', 'boot', 'sneaker', 'sandal', 'heel', 'footwear', 'loafer', 'pump'],
                'details': ['sole', 'laces', 'buckle', 'heel', 'toe', 'insole'],
                'description': 'Обувь',
                'priority_rules': {
                    'first_photo': 'Полный вид обуви',
                    'second_photo': 'Детали или на ноге'
                }
            },
            'cosmetics': {
                'keywords': ['cosmetic', 'makeup', 'cream', 'beauty', 'skincare', 'lipstick', 'foundation'],
                'details': ['brush', 'applicator', 'mirror', 'case', 'tube'],
                'description': 'Косметика, уход',
                'priority_rules': {
                    'first_photo': 'Основной продукт',
                    'second_photo': 'Применение или детали'
                }
            },
            'general': {
                'keywords': ['product', 'object', 'item', 'accessory', 'tool', 'equipment'],
                'details': ['part', 'component', 'material', 'texture'],
                'description': 'Универсальная категория',
                'priority_rules': {
                    'first_photo': 'Основной товар',
                    'second_photo': 'Дополнительная информация'
                }
            }
        }
        
        print("✅ Универсальный селектор инициализирован!")
        print(f"📋 Поддерживаемые категории: {len(self.product_categories)}")
    
    def detect_product_category(self, photo_scores: List[Dict]) -> Tuple[str, float]:
        """
        Автоматически определяет категорию товара на основе AI анализа
        
        Args:
            photo_scores: Результаты анализа фотографий
            
        Returns:
            Tuple[str, float]: (категория, уверенность)
        """
        print("🔍 Определение категории товара...")
        
        # Собираем все AI метки
        all_labels = []
        for photo in photo_scores:
            if 'ai_analysis' in photo:
                for label, confidence in photo['ai_analysis']:
                    all_labels.append((label.lower(), confidence))
        
        if not all_labels:
            print("⚠️ Не удалось получить AI анализ, используем универсальную категорию")
            return 'general', 0.5
        
        # Подсчитываем баллы для каждой категории
        category_scores = {}
        for category, config in self.product_categories.items():
            score = 0
            total_matches = 0
            
            for label, confidence in all_labels:
                if label in config['keywords']:
                    score += confidence * 2.0  # Основные товары имеют больший вес
                    total_matches += 1
                elif label in config['details']:
                    score += confidence * 0.5  # Детали имеют меньший вес
            
            if total_matches > 0:
                category_scores[category] = score / total_matches
            else:
                category_scores[category] = 0
        
        # Выбираем категорию с наивысшим баллом
        if category_scores:
            best_category = max(category_scores, key=category_scores.get)
            confidence = category_scores[best_category]
            
            print(f"🎯 Определена категория: {best_category}")
            print(f"   📝 {self.product_categories[best_category]['description']}")
            print(f"   🎯 Уверенность: {confidence:.2f}")
            
            return best_category, confidence
        
        print("⚠️ Не удалось определить категорию, используем 'general'")
        return 'general', 0.3
    
    def apply_category_rules(self, photo_scores: List[Dict], category: str) -> List[Dict]:
        """
        Применяет правила выбора для конкретной категории товара
        
        Args:
            photo_scores: Результаты анализа фотографий
            category: Определенная категория товара
            
        Returns:
            List[Dict]: Отфильтрованные и отсортированные фотографии
        """
        print(f"⚙️ Применение правил для категории: {category}")
        
        if category not in self.product_categories:
            print(f"⚠️ Категория '{category}' не найдена, используем базовые правила")
            return self.base_selector._smart_select_best(photo_scores, 2, "")
        
        config = self.product_categories[category]
        print(f"📋 Правила: {config['priority_rules']}")
        
        # Применяем специальные правила для категории
        if category == 'bags':
            return self._apply_bag_rules(photo_scores)
        elif category == 'clothing':
            return self._apply_clothing_rules(photo_scores)
        elif category == 'electronics':
            return self._apply_electronics_rules(photo_scores)
        elif category == 'jewelry':
            return self._apply_jewelry_rules(photo_scores)
        elif category == 'shoes':
            return self._apply_shoes_rules(photo_scores)
        elif category == 'cosmetics':
            return self._apply_cosmetics_rules(photo_scores)
        else:
            return self._apply_general_rules(photo_scores)
    
    def _apply_bag_rules(self, photo_scores: List[Dict]) -> List[Dict]:
        """Специальные правила для сумок"""
        print("👜 Применение правил для сумок...")
        
        # Разделяем на основные товары и детали
        main_products = []
        detail_photos = []
        
        for photo in photo_scores:
            if 'ai_analysis' in photo:
                has_main_product = False
                has_details = False
                
                for label, confidence in photo['ai_analysis']:
                    label_lower = label.lower()
                    if label_lower in ['mailbag', 'postbag', 'backpack', 'purse', 'handbag', 'bag']:
                        has_main_product = True
                    if label_lower in ['buckle', 'wallet', 'zipper', 'pocket']:
                        has_details = True
                
                if has_main_product and not has_details:
                    main_products.append(photo)
                elif has_details:
                    detail_photos.append(photo)
                else:
                    main_products.append(photo)  # Фото без четкой классификации
        
        # Сортируем основные товары по качеству
        main_products.sort(key=lambda x: x.get('final_score', 0), reverse=True)
        
        # Выбираем лучшие
        selected = []
        if main_products:
            selected.append(main_products[0])  # Первое фото - только основной товар
        
        if len(main_products) > 1:
            selected.append(main_products[1])  # Второе фото - тоже основной товар
        elif detail_photos:
            detail_photos.sort(key=lambda x: x.get('final_score', 0), reverse=True)
            selected.append(detail_photos[0])  # Или фото с деталями
        
        return selected[:2]
    
    def _apply_clothing_rules(self, photo_scores: List[Dict]) -> List[Dict]:
        """Специальные правила для одежды"""
        print("👗 Применение правил для одежды...")
        
        # Приоритет: полный вид товара, хороший ракурс
        sorted_photos = sorted(photo_scores, key=lambda x: (
            x.get('viewpoint_score', 0),
            x.get('final_score', 0)
        ), reverse=True)
        
        return sorted_photos[:2]
    
    def _apply_electronics_rules(self, photo_scores: List[Dict]) -> List[Dict]:
        """Специальные правила для электроники"""
        print("📱 Применение правил для электроники...")
        
        # Приоритет: четкость, основной товар в фокусе
        sorted_photos = sorted(photo_scores, key=lambda x: (
            x.get('content_score', 0),
            x.get('final_score', 0),
            x.get('viewpoint_score', 0)
        ), reverse=True)
        
        return sorted_photos[:2]
    
    def _apply_jewelry_rules(self, photo_scores: List[Dict]) -> List[Dict]:
        """Специальные правила для украшений"""
        print("💍 Применение правил для украшений...")
        
        # Приоритет: четкость, детали, качество
        sorted_photos = sorted(photo_scores, key=lambda x: (
            x.get('final_score', 0),
            x.get('content_score', 0)
        ), reverse=True)
        
        return sorted_photos[:2]
    
    def _apply_shoes_rules(self, photo_scores: List[Dict]) -> List[Dict]:
        """Специальные правила для обуви"""
        print("👟 Применение правил для обуви...")
        
        # Приоритет: полный вид, качество, ракурс
        sorted_photos = sorted(photo_scores, key=lambda x: (
            x.get('viewpoint_score', 0),
            x.get('final_score', 0)
        ), reverse=True)
        
        return sorted_photos[:2]
    
    def _apply_cosmetics_rules(self, photo_scores: List[Dict]) -> List[Dict]:
        """Специальные правила для косметики"""
        print("💄 Применение правил для косметики...")
        
        # Приоритет: основной продукт, качество
        sorted_photos = sorted(photo_scores, key=lambda x: (
            x.get('content_score', 0),
            x.get('final_score', 0)
        ), reverse=True)
        
        return sorted_photos[:2]
    
    def _apply_general_rules(self, photo_scores: List[Dict]) -> List[Dict]:
        """Общие правила для неизвестных категорий"""
        print("🔧 Применение общих правил...")
        
        # Простая сортировка по общему качеству
        sorted_photos = sorted(photo_scores, key=lambda x: x.get('final_score', 0), reverse=True)
        return sorted_photos[:2]
    
    def select_best_photos(self, input_folder: str, num_best: int = 2) -> List[Dict]:
        """
        Основной метод выбора лучших фотографий с автоматическим определением категории
        
        Args:
            input_folder: Папка с фотографиями
            num_best: Количество лучших фотографий
            
        Returns:
            List[Dict]: Лучшие фотографии с метаданными
        """
        print(f"🚀 Универсальный анализ папки: {input_folder}")
        
        # Используем базовый селектор для анализа
        photo_scores = self.base_selector.analyze_photos(input_folder)
        
        if not photo_scores:
            print("❌ Не удалось проанализировать фотографии")
            return []
        
        print(f"📊 Проанализировано фотографий: {len(photo_scores)}")
        
        # Автоматически определяем категорию товара
        category, confidence = self.detect_product_category(photo_scores)
        
        # Применяем правила для определенной категории
        best_photos = self.apply_category_rules(photo_scores, category)
        
        if best_photos:
            print(f"✅ Выбрано лучших фотографий: {len(best_photos)}")
            print(f"🎯 Категория: {category} (уверенность: {confidence:.2f})")
            
            # Показываем результаты
            self._display_results(best_photos, category)
            
            # Сохраняем результаты
            self._save_results(best_photos, input_folder, category)
            
            return best_photos
        else:
            print("❌ Не удалось выбрать лучшие фотографии")
            return []
    
    def _display_results(self, best_photos: List[Dict], category: str):
        """Отображает результаты выбора"""
        print(f"\n🏆 РЕЗУЛЬТАТЫ ВЫБОРА ДЛЯ КАТЕГОРИИ '{category.upper()}':")
        print("=" * 60)
        
        for i, photo in enumerate(best_photos, 1):
            print(f"\n📸 ФОТО #{i}: {photo['filename']}")
            print(f"   📊 Общий балл: {photo.get('final_score', 0):.2f}")
            print(f"   🎯 Содержимое: {photo.get('content_score', 0):.2f}")
            print(f"   📐 Ракурс: {photo.get('viewpoint_score', 0):.2f}")
            print(f"   📁 Путь: {photo['path']}")
            
            if 'ai_analysis' in photo:
                print("   🤖 AI анализ:")
                for label, confidence in photo['ai_analysis'][:3]:  # Показываем топ-3 метки
                    print(f"      • {label}: {confidence:.3f}")
    
    def _save_results(self, best_photos: List[Dict], input_folder: str, category: str):
        """Сохраняет результаты в папку"""
        output_dir = f"universal_results_{category}"
        os.makedirs(output_dir, exist_ok=True)
        
        print(f"\n💾 Сохранение результатов в: {output_dir}")
        
        for i, photo in enumerate(best_photos, 1):
            src_path = photo['path']
            filename = photo['filename']
            new_filename = f"{i:02d}_{category}_{filename}"
            dst_path = os.path.join(output_dir, new_filename)
            
            try:
                shutil.copy2(src_path, dst_path)
                print(f"   ✅ {new_filename}")
            except Exception as e:
                print(f"   ❌ Ошибка копирования {filename}: {e}")
        
        # Сохраняем отчет
        report = {
            'category': category,
            'input_folder': input_folder,
            'analysis_date': str(Path().cwd()),
            'best_photos': [
                {
                    'filename': photo['filename'],
                    'final_score': photo.get('final_score', 0),
                    'content_score': photo.get('content_score', 0),
                    'viewpoint_score': photo.get('viewpoint_score', 0)
                }
                for photo in best_photos
            ]
        }
        
        report_path = os.path.join(output_dir, f"analysis_report_{category}.json")
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        print(f"📄 Отчет сохранен: {report_path}")


def main():
    """Главная функция"""
    import sys
    
    if len(sys.argv) != 2:
        print("❌ Использование: python universal_smart_selector.py <папка_с_фотографиями>")
        print("Пример: python universal_smart_selector.py fotos/1/big")
        sys.exit(1)
    
    input_folder = sys.argv[1]
    
    if not os.path.exists(input_folder):
        print(f"❌ Папка не найдена: {input_folder}")
        sys.exit(1)
    
    # Создаем и запускаем универсальный селектор
    selector = UniversalSmartSelector()
    
    try:
        best_photos = selector.select_best_photos(input_folder)
        
        if best_photos:
            print(f"\n🎉 Анализ завершен успешно!")
            print(f"📁 Результаты сохранены в папку с названием категории")
        else:
            print(f"\n❌ Анализ не удался")
            sys.exit(1)
            
    except Exception as e:
        print(f"❌ Ошибка во время анализа: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()

