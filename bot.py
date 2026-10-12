import telebot
from telebot import types
import requests

# Токен вашего бота
BOT_TOKEN = "8843932444:AAE8HqMg3YIy04OBvAGO8Idbi2FPPkY27uk"
bot = telebot.TeleBot(BOT_TOKEN)

# Настройки поставщика SMMPrime
API_URL = "https://smmprime.com"
API_KEY = "7fdbede913624c23018217e8be7a89f9"
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

# ID услуг для TikTok с панели SMMPrime. 
# Внимание: Проверьте в разделе API на сайте smmprime.com актуальные ID, если захотите сменить базу!
SERVICES = {
    "likes": 26,       # Пример ID для: TikTok Лайки
    "followers": 25,   # Пример ID для: TikTok Подписчики
    "views": 24        # Пример ID для: TikTok Просмотры
}

# Временное хранилище выбранных услуг для пользователей
user_states = {}

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
        service_name = "лайков"
    elif message.text == "👥 Заказать Подписчиков":
        user_states[message.chat.id] = "followers"
        service_name = "подписчиков"
    elif message.text == "👁️ Заказать Просмотры":
        user_states[message.chat.id] = "views"
        service_name = "просмотров"
        
    bot.send_message(
        message.chat.id, 
        f"Вы выбрали накрутку {service_name}.\n\nОтправьте ссылку и количество через запятую.\nПример: ссылка на видео, 100"
    )

# Принятие ссылки и количества (содержит запятую)
@bot.message_handler(func=lambda msg: "," in msg.text)
def process_order(message):
    chat_id = message.chat.id
    
    # Проверка, выбрана ли услуга
    if chat_id not in user_states:
        bot.send_message(chat_id, "⚠️ Сначала выберите тип накрутки на кнопках внизу!")
        return
        
    current_service = user_states[chat_id]
    service_id = SERVICES[current_service]

    # Парсинг ссылки и количества
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

    # Отправка POST запроса к SMMPrime по протоколу API v2
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
            # Очищаем состояние пользователя
            del user_states[chat_id]
        elif "error" in result:
            bot.send_message(chat_id, f"❌ Ошибка от поставщика: {result['error']}")
        else:
            bot.send_message(chat_id, "❌ Неизвестный ответ от сервера API поставщика.")
            
    except Exception as e:
        bot.send_message(chat_id, f"💥 Ошибка сети или разбора ответа: {str(e)}")

# Запуск постоянного опроса бота
if __name__ == '__main__':
    print("Бот успешно запущен локально!")
    bot.infinity_polling()
