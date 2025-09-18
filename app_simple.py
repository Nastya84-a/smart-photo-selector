from flask import Flask, request, jsonify
import os
import tempfile
import shutil
import time
from universal_smart_selector import UniversalSmartSelector
from celery import Celery

app = Flask(__name__)

# Увеличиваем лимит загрузки файлов до 500MB
app.config['MAX_CONTENT_LENGTH'] = 500 * 1024 * 1024

# Настройка Celery
app.config['CELERY_BROKER_URL'] = os.environ.get('CELERY_BROKER_URL', 'redis://localhost:6379/0')
app.config['CELERY_RESULT_BACKEND'] = os.environ.get('CELERY_RESULT_BACKEND', 'redis://localhost:6379/0')

celery = Celery(app.name, broker=app.config['CELERY_BROKER_URL'])
celery.conf.update(app.config)

@celery.task
def analyze_photos_task(image_files, temp_dir):
    """Фоновая задача для анализа фото"""
    try:
        print(f"DEBUG: temp_dir = {temp_dir}")
        print(f"DEBUG: image_files = {image_files}")
        
        # Создаем структуру для AI анализа - используем существующую папку big
        folder_1 = os.path.join(temp_dir, "1", "big")
        os.makedirs(folder_1, exist_ok=True)
        
        print(f"DEBUG: Created folder_1 = {folder_1}")
        
        # Копируем изображения из папки big в папку 1/big
        copied_files = []
        for img_file in image_files:
            if os.path.exists(img_file):
                img_name = os.path.basename(img_file)
                dest_path = os.path.join(folder_1, img_name)
                shutil.copy2(img_file, dest_path)
                copied_files.append(dest_path)
                print(f"DEBUG: Copied {img_file} -> {dest_path}")
            else:
                print(f"DEBUG: File not found: {img_file}")
        
        print(f"DEBUG: Copied {len(copied_files)} files to {folder_1}")
        
        # Проверяем что файлы скопированы
        if not copied_files:
            return {"success": False, "error": "No image files were copied"}
        
        # Запускаем AI анализ
        selector = UniversalSmartSelector()
        ai_results = selector.select_best_photos(folder_1, 2)
        
        print(f"DEBUG: AI results = {ai_results}")
        
        return {"success": True, "results": ai_results}
        
    except Exception as e:
        print(f"DEBUG: Error in analyze_photos_task: {str(e)}")
        return {"success": False, "error": str(e)}

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
        <h1> Smart Photo Selector</h1>
        
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
            
            loading.style.display = 'block';
            results.style.display = 'none';
            analyzeBtn.disabled = true;
            analyzeBtn.textContent = 'Analyzing...';
            
            let progress = 0;
            const progressInterval = setInterval(() => {
                progress += Math.random() * 15;
                if (progress > 90) progress = 90;
                progressFill.style.width = progress + '%';
                
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
                
                if (response.ok) {
                    const data = await response.json();
                    if (data.success) {
                        // Получили task_id - начинаем проверку статуса
                        const taskId = data.task_id;
                        statusText.textContent = '📤 Files uploaded! Starting AI analysis...';
                        
                        // Проверяем статус каждые 2 секунды
                        const statusInterval = setInterval(async () => {
                            try {
                                const statusResponse = await fetch(`/status/${taskId}`);
                                const statusData = await statusResponse.json();
                                
                                if (statusData.status === 'processing') {
                                    statusText.textContent = '🤖 AI is analyzing photos...';
                                    progressFill.style.width = '75%';
                                } else if (statusData.status === 'completed') {
                                    // Анализ завершен
                                    clearInterval(statusInterval);
                                    clearInterval(progressInterval);
                                    progressFill.style.width = '100%';
                                    statusText.textContent = '✅ Analysis completed!';
                                    
                                    // Показываем результаты
                                    document.getElementById('resultsContent').innerHTML = statusData.html;
                                    results.style.display = 'block';
                                    
                                    // Скрываем загрузку
                                    setTimeout(() => {
                                        loading.style.display = 'none';
                                        analyzeBtn.disabled = false;
                                        analyzeBtn.textContent = 'Analyze';
                                    }, 1000);
                                    
                                } else if (statusData.status === 'error') {
                                    // Ошибка
                                    clearInterval(statusInterval);
                                    clearInterval(progressInterval);
                                    loading.style.display = 'none';
                                    analyzeBtn.disabled = false;
                                    analyzeBtn.textContent = 'Analyze';
                                    alert('Error: ' + statusData.error);
                                }
                            } catch (err) {
                                console.error('Status check error:', err);
                            }
                        }, 2000);
                        
                    } else {
                        clearInterval(progressInterval);
                        loading.style.display = 'none';
                        analyzeBtn.disabled = false;
                        analyzeBtn.textContent = 'Analyze';
                        alert('Error: ' + data.error);
                    }
                } else {
                    clearInterval(progressInterval);
                    loading.style.display = 'none';
                    analyzeBtn.disabled = false;
                    analyzeBtn.textContent = 'Analyze';
                    alert('Upload failed');
                }
                
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
            return jsonify({'success': False, 'error': 'No files uploaded'})
        
        # Создаем папку в общем volume (не временную)
        temp_dir = os.path.join('/app', 'temp_uploads', f'upload_{int(time.time())}')
        os.makedirs(temp_dir, exist_ok=True)
        image_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.bmp']
        image_files = []
        
        print(f"DEBUG: Uploading {len(files)} files to {temp_dir}")
        
        # Создаем папку big для изображений
        big_folder = os.path.join(temp_dir, "big")
        os.makedirs(big_folder, exist_ok=True)
        
        # Сохраняем файлы
        for file in files:
            if file.filename:
                safe_filename = file.filename.replace('/', os.sep).replace('\\', os.sep)
                # Убираем лишние папки из имени файла
                safe_filename = os.path.basename(safe_filename)
                file_path = os.path.join(big_folder, safe_filename)
                file.save(file_path)
                
                print(f"DEBUG: Saved file: {file_path}")
                
                if any(file.filename.lower().endswith(ext) for ext in image_extensions):
                    image_files.append(file_path)
                    print(f"DEBUG: Added image file: {file_path}")
        
        print(f"DEBUG: Total image files: {len(image_files)}")
        print(f"DEBUG: Image files list: {image_files}")
        
        # Запускаем фоновую задачу
        task = analyze_photos_task.delay(image_files, temp_dir)
        
        return jsonify({
            'success': True, 
            'task_id': task.id,
            'message': 'Files uploaded! AI analysis started in background...'
        })
    
    except Exception as e:
        print(f"DEBUG: Upload error: {str(e)}")
        return jsonify({'success': False, 'error': str(e)})

@app.route('/status/<task_id>')
def task_status(task_id):
    """Проверка статуса задачи"""
    task = analyze_photos_task.AsyncResult(task_id)
    
    if task.state == 'PENDING':
        return jsonify({'status': 'processing', 'message': 'AI is analyzing photos...'})
    elif task.state == 'SUCCESS':
        result = task.result
        if result['success']:
            # Форматируем результаты
            ai_results = result['results']
            analysis_result = "✅ AI analysis completed successfully!\n\nBEST PHOTOGRAPHS:\n"
            analysis_result += "=" * 50 + "\n"
            
            for i, result_item in enumerate(ai_results, 1):
                filename = result_item.get('filename', 'Unknown')
                final_score = result_item.get('final_score', 0)
                content_type = result_item.get('content_type', 'Unknown')
                width = result_item.get('width', 0)
                height = result_item.get('height', 0)
                
                if final_score >= 8.0:
                    score_text = "⭐ Excellent"
                elif final_score >= 6.0:
                    score_text = "⭐ Good"
                elif final_score >= 4.0:
                    score_text = "⭐ Average"
                else:
                    score_text = "⭐ Needs improvement"
                
                if content_type == 'MAIN_PRODUCT':
                    type_text = "🏷 Main product photo"
                elif content_type == 'MIXED':
                    type_text = "🎯 Mixed content"
                elif content_type == 'DETAILS_ONLY':
                    type_text = "🎯 Detail view"
                else:
                    type_text = f"🎯 {content_type}"
                
                analysis_result += f"\n🥇 PHOTO #{i}: {filename}\n   {score_text}\n   {type_text}\n   📐 Dimensions: {width} × {height}\n"
            
            analysis_result += "\n" + "=" * 50 + "\n🎉 AI selected the best photos for your product!\n"
            
            html_results = f'''
            <div style="background: white; padding: 20px; border-radius: 10px; margin-bottom: 20px;">
                <h4>🎯 AI Analysis Results</h4>
                <pre style="background: #f8f9fa; padding: 15px; border-radius: 5px; overflow-x: auto; max-height: 400px;">{analysis_result}</pre>
            </div>
            '''
            
            return jsonify({
                'status': 'completed', 
                'html': html_results,
                'message': 'Analysis completed!'
            })
        else:
            return jsonify({'status': 'error', 'error': result['error']})
    else:
        return jsonify({'status': 'error', 'error': f'Task failed with state: {task.state}'})

if __name__ == '__main__':
    # Для локального использования используем localhost
    app.run(host='0.0.0.0', port=5000, debug=True)
