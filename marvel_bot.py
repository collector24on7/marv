import os
import json
import logging
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

# Налаштування логування
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Отримуємо дані з змінних оточення Render
BOT_TOKEN = os.environ.get("BOT_TOKEN")
ADMIN_ID = int(os.environ.get("ADMIN_ID")) if os.environ.get("ADMIN_ID") else None

# Перевірка чи є токен
if not BOT_TOKEN:
    print("❌ ПОМИЛКА: BOT_TOKEN не знайдено! Додайте змінну оточення BOT_TOKEN на Render")
    exit(1)

print(f"✅ Бот запускається з токеном: {BOT_TOKEN[:10]}...")
print(f"👑 Адмін ID: {ADMIN_ID if ADMIN_ID else 'Не налаштовано'}")

# ... (ВЕСЬ ІНШИЙ КОД ЗАЛИШАЄТЬСЯ ТАКИМ Ж, ДО ФУНКЦІЇ main) ...

# ──────────────────────────────────────────────
#  База даних фільмів MCU (така ж як була)
# ──────────────────────────────────────────────
MCU_FILMS = {
    "Фаза 1 — Перші Месники": [
        {"id": "f1", "title": "Залізна людина", "year": 2008, "trailer": "https://youtu.be/8hYlB38asDY", "emoji": "🦾"},
        {"id": "f2", "title": "Неймовірний Галк", "year": 2008, "trailer": "https://youtu.be/TqgSiS7XHSQ", "emoji": "💚"},
        {"id": "f3", "title": "Залізна людина 2", "year": 2010, "trailer": "https://youtu.be/ygM3DxkpUhA", "emoji": "🦾"},
        {"id": "f4", "title": "Тор", "year": 2011, "trailer": "https://youtu.be/JOddp-nlNvQ", "emoji": "⚡"},
        {"id": "f5", "title": "Капітан Америка: Перший Месник", "year": 2011, "trailer": "https://youtu.be/JerVrbLldXw", "emoji": "🛡️"},
        {"id": "f6", "title": "Месники", "year": 2012, "trailer": "https://youtu.be/eOrNdBpGMv8", "emoji": "🦸"},
    ],
    "Фаза 2 — Темний світ": [
        {"id": "f7", "title": "Залізна людина 3", "year": 2013, "trailer": "https://youtu.be/2CzoSeClcw0", "emoji": "🦾"},
        {"id": "f8", "title": "Тор: Царство темряви", "year": 2013, "trailer": "https://youtu.be/npGMUgMuMSk", "emoji": "⚡"},
        {"id": "f9", "title": "Капітан Америка: Зимовий солдат", "year": 2014, "trailer": "https://youtu.be/7SlILk2WMTI", "emoji": "🛡️"},
        {"id": "f10", "title": "Вартові Галактики", "year": 2014, "trailer": "https://youtu.be/d96cjJhvlMA", "emoji": "🚀"},
        {"id": "f11", "title": "Месники: Ера Альтрона", "year": 2015, "trailer": "https://youtu.be/tmeOjFno6Do", "emoji": "🤖"},
        {"id": "f12", "title": "Людина-мураха", "year": 2015, "trailer": "https://youtu.be/pWdKf3MneyI", "emoji": "🐜"},
    ],
    "Фаза 3 — Інфінітні війни": [
        {"id": "f13", "title": "Перший Месник: Протистояння", "year": 2016, "trailer": "https://youtu.be/dKrVegVI0Us", "emoji": "🛡️"},
        {"id": "f14", "title": "Доктор Стрендж", "year": 2016, "trailer": "https://youtu.be/HSzx-zryEgM", "emoji": "🔮"},
        {"id": "f15", "title": "Вартові Галактики 2", "year": 2017, "trailer": "https://youtu.be/dW1BIid8Osg", "emoji": "🚀"},
        {"id": "f16", "title": "Людина-павук: Повернення додому", "year": 2017, "trailer": "https://youtu.be/rk-dF1lIbIg", "emoji": "🕷️"},
        {"id": "f17", "title": "Тор: Рагнарок", "year": 2017, "trailer": "https://youtu.be/ue80QwXMRHg", "emoji": "⚡"},
        {"id": "f18", "title": "Чорна пантера", "year": 2018, "trailer": "https://youtu.be/xjDjIWPwcPU", "emoji": "🐾"},
        {"id": "f19", "title": "Месники: Війна нескінченності", "year": 2018, "trailer": "https://youtu.be/6ZfuNTqbHE8", "emoji": "💎"},
        {"id": "f20", "title": "Людина-мураха та Оса", "year": 2018, "trailer": "https://youtu.be/Ct3Ul2fjBIE", "emoji": "🐜"},
        {"id": "f21", "title": "Капітан Марвел", "year": 2019, "trailer": "https://youtu.be/Z1BCujX3pw8", "emoji": "⭐"},
        {"id": "f22", "title": "Месники: Завершення", "year": 2019, "trailer": "https://youtu.be/TcMBFSGVi1c", "emoji": "🏆"},
        {"id": "f23", "title": "Людина-павук: Далеко від дому", "year": 2019, "trailer": "https://youtu.be/Nt9L1jCKGnE", "emoji": "🕷️"},
    ],
    "Фаза 4 — Мультивсесвіт": [
        {"id": "f24", "title": "Чорна вдова", "year": 2021, "trailer": "https://youtu.be/ybji16u608U", "emoji": "🕸️"},
        {"id": "f25", "title": "Шан-Чі та легенда десяти кілець", "year": 2021, "trailer": "https://youtu.be/8YjFbMbfXaQ", "emoji": "🐉"},
        {"id": "f26", "title": "Вічні", "year": 2021, "trailer": "https://youtu.be/x_me3xsvDgk", "emoji": "✨"},
        {"id": "f27", "title": "Людина-павук: Немає шляху додому", "year": 2021, "trailer": "https://youtu.be/JfVOs4VSpmA", "emoji": "🕷️"},
        {"id": "f28", "title": "Доктор Стрендж у мультивсесвіті божевілля", "year": 2022, "trailer": "https://youtu.be/aWzlQ2N6qqg", "emoji": "🔮"},
        {"id": "f29", "title": "Тор: Любов і грім", "year": 2022, "trailer": "https://youtu.be/tgB1wUcmbbw", "emoji": "⚡"},
        {"id": "f30", "title": "Чорна пантера: Ваканда назавжди", "year": 2022, "trailer": "https://youtu.be/RlOB3UALvrQ", "emoji": "🐾"},
    ],
    "Фаза 5 — Мультивсесвіт": [
        {"id": "f31", "title": "Людина-мураха та Оса: Квантоманія", "year": 2023, "trailer": "https://youtu.be/ZlNFpri-Y40", "emoji": "🐜"},
        {"id": "f32", "title": "Вартові Галактики 3", "year": 2023, "trailer": "https://youtu.be/u3V5KDHRQvk", "emoji": "🚀"},
        {"id": "f33", "title": "Марвели", "year": 2023, "trailer": "https://youtu.be/wS_qbMF9XW8", "emoji": "⭐"},
        {"id": "f34", "title": "Дедпул і Росомаха", "year": 2024, "trailer": "https://youtu.be/73_1biulkYk", "emoji": "💀"},
        {"id": "f35", "title": "Капітан Америка: Чудесний новий світ", "year": 2025, "trailer": "https://youtu.be/MJTvWcU_dlI", "emoji": "🛡️"},
        {"id": "f36", "title": "Громовержці*", "year": 2025, "trailer": "https://youtu.be/TuFGTLs5-9s", "emoji": "⚡"},
    ],
    "Фаза 6 — Нова ера": [
        {"id": "f37", "title": "Фантастична четвірка: Перші кроки", "year": 2025, "trailer": "https://youtu.be/BFrYCMgvFis", "emoji": "🔥"},
        {"id": "f38", "title": "Месники: Сходження Доктора Дума", "year": 2026, "trailer": "", "emoji": "💀"},
        {"id": "f39", "title": "Месники: Таємні війни", "year": 2027, "trailer": "", "emoji": "🌌"},
    ]
}

ALL_FILMS = {}
for phase, films in MCU_FILMS.items():
    for film in films:
        ALL_FILMS[film["id"]] = {**film, "phase": phase}

# Файли для збереження даних
DATA_FILE = "user_data.json"
ACTIVITY_FILE = "user_activity.json"

def load_data() -> dict:
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            return {}
    return {}

def save_data(data: dict):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def log_activity(user_id: int, username: str, action: str, film_id: str = None):
    activity = {}
    if os.path.exists(ACTIVITY_FILE):
        try:
            with open(ACTIVITY_FILE, "r", encoding="utf-8") as f:
                activity = json.load(f)
        except:
            pass
    
    uid = str(user_id)
    if uid not in activity:
        activity[uid] = {
            "user_id": user_id,
            "username": username,
            "first_seen": datetime.now().isoformat(),
            "actions": []
        }
    
    activity[uid]["actions"].append({
        "timestamp": datetime.now().isoformat(),
        "action": action,
        "film_id": film_id
    })
    
    with open(ACTIVITY_FILE, "w", encoding="utf-8") as f:
        json.dump(activity, f, ensure_ascii=False, indent=2)

def get_user_watched(user_id: int) -> set:
    data = load_data()
    return set(data.get(str(user_id), {}).get("watched", []))

def toggle_watched(user_id: int, film_id: str) -> bool:
    data = load_data()
    uid = str(user_id)
    if uid not in data:
        data[uid] = {"watched": []}
    watched = set(data[uid]["watched"])
    if film_id in watched:
        watched.discard(film_id)
        result = False
    else:
        watched.add(film_id)
        result = True
    data[uid]["watched"] = list(watched)
    data[uid]["last_update"] = datetime.now().isoformat()
    save_data(data)
    return result

# ──────────────────────────────────────────────
#  Клавіатури
# ──────────────────────────────────────────────
def main_menu_keyboard():
    buttons = []
    for phase in MCU_FILMS:
        total = len(MCU_FILMS[phase])
        buttons.append([InlineKeyboardButton(f"📽️ {phase} ({total})", callback_data=f"phase:{phase}")])
    buttons.append([InlineKeyboardButton("📊 Мій прогрес", callback_data="progress")])
    buttons.append([InlineKeyboardButton("🔄 Скинути", callback_data="confirm_reset")])
    return InlineKeyboardMarkup(buttons)

def phase_keyboard(phase: str, user_id: int):
    films = MCU_FILMS[phase]
    watched = get_user_watched(user_id)
    buttons = []
    for film in films:
        checked = "✅" if film["id"] in watched else "⬜"
        buttons.append([InlineKeyboardButton(f"{checked} {film['emoji']} {film['title']}", callback_data=f"film:{film['id']}")])
    buttons.append([InlineKeyboardButton("⬅️ Назад", callback_data="main_menu")])
    return InlineKeyboardMarkup(buttons)

def film_keyboard(film_id: str, user_id: int):
    film = ALL_FILMS[film_id]
    watched = get_user_watched(user_id)
    is_watched = film_id in watched
    check_label = "❌ Прибрати" if is_watched else "✅ Відмітити"
    buttons = []
    if film.get("trailer") and len(film["trailer"]) > 20:
        buttons.append([InlineKeyboardButton("🎬 Трейлер", url=film["trailer"])])
    buttons.append([InlineKeyboardButton(check_label, callback_data=f"toggle:{film_id}")])
    buttons.append([InlineKeyboardButton("⬅️ Назад", callback_data=f"phase:{film['phase']}")])
    return InlineKeyboardMarkup(buttons)

# ──────────────────────────────────────────────
#  Handlers
# ──────────────────────────────────────────────
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    log_activity(user.id, user.username or user.first_name, "start")
    await update.message.reply_text(
        f"🦸 Привіт, {user.first_name}!\n\nЦе трекер фільмів Marvel MCU 🎬\n\nОбирай фазу 👇",
        reply_markup=main_menu_keyboard()
    )

async def get_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    await update.message.reply_text(f"🆔 Ваш Telegram ID: `{user_id}`", parse_mode="Markdown")

async def admin_stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if ADMIN_ID and update.effective_user.id != ADMIN_ID:
        await update.message.reply_text("❌ Немає доступу")
        return
    data = load_data()
    await update.message.reply_text(f"📊 Користувачів: {len(data)}")

async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data
    user_id = query.from_user.id
    username = query.from_user.username or query.from_user.first_name
    
    if data == "main_menu":
        await query.edit_message_text("Обирай фазу 👇", reply_markup=main_menu_keyboard())
    
    elif data.startswith("phase:"):
        phase = data[6:]
        films = MCU_FILMS.get(phase, [])
        watched = get_user_watched(user_id)
        count = sum(1 for f in films if f["id"] in watched)
        await query.edit_message_text(
            f"📽️ {phase}\nПереглянуто: {count}/{len(films)}",
            reply_markup=phase_keyboard(phase, user_id)
        )
    
    elif data.startswith("film:"):
        film_id = data[5:]
        film = ALL_FILMS.get(film_id)
        if film:
            watched = get_user_watched(user_id)
            status = "✅" if film_id in watched else "⬜"
            await query.edit_message_text(
                f"{film['emoji']} {film['title']}\nРік: {film['year']}\nСтатус: {status}",
                reply_markup=film_keyboard(film_id, user_id)
            )
    
    elif data.startswith("toggle:"):
        film_id = data[7:]
        film = ALL_FILMS.get(film_id)
        if film:
            result = toggle_watched(user_id, film_id)
            action = "mark_watched" if result else "mark_unwatched"
            log_activity(user_id, username, action, film_id)
            status = "✅" if result else "⬜"
            await query.edit_message_text(
                f"{film['emoji']} {film['title']}\nРік: {film['year']}\nСтатус: {status}",
                reply_markup=film_keyboard(film_id, user_id)
            )
    
    elif data == "progress":
        watched = get_user_watched(user_id)
        total = len(ALL_FILMS)
        await query.edit_message_text(
            f"📊 Прогрес: {len(watched)}/{total}",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ Назад", callback_data="main_menu")]])
        )
    
    elif data == "confirm_reset":
        await query.edit_message_text(
            "⚠️ Скинути всі позначки?",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("✅ Так", callback_data="reset_confirmed"),
                 InlineKeyboardButton("❌ Ні", callback_data="main_menu")]
            ])
        )
    
    elif data == "reset_confirmed":
        data_all = load_data()
        uid = str(user_id)
        if uid in data_all:
            data_all[uid]["watched"] = []
            save_data(data_all)
        await query.edit_message_text("✅ Скинуто!", reply_markup=main_menu_keyboard())

# ──────────────────────────────────────────────
#  Запуск
# ──────────────────────────────────────────────
def main():
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("getid", get_id))
    app.add_handler(CommandHandler("stats", admin_stats))
    app.add_handler(CallbackQueryHandler(handle_callback))
    
    print("🦸 Бот запущено!")
    app.run_polling(allowed_updates=["message", "callback_query"])

if __name__ == "__main__":
    main()
