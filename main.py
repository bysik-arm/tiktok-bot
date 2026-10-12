import telebot
import requests

# Ваши данные уже вставлены внутри кавычек
TG_TOKEN = '8843932444:AAE8HqMg3YIy04OBvAGO8Idbi2FPPkY27uk'
SMM_API_KEY = "7fdbede913624c23018217e8be7a89f9"
SMM_API_URL ='https://smmprime.com/api/v2' 

bot = telebot.TeleBot(TG_TOKEN)

@bot.message_handler(commands=['start'])
def send_welcome(message):
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    item1 = telebot.types.KeyboardButton('❤️ Заказать Лайки')
    markup.add(item1)
    bot.send_message(message.chat.id, "Привет! Я твой бот-накрутчик TikTok. Нажми кнопку ниже.", reply_markup=markup)

@bot.message_handler(func=lambda message: message.text == '❤️ Заказать Лайки')
def start_order(message):
    msg = bot.send_message(message.chat.id, "Отправь ссылку на видео и количество через запятую.\nПример: ссылка, 100")
    bot.register_next_step_handler(msg, process_order)

def process_order(message):
    try:
        text_data = message.text.split(',')
        tiktok_url = text_data[0].strip()
        quantity = int(text_data[1].strip())
        
        bot.send_message(message.chat.id, f"🔄 Отправляю заказ на {quantity} лайков...")
        
        payload = {
            'key': SMM_API_KEY,
            'action': 'add',
            'service': '101',  # ID услуги на SMM Prime (проверьте в их кабинете)
            'link': tiktok_url,
            'quantity': quantity
        }
        
        response = requests.post(SMM_API_URL, data=payload).json()
        
        if 'order' in response:
            bot.send_message(message.chat.id, f"✅ Успешно! ID заказа: {response['order']}")
        else:
            bot.send_message(message.chat.id, f"❌ Ошибка панели: {response.get('error', 'Неизвестный сбой')}")
            
    except Exception as e:
        bot.send_message(message.chat.id, "❌ Ошибка! Напишите строго через запятую: ссылка, количество")

if __name__ == '__main__':
    print("Бот успешно запущен!")
    bot.infinity_polling()
