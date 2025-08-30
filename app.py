from flask import Flask, render_template, request, jsonify, send_from_directory
import os
import shutil
from universal_smart_selector import UniversalSmartSelector
import tempfile

app = Flask(__name__)

# Папка для загруженных файлов
UPLOAD_FOLDER = 'uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

@app.route('/')
def index():
    return '''
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Smart Photo Selector - AI-Powered Product Photo Analysis</title>
        <style>
            * {
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }
            
            body {
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                line-height: 1.6;
                color: #333;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
            }
            
            .container {
                max-width: 1200px;
                margin: 0 auto;
                padding: 20px;
            }
            
            /* Header */
            .header {
                text-align: center;
                padding: 60px 0;
                color: white;
            }
            
            .header h1 {
                font-size: 3.5rem;
                margin-bottom: 20px;
                text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
                animation: fadeInUp 1s ease-out;
            }
            
            .header .subtitle {
                font-size: 1.5rem;
                opacity: 0.9;
                margin-bottom: 30px;
                animation: fadeInUp 1s ease-out 0.2s both;
            }
            
            .header .emoji {
                font-size: 4rem;
                margin-bottom: 20px;
                animation: bounce 2s infinite;
            }
            
            /* Navigation */
            .nav {
    background: rgba(255,255,255,0.1);
    backdrop-filter: blur(10px);
    border-radius: 50px;
    padding: 15px 30px;
    margin: 20px auto;
    max-width: 600px;
    display: flex;
    justify-content: center;
    gap: 30px;
    animation: fadeInUp 1s ease-out 0.4s both;
    flex-wrap: wrap;
}

.nav a {
    color: white;
    text-decoration: none;
    padding: 10px 20px;
    border-radius: 25px;
    transition: all 0.3s ease;
    font-weight: 500;
    white-space: nowrap;
    display: inline-block;
}

.nav a:hover {
    background: rgba(255,255,255,0.2);
    transform: translateY(-2px);
    box-shadow: 0 5px 15px rgba(0,0,0,0.2);
}

/* Responsive Design для навигации */
@media (max-width: 768px) {
    .nav {
        flex-direction: column;
        gap: 15px;
        max-width: 400px;
    }
    
    .nav a {
        text-align: center;
        width: 100%;
    }
}
            
            /* Main Content */
            .main-content {
                background: white;
                border-radius: 20px;
                padding: 40px;
                margin: 40px 0;
                box-shadow: 0 20px 40px rgba(0,0,0,0.1);
                animation: fadeInUp 1s ease-out 0.6s both;
            }
            
            .section {
                margin-bottom: 50px;
            }
            
            .section h2 {
                font-size: 2.5rem;
                color: #667eea;
                margin-bottom: 20px;
                display: flex;
                align-items: center;
                gap: 15px;
            }
            
            .section h3 {
                font-size: 1.8rem;
                color: #764ba2;
                margin: 30px 0 15px 0;
            }
            
            .section p {
                font-size: 1.1rem;
                margin-bottom: 15px;
                color: #555;
            }
            
            /* Upload Section */
            .upload-section {
                background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
                color: white;
                padding: 40px;
                border-radius: 20px;
                text-align: center;
                margin: 30px 0;
            }
            
            .upload-section h3 {
                font-size: 2rem;
                margin-bottom: 20px;
            }
            
            .file-input {
                display: none;
            }
            
            .file-label {
                background: rgba(255,255,255,0.2);
                color: white;
                padding: 15px 30px;
                border-radius: 25px;
                cursor: pointer;
                display: inline-block;
                font-weight: 600;
                transition: all 0.3s ease;
                margin: 20px 10px;
                border: 2px solid rgba(255,255,255,0.3);
            }
            
            .file-label:hover {
                background: rgba(255,255,255,0.3);
                transform: translateY(-3px);
            }
            
            .btn {
                background: rgba(255,255,255,0.2);
                color: white;
                border: 2px solid rgba(255,255,255,0.3);
                padding: 15px 30px;
                border-radius: 25px;
                font-size: 16px;
                font-weight: 600;
                cursor: pointer;
                transition: all 0.3s ease;
                margin: 10px;
            }
            
            .btn:hover {
                background: rgba(255,255,255,0.3);
                transform: translateY(-3px);
            }
            
            .btn:disabled {
                opacity: 0.6;
                cursor: not-allowed;
            }
            
            /* Features Grid */
            .features-grid {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
                gap: 30px;
                margin: 30px 0;
            }
            
            .feature-card {
                background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
                color: white;
                padding: 30px;
                border-radius: 15px;
                text-align: center;
                transition: transform 0.3s ease;
                box-shadow: 0 10px 20px rgba(0,0,0,0.1);
            }
            
            .feature-card:hover {
                transform: translateY(-10px);
            }
            
            .feature-card .emoji {
                font-size: 3rem;
                margin-bottom: 20px;
            }
            
            .feature-card h4 {
                font-size: 1.5rem;
                margin-bottom: 15px;
            }
            
            /* Code Blocks */
            .code-block {
                background: #2d3748;
                color: #e2e8f0;
                padding: 20px;
                border-radius: 10px;
                margin: 20px 0;
                overflow-x: auto;
                font-family: 'Courier New', monospace;
            }
            
            .code-block code {
                color: #68d391;
            }
            
            .code-block .comment {
                color: #a0aec0;
            }
            
            /* Results */
            .results {
    background: #f8f9fa;
    border-radius: 15px;
    padding: 30px;
    margin-top: 30px;
    display: none;
    border: 2px solid #28a745;
    box-shadow: 0 10px 25px rgba(0,0,0,0.1);
}

.results.show {
    display: block !important;
    animation: fadeIn 0.5s ease-in;
}

@keyframes fadeIn {
    from { opacity: 0; transform: translateY(20px); }
    to { opacity: 1; transform: translateY(0); }
}

#resultsContent {
    background: white;
    padding: 20px;
    border-radius: 10px;
    margin: 20px 0;
    border: 1px solid #dee2e6;
}
            /* Stats */
            .stats {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                gap: 20px;
                margin: 30px 0;
            }
            
            .stat-item {
                text-align: center;
                padding: 20px;
                background: linear-gradient(135deg, #a8edea 0%, #fed6e3 100%);
                border-radius: 15px;
                color: #333;
            }
            
            .stat-number {
                font-size: 2.5rem;
                font-weight: bold;
                color: #667eea;
            }
            
            .stat-label {
                font-size: 1.1rem;
                color: #666;
            }
            
            /* Footer */
            .footer {
                text-align: center;
                padding: 40px 0;
                color: white;
                animation: fadeInUp 1s ease-out 0.8s both;
            }
            
            .footer .social-links {
                margin: 20px 0;
            }
            
            .footer .social-links a {
                color: white;
                font-size: 1.5rem;
                margin: 0 15px;
                text-decoration: none;
                transition: transform 0.3s ease;
            }
            
            .footer .social-links a:hover {
                transform: scale(1.2);
            }
            
            /* Animations */
            @keyframes fadeInUp {
                from {
                    opacity: 0;
                    transform: translateY(30px);
                }
                to {
                    opacity: 1;
                    transform: translateY(0);
                }
            }
            
            @keyframes bounce {
                0%, 20%, 50%, 80%, 100% {
                    transform: translateY(0);
                }
                40% {
                    transform: translateY(-10px);
                }
                60% {
                    transform: translateY(-5px);
                }
            }
            
            /* Responsive Design */
            @media (max-width: 768px) {
                .header h1 {
                    font-size: 2.5rem;
                }
                
                .nav {
                    flex-direction: column;
                    gap: 15px;
                }
                
                .main-content {
                    padding: 20px;
                }
                
                .features-grid {
                    grid-template-columns: 1fr;
                }
            }
        </style>
    </head>
    <body>
        <div class="container">
            <!-- Header -->
            <header class="header">
                <div class="emoji">📸</div>
                <h1>Smart Photo Selector</h1>
                <p class="subtitle">AI-Powered Product Photo Analysis with ConvNeXt Large</p>
                <p>Automatically select the best product photos using intelligent rules and machine learning</p>
            </header>

            <!-- Navigation -->
            <nav class="nav">
                <a href="#features">Features</a>
                <a href="#how-it-works">How It Works</a>
                <a href="#upload">Upload & Analyze</a>
                <a href="#installation">Installation</a>
                <a href="#usage">Usage</a>
                <a href="#github">GitHub</a>
            </nav>

            <!-- Main Content -->
<main class="main-content">
    <!-- Features Section -->
<section id="features" class="section">
    <h2>🚀 Features</h2>
    <div class="features-grid">
        <div class="feature-card">
            <div class="emoji">🤖</div>
            <h4>AI-Powered Analysis</h4>
            <p>Uses ConvNeXt Large model with 86.6% accuracy for intelligent photo analysis</p>
        </div>
        <div class="feature-card">
            <div class="emoji">🧠</div>
            <h4>Smart Rules</h4>
            <p>Automatic rules for content analysis, viewpoint detection, and quality assessment</p>
        </div>
        <div class="feature-card">
            <div class="emoji">📁</div>
            <h4>Batch Processing</h4>
            <p>Process multiple folders automatically with structured output organization</p>
        </div>
        <div class="feature-card">
            <div class="emoji">🎯</div>
            <h4>Intelligent Selection</h4>
            <p>Smart filtering to exclude details, mixed product types, and poor angles</p>
        </div>
    </div>
</section>
    ...
</main>

                <!-- Upload Section -->
                <section id="upload" class="section">
                    <h2>📁 Upload & Analyze Photos</h2>
                    <div class="upload-section">
                        <h3>🚀 Загрузите папку с фотографиями для AI анализа</h3>
                        <p>Выберите папку, содержащую фотографии товаров для автоматического выбора лучших</p>
                        
                        <form id="uploadForm">
                            <input type="file" id="folderInput" class="file-input" webkitdirectory directory multiple>
                            <label for="folderInput" class="file-label">📁 Выбрать папку с фотографиями</label>
                            
                            <div id="fileList" style="margin-top: 20px; text-align: left; background: rgba(255,255,255,0.1); padding: 20px; border-radius: 10px;"></div>
                            
                            <button type="submit" class="btn" id="analyzeBtn" disabled>
                                🤖 AI Анализ фотографий
                            </button>
                        </form>
                    </div>
                </section>

                <!-- How It Works Section -->
                <section id="how-it-works" class="section">
                    <h2>⚙️ How It Works</h2>

                    <h3>1. AI Analysis</h3>
                    <p>The system loads the ConvNeXt Large model and analyzes each photograph to determine content and viewpoint.</p>

                    <h3>2. Smart Rules</h3>
                    <p>Automatic rules ensure the first photo shows only the main product without details, while the second photo can be complementary.</p>

                    <h3>3. Quality Assessment</h3>
                    <p>Photos are evaluated based on resolution, aspect ratio, technical quality, and AI analysis results.</p>

                    <h3>4. Intelligent Selection</h3>
                    <p>Photos are sorted by quality, content, and viewpoint to select the best ones for product presentation.</p>
                </section>

                <!-- Installation Section -->
                <section id="installation" class="section">
                    <h2>📦 Installation</h2>

                    <h3>Requirements</h3>
                    <div class="code-block">
                        <code>pip install -r requirements.txt</code>
                    </div>

                    <h3>Clone Repository</h3>
                    <div class="code-block">
                        <code>git clone https://github.com/Nastya84-a/smart-photo-selector.git</code><br>
                        <code>cd smart-photo-selector</code>
                    </div>

                    <h3>Download AI Model</h3>
                    <div class="code-block">
                        <code>python fix_model_download.py</code>
                    </div>
                </section>

                <!-- Usage Section -->
                <section id="usage" class="section">
                    <h2>🎯 Usage</h2>

                    <h3>Analyze Single Folder</h3>
                    <div class="code-block">
                        <code>python smart_photo_selector.py "fotos/1/big"</code>
                    </div>

                    <h3>Batch Analysis</h3>
                    <div class="code-block">
                        <code>python smart_analyze_all.py</code>
                    </div>

                    <h3>Example Results</h3>
                    <p>The system automatically selects and saves the best photos in organized folders:</p>
                    <ul style="margin-left: 20px; margin-bottom: 20px;">
                        <li><strong>Folder 1:</strong> image_005.jpg (first), image_003.jpg (second)</li>
                        <li><strong>Folder 2:</strong> image_006.jpg (first), image_004.jpg (second)</li>
                        <li><strong>Folder 3:</strong> Automatic selection based on AI analysis</li>
                        <li><strong>Folder 4:</strong> Automatic selection with smart rules</li>
                    </ul>
                </section>

                <!-- Performance Stats -->
                <section class="section">
                    <h2>📊 Performance</h2>
                    <div class="stats">
                        <div class="stat-item">
                            <div class="stat-number">86.6%</div>
                            <div class="stat-label">AI Accuracy</div>
                        </div>
                        <div class="stat-item">
                            <div class="stat-number">2-3s</div>
                            <div class="stat-label">Per Photo</div>
                        </div>
                        <div class="stat-item">
                            <div class="stat-number">500MB</div>
                            <div class="stat-label">Memory Usage</div>
                        </div>
                        <div class="stat-item">
                            <div class="stat-number">∞</div>
                            <div class="stat-label">Scalability</div>
                        </div>
                    </div>
                </section>

                <!-- GitHub Section -->
                <section id="github" class="section">
                    <h2>📚 GitHub Repository</h2>
                    <p>This project is open source and available on GitHub with comprehensive documentation, examples, and installation instructions.</p>

                    <div style="text-align: center; margin: 30px 0;">
                        <a href="https://github.com/Nastya84-a/smart-photo-selector" class="btn" target="_blank" style="text-decoration: none; display: inline-block;">
                            🌟 View on GitHub
                        </a>
                        <a href="https://github.com/Nastya84-a/smart-photo-selector/archive/refs/heads/main.zip" class="btn" download style="text-decoration: none; display: inline-block;">
                            📥 Download ZIP
                        </a>
                    </div>

                    <h3>Repository Features</h3>
                    <ul style="margin-left: 20px; margin-bottom: 20px;">
                        <li>Complete source code with AI integration</li>
                        <li>Detailed README with examples</li>
                        <li>Requirements and dependencies</li>
                        <li>Installation and usage instructions</li>
                        <li>Performance benchmarks and results</li>
                    </ul>
                </section>

                <!-- Results Section -->
                <div id="loading" class="loading" style="display: none;">
                    <div class="spinner"></div>
                    <p>�� AI анализирует фотографии...</p>
                    <p>Это может занять несколько минут</p>
                </div>
                
                <div id="results" class="results">
                    <h3>🎯 Результаты AI анализа</h3>
                    <div id="resultsContent"></div>
                    <button onclick="resetForm()" class="btn">🔄 Новый анализ</button>
                </div>
                
                <div id="error" class="error" style="display: none;"></div>
            </main>

            <!-- Footer -->
            <footer class="footer">
                <h3>Smart Photo Selector</h3>
                <p>AI-Powered Product Photo Analysis Tool</p>

                <div class="social-links">
                    <a href="https://github.com/Nastya84-a" target="_blank" title="GitHub Profile">📚</a>
                    <a href="https://github.com/Nastya84-a/smart-photo-selector" target="_blank" title="Project Repository">📸</a>
                    <a href="https://huggingface.co/facebook/convnext-large-224" target="_blank" title="AI Model">🤖</a>
                </div>

                <p>&copy; 2024 Anastasiia (Nastya84-a). All rights reserved.</p>
                <p>Built with ❤️ using Python, ConvNeXt Large, and modern web technologies</p>
            </footer>
        </div>
        
        <script>
    const folderInput = document.getElementById('folderInput');
    const fileList = document.getElementById('fileList');
    const analyzeBtn = document.getElementById('analyzeBtn');
    const uploadForm = document.getElementById('uploadForm');
    const loading = document.getElementById('loading');
    const results = document.getElementById('results');
    const error = document.getElementById('error');
    
    console.log('JavaScript загружен!');
    
    folderInput.addEventListener('change', function(e) {
        console.log('Файлы выбраны:', e.target.files.length);
        const files = Array.from(e.target.files);
        if (files.length > 0) {
            fileList.innerHTML = `<strong style="color: white;">�� Выбрано файлов: ${files.length}</strong><br>`;
            files.forEach(file => {
                fileList.innerHTML += `<span style="color: white;">�� ${file.name}</span><br>`;
            });
            analyzeBtn.disabled = false;
            console.log('Кнопка активирована');
        } else {
            fileList.innerHTML = '';
            analyzeBtn.disabled = true;
        }
    });
    
    uploadForm.addEventListener('submit', async function(e) {
        e.preventDefault();
        console.log('Форма отправлена!');
        
        const files = Array.from(folderInput.files);
        if (files.length === 0) {
            console.log('Нет файлов для загрузки');
            return;
        }
        
        console.log('Начинаю загрузку файлов...');
        
        // Показываем загрузку
        loading.style.display = 'block';
        results.style.display = 'none';
        error.style.display = 'none';
        
        // Создаем FormData
        const formData = new FormData();
        files.forEach(file => {
            formData.append('files', file);
            console.log('Добавляю файл:', file.name);
        });
        
        try {
            console.log('Отправляю запрос на /upload...');
            const response = await fetch('/upload', {
                method: 'POST',
                body: formData
            });
            
            console.log('Ответ получен:', response.status);
            
            if (response.ok) {
                const data = await response.json();
                console.log('Данные получены:', data);
                
                if (data.success) {
                    console.log('Показываю результаты...');
                    
                    // Показываем alert с информацией о результатах
                    alert('✅ Результаты готовы!\n\nHTML длина: ' + data.html.length + ' символов\n\nПроверьте страницу ниже!');
                    
                    document.getElementById('resultsContent').innerHTML = data.html;
                    results.style.display = 'block';
                    results.classList.add('show');
                    console.log('Результаты показаны!');
                } else {
                    console.log('Ошибка в данных:', data.error);
                    throw new Error(data.error);
                }
            } else {
                console.log('Ошибка HTTP:', response.status);
                throw new Error('Ошибка сервера: ' + response.status);
            }
        } catch (err) {
            console.log('Ошибка:', err.message);
            error.textContent = '❌ Ошибка: ' + err.message;
            error.style.display = 'block';
        } finally {
            console.log('Скрываю загрузку');
            loading.style.display = 'none';
        }
    });
    
    function resetForm() {
        console.log('Сброс формы');
        folderInput.value = '';
        fileList.innerHTML = '';
        analyzeBtn.disabled = true;
        results.style.display = 'none';
        error.style.display = 'none';
    }
    
    // Smooth scrolling for navigation links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });
    
    console.log('Все обработчики событий настроены!');
</script>
    </body>
    </html>
    '''

@app.route('/upload', methods=['POST'])
def upload_files():
    try:
        print("=== НАЧАЛО ЗАГРУЗКИ ===")
        
        if 'files' not in request.files:
            print("❌ Файлы не найдены в request.files")
            return jsonify({'success': False, 'error': 'Файлы не загружены'})
        
        files = request.files.getlist('files')
        print(f" Получено файлов: {len(files)}")
        
        if not files:
            print("❌ Список файлов пуст")
            return jsonify({'success': False, 'error': 'Файлы не выбраны'})
        
        # Создаем временную папку для загруженных файлов
        with tempfile.TemporaryDirectory() as temp_dir:
            print(f"📂 Создана временная папка: {temp_dir}")
            
            # Сохраняем файлы во временную папку
            saved_files = []
            for i, file in enumerate(files):
                if file.filename:
                    print(f" Обрабатываю файл {i+1}: {file.filename}")
                    
                    # Исправляем пути - заменяем слеши на правильные
                    safe_filename = file.filename.replace('/', os.sep).replace('\\', os.sep)
                    file_path = os.path.join(temp_dir, safe_filename)
                    
                    print(f"🔧 Безопасное имя: {safe_filename}")
                    print(f" Полный путь: {file_path}")
                    
                    # Создаем папки если нужно
                    dir_path = os.path.dirname(file_path)
                    if dir_path != temp_dir:
                        print(f" Создаю папку: {dir_path}")
                        os.makedirs(dir_path, exist_ok=True)
                    
                    # Сохраняем файл
                    file.save(file_path)
                    saved_files.append(file_path)
                    
                    # Проверяем что файл сохранился
                    if os.path.exists(file_path):
                        file_size = os.path.getsize(file_path)
                        print(f"✅ Файл сохранен: {file_path} ({file_size} байт)")
                    else:
                        print(f"❌ Файл НЕ сохранен: {file_path}")
                else:
                    print(f"⚠️ Файл {i+1} без имени")
            
            print(f"📊 Всего сохранено файлов: {len(saved_files)}")
            
            # Проверяем содержимое временной папки
            print(f"🔍 Содержимое временной папки {temp_dir}:")
            for root, dirs, files_in_dir in os.walk(temp_dir):
                level = root.replace(temp_dir, '').count(os.sep)
                indent = ' ' * 2 * level
                print(f"{indent}{os.path.basename(root)}/")
                subindent = ' ' * 2 * (level + 1)
                for file_in_dir in files_in_dir:
                    file_full_path = os.path.join(root, file_in_dir)
                    file_size = os.path.getsize(file_full_path)
                    print(f"{subindent}{file_in_dir} ({file_size} байт)")
            
            # Проверяем что файлы сохранились
            if not saved_files:
                print("❌ Нет сохраненных файлов")
                return jsonify({'success': False, 'error': 'Файлы не сохранились'})
            
            # Показываем информацию о загруженных файлах
            file_info = f"Загружено файлов: {len(saved_files)}\n"
            file_info += f"Временная папка: {temp_dir}\n"
            file_info += "Список файлов:\n"
            for file_path in saved_files:
                if os.path.exists(file_path):
                    file_size = os.path.getsize(file_path)
                    file_info += f"- {os.path.basename(file_path)} ({file_size} байт)\n"
                else:
                    file_info += f"- {os.path.basename(file_path)} (ФАЙЛ НЕ НАЙДЕН!)\n"
            
            # Показываем содержимое временной папки
            temp_contents = []
            for root, dirs, files_in_dir in os.walk(temp_dir):
                for file_in_dir in files_in_dir:
                    file_full_path = os.path.join(root, file_in_dir)
                    temp_contents.append(file_full_path)
            
            file_info += f"\nВсего файлов в папке: {len(temp_contents)}\n"
            file_info += "Содержимое:\n"
            for file_path in temp_contents:
                file_size = os.path.getsize(file_path)
                file_info += f"- {file_path} ({file_size} байт)\n"
            
         # Пробуем проанализировать фотографии
            try:                            # Пробуем разные пути - добавляем все возможные подпапки
                            analysis_paths = [
                                temp_dir,  # Корневая папка
                                os.path.join(temp_dir, '9'),  # Папка 9
                                os.path.join(temp_dir, '9', 'big'),  # Папка 9/big
                                os.path.join(temp_dir, '9', 'small'),  # Папка 9/small
                                os.path.join(temp_dir, 'big'),  # Папка big (если есть)
                                os.path.join(temp_dir, 'small')  # Папка small (если есть)
                            ]
                            
                            # Добавляем все найденные подпапки
                            for root, dirs, files_in_dir in os.walk(temp_dir):
                                for dir_name in dirs:
                                    full_dir_path = os.path.join(root, dir_name)
                                    if full_dir_path not in analysis_paths:
                                        analysis_paths.append(full_dir_path)
                                        print(f"🔍 Добавлен путь для анализа: {full_dir_path}")
                            
                            print(f"🎯 Всего путей для анализа: {len(analysis_paths)}")
                            
                            analysis_success = False
                            for path in analysis_paths:
                                if os.path.exists(path):
                                    print(f"🎯 Пробую проанализировать путь: {path}")
                                    try:
                                        # Проверяем что в папке есть изображения
                                        path_files = []
                                        for root, dirs, files_in_dir in os.walk(path):
                                            for file_in_dir in files_in_dir:
                                                file_full_path = os.path.join(root, file_in_dir)
                                                file_ext = os.path.splitext(file_in_dir)[1].lower()
                                                if file_ext in image_extensions:
                                                    path_files.append(file_full_path)
                                        
                                        if path_files:
                                            print(f"🖼️ В пути {path} найдено {len(path_files)} изображений")
                                            try:
                                                results = selector.select_best_photos(path, 2)
                                                if results and str(results).strip():
                                                    analysis_result = f"AI анализ завершен!\n\nПуть анализа: {path}\n\nНайдено изображений в пути: {len(path_files)}\n\nРезультаты:\n{results}"
                                                    print(f"✅ select_best_photos работает с путем: {path}")
                                                    analysis_success = True
                                                    break
                                                else:
                                                    print(f"⚠️ select_best_photos вернул пустой результат для пути: {path}")
                                            except Exception as e:
                                                print(f"❌ select_best_photos не работает с путем {path}: {str(e)}")
                                                continue
                                        else:
                                            print(f"⚠️ В пути {path} нет изображений")
                                            continue
                                    except Exception as e:
                                        print(f"❌ Ошибка при проверке пути {path}: {str(e)}")
                                        continue
                            
                            if not analysis_success:
                                # Если все пути не сработали
                                analysis_result = f"AI анализ не удался для всех путей.\n\nНайдено изображений: {len(image_files)}\n\nПопробованные пути:\n"
                                for path in analysis_paths:
                                    if os.path.exists(path):
                                        analysis_result += f"- {path}\n"
                                
                                analysis_result += f"\nДля полного анализа используйте командную строку:\npython universal_smart_selector.py {temp_dir}"
                                
            except Exception as e:
                            print(f"❌ Ошибка при анализе: {str(e)}")
                            analysis_result = f"Ошибка при анализе: {str(e)}\n\nНайдено изображений: {len(image_files)}\n\nДля полного анализа используйте командную строку:\npython universal_smart_selector.py {temp_dir}"
        print("=== КОНЕЦ ЗАГРУЗКИ ===")
            
            # Форматируем результаты в HTML
        html_results = f'''
            <div style="background: white; padding: 20px; border-radius: 10px; margin-bottom: 20px;">
                <h4>🎯 Результаты загрузки и анализа</h4>
                <pre style="background: #f8f9fa; padding: 15px; border-radius: 5px; overflow-x: auto; max-height: 400px;">{final_results}</pre>
            </div>
            '''
            
        return jsonify({
                'success': True,
                'html': html_results
            })
            
    except Exception as e:
        print(f"❌ Общая ошибка: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        })
if __name__ == '__main__':
    print("🌐 Запускаю веб-сервер на http://localhost:3000")
    print("📸 Красивый сайт с функционалом загрузки готов!")
    app.run(host='localhost', port=3000, debug=True)
