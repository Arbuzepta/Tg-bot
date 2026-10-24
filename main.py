import telebot
import random
import uuid
import time
import asyncio
from telebot import types

BOT_TOKEN = "8997952716:AAG7XAEhK9HZQgqSoARA5H7KhddYNQvMMRE"
OWNER_ID = 7838553850

bot = telebot.TeleBot(BOT_TOKEN)

active_slots_games = {}
guess_number_game = {"active": False, "number": None, "range": (0, 0), "prize": ""}
clash_game = {"active": False, "time_left": 0, "price": "1", "prize": "", "chat_id": None, "last_user": None, "countdown_msg_id": None}

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
    time.sleep(2.0)
    
    # 🎰 ВЫПАЛО 777
    if value == 64:
        bot.reply_to(message, "🎉 Молодец, ты выбил 777!\nПеред тобой 25 ячеек, выбери одну и получай приз!")
        game_id = str(uuid.uuid4())[:8]
        
        # NFT теперь ВСЕГДА генерируется в одной из ячеек на поле!
        pool = ["NFT 🍊"] + ["🧸"] * 10 + ["🌹"] * 11 + ["🚀"] * 3
        random.shuffle(pool)
        active_slots_games[game_id] = pool
        
        markup = types.InlineKeyboardMarkup(row_width=5)
        buttons = [types.InlineKeyboardButton(text="❓", callback_data=f"g7:{user_id}:{game_id}:{i}") for i in range(25)]
        markup.add(*buttons)
        bot.send_message(message.chat.id, "Выбирай ячейку 👇", reply_markup=markup)
        
    # 🍓 ВЫПАЛИ ДРУГИЕ КОМБИНАЦИИ (бары=1, виноград=22, лимоны=43)
    elif value in:
        bot.reply_to(message, "🔥 Молодец! Ты выбил комбинацию!\nПеред тобой 3 ячейки, выбери одну. Если выберешь правильную — ты получишь мишку!")
        game_id = str(uuid.uuid4())[:8]
        slots_3 = ["❌", "❌", "❌"]
        slots_3[random.randint(0, 2)] = "🧸"
        active_slots_games[game_id] = slots_3
        
        markup = types.InlineKeyboardMarkup(row_width=3)
        buttons = [types.InlineKeyboardButton(text="❓", callback_data=f"g3:{user_id}:{game_id}:{i}") for i in range(3)]
        markup.add(*buttons)
        bot.send_message(message.chat.id, "Выбирай ячейку 👇", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith('g7:'))
def process_777_click(call):
    data = call.data.split(":")
    owner_id, game_id, chosen_idx = int(data[1]), data[2], int(data[3])
    
    if call.from_user.id != owner_id:
        bot.answer_callback_query(call.id, "не ну не ты же выйграл", show_alert=True)
        return
        
    if game_id not in active_slots_games:
        bot.answer_callback_query(call.id, "Игра завершена ❌", show_alert=True)
        return
        
    all_prizes = active_slots_games[game_id]
    chosen_prize = all_prizes[chosen_idx]
    
    # Расчет супер-шанса 0.001% (1 к 1000) при клике на ячейку с NFT
    if chosen_prize == "NFT 🍊":
        win_nft = random.randint(1, 1000) == 777
        if not win_nft:
            chosen_prize = "🧸"  # Если не повезло, подменяем выигрыш на мишку
            all_prizes[chosen_idx] = "🧸"
    
    markup = types.InlineKeyboardMarkup(row_width=5)
    buttons = []
    for idx, prize in enumerate(all_prizes):
        txt = f"👉{prize}👈" if idx == chosen_idx else prize
        buttons.append(types.InlineKeyboardButton(text=txt, callback_data="void"))
    markup.add(*buttons)
    
    bot.edit_message_text("Все ячейки открыты! Посмотри на поле ниже 👇", call.message.chat.id, call.message.message_id, reply_markup=markup)
    
    if chosen_prize == "NFT 🍊":
        bot.send_message(call.message.chat.id, "🌟 Ничего себе! Ты выиграл уникальный NFT 🍊! Улучшению не подлежит.")
    else:
        prize_map = {"🧸": "мишку", "🌹": "розу", "🚀": "ракету"}
        bot.send_message(call.message.chat.id, f"Молодец ты выйграл {prize_map.get(chosen_prize, '')} хочешь улучшить?")
        
        markup_up = types.InlineKeyboardMarkup(row_width=2)
        markup_up.add(
            types.InlineKeyboardButton(text="Да ✅", callback_data=f"up:yes:{owner_id}:{chosen_prize}"),
            types.InlineKeyboardButton(text="Нет ❌", callback_data=f"up:no:{owner_id}:none")
        )
        bot.send_message(call.message.chat.id, "Сделай выбор:", reply_markup=markup_up)
        
    active_slots_games.pop(game_id, None)
    bot.answer_callback_query(call.id)
rt_clash_countdown(message.chat.id, seconds))
        except Exception:
            bot.reply_to(message, "❌ Ошибка! Пример: `начать перебив 30 1 нфт`")
            
    # Команда: начать угадай число 1-1000 нфт приз
    elif clean.startswith("угадай число"):
        try:
            parts = message.text.split(" ")
            idx = next(i for i, w in enumerate(parts) if "число" in w.lower()) + 1
            
            range_part = parts[idx]
            prize = " ".join(parts[idx+1:])
            start, end = map(int, range_part.split("-"))
            
            secret_number = random.randint(start, end)
            guess_number_game.update({"active": True, "number": secret_number, "range": (start, end), "prize": prize})
            
            text = f"НАЧАЛАСЬ ИГРА УГАДАЙ ЧИСЛО!\n\nПРИЗ: {prize}\n\nДИАПАЗОН: от {start} до {end}\n\nПишите ваши варианты в чат!"
            bot.send_message(message.chat.id, text)
            
            try:
                bot.send_message(OWNER_ID, f"🤫 Загаданное число для игры: **{secret_number}**")
            except Exception:
                bot.reply_to(message, "⚠️ Владелец, напиши мне в ЛС (/start), чтобы получать загаданные числа!")
        except Exception:
            bot.reply_to(message, "❌ Ошибка! Пример: `начать угадай число 1-1000 нфт`")

# Перехват любых текстовых сообщений для сброса таймера ПЕРЕБИВА и проверки ЧИСЛА
@bot.message_handler(func=lambda message: message.text)
def handle_chat_activity(message):
    # Если идет ПЕРЕБИВ — любое текстовое сообщение сбрасывает таймер
    if clash_game["active"] and message.chat.id == clash_game["chat_id"]:
        clash_game["last_user"] = message.from_user.username or message.from_user.first_name
        # Бот фиксирует активность и может выводить новые метрики цены при необходимости
        
    # Если идет УГАДАЙ ЧИСЛО
    if guess_number_game["active"] and message.text.isdigit():
        user_guess = int(message.text)
        secret = guess_number_game["number"]
        start, end = guess_number_game["range"]
        
        if start <= user_guess <= end and user_guess == secret:
            name = message.from_user.username or message.from_user.first_name
            bot.reply_to(message, f"🎉 ПОЗДРАВЛЯЕМ! @{name} угадал число **{secret}** и выигрывает приз: {guess_number_game['prize']}!")
            guess_number_game["active"] = False

if __name__ == "__main__":
    bot.infinity_polling()

    @bot.callback_query_handler(func=lambda call: call.data.startswith('up:'))
def process_upgrade(call):
    data = call.data.split(":")
    choice, owner_id, current_item = data[1], int(data[2]), data[3]
    
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

@bot.callback_query_handler(func=lambda call: call.data.startswith('g3:'))
def process_3_click(call):
    data = call.data.split(":")
    owner_id, game_id, chosen_idx = int(data[1]), data[2], int(data[3])
    
    if call.from_user.id != owner_id:
        bot.answer_callback_query(call.id, "не ну не ты же выйграл", show_alert=True)
        return
        
    if game_id not in active_slots_games:
        bot.answer_callback_query(call.id, "Игра завершена ❌", show_alert=True)
        return
        
    all_prizes = active_slots_games[game_id]
    chosen_prize = all_prizes[chosen_idx]
    
    markup = types.InlineKeyboardMarkup(row_width=3)
    buttons = []
    for idx, prize in enumerate(all_prizes):
        txt = f"👉{prize}👈" if idx == chosen_idx else prize
        buttons.append(types.InlineKeyboardButton(text=txt, callback_data="void"))
    markup.add(*buttons)
    
    bot.edit_message_text(f"Результат раскрытия ячеек ниже 👇", call.message.chat.id, call.message.message_id, reply_markup=markup)
    
    if chosen_prize == "🧸":
        bot.send_message(call.message.chat.id, "Поздравляю! Ты выбил мишку скоро отправим подарок🧸!")
    else:
        bot.send_message(call.message.chat.id, "К сожелению ты не выйграл но у тебя точно скоро получится! 🍀")
        
    active_slots_games.pop(game_id, None)
    bot.answer_callback_query(call.id)

async def start_clash_countdown(chat_id, total_seconds):
    clash_game["time_left"] = total_seconds
    
    while clash_game["time_left"] > 10:
        if not clash_game["active"]:
            return
        await asyncio.sleep(1)
        clash_game["time_left"] -= 1

    if clash_game["active"]:
        msg = bot.send_message(chat_id, f"⚠️ Осталось секунд: 10")
        clash_game["countdown_msg_id"] = msg.message_id
        
        while clash_game["time_left"] > 0:
            if not clash_game["active"]:
                return
            await asyncio.sleep(1)
            clash_game["time_left"] -= 1
            try:
                bot.edit_message_text(f"⚠️ Осталось секунд: {clash_game['time_left']}", chat_id, msg.message_id)
            except Exception:
                pass

        if clash_game["active"]:
            if clash_game["last_user"]:
                bot.send_message(chat_id, f"🎉 ВРЕМЯ ВЫШЛО! В перебиве побеждает @{clash_game['last_user']} и забирает свой приз: {clash_game['prize']}!")
            else:
                bot.send_message(chat_id, "⏳ Время перебива вышло! Никто не принял участие.")
            clash_game["active"] = False

@bot.message_handler(func=lambda message: message.text and (message.text.lower().startswith('начать') or message.text.lower().startswith('/начать')))
def admin_commands(message):
    if message.from_user.id != OWNER_ID:
        return
        
    clean = message.text.lower().replace("/начать", "").replace("начать", "").strip()
    if not clean:
        return
        
    if clean.startswith("перебив"):
        try:
            parts = message.text.split(" ")
            idx = next(i for i, w in enumerate(parts) if "перебив" in w.lower()) + 1
            
            seconds = int(parts[idx])
            price = parts[idx+1]
            prize = " ".join(parts[idx+2:])
            
            clash_game.update({"active": True, "price": price, "prize": prize, "chat_id": message.chat.id, "last_user": None, "countdown_msg_id": None})
            
            text = f"НАЧАЛСЯ ПЕРЕБИВ!\n\nПРИЗ: {prize}\n\nЦЕНА ЗА СООБЩЕНИЯ: {price}⭐\n\nВРЕМЯ НА ПЕРЕБИВ: {format_time(seconds)}"
            bot.send_message(message.chat.id, text)
            
            try:
                loop = asyncio.get_event_loop()
            except RuntimeError:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
            loop.run_until_complete(start_clash_countdown(message.chat.id, seconds))
        except Exception:
            bot.reply_to(message, "❌ Ошибка! Пример: `начать перебив 30 1 нфт`")
            
    elif clean.startswith("угадай число"):
        try:
            parts = message.text.split(" ")
            idx = next(i for i, w in enumerate(parts) if "число" in w.lower()) + 1
            
            range_part = parts[idx]
            prize = " ".join(parts[idx+1:])
            start, end = map(int, range_part.split("-"))
            
            secret_number = random.randint(start, end)
            guess_number_game.update({"active": True, "number": secret_number, "range": (start, end), "prize": prize})
            
            text = f"НАЧАЛАСЬ ИГРА УГАДАЙ ЧИСЛО!\n\nПРИЗ: {prize}\n\nДИАПАЗОН: от {start} до {end}\n\nПишите ваши варианты в чат!"
            bot.send_message(message.chat.id, text)
            
            try:
                bot.send_message(OWNER_ID, f"🤫 Загаданное число для игры: **{secret_number}**")
            except Exception:
                bot.reply_to(message, "⚠️ Владелец, напиши мне в ЛС (/start) для получения секретных чисел!")
        except Exception:
            bot.reply_to(message, "❌ Ошибка! Пример: `начать угадай число 1-1000`")

@bot.message_handler(func=lambda message: message.text)
def handle_chat_activity(message):
    if clash_game["active"] and message.chat.id == clash_game["chat_id"]:
        clash_game["last_user"] = message.from_user.username or message.from_user.first_name
        
    if guess_number_game["active"] and message.text.isdigit():
        user_guess = int(message.text)
        secret = guess_number_game["number"]
        start, end = guess_number_game["range"]
        
        if start <= user_guess <= end and user_guess == secret:
            name = message.from_user.username or message.from_user.first_name
            bot.reply_to(message, f"🎉 ПОЗДРАВЛЯЕМ! @{name} угадал число **{secret}** и выигрывает приз: {guess_number_game['prize']}!")
            guess_number_game["active"] = False

if __name__ == "__main__":
    bot.infinity_polling()
    
