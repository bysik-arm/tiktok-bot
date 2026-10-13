import telebot
from telebot import types
import requests
# Добавляем модули для фонового веб-сервера
from flask import Flask
from threading import Thread

# Токен вашего бота
BOT_TOKEN = "8843932444:AAG3TWlypvTANbI2ELBBfSRiYB_GEyPyD_M"
bot = telebot.TeleBot(BOT_TOKEN)

# Настройки поставщика SMMPrime
API_URL = "https://smmprime.com" 
API_KEY = "7fdbede913624c23018217e8be7a89f9"

# Объединенный справочник услуг (ID для TikTok)
SERVICES = {
    "likes": {
        "id": 26, 
        "name": "лайков", 
        "price_per_one": 0.05
    },
    "followers": {
        "id": 25, 
        "name": "подписчиков", 
        "price_per_one": 0.15
    },
    "views": {
        "id": 24, 
        "name": "просмотров", 
        "price_per_one": 0.002
    }
}

# Временное хранилище выбранных услуг для пользователей
user_states = {}

# --- БЛОК ВЕБ-СЕРВЕРА ДЛЯ RENDER ---
app = Flask('')

@app.route('/')
def home():
    return "Бот запущен и работает 24/7!"

@app.route('/health')
def health():
    return "OK", 200

def run_server():
    import os
    # Render автоматически передает порт в переменные окружения
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

def keep_alive():
    t = Thread(target=run_server)
    t.start()
# -----------------------------------

# Команда /start
@bot.message_handler(commands=['start'])
def start_cmd(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    btn_likes = types.KeyboardButton("❤️ Заказать Лайки")
    btn_followers = types.KeyboardButton("👥 Заказать Подписчиков")
    btn_views = types.KeyboardButton("👁️ Заказать Просмотры")
    
    markup.add(btn_likes)
    markup.add(btn_followers, btn_views)
    
    bot.send_message(
        message.chat.id, 
        "Привет! Я твой бот-накрутчик TikTok. Выберите, что именно хотите накрутить 👇", 
        reply_markup=markup
    )

# Обработка нажатий на кнопки выбора услуги
@bot.message_handler(func=lambda msg: msg.text in ["❤️ Заказать Лайки", "👥 Заказать Подписчиков", "👁️ Заказать Просмотры"])
def handle_service_choice(message):
    if message.text == "❤️ Заказать Лайки":
        user_states[message.chat.id] = "likes"
    elif message.text == "👥 Заказать Подписчиков":
        user_states[message.chat.id] = "followers"
    elif message.text == "👁️ Заказать Просмотры":
        user_states[message.chat.id] = "views"
        
    service_name = SERVICES[user_states[message.chat.id]]["name"]
    bot.send_message(
        message.chat.id, 
        f"Вы выбрали накрутку {service_name}.\n\nОтправьте ссылку и количество через запятую.\nПример: https://tiktok.com..., 100"
    )

# Принятие ссылки и количества (содержит запятую)
@bot.message_handler(func=lambda msg: "," in msg.text)
def process_order(message):
    chat_id = message.chat.id
    
    if chat_id not in user_states:
        bot.send_message(chat_id, "⚠️ Сначала выберите тип накрутки на кнопках внизу!")
        return
        
    current_service = user_states[chat_id]
    service_id = SERVICES[current_service]["id"]

    try:
        link, quantity = message.text.split(",", 1)
        link = link.strip()
        quantity = int(quantity.strip())
        
        if quantity <= 0:
            raise ValueError
    except ValueError:
        bot.send_message(chat_id, "⚠️ Ошибка! Неверный формат. Напишите строго по шаблону: ссылка, количество")
        return

    bot.send_message(chat_id, "⏳ Отправляем заказ на панель SMMPrime...")

    payload = {
        'key': API_KEY,
        'action': 'add',
        'service': service_id,
        'link': link,
        'quantity': quantity
    }

    try:
        response = requests.post(API_URL, data=payload, timeout=15)
        result = response.json()

        if "order" in result:
            bot.send_message(chat_id, f"✅ Заказ успешно создан!\nID заказа в системе SMMPrime: {result['order']}")
            del user_states[chat_id]
        elif "error" in result:
            bot.send_message(chat_id, f"❌ Ошибка от поставщика: {result['error']}")
        else:
            bot.send_message(chat_id, "❌ Неизвестный ответ от сервера API поставщика.")
            
    except Exception as e:
        bot.send_message(chat_id, f"💥 Ошибка сети или разбора ответа: {str(e)}")

if __name__ == '__main__':
    print("Запуск фонового веб-сервера...")
    keep_alive() # Запускаем веб-сайт, чтобы Render не усыплял бота
    print("Бот успешно запущен в облаке!")
    bot.infinity_polling()
