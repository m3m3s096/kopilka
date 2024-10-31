import telebot
import requests
import os

API_TOKEN = '8062613447:AAFgOGUckVLXhzB5FAoPlAGUe7nprEnaeiQ'
WEB_APP_URL = 'http://memip.ru:5000'  # Измените на ваш сайт
bot = telebot.TeleBot(API_TOKEN)

def generate_login_link(username):
    return f"{WEB_APP_URL}/login/{username}"

@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, "Welcome! To register, use /register")

@bot.message_handler(commands=['register'])
def register(message):
    username = message.from_user.username
    if username:
        # Проверка существования пользователя через API
        response = requests.get(f"{WEB_APP_URL}/register/{username}")
        if response.status_code == 200:
            login_link = generate_login_link(username)
            bot.reply_to(message, f"Registered! Use this link to log in: {login_link}")
        else:
            bot.reply_to(message, response.json().get('error', 'Error during registration'))
    else:
        bot.reply_to(message, "You do not have a username set. Please set a username in your profile.")

if __name__ == '__main__':
    bot.polling(none_stop=True)
