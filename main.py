import asyncio
import random
import uuid
from aiogram import Bot, Dispatcher, F, types
from aiogram.filters import Command, CommandObject
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.fsm.storage.memory import MemoryStorage

BOT_TOKEN = "8997952716:AAG7XAEhK9HZQgqSoARA5H7KhddYNQvMMRE"
OWNER_ID = 7838553850

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(storage=MemoryStorage())

guess_number_game = {"active": False, "number": None, "range": (0, 0)}
clash_game = {"active": False}

def format_time(seconds: int) -> str:
    if seconds >= 60:
        minutes = seconds // 60
        rem_seconds = seconds % 60
        return f"{minutes} мин." if rem_seconds == 0 else f"{minutes} мин. {rem_seconds} сек."
    return f"{seconds} сек."

@dp.message(F.dice.emoji == "🎰")
async def handle_slots(message: types.Message):
    value = message.dice.value
    user_id = message.from_user.id
    await asyncio.sleep(2.0)
    
    if value == 64:
        await message.reply("🎉 Молодец, ты выбил 777!\nПеред тобой 25 ячеек, выбери одну и получай приз!")
        game_id = str(uuid.uuid4())[:8]
        is_nft = random.randint(1, 1000) == 777
        
        pool = []
        if is_nft:
            pool.append("NFT 🍊")
            pool.extend(["🧸"] * 11 + ["🌹"] * 10 + ["🚀"] * 3)
        else:
            pool = ["🧸"] * 11 + ["🌹"] * 11 + ["🚀"] * 3
            
        random.shuffle(pool)
        
        builder = InlineKeyboardBuilder()
        for i in range(25):
            prize_code = pool[i]
            pool_str = "".join(pool).replace("NFT 🍊", "N")
            builder.button(text="❓", callback_data=f"c7:{user_id}:{game_id}:{prize_code}:{i}:{pool_str}")
        builder.adjust(5)
        await message.answer("Выбирай ячейку 👇", reply_markup=builder.as_markup())
        
    elif value in:
        await message.reply("🔥 Молодец! Ты выбил комбинацию!\nПеред тобой 3 ячейки, выбери одну. Если выберешь правильную — ты получишь мишку!")
        game_id = str(uuid.uuid4())[:8]
        slots_3 = ["❌", "❌", "❌"]
        slots_3[random.randint(0, 2)] = "🧸"
        
        builder = InlineKeyboardBuilder()
        for i in range(3):
            pool_str = "".join(slots_3)
            builder.button(text="❓", callback_data=f"c3:{user_id}:{game_id}:{slots_3[i]}:{pool_str}")
        builder.adjust(3)
        await message.answer("Выбирай ячейку 👇", reply_markup=builder.as_markup())

@dp.callback_query(F.data.startswith("c7:"))
async def process_777_click(callback: types.CallbackQuery):
    data = callback.data.split(":")
    owner_id = int(data[1])
    chosen_prize = data[3]
    chosen_idx = int(data[4])
    pool_str = data[5]
    
    if callback.from_user.id != owner_id:
        await callback.answer("не ну не ты же выйграл", show_alert=True)
        return
        
    all_prizes = ["NFT 🍊" if char == "N" else char for char in pool_str]
    revealed_text = "Вот что скрывалось в ячейках:\n"
    for idx, prize in enumerate(all_prizes):
        revealed_text += f"👉[{prize}]👈 " if idx == chosen_idx else f"{prize} "
        if (idx + 1) % 5 == 0:
            revealed_text += "\n"
            
    await callback.message.edit_text(revealed_text)
    
    if chosen_prize in ["N", "NFT 🍊"]:
        await callback.message.answer("🌟 Ничего себе! Ты выиграл уникальный NFT 🍊! Улучшению не подлежит.")
    else:
        prize_map = {"🧸": "мишку", "🌹": "розу", "🚀": "ракету"}
        await callback.message.answer(f"Молодец ты выйграл {prize_map.get(chosen_prize, '')} хочешь улучшить?")
        builder = InlineKeyboardBuilder()
        builder.button(text="Да ✅", callback_data=f"up:yes:{owner_id}:{chosen_prize}")
        builder.button(text="Нет ❌", callback_data=f"up:no:{owner_id}:none")
        await callback.message.answer("Сделай выбор:", reply_markup=builder.as_markup())
    await callback.answer()

@dp.callback_query(F.data.startswith("up:"))
async def process_upgrade(callback: types.CallbackQuery):
    data = callback.data.split(":")
    choice = data[1]
    owner_id = int(data[2])
    current_item = data[3]
    
    if callback.from_user.id != owner_id:
        await callback.answer("не ну не ты же выйграл", show_alert=True)
        return
        
    if choice == "no":
        await callback.message.edit_text("Ты решил забрать свой текущий подарок! 🎁")
        await callback.answer()
        return
        
    next_item_map = {"🧸": ("🌹", "розы"), "🌹": ("🚀", "ракеты")}
    if current_item not in next_item_map:
        await callback.message.edit_text("Этот предмет нельзя улучшить дальше! 🏆")
        await callback.answer()
        return
        
    next_item_emoji, next_item_name = next_item_map[current_item]
    bounce_msg = await callback.message.answer_dice(emoji="🏀")
    await asyncio.sleep(3.5)
    
    if bounce_msg.dice.value in:
        await callback.message.answer(f"Молодец ты улучшил подарок до {next_item_name} хочешь продолжить?")
        builder = InlineKeyboardBuilder()
        builder.button(text="Да ✅", callback_data=f"up:yes:{owner_id}:{next_item_emoji}")
        builder.button(text="Нет ❌", callback_data=f"up:no:{owner_id}:none")
        await callback.message.answer("Сделай выбор:", reply_markup=builder.as_markup())
    else:
        await callback.message.answer("К сожелению ты не попал удачи в следующий раз! 💔")
    await callback.answer()

@dp.callback_query(F.data.startswith("c3:"))
async def process_3_click(callback: types.CallbackQuery):
    data = callback.data.split(":")
    owner_id = int(data[1])
    chosen_prize = data[3]
    pool_str = data[4]
    
    if callback.from_user.id != owner_id:
        await callback.answer("не ну не ты же выйграл", show_alert=True)
        return
        
    all_prizes = [char for char in pool_str]
    revealed_text = f"Результат: Кто где прятался: {' | '.join(all_prizes)}\n\n"
    
    if chosen_prize == "🧸":
        await callback.message.edit_text(revealed_text + "Поздравляю! Ты выбил мишку скоро отправим подарок🧸!")
    else:
        await callback.message.edit_text(revealed_text + "К сожелению ты не выйграл но у тебя точно скоро получится! 🍀")
    await callback.answer()

@dp.message(Command("начать"), F.from_user.id == OWNER_ID)
async def start_games(message: types.Message, command: CommandObject):
    args = command.args
    if not args: return
        
    if args.startswith("перебив"):
        try:
            params = args.replace("перебив ", "", 1).split(" ")
            price, seconds, prize = params[0], int(params[1]), " ".join(params[2:])
            clash_game["active"] = True
            await message.answer(f"📣 **Перебив начался!**\n\nЦена за сообщение в чате: {price}⭐\nВремя на перебив: {format_time(seconds)}\nПриз: *{prize}*", parse_mode="Markdown")
            await asyncio.sleep(seconds)
            if clash_game["active"]:
                await message.answer("⏳ Время перебива вышло! Игра окончена.")
                clash_game["active"] = False
        except Exception:
            await message.reply("❌ Ошибка! Пример: `начать перебив 1 30 ракета бомба`")
            
    elif args.startswith("угадай число"):
        try:
            range_part = args.replace("угадай число ", "", 1).strip()
            start, end = map(int, range_part.split("-"))
            secret_number = random.randint(start, end)
            guess_number_game.update({"active": True, "number": secret_number, "range": (start, end)})
            await message.answer(f"🎲 Игра «Угадай число» запущена! Диапазон: от {start} до {end}. Пишите варианты!")
            try:
                await bot.send_message(chat_id=OWNER_ID, text=f"🤫 Загаданное число: **{secret_number}**")
            except Exception:
                await message.reply("⚠️ Владелец, напиши мне в ЛС (/start) для получения секретных чисел!")
        except Exception:
            await message.reply("❌ Ошибка! Пример: `начать угадай число 1-1000`")

@dp.message(F.text.digit())
async def check_guessed_number(message: types.Message):
    if not guess_number_game["active"]: return
    user_guess = int(message.text)
    secret = guess_number_game["number"]
    start, end = guess_number_game["range"]
    
    if start <= user_guess <= end and user_guess == secret:
        await message.reply(f"🎉 Поздравляем! @{message.from_user.username or message.from_user.first_name} угадал число **{secret}**!")
        guess_number_game["active"] = False

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
  
