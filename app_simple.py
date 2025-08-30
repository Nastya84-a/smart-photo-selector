from flask import Flask, render_template, request, jsonify
import os
import tempfile
import shutil
from universal_smart_selector import UniversalSmartSelector

app = Flask(__name__)

@app.route('/')
def index():
    return '''
<!DOCTYPE html>
<html>
<head>
    <title>Smart Photo Selector</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; }
        .container { max-width: 800px; margin: 0 auto; }
        .upload-section { background: #f0f0f0; padding: 30px; border-radius: 10px; margin: 20px 0; }
        .results { background: #e8f5e8; padding: 20px; border-radius: 10px; margin: 20px 0; display: none; }
        .btn { background: #007bff; color: white; padding: 10px 20px; border: none; border-radius: 5px; cursor: pointer; }
        .btn:disabled { background: #ccc; }
        .loading { display: none; text-align: center; margin: 20px 0; }
        .spinner { border: 4px solid #f3f3f3; border-top: 4px solid #007bff; border-radius: 50%; width: 40px; height: 40px; animation: spin 1s linear infinite; margin: 0 auto 10px; }
        @keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }
        .progress-bar { width: 100%; height: 20px; background-color: #f0f0f0; border-radius: 10px; overflow: hidden; margin: 10px 0; }
        .progress-fill { height: 100%; background-color: #007bff; width: 0%; transition: width 0.3s ease; }
        .status { color: #007bff; font-weight: bold; margin: 10px 0; }
    </style>
</head>
<body>
    <div class="container">
        <h1>📸 Smart Photo Selector</h1>
        
        <div class="upload-section">
            <h3>Upload a folder with photos</h3>
            <form id="uploadForm">
                <input type="file" id="folderInput" webkitdirectory multiple>
                <br><br>
                <button type="submit" class="btn" id="analyzeBtn" disabled>Analyze</button>
            </form>
        </div>
        
        <div id="loading" class="loading">
            <div class="spinner"></div>
            <div class="status" id="statusText">Preparing for analysis...</div>
            <div class="progress-bar">
                <div class="progress-fill" id="progressFill"></div>
            </div>
        </div>
        
        <div id="results" class="results">
            <h3>Results</h3>
            <div id="resultsContent"></div>
        </div>
    </div>
    
    <script>
        const folderInput = document.getElementById('folderInput');
        const analyzeBtn = document.getElementById('analyzeBtn');
        const uploadForm = document.getElementById('uploadForm');
        const results = document.getElementById('results');
        const loading = document.getElementById('loading');
        const statusText = document.getElementById('statusText');
        const progressFill = document.getElementById('progressFill');
        
        folderInput.addEventListener('change', function(e) {
            analyzeBtn.disabled = e.target.files.length === 0;
        });
        
        uploadForm.addEventListener('submit', async function(e) {
            e.preventDefault();
            
            const files = Array.from(folderInput.files);
            if (files.length === 0) return;
            
            // Показываем индикатор загрузки
            loading.style.display = 'block';
            results.style.display = 'none';
            analyzeBtn.disabled = true;
            analyzeBtn.textContent = 'Analyzing...';
            
            // Симулируем прогресс
            let progress = 0;
            const progressInterval = setInterval(() => {
                progress += Math.random() * 15;
                if (progress > 90) progress = 90;
                progressFill.style.width = progress + '%';
                
                // Обновляем статус
                if (progress < 30) {
                    statusText.textContent = 'Uploading files...';
                } else if (progress < 60) {
                    statusText.textContent = 'Analyzing images...';
                } else if (progress < 90) {
                    statusText.textContent = '🤖 AI thinking...';
                }
            }, 200);
            
            const formData = new FormData();
            files.forEach(file => formData.append('files', file));
            
            try {
                const response = await fetch('/upload', {
                    method: 'POST',
                    body: formData
                });
                
                // Завершаем прогресс
                clearInterval(progressInterval);
                progressFill.style.width = '100%';
                statusText.textContent = '✅ Analysis completed!';
                
                // Небольшая задержка для показа завершения
                setTimeout(async () => {
                    if (response.ok) {
                        const data = await response.json();
                        
                        if (data.success) {
                            document.getElementById('resultsContent').innerHTML = data.html;
                            results.style.display = 'block';
                        } else {
                            alert('Ошибка: ' + data.error);
                        }
                    }
                    
                    // Скрываем индикатор загрузки
                    loading.style.display = 'none';
                    analyzeBtn.disabled = false;
                    analyzeBtn.textContent = 'Analyze';
                }, 500);
                
            } catch (err) {
                clearInterval(progressInterval);
                loading.style.display = 'none';
                analyzeBtn.disabled = false;
                analyzeBtn.textContent = 'Analyze';
                alert('Error: ' + err.message);
            }
        });
    </script>
</body>
</html>
'''

@app.route('/upload', methods=['POST'])
def upload_files():
    try:
        files = request.files.getlist('files')
        
        if not files:
            return jsonify({'success': False, 'error': 'Нет файлов'})
        
        # Создаем временную папку
        with tempfile.TemporaryDirectory() as temp_dir:
            # Сохраняем файлы
            saved_files = []
            image_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.bmp']
            image_files = []
            
            for file in files:
                if file.filename:
                    # Создаем правильные пути
                    safe_filename = file.filename.replace('/', os.sep).replace('\\', os.sep)
                    file_path = os.path.join(temp_dir, safe_filename)
                    
                    # Создаем папки если нужно
                    os.makedirs(os.path.dirname(file_path), exist_ok=True)
                    file.save(file_path)
                    saved_files.append(file_path)
                    
                    # Проверяем если это изображение
                    if any(file.filename.lower().endswith(ext) for ext in image_extensions):
                        image_files.append(file_path)
            
            # Формируем результаты
            file_info = f"Files uploaded: {len(saved_files)}\n"
            file_info += f"Images found: {len(image_files)}\n"
            file_info += f"Temporary folder: {temp_dir}\n\n"
            
            # Показываем список изображений
            if image_files:
                file_info += "Image list:\n"
                for i, img_file in enumerate(image_files[:10]):  # Показываем первые 10
                    file_info += f"- {os.path.basename(img_file)}\n"
                if len(image_files) > 10:
                    file_info += f"... and {len(image_files) - 10} more files\n"
            
            # Пробуем AI анализ
            analysis_result = "\n🤖 AI Analysis:\n"
            try:
                # Создаем структуру как в оригинальных папках foto/
                # Создаем папку "1" с подпапкой "big"
                folder_1 = os.path.join(temp_dir, "1", "big")
                os.makedirs(folder_1, exist_ok=True)
                
                # Копируем изображения в папку 1/big
                ai_image_files = []
                for i, img_file in enumerate(image_files):
                    img_name = os.path.basename(img_file)
                    ai_img_path = os.path.join(folder_1, img_name)
                    shutil.copy2(img_file, ai_img_path)
                    ai_image_files.append(ai_img_path)
                
                print(f"Folder structure created: {temp_dir}")
                print(f"AI folder: {folder_1}")
                print(f"Images copied: {len(ai_image_files)}")
                
                # Пробуем AI анализ с папкой 1/big
                selector = UniversalSmartSelector()
                ai_results = selector.select_best_photos(folder_1, 2)
                
                if ai_results:
                    analysis_result += "✅ AI analysis completed successfully!\n\n"
                    analysis_result += "🏆 BEST PHOTOGRAPHS:\n"
                    analysis_result += "=" * 50 + "\n"
                    
                    for i, result in enumerate(ai_results, 1):
                        filename = result.get('filename', 'Unknown')
                        final_score = result.get('final_score', 0)
                        content_type = result.get('content_type', 'Unknown')
                        width = result.get('width', 0)
                        height = result.get('height', 0)
                        
                        # Преобразуем оценку в понятный текст
                        if final_score >= 8.0:
                            score_text = "⭐ Excellent"
                        elif final_score >= 6.0:
                            score_text = "⭐ Good"
                        elif final_score >= 4.0:
                            score_text = "⭐ Average"
                        else:
                            score_text = "⭐ Needs improvement"
                        
                        # Преобразуем тип в понятный текст
                        if content_type == 'MAIN_PRODUCT':
                            type_text = "🎯 Main product photo"
                        elif content_type == 'MIXED':
                            type_text = "🎯 Mixed content"
                        elif content_type == 'DETAILS_ONLY':
                            type_text = "🎯 Detail view"
                        else:
                            type_text = f"🎯 {content_type}"
                        
                        analysis_result += f"\n🥇 PHOTO #{i}: {filename}\n"
                        analysis_result += f"   {score_text}\n"
                        analysis_result += f"   {type_text}\n"
                        analysis_result += f"   📏 Dimensions: {width} × {height}\n"
                    
                    analysis_result += "\n" + "=" * 50 + "\n"
                    analysis_result += "🎉 AI selected the best photos for your product!\n"
                else:
                    analysis_result += "⚠️ AI analysis of folder 1/big failed\n"
                    analysis_result += "Trying root folder...\n"
                    
                    # Пробуем проанализировать корневую папку
                    try:
                        ai_results_root = selector.select_best_photos(temp_dir, 2)
                        if ai_results_root:
                            analysis_result += "✅ AI analysis of root folder successful!\n"
                            analysis_result += f"Results:\n{ai_results_root}\n"
                        else:
                            analysis_result += "❌ AI analysis not working\n"
                            analysis_result += "Trying to create structure like in foto/...\n"
                            
                            # Создаем структуру как в оригинальных папках
                            for i in range(1, 6):  # Создаем папки 1, 2, 3, 4, 5
                                folder_path = os.path.join(temp_dir, str(i), "big")
                                os.makedirs(folder_path, exist_ok=True)
                                
                                # Распределяем изображения по папкам
                                start_idx = (i-1) * 6  # 6 изображений на папку
                                end_idx = min(start_idx + 6, len(image_files))
                                
                                for j in range(start_idx, end_idx):
                                    if j < len(image_files):
                                        img_file = image_files[j]
                                        img_name = os.path.basename(img_file)
                                        new_img_path = os.path.join(folder_path, img_name)
                                        shutil.copy2(img_file, new_img_path)
                            
                            # Пробуем проанализировать папку 1/big
                            try:
                                ai_results_final = selector.select_best_photos(os.path.join(temp_dir, "1", "big"), 2)
                                if ai_results_final:
                                    analysis_result += "✅ AI analysis with correct structure successful!\n"
                                    analysis_result += f"Results:\n{ai_results_final}\n"
                                else:
                                    analysis_result += "❌ AI analysis still not working\n"
                                    analysis_result += f"Use command line:\npython universal_smart_selector.py {temp_dir}\n"
                            except Exception as e3:
                                analysis_result += f"❌ Final error: {str(e3)}\n"
                                
                    except Exception as e2:
                        analysis_result += f"❌ Root folder analysis error: {str(e2)}\n"
                    
            except Exception as e:
                analysis_result += f"❌ AI analysis error: {str(e)}\n"
                analysis_result += "Use command line:\n"
                analysis_result += f"python universal_smart_selector.py {temp_dir}\n"
            
            final_results = file_info + analysis_result
            
            # Форматируем в HTML
            html_results = f'''
            <div style="background: white; padding: 20px; border-radius: 10px; margin-bottom: 20px;">
                <h4>🎯 Upload and AI Analysis Results</h4>
                <pre style="background: #f8f9fa; padding: 15px; border-radius: 5px; overflow-x: auto; max-height: 400px;">{final_results}</pre>
            </div>
            '''
            
            print(f"DEBUG: final_results = {final_results}")
            print(f"DEBUG: html_results length = {len(html_results)}")
            
            return jsonify({
                'success': True,
                'html': html_results
            })
        
    except Exception as e:
        print(f"Ошибка: {str(e)}")
        return jsonify({'success': False, 'error': str(e)})

if __name__ == '__main__':
    app.run(host='localhost', port=3000, debug=True)
