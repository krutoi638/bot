import asyncio, json, os
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, BotCommand
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext

TOKEN = "8195530369:AAF6icdaf76w38rRUfuetDRNYDzuqPYB_QI"
ADMIN_IDS = [969783208, 7213947960]

WELCOME_TEXT = "<b>🕊 Здравствуйте, {name}!</b>\n\n🌊 Я бот флуда 'Первозданное море'"
RULES_TEXT = "📜 Ознакомьтесь с правилами:\nt.me/pristine_sea_Flood"
SUCCESS_TEXT = "✅ Регистрация завершена!\nВот ссылка на флуд:\nhttps://t.me/+bjlQJT5cBk02ZjAy"
WRONG_CODE_TEXT = "❌ Кодовое слово неверное. Попробуйте ещё раз."
CODEWORD = "гринфлейм"
OCCUPIED_FILE = "occupied.json"
BANNED_FILE = "banned.json"

ROLES = {
    "МОНДШТАДТ": ["Альбедо","Барбара","Беннет","Венти","Далия","Дилюк","Диона","Джинн","Кэйа","Кли","Лиза","Мона","Мика","Рэйзор","Розария","Сахароза","Фишль","Эмбер","Эола","Ноэлль","Дурин","Варка","Алиса","Николь"],
    "ЛИ ЮЭ": ["Бай Чжу","Бэй Доу","Гань Юй","Е Лань","Ка Мин","Кэ Цин","Нин Гуан","Син Цу","Сяо","Сян Лин","Синь Янь","Лань Янь","Ху Тао","Чун Юнь","Чжун Ли","Шэнь Хэ","Юнь Цзинь","Ци Ци","Янь Фей","Яо Яо","Сянь Юнь","Цзы Бай"],
    "ИНАДЗУМА": ["Аято","Аяка","Горо","Ёимия","Итто","Кокоми","Кадзуха","Куки","Кирара","Райден","Саю","Сара","Тиори","Тома","Хэйдзо","Яэ Мико","Мидзуки"],
    "СУМЕРУ": ["Аль-Хайтам","Дехья","Дори","Коллеи","Кавех","Кандакия","Лайла","Нилу","Нахида","Сайно","Сетос","Странник","Тигнари","Фарузан"],
    "ФОНТЕЙН": ["Клоринда","Лини","Линетт","Навия","Нёвиллет","Ризли","Сиджвин","Фокалорс","Фремине","Фурина","Шарлотта","Шеврёз","Эмилия"],
    "НАТЛАН": ["Муалани","Кинич","Качина","Мавуика","Часка","Шилонен","Иансан","Ситлали","Оропорон","Вареса","Ифа"],
    "НОД-КРАИ": ["Айно","Инеффа","Лаума","Нефер","Флинс","Ягода","Иллуга","Лоэн"],
    "ФАТУИ": ["Арлекино","Дотторе","Капитано","Коломбина","Панталоне","Пьеро","Пульчинелла","Синьора","Сандроне","Тарталья","Царица","Скарамучча"],
    "ДРУГИЕ": ["Дайнслейф","Итер","Люмин","Паймон","Скирк","Элой"]
}

# -------------------- Работа с файлами --------------------
def load_json(path, default):
    if not os.path.exists(path):
        return default
    with open(path, "r", encoding="utf-8") as f:
        try:
            return json.load(f)
        except:
            return default

def save_json(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

OCCUPIED = load_json(OCCUPIED_FILE, {})
BANNED = set(load_json(BANNED_FILE, []))

def save_occupied():
    save_json(OCCUPIED_FILE, OCCUPIED)

def save_banned():
    save_json(BANNED_FILE, list(BANNED))



# -------------------- FSM --------------------
class RegisterFSM(StatesGroup):
    rules = State()
    region = State()
    character = State()
    confirm = State()
    birthday = State()
    codeword = State()

class QuestionFSM(StatesGroup):
    waiting_question = State()

class FreeFSM(StatesGroup):
    select_region = State()
    select_character = State()

class ComplaintFSM(StatesGroup):
    waiting_target = State()
    waiting_text = State()

class AdminAnswerFSM(StatesGroup):
    waiting_answer = State()

# -------------------- Инициализация --------------------
bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher()
async def set_bot_commands():
    commands = [
        BotCommand(command="start", description="Перезапустить бота"),
    ]
    try:
        await bot.set_my_commands(commands)
        print("Команды меню установлены ✅")
    except Exception as e:
        print(f"Ошибка при установке команд: {e}")

async def main():
    await set_bot_commands()  # Устанавливаем меню команд
    await dp.start_polling(bot)


# -------------------- Клавиатуры --------------------
def start_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📝 Я хочу вступить", callback_data="start_register")],
        [InlineKeyboardButton(text="❓ Я хочу задать вопрос", callback_data="start_question")]
    ])

def rules_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✅ Я прочитал, далее", callback_data="rules_ok")]
    ])

def regions_kb(free=False):
    kb, row = [], []
    for r in ROLES.keys():
        row.append(InlineKeyboardButton(text=r, callback_data=f"{'free_' if free else 'reg_'}{r}"))
        if len(row) == 2:
            kb.append(row)
            row = []
    if row: kb.append(row)
    return InlineKeyboardMarkup(inline_keyboard=kb)

def characters_kb(region, free=False):
    kb, row = [], []
    for char in ROLES.get(region, []):
        status = "❌" if char in OCCUPIED else "✅"
        row.append(InlineKeyboardButton(text=f"{char} {status}", callback_data=f"{'free_' if free else 'char_'}{char}"))
        if len(row) == 2:
            kb.append(row)
            row = []
    if row: kb.append(row)
    kb.append([InlineKeyboardButton(text="⬅ Назад", callback_data=f"{'free_' if free else ''}back_to_regions")])
    return InlineKeyboardMarkup(inline_keyboard=kb)

def confirm_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✅ Да", callback_data="confirm_yes"),
         InlineKeyboardButton(text="❌ Нет", callback_data="confirm_no")]
    ])

def birthday_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🙈 Не хочу говорить", callback_data="skip_bday")]
    ])

def start_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📝 Я хочу вступить", callback_data="start_register")],
        [InlineKeyboardButton(text="❓ Я хочу задать вопрос", callback_data="start_question")],
        [InlineKeyboardButton(text="⚠ Жалоба на участника/админа", callback_data="start_complaint")]
    ])

def answer_kb(user_id: int):
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✏ Ответить", callback_data=f"ans_{user_id}")]
    ])


# -------------------- Хелперы --------------------
async def check_ban(user_id: int, message: types.Message = None):
    if user_id in BANNED:
        if message:
            await message.answer("🚫 Вы забанены и не можете использовать бота.")
        return True
    return False

async def delete_previous_bot_msg(state: FSMContext):
    data = await state.get_data()
    chat_id = data.get("chat_id")
    msg_id = data.get("last_bot_msg_id")
    if chat_id and msg_id:
        try:
            await bot.delete_message(chat_id=chat_id, message_id=msg_id)
        except:
            pass


# -------------------- Обработчики --------------------

# ----- Старт -----
@dp.message(Command("start"))
async def cmd_start(message: types.Message, state:FSMContext):
    if await check_ban(message.from_user.id, message):
        return
    await state.clear()
    await state.update_data(chat_id=message.chat.id)
    msg = await message.answer(WELCOME_TEXT.format(name=message.from_user.full_name),
                               reply_markup=start_kb())
    await state.update_data(last_bot_msg_id=msg.message_id)

# ----- Вопросы -----
@dp.callback_query(lambda c: c.data == "start_question")
async def start_question(call: types.CallbackQuery, state: FSMContext):
    await call.message.delete()  # удаляем кнопку
    await call.message.answer("❓ Напишите ваш вопрос:")
    await state.set_state(QuestionFSM.waiting_question)


@dp.message(QuestionFSM.waiting_question)
async def get_question(message: types.Message, state:FSMContext):
    if await check_ban(message.from_user.id, message):
        return
    for admin in ADMIN_IDS:
        await bot.send_message(
            admin,
            f"❓ Вопрос от @{message.from_user.username or 'нет'}\n"
            f"ID: {message.from_user.id}\n\n"
            f"{message.text}",
            reply_markup=answer_kb(message.from_user.id)
        )

    await message.answer("✅ Вопрос отправлен!")
    await state.clear()


# ----- Регистрация -----
@dp.callback_query(lambda c: c.data == "start_register")
async def start_register(call: types.CallbackQuery, state: FSMContext):
    # пробуем удалить старое сообщение бота
    await delete_previous_bot_msg(state)
    
    # Отправляем новое сообщение с правилами
    msg = await call.message.answer(RULES_TEXT, reply_markup=rules_kb())
    await state.update_data(last_bot_msg_id=msg.message_id)  # сохраняем новый id
    await state.set_state(RegisterFSM.rules)


@dp.callback_query(lambda c: c.data == "rules_ok", RegisterFSM.rules)
async def after_rules(call: types.CallbackQuery, state: FSMContext):
    await call.message.edit_text("🌍 Выберите регион:", reply_markup=regions_kb())
    await state.set_state(RegisterFSM.region)


@dp.callback_query(RegisterFSM.region, F.data.startswith("reg_"))
async def region_chosen(call: types.CallbackQuery, state:FSMContext):
    region = call.data.replace("reg_","")
    await state.update_data(region=region)
    await call.message.edit_text(f"🎭 Регион {region}. Выберите персонажа:", reply_markup=characters_kb(region))
    await state.set_state(RegisterFSM.character)

@dp.callback_query(RegisterFSM.character, F.data.startswith("char_"))
async def char_chosen(call: types.CallbackQuery, state:FSMContext):
    char = call.data.replace("char_","")
    if char in OCCUPIED:
        await call.answer("❌ Эта роль уже занята", show_alert=True)
        return
    await state.update_data(character=char)
    await call.message.edit_text(f"Вы уверены, что хотите выбрать роль <b>{char}</b>?", reply_markup=confirm_kb())
    await state.set_state(RegisterFSM.confirm)

@dp.callback_query(RegisterFSM.character, F.data=="back_to_regions")
async def back_to_regions(call: types.CallbackQuery, state: FSMContext):
    await state.set_state(RegisterFSM.region)
    await call.message.edit_text("🌍 Выберите регион:", reply_markup=regions_kb())


@dp.callback_query(RegisterFSM.confirm, F.data=="confirm_yes")
async def confirm_yes(call: types.CallbackQuery, state:FSMContext):
    await call.message.edit_text("📅 Введите дату рождения (дд.мм) или нажмите кнопку:", reply_markup=birthday_kb())
    await state.set_state(RegisterFSM.birthday)

@dp.callback_query(RegisterFSM.confirm, F.data=="confirm_no")
async def confirm_no(call: types.CallbackQuery, state:FSMContext):
    data = await state.get_data()
    region = data["region"]
    await call.message.edit_text("🎭 Выберите персонажа:", reply_markup=characters_kb(region))
    await state.set_state(RegisterFSM.character)

@dp.callback_query(RegisterFSM.birthday, F.data=="skip_bday")
async def skip_bday(call: types.CallbackQuery, state:FSMContext):
    await state.update_data(birthday="Не указана")
    await call.message.edit_text("🔑 Введите кодовое слово из правил:")
    await state.set_state(RegisterFSM.codeword)

@dp.message(RegisterFSM.birthday)
async def get_bday(message: types.Message, state:FSMContext):
    await state.update_data(birthday=message.text)
    await message.answer("🔑 Введите кодовое слово из правил:")
    await state.set_state(RegisterFSM.codeword)

@dp.message(RegisterFSM.codeword)
async def check_code(message: types.Message, state: FSMContext):
    if message.text.lower() != CODEWORD.lower():
        await message.answer(WRONG_CODE_TEXT)
        return

    data = await state.get_data()
    region = data["region"]
    char = data["character"]
    birthday = data["birthday"]

    # Сохраняем занятую роль
    OCCUPIED[char] = message.from_user.id
    save_occupied()

    # Сообщение пользователю о завершении регистрации
    await message.answer(SUCCESS_TEXT)


    # Лог админам
    admin_text = (
        f"📋 Новая анкета\n"
        f"Пользователь: @{message.from_user.username or 'нет'}\n"
        f"ID: {message.from_user.id}\n"
        f"Персонаж: {char}\n"
        f"Дата рождения: {birthday}"
    )
    for admin in ADMIN_IDS:
        await bot.send_message(admin, admin_text)

    await state.clear()


# ----- Free для админов -----
@dp.message(Command("free"))
async def free_start(message: types.Message, state:FSMContext):
    if message.from_user.id not in ADMIN_IDS:
        await message.reply("❌ Только админы могут использовать эту команду.")
        return
    await state.set_state(FreeFSM.select_region)
    await message.answer("Выберите регион:", reply_markup=regions_kb(free=True))

@dp.callback_query(FreeFSM.select_region, F.data.startswith("free_"))
async def free_region(call: types.CallbackQuery, state:FSMContext):
    region = call.data.replace("free_","")
    await state.update_data(region=region)
    await state.set_state(FreeFSM.select_character)
    await call.message.edit_text(f"Редактирование ролей в регионе {region}:", reply_markup=characters_kb(region, free=True))

@dp.callback_query(FreeFSM.select_character, F.data.startswith("free_"))
async def free_character(call: types.CallbackQuery, state:FSMContext):
    data = await state.get_data()
    region = data["region"]
    char = call.data.replace("free_","")
    if char == "back_to_regions":
        await state.set_state(FreeFSM.select_region)
        await call.message.edit_text("Выберите регион:", reply_markup=regions_kb(free=True))
        return
    if char in OCCUPIED:
        OCCUPIED.pop(char)
    else:
        OCCUPIED[char] = 0
    save_occupied()
    await call.message.edit_text(f"Персонаж {char} теперь {'свободен' if char not in OCCUPIED else 'занят'}", reply_markup=characters_kb(region, free=True))

# ----- Бан и разбан -----
@dp.message(Command("ban"))
async def ban_user(message: types.Message):
    if message.from_user.id not in ADMIN_IDS:
        return
    parts = message.text.split()
    if len(parts) < 2: return
    user_id = int(parts[1])
    BANNED.add(user_id)
    save_banned()
    await message.reply(f"✅ Пользователь {user_id} забанен.")

@dp.message(Command("unban"))
async def unban_user(message: types.Message):
    if message.from_user.id not in ADMIN_IDS:
        return
    parts = message.text.split()
    if len(parts) < 2: return
    user_id = int(parts[1])
    if user_id in BANNED: BANNED.remove(user_id)
    save_banned()
    await message.reply(f"✅ Пользователь {user_id} разбанен.")

async def main():
    await dp.start_polling(bot)

# ---------- Начало жалобы ----------
@dp.callback_query(lambda c: c.data == "start_complaint")
async def start_complaint(call: types.CallbackQuery, state: FSMContext):
    if await check_ban(call.from_user.id, call.message):
        return
    await delete_previous_bot_msg(state)
    await call.message.answer("🖊 Укажите роль или @ник пользователя, на кого жалоба:")
    await state.set_state(ComplaintFSM.waiting_target)

# ---------- Получаем цель жалобы ----------
@dp.message(ComplaintFSM.waiting_target)
async def get_complaint_target(message: types.Message, state: FSMContext):
    if await check_ban(message.from_user.id, message):
        return
    await state.update_data(target=message.text)
    await message.answer("✏ Опишите вашу жалобу:")
    await state.set_state(ComplaintFSM.waiting_text)

# ---------- Получаем текст жалобы и отправляем админам ----------
@dp.message(ComplaintFSM.waiting_text)
async def send_complaint(message: types.Message, state: FSMContext):
    if await check_ban(message.from_user.id, message):
        return
    data = await state.get_data()
    target = data.get("target", "не указано")
    complaint_text = message.text
    report = (
        f"⚠ Жалоба от @{message.from_user.username or 'нет'}\n"
        f"ID: {message.from_user.id}\n"
        f"На кого/роль: {target}\n"
        f"Текст жалобы:\n{complaint_text}"
    )
    for admin in ADMIN_IDS:
        await bot.send_message(admin, report)
    await message.answer("✅ Жалоба отправлена администраторам.")
    await state.clear()


# -------------- ответы админов ---------------------
@dp.callback_query(F.data.startswith("ans_"))
async def admin_start_answer(call: types.CallbackQuery, state: FSMContext):
    if call.from_user.id not in ADMIN_IDS:
        await call.answer("❌ Только админы", show_alert=True)
        return

    user_id = int(call.data.replace("ans_",""))
    await state.update_data(answer_target=user_id)
    await call.message.answer("✏ Введите текст ответа пользователю:")
    await state.set_state(AdminAnswerFSM.waiting_answer)

@dp.message(AdminAnswerFSM.waiting_answer)
async def admin_send_answer(message: types.Message, state: FSMContext):
    if message.from_user.id not in ADMIN_IDS:
        return

    data = await state.get_data()
    target_id = data["answer_target"]

    try:
        await bot.send_message(
            target_id,
            f"💬 Ответ администрации:\n\n{message.text}"
        )
        await message.answer("✅ Ответ отправлен пользователю.")
    except:
        await message.answer("❌ Не удалось отправить ответ.")

    await state.clear()


if __name__ == "__main__":
    asyncio.run(main())


