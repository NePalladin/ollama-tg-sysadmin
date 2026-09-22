import os
import requests
import telebot

TOKEN = os.environ.get('TELEGRAM_TOKEN')
OLLAMA_URL = os.environ.get('OLLAMA_URL')
MODEL_NAME = os.environ.get('MODEL_NAME')

bot = telebot.TeleBot(TOKEN)
bot_info = bot.get_me()

# Простая оперативная память для бота. Ключ - ID чата, значение - список сообщений.
chat_history = {}
MAX_HISTORY = 15 # Сколько последних реплик помнит бот (чтобы не перегружать контекст)

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    chat_id = message.chat.id
    text = message.text
    author = message.from_user.first_name

    # Инициализируем память для нового чата, если её еще нет
    if chat_id not in chat_history:
        chat_history[chat_id] = []

    # Записываем каждое входящее сообщение в историю.
    # Важно подписывать автора, чтобы бот различал людей в групповом чате!
    chat_history[chat_id].append({"role": "user", "content": f"[{author}]: {text}"})

    # Обрезаем историю, чтобы она не разрасталась бесконечно и не сожрала всю память
    if len(chat_history[chat_id]) > MAX_HISTORY:
        chat_history[chat_id].pop(0)

    # Проверяем, нужно ли боту генерировать ответ прямо сейчас
    should_reply = False
    if message.chat.type in ['group', 'supergroup']:
        is_reply_to_bot = message.reply_to_message and message.reply_to_message.from_user.id == bot_info.id
        is_mention = f"@{bot_info.username}" in text
        if is_reply_to_bot or is_mention:
            should_reply = True
    else:
        # В личных сообщениях отвечаем на всё
        should_reply = True

    # Если бот просто "слушает" группу, прерываем выполнение (ответ не генерируем)
    if not should_reply:
        return

    # Отправляем заглушку
    msg = bot.send_message(chat_id, "⏳ Грею ядро...", reply_to_message_id=message.message_id)

    payload = {
        "model": MODEL_NAME,
        "messages": chat_history[chat_id], # Отправляем весь накопленный контекст!
        "stream": False
    }

    try:
        response = requests.post(OLLAMA_URL, json=payload)
        response.raise_for_status()
        data = response.json()
        reply_text = data.get("message", {}).get("content", "Ядро упало в панику, ответа нет.")

        # Сохраняем сгенерированный ответ бота обратно в историю
        chat_history[chat_id].append({"role": "assistant", "content": reply_text})

        # Снова проверяем лимит (вдруг мы вылезли за MAX_HISTORY после ответа)
        if len(chat_history[chat_id]) > MAX_HISTORY:
            chat_history[chat_id].pop(0)

    except Exception as e:
        reply_text = f"Ошибка связи с Ollama: {e}"

    # Заменяем заглушку на готовый текст
    bot.edit_message_text(chat_id=chat_id, message_id=msg.message_id, text=reply_text)

if __name__ == '__main__':
    print("Бот запущен...")
    bot.infinity_polling()
