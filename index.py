import os
from flask import Flask, render_template, send_from_directory

app = Flask(__name__)

# Настройка папки для статических файлов
app.static_folder = 'static'

# Функция для обхода файлов в папке templates и создания URL-адресов
def register_template_routes(app, template_folder='templates_shorts'):
    for root, dirs, files in os.walk(template_folder):
        for filename in files:
            if filename.endswith('.html'):
                template_name = os.path.splitext(filename)[0]
                url = f'/{template_name}'
                # Префикс 'template_' добавлен к имени функции для избежания конфликта с статическим файлом
                app.add_url_rule(url, f'template_{template_name}', lambda t=template_name: render_template(f'{t}.html'))

# Регистрация URL-адресов для всех шаблонов
register_template_routes(app)

# Обслуживание статических файлов
@app.route('/static/<path:filename>')
def static_files(filename):
    return send_from_directory(app.static_folder, filename)

if __name__ == '__main__':
    app.run(debug=True, port="4040")
