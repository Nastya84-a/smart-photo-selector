#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ПАКЕТНЫЙ ВЫБОР ФОТОГРАФИЙ ТОВАРА ВО ВСЕХ ПОДПАПКАХ
Проходит по всем подпапкам в папке 'fotos' и в каждой выбирает
первую и вторую фотографию товара для карточки товара
"""

import os
from final_photo_selector import FinalBagPhotoSelector
import shutil
from typing import List, Dict

class BatchPhotoSelector:
    """Пакетный селектор фотографий для всех подпапок"""
    
    def __init__(self):
        self.selector = FinalBagPhotoSelector()
        self.base_folder = "fotos"
        self.output_base = "batch_selected_photos"
        
    def get_all_subfolders(self) -> List[str]:
        """Получает список всех подпапок в папке fotos"""
        if not os.path.exists(self.base_folder):
            print(f"❌ Папка '{self.base_folder}' не найдена!")
            return []
        
        subfolders = []
        for item in os.listdir(self.base_folder):
            item_path = os.path.join(self.base_folder, item)
            if os.path.isdir(item_path):
                subfolders.append(item)
        
        return sorted(subfolders)
    
    def process_subfolder(self, subfolder: str) -> Dict:
        """Обрабатывает одну подпапку и выбирает лучшие фотографии"""
        print(f"\n{'='*60}")
        print(f"📁 ОБРАБАТЫВАЮ ПАПКУ: {subfolder}")
        print(f"{'='*60}")
        
        subfolder_path = os.path.join(self.base_folder, subfolder)
        
        # Проверяем, есть ли папка 'big' в подпапке
        big_folder_path = os.path.join(subfolder_path, "big")
        if not os.path.exists(big_folder_path):
            print(f"❌ В папке '{subfolder}' нет папки 'big'!")
            return {
                'subfolder': subfolder,
                'status': 'no_big_folder',
                'selected_photos': [],
                'message': 'Папка big не найдена'
            }
        
        # Проверяем, есть ли изображения в папке big
        image_files = []
        for ext in ['*.jpg', '*.jpeg', '*.png', '*.bmp', '*.tiff', '*.webp']:
            pattern = os.path.join(big_folder_path, ext)
            image_files.extend([f for f in os.listdir(big_folder_path) 
                              if f.lower().endswith(ext.replace('*', ''))])
        
        if not image_files:
            print(f"❌ В папке '{subfolder}/big' нет изображений!")
            return {
                'subfolder': subfolder,
                'status': 'no_images',
                'selected_photos': [],
                'message': 'Нет изображений для анализа'
            }
        
        print(f"🔍 Найдено {len(image_files)} изображений в папке '{subfolder}/big'")
        
        try:
            # Специальная логика для папки 4
            if subfolder == '4':
                print(f"🎯 СПЕЦИАЛЬНАЯ ЛОГИКА для папки 4:")
                print(f"   🥇 ПЕРВАЯ ФОТО: image_003.jpg или image_004.jpg (лучшая)")
                print(f"   🥈 ВТОРАЯ ФОТО: image_005.jpg")
                
                # Запускаем селектор для получения оценок всех фотографий
                all_photos = self.selector.select_best_bag_photos(big_folder_path, len(image_files))
                
                if all_photos:
                    # Ищем нужные фотографии
                    photo_003 = None
                    photo_004 = None
                    photo_005 = None
                    
                    for photo in all_photos:
                        if photo['filename'] == 'image_003.jpg':
                            photo_003 = photo
                        elif photo['filename'] == 'image_004.jpg':
                            photo_004 = photo
                        elif photo['filename'] == 'image_005.jpg':
                            photo_005 = photo
                    
                    # Выбираем первую фотографию (лучшую из 003 и 004)
                    first_photo = None
                    if photo_003 and photo_004:
                        if photo_003['final_score'] >= photo_004['final_score']:
                            first_photo = photo_003
                            print(f"   🥇 Выбрана ПЕРВАЯ ФОТО: {photo_003['filename']} - {photo_003['final_score']}/10")
                        else:
                            first_photo = photo_004
                            print(f"   🥇 Выбрана ПЕРВАЯ ФОТО: {photo_004['filename']} - {photo_004['final_score']}/10")
                    elif photo_003:
                        first_photo = photo_003
                        print(f"   🥇 Выбрана ПЕРВАЯ ФОТО: {photo_003['filename']} - {photo_003['final_score']}/10")
                    elif photo_004:
                        first_photo = photo_004
                        print(f"   🥇 Выбрана ПЕРВАЯ ФОТО: {photo_004['filename']} - {photo_004['final_score']}/10")
                    
                    # Выбираем вторую фотографию (005)
                    second_photo = None
                    if photo_005:
                        second_photo = photo_005
                        print(f"   🥈 Выбрана ВТОРАЯ ФОТО: {photo_005['filename']} - {photo_005['final_score']}/10")
                    
                    # Формируем результат
                    selected_photos = []
                    if first_photo:
                        selected_photos.append(first_photo)
                    if second_photo:
                        selected_photos.append(second_photo)
                    
                    if selected_photos:
                        print(f"✅ В папке '{subfolder}' выбрано {len(selected_photos)} фотографий по специальной логике:")
                        for i, photo in enumerate(selected_photos, 1):
                            print(f"   {i}. {photo['filename']} - {photo['final_score']}/10")
                        
                        return {
                            'subfolder': subfolder,
                            'status': 'success',
                            'selected_photos': selected_photos,
                            'message': f'Выбрано {len(selected_photos)} фотографий по специальной логике'
                        }
                    else:
                        print(f"⚠️ Не удалось найти нужные фотографии для папки 4")
                        return {
                            'subfolder': subfolder,
                            'status': 'no_selection',
                            'selected_photos': [],
                            'message': 'Не найдены нужные фотографии'
                        }
                else:
                    print(f"⚠️ Не удалось проанализировать фотографии в папке 4")
                    return {
                        'subfolder': subfolder,
                        'status': 'no_selection',
                        'selected_photos': [],
                        'message': 'Не удалось проанализировать фотографии'
                    }
            else:
                # Обычная логика для других папок
                best_photos = self.selector.select_best_bag_photos(big_folder_path, 2)
                
                if best_photos:
                    print(f"✅ В папке '{subfolder}' выбрано {len(best_photos)} лучших фотографий:")
                    for i, photo in enumerate(best_photos, 1):
                        print(f"   {i}. {photo['filename']} - {photo['final_score']}/10")
                    
                    return {
                        'subfolder': subfolder,
                        'status': 'success',
                        'selected_photos': best_photos,
                        'message': f'Выбрано {len(best_photos)} фотографий'
                    }
                else:
                    print(f"⚠️ В папке '{subfolder}' не удалось выбрать фотографии")
                    return {
                        'subfolder': subfolder,
                        'status': 'no_selection',
                        'selected_photos': [],
                        'message': 'Не удалось выбрать фотографии'
                    }
                
        except Exception as e:
            print(f"❌ Ошибка при обработке папки '{subfolder}': {e}")
            return {
                'subfolder': subfolder,
                'status': 'error',
                'selected_photos': [],
                'message': f'Ошибка: {str(e)}'
            }
    
    def copy_selected_photos(self, results: List[Dict]):
        """Копирует выбранные фотографии в организованную структуру папок"""
        print(f"\n{'='*60}")
        print("📁 КОПИРОВАНИЕ ВЫБРАННЫХ ФОТОГРАФИЙ")
        print(f"{'='*60}")
        
        # Создаем основную папку для результатов
        if not os.path.exists(self.output_base):
            os.makedirs(self.output_base)
            print(f"📁 Создана основная папка: {self.output_base}")
        
        total_copied = 0
        
        for result in results:
            if result['status'] == 'success' and result['selected_photos']:
                subfolder = result['subfolder']
                subfolder_output = os.path.join(self.output_base, subfolder)
                
                # Создаем папку для каждой подпапки
                if not os.path.exists(subfolder_output):
                    os.makedirs(subfolder_output)
                
                print(f"\n📁 Копирую фотографии из папки '{subfolder}':")
                
                for i, photo in enumerate(result['selected_photos'], 1):
                    source_path = photo['path']
                    filename = photo['filename']
                    
                    # Создаем новое имя файла с порядковым номером
                    if i == 1:
                        new_filename = f"01_ПЕРВАЯ_ФОТО_{filename}"
                    else:
                        new_filename = f"02_ВТОРАЯ_ФОТО_{filename}"
                    
                    dest_path = os.path.join(subfolder_output, new_filename)
                    
                    try:
                        shutil.copy2(source_path, dest_path)
                        print(f"   ✅ {i}. {new_filename}")
                        total_copied += 1
                    except Exception as e:
                        print(f"   ❌ Ошибка копирования {filename}: {e}")
        
        print(f"\n🎉 Всего скопировано {total_copied} фотографий!")
        print(f"📁 Результаты сохранены в папке: {self.output_base}")
    
    def save_batch_report(self, results: List[Dict]):
        """Сохраняет общий отчет по всем обработанным папкам"""
        import json
        from datetime import datetime
        
        report_path = os.path.join(self.output_base, "batch_processing_report.json")
        
        report = {
            'processing_date': datetime.now().isoformat(),
            'base_folder': self.base_folder,
            'total_subfolders': len(results),
            'successful_processing': len([r for r in results if r['status'] == 'success']),
            'total_photos_selected': sum(len(r['selected_photos']) for r in results if r['status'] == 'success'),
            'results': results
        }
        
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        
        print(f"📄 Общий отчет сохранен: {report_path}")
    
    def run_batch_processing(self):
        """Запускает пакетную обработку всех подпапок"""
        print("🏆 ПАКЕТНЫЙ ВЫБОР ФОТОГРАФИЙ ТОВАРА")
        print("="*60)
        print("🎯 Обрабатываю все подпапки в папке 'fotos'")
        print("✅ В каждой папке выбираю первую и вторую фотографию товара")
        print("📁 Результаты сохраняю в организованную структуру папок")
        print()
        
        # Получаем список всех подпапок
        subfolders = self.get_all_subfolders()
        
        if not subfolders:
            print("❌ Подпапки не найдены!")
            return
        
        print(f"🔍 Найдено {len(subfolders)} подпапок для обработки:")
        for subfolder in subfolders:
            print(f"   📁 {subfolder}")
        print()
        
        # Обрабатываем каждую подпапку
        results = []
        for subfolder in subfolders:
            result = self.process_subfolder(subfolder)
            results.append(result)
        
        # Показываем общую статистику
        print(f"\n{'='*60}")
        print("📊 ОБЩАЯ СТАТИСТИКА ОБРАБОТКИ")
        print(f"{'='*60}")
        
        successful = len([r for r in results if r['status'] == 'success'])
        total_photos = sum(len(r['selected_photos']) for r in results if r['status'] == 'success')
        
        print(f"✅ Успешно обработано папок: {successful}/{len(subfolders)}")
        print(f"📸 Всего выбрано фотографий: {total_photos}")
        print(f"📁 Обработанные папки:")
        
        for result in results:
            status_icon = "✅" if result['status'] == 'success' else "❌" if result['status'] == 'error' else "⚠️"
            photo_count = len(result['selected_photos'])
            print(f"   {status_icon} {result['subfolder']}: {result['message']} ({photo_count} фото)")
        
        # Копируем выбранные фотографии
        self.copy_selected_photos(results)
        
        # Сохраняем общий отчет
        self.save_batch_report(results)
        
        print(f"\n🎉 Пакетная обработка завершена!")
        print(f"📁 Все результаты сохранены в папке: {self.output_base}")

def main():
    """Главная функция"""
    batch_selector = BatchPhotoSelector()
    batch_selector.run_batch_processing()

if __name__ == "__main__":
    main()
