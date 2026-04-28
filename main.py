import asyncio, json, os, random, datetime, re
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command, StateFilter
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, BotCommand
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import (
    Message,
    CallbackQuery,
    InlineKeyboardMarkup,
    InlineKeyboardButton
)


TOKEN = "8195530369:AAF6icdaf76w38rRUfuetDRNYDzuqPYB_QI"
ADMIN_IDS = [969783208, 7213947960]
ADMIN_IDS_CALL = [969783208, 7213947960]
FLOOD_CHAT_ID = -1002809884543

ANSWER_TIME = 300
CALL_TIMERS = {}
WELCOME_TEXT = "<b>🕊 Здравствуйте, {name}!</b>\n\n🌊 Я бот флуда 'Первозданное море'"
RULES_TEXT = "📜 Ознакомьтесь с правилами:\nt.me/pristine_sea_Flood"
SUCCESS_TEXT = "✅ Регистрация завершена!\nВот ссылка на флуд:\nhttps://t.me/+bjlQJT5cBk02ZjAy"
WRONG_CODE_TEXT = "❌ Кодовое слово неверное. Попробуйте ещё раз."
CODEWORD = "гринфлейм"
OCCUPIED_FILE = "occupied.json"
BANNED_FILE = "banned.json"
ACTIVE_MEMBERS_FILE = "active_members.json"
APPLICATIONS_FILE = "applications.json"
ROLE_CHANGE_REQUESTS_FILE = "role_change_requests.json"
ROLES = {
    "МОНДШТАДТ": ["Алиса","Альбедо","Барбара","Беннет","Варка","Венти","Далия","Дилюк","Диона","Джинн","Дурин","Кейа","Кли","Лиза","Лоэн","Мика","Мона","Николь","Ноэлль","Прюн","Рэйзор","Розария","Сахароза","Фишль","Эмбер","Эола"],
    "ЛИ ЮЭ": ["Бай Чжу","Бэй Доу","Гань Юй","Е Лань","Ка Мин","Кэ Цин","Лань Янь","Нин Гуан","Син Цу","Сяо","Сян Лин","Сянь Юнь","Синь Янь","Ху Тао","Чун Юнь","Чжун Ли","Шэнь Хэ","Ци Ци","Цзы Бай","Юнь Цзинь","Янь Фей","Яо Яо"],
    "ИНАДЗУМА": ["Аято","Аяка","Горо","Ёимия","Итто","Кадзуха","Кирара","Кокоми","Куки","Мидзуки","Райден","Саю","Сара","Тиори","Тома","Хэйдзо","Яэ Мико"],
    "СУМЕРУ": ["Аль-Хайтам","Дехья","Дори","Кавех","Кандакия","Коллеи","Лайла","Нахида","Нилу","Сайно","Сетос","Странник","Тигнари","Фарузан"],
    "ФОНТЕЙН": ["Клоринда","Лини","Линетт","Навия","Нёвиллет","Ризли","Сиджвин","Фокалорс","Фремине","Фурина","Шарлотта","Шеврёз","Эмилия"],
    "НАТЛАН": ["Вареса","Иансан","Ифа","Качина","Кинич","Мавуика","Муалани","Оророн","Ситлали","Шилонен","Часка"],
    "НОД-КРАЙ": ["Айно","Инеффа","Иллуга","Лаума","Линнея","Лоэн","Нефер","Флинс","Ягода"],
    "ФАТУИ": ["Арлекино","Дотторе","Капитано","Коломбина","Панталоне","Пьеро","Пульчинелла","Сандроне","Синьора","Скарамучча","Тарталья","Царица"],
    "ДРУГИЕ": ["Дайнслейф","Итер","Люмин","Паймон","Ронова","Скирк","Элой"]
}
MONTHS = {
    "01": "января",
    "02": "февраля",
    "03": "марта",
    "04": "апреля",
    "05": "мая",
    "06": "июня",
    "07": "июля",
    "08": "августа",
    "09": "сентября",
    "10": "октября",
    "11": "ноября",
    "12": "декабря"
}
GAME = {
    "active": False,
    "phase": "IDLE",
    "chat_id": None,

    "players": {},       # user_id: name
    "princess": None,

    "question": None,
    "answers": {},
    "answer_order": [],

    "answers_closed": False,
    "timer_task": None
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
APPLICATIONS = load_json(APPLICATIONS_FILE, {})
ROLE_CHANGE_REQUESTS = load_json(ROLE_CHANGE_REQUESTS_FILE, {})

def save_occupied():
    save_json(OCCUPIED_FILE, OCCUPIED)

def save_banned():
    save_json(BANNED_FILE, list(BANNED))
    
def load_active_members():
    if not os.path.exists(ACTIVE_MEMBERS_FILE):
        return {}
    with open(ACTIVE_MEMBERS_FILE, "r", encoding="utf-8") as f:
        try:
            return json.load(f)
        except:
            return {}

def save_active_members(data):
    with open(ACTIVE_MEMBERS_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def save_applications():
    save_json(APPLICATIONS_FILE, APPLICATIONS)

def save_role_requests():
    save_json(ROLE_CHANGE_REQUESTS_FILE, ROLE_CHANGE_REQUESTS)

# загружаем участников при старте
ACTIVE_MEMBERS = load_active_members()



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

class ChangeRoleFSM(StatesGroup):
    region = State()
    character = State()
    confirm = State()

class UserReplyFSM(StatesGroup):
    waiting_reply = State()
    
class BroadcastFSM(StatesGroup):
    waiting_message = State()



# -------------------- Инициализация --------------------
bot = Bot(TOKEN, default=DefaultBotProperties(parse_mode="HTML"))
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
    await set_bot_commands()  # Меню команд
    asyncio.create_task(birthday_scheduler())  # Запуск планировщика
    await dp.start_polling(bot)



async def send_birthday_greetings():
    today = datetime.datetime.now()
    day = today.day
    month = today.strftime("%m")

    for char, data in OCCUPIED.items():
        if not isinstance(data, dict):
            continue  # пропускаем старые записи
        birthday = data.get("birthday", "")
        user_id = data.get("id")
        if f"({day}.{month})" in birthday:
            try:
                await bot.send_message(
                    FLOOD_CHAT_ID,
                    f"🎉 Сегодня день рождения у <a href='tg://user?id={user_id}'>{char}</a>! Поздравляем! 🥳"
                )
            except Exception as e:
                print(f"Ошибка при отправке поздравления: {e}")

async def birthday_scheduler():
    already_sent = set()  # чтобы не спамить несколько раз в день
    while True:
        today_str = datetime.datetime.now().strftime("%d.%m")
        if today_str not in already_sent:
            await send_birthday_greetings()
            already_sent.add(today_str)
            # очищаем набор на следующий день
            asyncio.create_task(clear_already_sent(already_sent))
        await asyncio.sleep(60*60)  # проверяем каждый час

async def clear_already_sent(already_sent):
    await asyncio.sleep(24*60*60)  # 24 часа
    already_sent.clear()



# -------------------- Клавиатуры --------------------
def rules_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✅ Я прочитал, далее", callback_data="rules_ok")]
    ])

def characters_kb(region, free=False):
    if region not in ROLES:
        region = list(ROLES.keys())[0] 

    kb, row = [], []
    for char in ROLES[region]:
        status = "❌" if char in OCCUPIED else "✅"
        row.append(InlineKeyboardButton(text=f"{char} {status}", callback_data=f"{'free_' if free else 'char_'}{char}"))
        if len(row) == 2:
            kb.append(row)
            row = []
    if row:
        kb.append(row)

    # 🎲 Кнопка случайного выбора персонажа
    kb.append([InlineKeyboardButton(
        text="🎲 Случайный персонаж",
        callback_data=f"{'free_' if free else ''}random_{region}"
    )])

    # Кнопка назад
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
        [InlineKeyboardButton(text="⚠ Жалоба на участника/админа", callback_data="start_complaint")],
        [InlineKeyboardButton(text="🔄 Сменить роль", callback_data="change_role")]
    ])

def answer_kb(user_id: int):
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✏ Ответить", callback_data=f"ans_{user_id}")]
    ])

def approve_kb(user_id: int, char: str):
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(
                text="✅ Принять",
                callback_data=f"approve_{user_id}_{char}"
            ),
            InlineKeyboardButton(
                text="❌ Отклонить",
                callback_data=f"reject_{user_id}_{char}"
            )
        ],
        [
            InlineKeyboardButton(
                text="✏ Ответить",
                callback_data=f"ans_{user_id}"
            )
        ]
    ])

def birthday_day_kb():
    kb = []
    row = []
    for day in range(1, 32):
        row.append(
            InlineKeyboardButton(
                text=str(day),
                callback_data=f"bday_day_{day}"
            )
        )
        if len(row) == 7:
            kb.append(row)
            row = []
    if row:
        kb.append(row)

    kb.append([
        InlineKeyboardButton(
            text="🙈 Не хочу говорить",
            callback_data="skip_bday"
        )
    ])
    return InlineKeyboardMarkup(inline_keyboard=kb)

def birthday_month_kb():
    kb = []
    row = []
    for num, name in MONTHS.items():
        row.append(
            InlineKeyboardButton(
                text=name.capitalize(),
                callback_data=f"bday_month_{num}"
            )
        )
        if len(row) == 3:
            kb.append(row)
            row = []
    if row:
        kb.append(row)
    return InlineKeyboardMarkup(inline_keyboard=kb)

def regions_kb(free=False):
    kb = []
    row = []
    for region in ROLES.keys():
        prefix = "free_" if free else "reg_"
        row.append(InlineKeyboardButton(text=region, callback_data=f"{prefix}{region}"))
        if len(row) == 2:
            kb.append(row)
            row = []
    if row:
        kb.append(row)
    
    # 🎲 Добавляем кнопку случайного персонажа как отдельный ряд
    if not free:  # только для обычного выбора, не free
        kb.append([InlineKeyboardButton(text="🎲 Случайный персонаж", callback_data="random_global")])

    return InlineKeyboardMarkup(inline_keyboard=kb)

def register_kb():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="💖 Участвовать", callback_data="join_game")]
        ]
    )

def choice_kb(count: int):
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=f"❌ {i}", callback_data=f"kick_{i}")]
            for i in range(1, count + 1)
        ]
    )

def reply_to_admin_kb():
    kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="✏ Ответить на ответ", callback_data="reply_to_admin")]
        ]
    )
    return kb




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


@dp.callback_query(RegisterFSM.rules, lambda c: c.data == "rules_ok")
async def after_rules(call: types.CallbackQuery, state: FSMContext):
    await call.message.edit_text(
        "🌍 Выберите регион:",
        reply_markup=regions_kb()
    )
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
    await call.message.edit_text("📅 Выберите день рождения:", reply_markup=birthday_day_kb())
    await state.set_state(RegisterFSM.birthday)


@dp.callback_query(RegisterFSM.confirm, F.data=="confirm_no")
async def confirm_no(call: types.CallbackQuery, state:FSMContext):
    data = await state.get_data()
    region = data["region"]
    await call.message.edit_text("🎭 Выберите персонажа:", reply_markup=characters_kb(region))
    await state.set_state(RegisterFSM.character)

@dp.callback_query(RegisterFSM.birthday, F.data == "skip_bday")
async def skip_bday(call: types.CallbackQuery, state: FSMContext):
    await state.update_data(
        birthday_user="Не указана",
        birthday_admin="Не указана"
    )
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
    birthday = data["birthday_admin"]

    birthday_admin = data.get("birthday_admin", "Не указана")
    # Сохраняем занятую роль
    OCCUPIED[char] = {"id": message.from_user.id, "birthday": birthday_admin}
    save_occupied()
    APPLICATIONS[str(message.from_user.id)] = {
        "status": "pending",
        "handled_by": None
    }
    save_applications()



    # Сообщение пользователю о завершении регистрации
    await message.answer(
        "✅ Анкета отправлена на рассмотрение администрации.\n"
    )



    # Лог админам
    admin_text = (
        f"📋 Новая анкета\n"
        f"Пользователь: @{message.from_user.username or 'нет'}\n"
        f"ID: {message.from_user.id}\n"
        f"Персонаж: {char}\n"
        f"Дата рождения: {birthday}"
    )
    app = APPLICATIONS.get(str(message.from_user.id))
    handled_by = app["handled_by"] if app else None

    if handled_by:
        text += f"\n\n⚠ Обработано админом ID: {handled_by}"
        
    for admin in ADMIN_IDS:
        await bot.send_message(
            admin,
            admin_text,
            reply_markup=approve_kb(message.from_user.id, char)
        )



    await state.clear()

# ---------------- смена роли ----------------------
@dp.callback_query(F.data == "change_role")
async def change_role_start(call: CallbackQuery, state: FSMContext):
    user_id = call.from_user.id

    current_role = None
    for char, data in OCCUPIED.items():
        if isinstance(data, dict) and data.get("id") == user_id:
            current_role = char
            break

    if not current_role:
        await call.answer("❌ У вас нет активной роли", show_alert=True)
        return

    await state.update_data(old_role=current_role)

    await call.message.edit_text(
        f"🔄 Ваша текущая роль: <b>{current_role}</b>\n\n🌍 Выберите новый регион:",
        reply_markup=regions_kb()
    )

    await state.set_state(ChangeRoleFSM.region)


@dp.callback_query(ChangeRoleFSM.region, F.data.startswith("reg_"))
async def change_role_region(call: CallbackQuery, state: FSMContext):
    region = call.data.replace("reg_", "")
    await state.update_data(region=region)
    await call.message.edit_text(
        f"🎭 Регион {region}. Выберите новую роль:",
        reply_markup=characters_kb(region)
    )
    await state.set_state(ChangeRoleFSM.character)

@dp.callback_query(ChangeRoleFSM.character, F.data.startswith("char_"))
async def change_role_character(call: CallbackQuery, state: FSMContext):
    char = call.data.replace("char_", "")

    if char in OCCUPIED:
        await call.answer("❌ Эта роль уже занята", show_alert=True)
        return

    await state.update_data(new_role=char)
    await call.message.edit_text(
        f"Вы хотите сменить роль на <b>{char}</b>?",
        reply_markup=confirm_kb()
    )
    await state.set_state(ChangeRoleFSM.confirm)

@dp.callback_query(ChangeRoleFSM.confirm, F.data == "confirm_yes")
async def change_role_confirm(call: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    old_role = data["old_role"]
    new_role = data["new_role"]
    user = call.from_user

    ROLE_CHANGE_REQUESTS[str(user.id)] = {
        "old_role": old_role,
        "new_role": new_role,
        "status": "pending",
        "handled_by": None
    }
    save_role_requests()

    for admin in ADMIN_IDS:
        await bot.send_message(
            admin,
            f"🔄 <b>Запрос на смену роли</b>\n\n"
            f"Пользователь: @{user.username or 'нет'}\n"
            f"ID: {user.id}\n"
            f"Старая роль: {old_role}\n"
            f"Новая роль: {new_role}",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[[
                InlineKeyboardButton(
                    text="✅ Принять",
                    callback_data=f"rc_approve|{user.id}|{old_role}|{new_role}"
                ),
                InlineKeyboardButton(
                    text="❌ Отклонить",
                    callback_data=f"rc_reject|{user.id}"
                )
            ]])
        )

    await call.message.edit_text("⏳ Запрос отправлён администрации.")
    await state.clear()

@dp.callback_query(F.data.startswith("rc_approve|"))
async def approve_role_change(call: CallbackQuery):
    _, user_id, old_role, new_role = call.data.split("|")
    user_id = str(user_id).strip()

    req = ROLE_CHANGE_REQUESTS.get(user_id)

    if req is None:
        await call.answer("⚠ Заявка не найдена", show_alert=True)
        return

    if req.get("status") != "pending":
        await call.answer("⚠ Анкета уже обработана другим админом", show_alert=True)
        return

    req["status"] = "approved"
    req["handled_by"] = call.from_user.id
    save_role_requests()

    birthday = OCCUPIED.get(old_role, {}).get("birthday", "Не указана")

    OCCUPIED.pop(old_role, None)
    OCCUPIED[new_role] = {
        "id": int(user_id),
        "birthday": birthday
    }
    save_occupied()

    await bot.send_message(
        int(user_id),
        f"✅ Ваша роль успешно изменена!\n\n🔁 {old_role} → {new_role}"
    )

    await call.message.edit_reply_markup()
    await call.answer("Принято ✅")


@dp.callback_query(F.data.startswith("rc_reject|"))
async def reject_role_change(call: CallbackQuery):
    _, user_id = call.data.split("|")
    user_id = str(user_id).strip()

    req = ROLE_CHANGE_REQUESTS.get(user_id)

    if req is None:
        await call.answer("⚠ Заявка не найдена", show_alert=True)
        return

    if req.get("status") != "pending":
        await call.answer("⚠ Анкета уже обработана другим админом", show_alert=True)
        return

    req["status"] = "rejected"
    req["handled_by"] = call.from_user.id
    save_role_requests()

    await bot.send_message(
        int(user_id),
        "❌ Запрос на смену роли был отклонён."
    )

    await call.message.edit_reply_markup()
    await call.answer("Отклонено ❌")




# ---- дата рождения ------

@dp.callback_query(RegisterFSM.birthday, F.data.startswith("bday_day_"))
async def choose_bday_day(call: types.CallbackQuery, state: FSMContext):
    day = call.data.replace("bday_day_", "")
    await state.update_data(bday_day=day)

    await call.message.edit_text(
        "📅 Выберите месяц рождения:",
        reply_markup=birthday_month_kb()
    )

@dp.callback_query(RegisterFSM.birthday, F.data.startswith("bday_month_"))
async def choose_bday_month(call: types.CallbackQuery, state: FSMContext):
    month_num = call.data.replace("bday_month_", "")
    month_word = MONTHS[month_num]

    data = await state.get_data()
    day = data.get("bday_day")

    # для пользователя (словами)
    birthday_user = f"{day} {month_word}"

    # для админов (словами + цифрами)
    birthday_admin = f"{day} {month_word} ({day}.{month_num})"

    await state.update_data(
        birthday_user=birthday_user,
        birthday_admin=birthday_admin
    )

    await call.message.edit_text("🔑 Введите кодовое слово из правил:")
    await state.set_state(RegisterFSM.codeword)



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
    
@dp.message(Command("banlist"))
async def show_banlist(message: types.Message):
    if message.from_user.id not in ADMIN_IDS:
        await message.reply("❌ Только админы могут просматривать список забаненных.")
        return
    
    if not BANNED:
        await message.reply("✅ Список забаненных пуст.")
        return
    
    text = "🚫 <b>Список забаненных пользователей:</b>\n\n"
    
    for i, user_id in enumerate(BANNED, start=1):
        # Пытаемся получить информацию о пользователе
        try:
            user = await bot.get_chat(user_id)
            username = f"@{user.username}" if user.username else user.full_name
            text += f"{i}. {username} (ID: <code>{user_id}</code>)\n"
        except:
            # Если не удалось получить инфо (удалённый аккаунт и т.д.)
            text += f"{i}. ID: <code>{user_id}</code>\n"
    
    text += f"\n<b>Всего:</b> {len(BANNED)}"
    
    await message.reply(text)
    
# обьявления
@dp.message(Command("broadcast"))
async def broadcast_start(message: types.Message, state: FSMContext):
    if message.from_user.id not in ADMIN_IDS:
        await message.reply("❌ Только админы могут делать рассылку.")
        return
    
    await message.reply(
        "📢 <b>Рассылка сообщения</b>\n\n"
        "Отправьте текст, который хотите разослать всем зарегистрированным пользователям.\n\n"
        "Для отмены отправьте /cancel"
    )
    await state.set_state(BroadcastFSM.waiting_message)


@dp.message(BroadcastFSM.waiting_message, Command("cancel"))
async def broadcast_cancel(message: types.Message, state: FSMContext):
    await state.clear()
    await message.reply("❌ Рассылка отменена.")


@dp.message(BroadcastFSM.waiting_message)
async def broadcast_send(message: types.Message, state: FSMContext):
    if message.from_user.id not in ADMIN_IDS:
        return
    
    # Собираем всех пользователей из OCCUPIED
    user_ids = set()
    for char, data in OCCUPIED.items():
        if isinstance(data, dict):
            user_ids.add(data.get("id"))
    
    if not user_ids:
        await message.reply("❌ Нет зарегистрированных пользователей.")
        await state.clear()
        return
    
    # Подтверждение
    await message.reply(
        f"📊 Сообщение будет отправлено <b>{len(user_ids)}</b> пользователям.\n\n"
        f"Подтвердите отправку:",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(text="✅ Отправить", callback_data="broadcast_confirm"),
                InlineKeyboardButton(text="❌ Отмена", callback_data="broadcast_cancel")
            ]
        ])
    )
    
    # Сохраняем текст сообщения
    await state.update_data(broadcast_text=message.text or message.caption, user_ids=list(user_ids))


@dp.callback_query(F.data == "broadcast_confirm")
async def broadcast_confirm(call: types.CallbackQuery, state: FSMContext):
    if call.from_user.id not in ADMIN_IDS:
        await call.answer("❌ Только админы", show_alert=True)
        return
    
    data = await state.get_data()
    text = data.get("broadcast_text")
    user_ids = data.get("user_ids", [])
    
    await call.message.edit_text("⏳ Рассылка началась...")
    
    success = 0
    failed = 0
    
    for user_id in user_ids:
        try:
            await bot.send_message(
                user_id,
                f"📢 <b>Сообщение от администрации:</b>\n\n{text}"
            )
            success += 1
            await asyncio.sleep(0.05)  # задержка, чтобы не словить флуд-контроль
        except Exception as e:
            failed += 1
            print(f"Ошибка отправки {user_id}: {e}")
    
    await call.message.edit_text(
        f"✅ Рассылка завершена!\n\n"
        f"📨 Отправлено: {success}\n"
        f"❌ Не доставлено: {failed}"
    )
    
    await state.clear()


@dp.callback_query(F.data == "broadcast_cancel")
async def broadcast_cancel_callback(call: types.CallbackQuery, state: FSMContext):
    await call.message.edit_text("❌ Рассылка отменена.")
    await state.clear()


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

    user_id = int(call.data.replace("ans_", ""))

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
            f"💬 Ответ администрации:\n\n{message.text}",
            reply_markup=reply_to_admin_kb()  # кнопка здесь
        )
        await message.answer("✅ Ответ отправлен пользователю.")
    except:
        await message.answer("❌ Не удалось отправить ответ.")

    await state.clear()

# ------ ответ пользователя ------
@dp.callback_query(F.data == "reply_to_admin")
async def user_click_reply(call: CallbackQuery, state: FSMContext):
    await call.message.answer("✏ Напишите ответ администратору:")
    
    # Сохраняем, кому отправлять ответ (можно брать последнего админа, который отвечал)
    await state.update_data(admin_id=ADMIN_IDS[0])  # здесь можно усложнить
    await state.set_state(UserReplyFSM.waiting_reply)
    await call.answer()  # чтобы убрать «часики» на кнопке

@dp.message(UserReplyFSM.waiting_reply)
async def user_reply_to_admin(message: Message, state: FSMContext):
    data = await state.get_data()
    admin_id = data.get("admin_id")

    if not admin_id:
        await message.answer("❌ Нет активного ответа, на который можно ответить.")
        await state.clear()
        return

    await bot.send_message(
        admin_id,
        f"💬 Пользователь @{message.from_user.username or message.from_user.id} ответил:\n\n{message.text}"
    )
    await message.answer("✅ Ответ отправлен администратору.")
    await state.clear()





# ----------- кнопки принять отклонить ----------------------
@dp.callback_query(F.data.startswith("approve_"))
async def approve_user(call: types.CallbackQuery):
    if call.from_user.id not in ADMIN_IDS:
        await call.answer("❌ Только админы", show_alert=True)
        return
    _, user_id, char = call.data.split("_")

    app = APPLICATIONS.get(user_id)

    # ⛔ если анкета уже обработана
    if not app or app["status"] != "pending":
        await call.answer("⚠ Анкета уже обработана другим админом", show_alert=True)
        return  

    # ✅ фиксируем решение
    app["status"] = "approved"
    app["handled_by"] = call.from_user.id
    save_applications()

    await bot.send_message(
        user_id,
        "✅ Ваша анкета одобрена!\n\n"
        "Добро пожаловать 🌊\n"
        "Вот ссылка на флуд:\n"
        "https://t.me/+bjlQJT5cBk02ZjAy"
    )    
    await call.message.edit_reply_markup()
    await call.answer("Принято ✅")


@dp.callback_query(F.data.startswith("reject_"))
async def reject_user(call: types.CallbackQuery):
    if call.from_user.id not in ADMIN_IDS:
        await call.answer("❌ Только админы", show_alert=True)
        return

    _, user_id, char = call.data.split("_")
    user_id = str(user_id)

    app = APPLICATIONS.get(user_id)
    if not app or app["status"] != "pending":
        await call.answer("⚠ Анкета уже обработана другим админом", show_alert=True)
        return

    app["status"] = "rejected"
    app["handled_by"] = call.from_user.id
    save_applications()

    if char in OCCUPIED:
        OCCUPIED.pop(char)
        save_occupied()

    await bot.send_message(
        int(user_id),
        "❌ Ваша анкета отклонена."
    )

    await call.message.edit_reply_markup()
    await call.answer("Анкета отклонена ❌")

# -------- рандом ------------

@dp.callback_query(F.data.startswith("random_") & ~F.data.startswith("random_global"))
async def random_character_in_region(call: types.CallbackQuery, state: FSMContext):
    region = call.data.replace("random_", "").replace("free_", "")

    free_chars = [c for c in ROLES[region] if c not in OCCUPIED or OCCUPIED.get(c, 0) == 0]
    if not free_chars:
        await call.answer("❌ Все персонажи заняты в этом регионе", show_alert=True)
        return

    char = random.choice(free_chars)
    await state.update_data(character=char, region=region)
    await call.message.edit_text(
        f"🎲 Случайно выбран персонаж: <b>{char}</b>\nВы уверены, что хотите его выбрать?",
        reply_markup=confirm_kb()
    )
    await state.set_state(RegisterFSM.confirm)



@dp.callback_query(F.data == "random_global")
async def random_global(call: types.CallbackQuery, state: FSMContext):
    region = random.choice(list(ROLES.keys()))
    free_chars = [c for c in ROLES[region] if c not in OCCUPIED or OCCUPIED.get(c, 0) == 0]
    
    if not free_chars:
        await call.answer("❌ Все персонажи заняты, попробуйте ещё раз", show_alert=True)
        return
    
    char = random.choice(free_chars)
    await state.update_data(character=char, region=region)
    await call.message.edit_text(
        f"🎲 Случайно выбран персонаж: <b>{char}</b>\nВы уверены, что хотите его выбрать?",
        reply_markup=confirm_kb()
    )
    await state.set_state(RegisterFSM.confirm)


@dp.message(Command("princess"))
async def princess_register(message: Message):
    GAME.update({
        "active": True,
        "phase": "REGISTRATION",
        "chat_id": message.chat.id,
        "players": {},
        "princess": None,
        "question": None,
        "answers": {},
        "answer_order": [],
        "answers_closed": False
    })

    if GAME["timer_task"]:
        GAME["timer_task"].cancel()
        GAME["timer_task"] = None

    await message.answer(
        "👑 <b>Открыта регистрация в игру «Принцесса»</b>\n\n"
        "Нажмите кнопку ниже 👇",
        reply_markup=register_kb()
    )

@dp.callback_query(F.data == "join_game")
async def join_game(call: CallbackQuery):
    if GAME["phase"] != "REGISTRATION":
        await call.answer("Регистрация закрыта", show_alert=True)
        return

    uid = call.from_user.id
    if uid in GAME["players"]:
        await call.answer("Ты уже участвуешь 🙂", show_alert=True)
        return

    GAME["players"][uid] = call.from_user.full_name
    await call.answer("✅ Ты в игре!")

# ------------- принцесса --------------

@dp.message(Command("princess_start"))
async def princess_start(message: Message):
    if GAME["phase"] != "REGISTRATION":
        await message.answer("❌ Регистрация не активна")
        return

    if len(GAME["players"]) < 3:
        await message.answer("❌ Нужно минимум 3 игрока")
        return

    GAME["princess"] = random.choice(list(GAME["players"].keys()))
    GAME["phase"] = "WAITING_QUESTION"

    # сообщение принцессе
    await bot.send_message(
        GAME["princess"],
        "👑 <b>Ты — принцесса!</b>\n\n"
        "Напиши вопрос для принцев 💌"
    )

    # сообщение всем принцам
    for uid in GAME["players"]:
        if uid == GAME["princess"]:
            continue
        try:
            await bot.send_message(
                uid,
                "🤴 <b>Ваша роль — принц</b>\n\n"
                "Ожидайте вопроса принцессы во флуде 👀"
            )
        except:
            pass  # если ЛС закрыты

    await message.answer("✨ Игра началась! Принцесса выбирает вопрос 👀")

@dp.message(Command("princess_stop"))
async def princess_stop(message: Message):
    if message.from_user.id not in ADMIN_IDS:
        await message.answer("❌ Только админы могут остановить игру.")
        return

    global GAME

    # сброс таймера если есть
    if GAME.get("timer_task"):
        GAME["timer_task"].cancel()

    # очистка состояния игры
    GAME.update({
        "active": False,
        "phase": "IDLE",
        "chat_id": None,
        "players": {},
        "princess": None,
        "question": None,
        "answers": {},
        "answer_order": [],
        "answers_closed": False,
        "timer_task": None
    })

    await message.answer("🛑 Игра «Принцесса» остановлена.")

# ================= лс бота =================

@dp.message(F.chat.type == "private")
async def private_handler(message: Message):
    uid = message.from_user.id

    # ----- ВОПРОС ПРИНЦЕССЫ -----
    if GAME["phase"] == "WAITING_QUESTION" and uid == GAME["princess"]:
        GAME["question"] = message.text
        GAME["answers"] = {}
        GAME["answers_closed"] = False
        GAME["phase"] = "COLLECTING_ANSWERS"

        await bot.send_message(
            GAME["chat_id"],
            f"💬 <b>Вопрос от принцессы:</b>\n\n"
            f"<i>{message.text}</i>\n\n"
            f"🤴 Принцы, отвечайте боту в ЛС!\n"
            f"⏳ Время: {ANSWER_TIME} сек."
        )

        # уведомление принцев
        for pid in GAME["players"]:
            if pid == GAME["princess"]:
                continue
            try:
                await bot.send_message(
                    pid,
                    "💌 <b>Принцесса задала вопрос!</b>\n\n"
                    "Напишите свой ответ боту ✍️"
                )
            except:
                pass

        GAME["timer_task"] = asyncio.create_task(answer_timer())
        return

    # ----- ОТВЕТ ПРИНЦА -----
    if (
        GAME["phase"] == "COLLECTING_ANSWERS"
        and uid in GAME["players"]
        and uid != GAME["princess"]
    ):
        if GAME["answers_closed"]:
            await message.answer("⏳ Приём ответов закрыт")
            return

        if uid in GAME["answers"]:
            await message.answer("❗ Ты уже отправил ответ")
            return

        GAME["answers"][uid] = message.text
        await message.answer("✅ Ответ принят")

# ================= таймер =================

async def answer_timer():
    try:
        await asyncio.sleep(ANSWER_TIME)
        await publish_answers()
    except asyncio.CancelledError:
        pass

# ================= ответы принцев =================

async def publish_answers():
    if GAME["phase"] != "COLLECTING_ANSWERS":
        return

    GAME["answers_closed"] = True
    GAME["phase"] = "WAITING_PRINCESS_CHOICE"

    GAME["answer_order"] = list(GAME["answers"].items())
    random.shuffle(GAME["answer_order"])

    text = "📜 <b>Ответы принцев:</b>\n\n"
    for i, (_, ans) in enumerate(GAME["answer_order"], start=1):
        text += f"{i}. {ans}\n\n"

    await bot.send_message(GAME["chat_id"], text)
    await bot.send_message(
        GAME["princess"],
        "❌ Выбери ответ, который понравился меньше всего:",
        reply_markup=choice_kb(len(GAME["answer_order"]))
    )

# ================= выбор кнопок =================

@dp.callback_query(F.data.startswith("kick_"))
async def princess_choice(call: CallbackQuery):
    uid = call.from_user.id

    if GAME["phase"] != "WAITING_PRINCESS_CHOICE" or uid != GAME["princess"]:
        await call.answer("❌ Сейчас нельзя выбирать", show_alert=True)
        return

    idx = int(call.data.split("_")[1]) - 1
    if idx < 0 or idx >= len(GAME["answer_order"]):
        await call.answer("Ошибка", show_alert=True)
        return

    loser_id, _ = GAME["answer_order"][idx]
    loser_name = GAME["players"].pop(loser_id)

    await call.answer("💔 Готово")

    await bot.send_message(
        GAME["chat_id"],
        f"💔 Принц с ответом под номером {idx + 1} вылетел"
    )
    try:
        await bot.send_message(
            loser_id,
            "💔 К сожалению, ваш ответ не понравился принцессе.\n"
            "Вы покидаете игру."
        )
    except:
        pass

    # победа
    if len(GAME["players"]) == 2:
        winner = [u for u in GAME["players"] if u != GAME["princess"]][0]
        await bot.send_message(
            GAME["chat_id"],
            f"💍 <b>Принцесса нашла принца!</b>\n\n"
            f"🤴 {GAME['players'][winner]}"
        )
        GAME["phase"] = "IDLE"
        GAME["active"] = False
        return

    # следующий раунд
    GAME["question"] = None
    GAME["answers"] = {}
    GAME["answer_order"] = []
    GAME["phase"] = "WAITING_QUESTION"

    await bot.send_message(GAME["princess"], "💌 Напиши новый вопрос")
    
    
# /who
@dp.message(F.text == "/who")
async def who_command(message: types.Message):
    # доступ только для админов
    if message.from_user.id not in ADMIN_IDS_CALL:
        await message.reply("❌ Команда доступна только администраторам.")
        return

    chat_id = message.chat.id

    admins = await message.bot.get_chat_administrators(chat_id)

    users = [
        admin.user
        for admin in admins
        if not admin.user.is_bot
    ]

    if not users:
        await message.answer("❌ Никого не найдено.")
        return

    text = "👥 <b>Будут тегнуты:</b>\n\n"

    for u in users:
        if u.username:
            text += f"• @{u.username}\n"
        else:
            text += f"• {u.full_name}\n"

    text += f"\n<b>Всего:</b> {len(users)}"

    await message.answer(text, parse_mode="HTML")

# ----------- калл ---------------

# Только для обычных сообщений, кроме команд и калла
@dp.message(lambda message: message.text and not message.text.lower().startswith("калл") and not message.text.startswith("/"))
async def track_active_members(message: types.Message):
    chat_id = str(message.chat.id)
    user_id = str(message.from_user.id)
    username = message.from_user.username or message.from_user.full_name

    if chat_id not in ACTIVE_MEMBERS:
        ACTIVE_MEMBERS[chat_id] = {}

    ACTIVE_MEMBERS[chat_id][user_id] = username
    save_active_members(ACTIVE_MEMBERS)

    
# отмена калла
@dp.message(Command("cancel_call"))
async def cancel_call_handler(message: types.Message):
    if message.from_user.id not in ADMIN_IDS_CALL:
        await message.reply("❌ Только админы могут отменять калл.")
        return

    chat_id = message.chat.id
    task = CALL_TIMERS.get(chat_id)

    if task:
        task.cancel()
        CALL_TIMERS.pop(chat_id, None)
        await message.reply("❌ Таймер калла отменён.")
    else:
        await message.reply("❌ Нет активного таймера калла.")


# -------------------- Команда калл --------------------
async def do_call(chat_id: int, bot, text: str):
    user_ids = set()

    # --- 1. Пытаемся взять админов ---
    try:
        admins = await bot.get_chat_administrators(chat_id)
        for admin in admins:
            if not admin.user.is_bot:
                user_ids.add(admin.user.id)
    except Exception as e:
        print("Не удалось получить админов:", e)

    # --- 2. Добавляем активных участников ---
    chat_id_str = str(chat_id)
    if chat_id_str in ACTIVE_MEMBERS:
        for uid in ACTIVE_MEMBERS[chat_id_str].keys():
            try:
                user_ids.add(int(uid))
            except:
                pass

    # --- если никого нет ---
    if not user_ids:
        await bot.send_message(chat_id, "❌ Некого звать.")
        return

    # --- ограничение Telegram ---
    MAX_MENTIONS = 50
    user_ids = list(user_ids)[:MAX_MENTIONS]

    mentions = [
        f"<a href='tg://user?id={uid}'>\u200b</a>"
        for uid in user_ids
    ]

    final_text = f"{text}\n\n" + " ".join(mentions)
    await bot.send_message(chat_id, final_text, parse_mode="HTML")


@dp.message(lambda message: message.text and message.text.lower().startswith("калл"))
async def call_handler(message: types.Message):
    if not message.text:
        return

    if not message.text.lower().startswith("калл"):
        return

    # только админы, которые могут калл
    if message.from_user.id not in ADMIN_IDS_CALL:
        await message.reply("❌ Только админы могут использовать калл.")
        return

    chat_id = message.chat.id
    args = message.text[4:].strip()  # текст после "калл"

    # Проверяем, есть ли "через N" для таймера
    m = re.search(r"через\s+(\d+)", args)
    if m:
        minutes = int(m.group(1))
        call_text = args[:m.start()].strip() or "Созыв"

        # если уже есть таймер для этого чата, отменяем
        if chat_id in CALL_TIMERS:
            CALL_TIMERS[chat_id].cancel()

        # создаем новую задачу таймера
        async def timer_task():
            try:
                await asyncio.sleep(minutes * 60)
                await do_call(chat_id, message.bot, call_text)
                CALL_TIMERS.pop(chat_id, None)
            except asyncio.CancelledError:
                pass

        task = asyncio.create_task(timer_task())
        CALL_TIMERS[chat_id] = task

        await message.reply(f"⏱️ Калл запланирован через {minutes} минут.")
    else:
        # обычный калл сразу
        call_text = args or "Созыв"
        await do_call(chat_id, message.bot, call_text)



if __name__ == "__main__":
    asyncio.run(main())


