from flask import Flask, request, redirect, url_for, session, render_template, jsonify
from flask_sqlalchemy import SQLAlchemy
import os

app = Flask(__name__)
app.secret_key = os.urandom(24)

# Настройка базы данных
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Модель пользователя
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    progress = db.Column(db.Integer, default=0)

# Создание базы данных в контексте приложения
with app.app_context():
    db.create_all()

# Главная страница с кликером
@app.route('/')
def index():
    username = session.get('username')
    if username:
        user = User.query.filter_by(username=username).first()
        return render_template('index.html', user=user)
    return redirect(url_for('login'))

# API для получения информации о пользователе
@app.route('/api/user_info', methods=['GET'])
def user_info():
    username = session.get('username')
    if username:
        user = User.query.filter_by(username=username).first()
        if user:
            return jsonify({'username': user.username, 'progress': user.progress})
    return jsonify({'error': 'User not logged in'}), 401

# Логин
@app.route('/login/<username>')
def login(username):
    session['username'] = username
    return redirect(url_for('index'))

# Обработка нажатия кнопки
@app.route('/click', methods=['POST'])
def click():
    username = session.get('username')
    if username:
        user = User.query.filter_by(username=username).first()
        if user:
            user.progress += 1
            db.session.commit()
    return redirect(url_for('index'))

# API для сохранения прогресса пользователя
@app.route('/api/save_progress', methods=['POST'])
def save_progress():
    username = session.get('username')
    if username:
        user = User.query.filter_by(username=username).first()
        if user:
            user.progress = user.progress  # Здесь мы просто подтверждаем, что прогресс не изменился
            db.session.commit()
            return jsonify({'success': True}), 200
    return jsonify({'error': 'User not logged in'}), 401

# Выход
@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('index'))

# Регистрация пользователя
@app.route('/register/<username>')
def register(username):
    if User.query.filter_by(username=username).first() is None:
        new_user = User(username=username, progress=0)
        db.session.add(new_user)
        db.session.commit()
        return jsonify({'success': True, 'message': f'User {username} registered successfully!'})
    return jsonify({'error': 'User already exists'}), 400

if __name__ == '__main__':
    app.run(debug=True, port="5000", host="0.0.0.0")
