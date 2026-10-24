import telebot
import random
import uuid
import time
from telebot import types

BOT_TOKEN = "8997952716:AAG7XAEhK9HZQgqSoARA5H7KhddYNQvMMRE"
OWNER_ID = 7838553850

bot = telebot.TeleBot(BOT_TOKEN)

# Временная база данных для текстовых игр
guess_number_game = {"active": False, "number": None, "range": (0, 0)}
clash_game = {"active": False}

def format_time(seconds: int) -> str:
    if seconds >= 60:
        minutes = seconds // 60
        rem_seconds = seconds % 60
        return f"{minutes} мин." if rem_seconds == 0 else f"{minutes} мин. {rem_seconds} сек."
    return f"{seconds} сек."

@bot.message_handler(content_types=['dice'])
def handle_dice(message):
    if message.dice.emoji != "🎰":
        return
        
    value = message.dice.value
    user_id = message.from_user.id
    
    # Ждем анимацию слотов
    time.sleep(2.0)
    
    if value == 64:  # Выпало 777
        bot.reply_to(message, "🎉 Молодец, ты выбил 777!\nПеред тобой 25 ячеек, выбери одну и получай приз!")
        
        game_id = str(uuid.uuid4())[:8]
        is_nft = random.randint(1, 1000) == 777
        
        if is_nft:
            pool = ["NFT 🍊"] + ["🧸"] * 11 + ["🌹"] * 10 + ["🚀"] * 3
        else:
            pool = ["🧸"] * 11 + ["🌹"] * 11 + ["🚀"] * 3
            
        random.shuffle(pool)
        
        markup = types.InlineKeyboardMarkup(row_width=5)
        buttons = []
        pool_str = "".join(pool).replace("NFT 🍊", "N")
        for i in range(25):
            prize_code = pool[i]
            buttons.append(types.InlineKeyboardButton(text="❓", callback_data=f"c7:{user_id}:{game_id}:{prize_code}:{i}:{pool_str}"))
        markup.add(*buttons)
        bot.send_message(message.chat.id, "Выбирай ячейку 👇", reply_markup=markup)
        
    elif value in:  # Другие комбинации (бары, виноград, лимоны)
        bot.reply_to(message, "🔥 Молодец! Ты выбил комбинацию!\nПеред тобой 3 ячейки, выбери одну. Если выберешь правильную — ты получишь мишку!")
        
        game_id = str(uuid.uuid4())[:8]
        slots_3 = ["❌", "❌", "❌"]
        slots_3[random.randint(0, 2)] = "🧸"
        
        markup = types.InlineKeyboardMarkup(row_width=3)
        buttons = []
        pool_str = "".join(slots_3)
        for i in range(3):
            buttons.append(types.InlineKeyboardButton(text="❓", callback_data=f"c3:{user_id}:{game_id}:{slots_3[i]}:{pool_str}"))
        markup.add(*buttons)
        bot.send_message(message.chat.id, "Выбирай ячейку 👇", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith('c7:'))
def process_777_click(call):
    data = call.data.split(":")
    owner_id = int(data[1])
    chosen_prize = data[3]
    chosen_idx = int(data[4])
    pool_str = data[5]
    
    if call.from_user.id != owner_id:
        bot.answer_callback_query(call.id, "не ну не ты же выйграл", show_alert=True)
        return
        
    all_prizes = ["NFT 🍊" if char == "N" else char for char in pool_str]
    revealed_text = "Вот что скрывалось в ячейках:\n"
    for idx, prize in enumerate(all_prizes):
        revealed_text += f"👉[{prize}]👈 " if idx == chosen_idx else f"{prize} "
        if (idx + 1) % 5 == 0:
            revealed_text += "\n"
            
    bot.edit_message_text(revealed_text, call.message.chat.id, call.message.message_id)
    
    if chosen_prize in ["N", "NFT 🍊"]:
        bot.send_message(call.message.chat.id, "🌟 Ничего себе! Ты выиграл уникальный NFT 🍊! Улучшению не подлежит.")
    else:
        prize_map = {"🧸": "мишку", "🌹": "розу", "🚀": "ракету"}
        bot.send_message(call.message.chat.id, f"Молодец ты выйграл {prize_map.get(chosen_prize, '')} хочешь улучшить?")
        
        markup = types.InlineKeyboardMarkup(row_width=2)
        markup.add(
            types.InlineKeyboardButton(text="Да ✅", callback_data=f"up:yes:{owner_id}:{chosen_prize}"),
            types.InlineKeyboardButton(text="Нет ❌", callback_data=f"up:no:{owner_id}:none")
        )
        bot.send_message(call.message.chat.id, "Сделай выбор:", reply_markup=markup)
    bot.answer_callback_query(call.id)

@bot.callback_query_handler(func=lambda call: call.data.startswith('up:'))
def process_upgrade(call):
    data = call.data.split(":")
    choice = data[1]
    owner_id = int(data[2])
    current_item = data[3]
    
    if call.from_user.id != owner_id:
        bot.answer_callback_query(call.id, "не ну не ты же выйграл", show_alert=True)
        return
        
    if choice == "no":
        bot.edit_message_text("Ты решил забрать свой текущий подарок! 🎁", call.message.chat.id, call.message.message_id)
        bot.answer_callback_query(call.id)
        return
        
    next_item_map = {"🧸": ("🌹", "розы"), "🌹": ("🚀", "ракеты")}
    if current_item not in next_item_map:
        bot.edit_message_text("Этот предмет нельзя улучшить дальше! 🏆", call.message.chat.id, call.message.message_id)
        bot.answer_callback_query(call.id)
        return
        
    next_item_emoji, next_item_name = next_item_map[current_item]
    bounce_msg = bot.send_dice(call.message.chat.id, emoji="🏀")
    time.sleep(3.5)
    
    if bounce_msg.dice.value in:
        bot.send_message(call.message.chat.id, f"Молодец ты улучшил подарок до {next_item_name} хочешь продолжить?")
        markup = types.InlineKeyboardMarkup(row_width=2)
        markup.add(
            types.InlineKeyboardButton(text="Да ✅", callback_data=f"up:yes:{owner_id}:{next_item_emoji}"),
            types.InlineKeyboardButton(text="Нет ❌", callback_data=f"up:no:{owner_id}:none")
        )
        bot.send_message(call.message.chat.id, "Сделай выбор:", reply_markup=markup)
    else:
        bot.send_message(call.message.chat.id, "К сожелению ты не попал удачи в следующий раз! 💔")
    bot.answer_callback_query(call.id)

@bot.callback_query_handler(func=lambda call: call.data.startswith('c3:'))
def process_3_click(call):
    data = call.data.split(":")
    owner_id = int(data[1])
    chosen_prize = data[3]
    pool_str = data[5]
    
    if call.from_user.id != owner_id:
        bot.answer_callback_query(call.id, "не ну не ты же выйграл", show_alert=True)
        return
        
    all_prizes = [char for char in pool_str]
    revealed_text = f"Результат: Кто где прятался: {' | '.join(all_prizes)}\n\n"
    
    if chosen_prize == "🧸":
        bot.edit_message_text(revealed_text + "Поздравляю! Ты выбил мишку скоро отправим подарок🧸!", call.message.chat.id, call.message.message_id)
    else:
        bot.edit_message_text(revealed_text + "К сожелению ты не выйграл но у тебя точно скоро получится! 🍀", call.message.chat.id, call.message.message_id)
    bot.answer_callback_query(call.id)

@bot.message_handler(commands=['начать'])
def start_games(message):
    if message.from_user.id != OWNER_ID:
        return
        
    args = message.text.replace("/начать", "").strip()
    if not args:
        return
        
    if args.startswith("перебив"):
        try:
            params = args.replace("перебив ", "", 1).split(" ")
            price = params[0]
            seconds = int(params[1])
            prize = " ".join(params[2:])
            
            clash_game["active"] = True
            bot.send_message(message.chat.id, f"📣 **Перебив начался!**\n\nЦена за сообщение в чате: {price}⭐\nВремя на перебив: {format_time(seconds)}\nПриз: *{prize}*", parse_mode="Markdown")
            
            time.sleep(seconds)
            if clash_game["active"]:
                bot.send_message(message.chat.id, "⏳ Время перебива вышло! Игра окончена.")
                clash_game["active"] = False
        except Exception:
            bot.reply_to(message, "❌ Ошибка! Пример: `/начать перебив 1 30 ракета бомба`")
            
    elif args.startswith("угадай число"):
        try:
            range_part = args.replace("угадай число ", "", 1).strip()
            start, end = map(int, range_part.split("-"))
            secret_number = random.randint(start, end)
            guess_number_game.update({"active": True, "number": secret_number, "range": (start, end)})
            bot.send_message(message.chat.id, f"🎲 Игра «Угадай число» запущена! Диапазон: от {start} до {end}. Пишите варианты!")
            try:
                bot.send_message(OWNER_ID, f"🤫 Загаданное число: **{secret_number}**")
            except Exception:
                bot.reply_to(message, "⚠️ Владелец, напиши мне в ЛС (/start) для получения секретных чисел!")
        except Exception:
            bot.reply_to(message, "❌ Ошибка! Пример: `/начать угадай число 1-1000`")

@bot.message_handler(func=lambda message: message.text and message.text.isdigit())
def check_guessed_number(message):
    if not guess_number_game["active"]:
        return
    user_guess = int(message.text)
    secret = guess_number_game["number"]
    start, end = guess_number_game["range"]
    
    if start <= user_guess <= end and user_guess == secret:
        name = message.from_user.username or message.from_user.first_name
        bot.reply_to(message, f"🎉 Поздравляем! @{name} угадал число **{secret}**!")
        guess_number_game["active"] = False

if __name__ == "__main__":
    bot.infinity_polling()
    
