import os
import sys

# Fix emoji output on Windows (cp1251 terminal)
if sys.stdout.encoding != "utf-8":
    sys.stdout.reconfigure(encoding="utf-8")
import json
import logging
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, CommandHandler, CallbackQueryHandler, ContextTypes
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

BOT_TOKEN = "8844824332:AAFJuC0GDd5ZQt3GbpgPkQtv04zE5Z_6C0w"
ADMIN_ID = 6653412161  # ID адміністратора /detid

# ──────────────────────────────────────────────
#  База даних фільмів MCU
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

# ──────────────────────────────────────────────
#  Розширене зберігання даних
# ──────────────────────────────────────────────
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

def load_activity() -> dict:
    if os.path.exists(ACTIVITY_FILE):
        try:
            with open(ACTIVITY_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            return {}
    return {}

def save_activity(data: dict):
    with open(ACTIVITY_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def log_activity(user_id: int, username: str, action: str, film_id: str = None):
    """Логує дії користувача"""
    activity = load_activity()
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
    
    # Обмежуємо історію до 1000 дій на користувача
    if len(activity[uid]["actions"]) > 1000:
        activity[uid]["actions"] = activity[uid]["actions"][-1000:]
    
    save_activity(activity)

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
#  Адмін функції
# ──────────────────────────────────────────────
async def admin_stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Показує статистику бота (тільки для адміна)"""
    if update.effective_user.id != ADMIN_ID:
        await update.message.reply_text("❌ У вас немає доступу до цієї команди.")
        return
    
    data = load_data()
    activity = load_activity()
    
    total_users = len(data)
    total_watched = sum(len(user_data["watched"]) for user_data in data.values())
    
    # Отримуємо останніх активних користувачів
    recent_users = []
    for uid, user_activity in activity.items():
        if user_activity.get("actions"):
            last_action = user_activity["actions"][-1]["timestamp"]
            recent_users.append((user_activity.get("username", uid), last_action))
    
    recent_users.sort(key=lambda x: x[1], reverse=True)
    recent_users = recent_users[:10]
    
    stats_text = (
        f"📊 *Статистика бота*\n\n"
        f"👥 Користувачів: {total_users}\n"
        f"🎬 Всього переглядів: {total_watched}\n"
        f"📈 Середній прогрес: {total_watched / total_users if total_users > 0 else 0:.1f} фільмів/користувача\n\n"
        f"🕐 *Останні активні:*\n"
    )
    
    for username, last_time in recent_users:
        stats_text += f"• {username}: {last_time[:16]}\n"
    
    await update.message.reply_text(stats_text, parse_mode="Markdown")

async def admin_export(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Експортує дані користувачів (тільки для адміна)"""
    if update.effective_user.id != ADMIN_ID:
        await update.message.reply_text("❌ У вас немає доступу.")
        return
    
    data = load_data()
    activity = load_activity()
    
    # Створюємо звіт
    report = {
        "generated": datetime.now().isoformat(),
        "users_data": data,
        "users_activity": activity,
        "total_users": len(data),
        "total_actions": sum(len(u.get("actions", [])) for u in activity.values())
    }
    
    # Зберігаємо тимчасовий файл
    report_file = f"report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(report_file, "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    
    # Відправляємо файл адміну
    with open(report_file, "rb") as f:
        await update.message.reply_document(
            document=f,
            filename=report_file,
            caption=f"📊 Звіт від {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        )
    
    # Видаляємо тимчасовий файл
    os.remove(report_file)

async def admin_user_progress(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Показує прогрес конкретного користувача (тільки для адміна)"""
    if update.effective_user.id != ADMIN_ID:
        await update.message.reply_text("❌ У вас немає доступу.")
        return
    
    # Очікуємо ID користувача
    try:
        user_id = int(context.args[0])
    except (IndexError, ValueError):
        await update.message.reply_text(
            "❌ Вкажіть ID користувача.\nПриклад: /user_progress 123456789"
        )
        return
    
    data = load_data()
    activity = load_activity()
    
    uid = str(user_id)
    if uid not in data:
        await update.message.reply_text(f"❌ Користувач з ID {user_id} не знайдений.")
        return
    
    user_data = data[uid]
    watched_films = user_data.get("watched", [])
    total_films = len(ALL_FILMS)
    
    # Отримуємо назви переглянутих фільмів
    watched_names = [ALL_FILMS.get(fid, {}).get("title", fid) for fid in watched_films]
    
    # Статистика по фазах
    phase_stats = {}
    for phase, films in MCU_FILMS.items():
        phase_watched = sum(1 for f in films if f["id"] in watched_films)
        phase_stats[phase] = phase_watched
    
    # Отримуємо інформацію про користувача
    user_info = activity.get(uid, {})
    username = user_info.get("username", "Невідомо")
    first_seen = user_info.get("first_seen", "Невідомо")
    last_action = user_info.get("actions", [{}])[-1].get("timestamp", "Невідомо")
    
    # Формуємо звіт
    report = (
        f"📊 *Прогрес користувача*\n\n"
        f"👤 ID: {user_id}\n"
        f"📛 Ім'я: {username}\n"
        f"📅 Перша поява: {first_seen[:16]}\n"
        f"🕐 Остання дія: {last_action[:16]}\n\n"
        f"🎬 *Загальний прогрес:*\n"
        f"✅ Переглянуто: {len(watched_films)}/{total_films} ({len(watched_films)*100//total_films}%)\n\n"
    )
    
    report += "*По фазах:*\n"
    for phase, count in phase_stats.items():
        phase_total = len(MCU_FILMS[phase])
        report += f"• {phase[:30]}: {count}/{phase_total}\n"
    
    if watched_names:
        report += f"\n*Переглянуті фільми:*\n"
        report += ", ".join(watched_names[:20])
        if len(watched_names) > 20:
            report += f" та ще {len(watched_names) - 20}"
    
    await update.message.reply_text(report, parse_mode="Markdown")

# ──────────────────────────────────────────────
#  Хелпери для клавіатур
# ──────────────────────────────────────────────
def main_menu_keyboard():
    buttons = []
    for phase in MCU_FILMS:
        total = len(MCU_FILMS[phase])
        buttons.append([InlineKeyboardButton(
            f"📽️ {phase} ({total} фільмів)",
            callback_data=f"phase:{phase}"
        )])
    buttons.append([InlineKeyboardButton("📊 Мій прогрес", callback_data="progress")])
    buttons.append([InlineKeyboardButton("🔄 Скинути всі позначки", callback_data="confirm_reset")])
    return InlineKeyboardMarkup(buttons)

def phase_keyboard(phase: str, user_id: int):
    films = MCU_FILMS[phase]
    watched = get_user_watched(user_id)
    buttons = []
    for film in films:
        checked = "✅" if film["id"] in watched else "⬜"
        buttons.append([
            InlineKeyboardButton(
                f"{checked} {film['emoji']} {film['title']} ({film['year']})",
                callback_data=f"film:{film['id']}"
            )
        ])
    buttons.append([InlineKeyboardButton("⬅️ Назад", callback_data="main_menu")])
    return InlineKeyboardMarkup(buttons)

def film_keyboard(film_id: str, user_id: int):
    film = ALL_FILMS[film_id]
    watched = get_user_watched(user_id)
    is_watched = film_id in watched
    check_label = "❌ Прибрати позначку" if is_watched else "✅ Відмітити як переглянутий"
    buttons = []
    if film.get("trailer") and len(film["trailer"]) > 20:
        buttons.append([InlineKeyboardButton("🎬 Дивитись трейлер", url=film["trailer"])])
    buttons.append([InlineKeyboardButton(check_label, callback_data=f"toggle:{film_id}")])
    buttons.append([InlineKeyboardButton("⬅️ Назад до фази", callback_data=f"phase:{film['phase']}")])
    return InlineKeyboardMarkup(buttons)

# ──────────────────────────────────────────────
#  Handlers
# ──────────────────────────────────────────────
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    # Логуємо початок
    log_activity(user.id, user.username or user.first_name, "start")
    
    text = (
        f"🦸 Привіт, {user.first_name}!\n\n"
        "Це твій особистий трекер фільмів Marvel MCU 🎬\n\n"
        "Тут ти можеш:\n"
        "• 📽️ Переглядати всі фільми по фазах\n"
        "• 🎬 Дивитись трейлери прямо тут\n"
        "• ✅ Відмічати переглянуті фільми\n"
        "• 📊 Стежити за своїм прогресом\n\n"
        "Обирай фазу 👇"
    )
    await update.message.reply_text(
        text,
        reply_markup=main_menu_keyboard()
    )

async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data
    user_id = query.from_user.id
    username = query.from_user.username or query.from_user.first_name
    
    # ── Головне меню ──
    if data == "main_menu":
        log_activity(user_id, username, "back_to_menu")
        await query.edit_message_text(
            "🦸 Marvel MCU — Трекер фільмів\n\nОбирай фазу 👇",
            reply_markup=main_menu_keyboard()
        )
    
    # ── Фаза ──
    elif data.startswith("phase:"):
        phase = data[len("phase:"):]
        log_activity(user_id, username, f"view_phase", phase)
        films = MCU_FILMS.get(phase, [])
        watched = get_user_watched(user_id)
        watched_count = sum(1 for f in films if f["id"] in watched)
        
        await query.edit_message_text(
            f"📽️ *{phase}*\n\n"
            f"Переглянуто: {watched_count}/{len(films)}\n\n"
            "Натисни на фільм щоб переглянути деталі:",
            parse_mode="Markdown",
            reply_markup=phase_keyboard(phase, user_id)
        )
    
    # ── Фільм ──
    elif data.startswith("film:"):
        film_id = data[len("film:"):]
        log_activity(user_id, username, f"view_film", film_id)
        film = ALL_FILMS.get(film_id)
        if not film:
            await query.edit_message_text("❌ Фільм не знайдено.")
            return
        watched = get_user_watched(user_id)
        status = "✅ Переглянуто" if film_id in watched else "⬜ Не переглянуто"
        has_trailer = film.get("trailer") and len(film["trailer"]) > 20
        
        text = (
            f"{film['emoji']} *{film['title']}*\n"
            f"📅 Рік: {film['year']}\n"
            f"🎭 Фаза: {film['phase']}\n"
            f"👁️ Статус: {status}\n"
        )
        if has_trailer:
            text += "\n🎬 Трейлер доступний!"
        
        await query.edit_message_text(
            text,
            parse_mode="Markdown",
            reply_markup=film_keyboard(film_id, user_id)
        )
    
    # ── Відмітити / зняти відмітку ──
    elif data.startswith("toggle:"):
        film_id = data[len("toggle:"):]
        film = ALL_FILMS.get(film_id)
        if not film:
            return
        result = toggle_watched(user_id, film_id)
        action = "mark_watched" if result else "mark_unwatched"
        log_activity(user_id, username, action, film_id)
        
        msg = "✅ Відмічено як переглянутий!" if result else "⬜ Позначку знято."
        await query.answer(msg, show_alert=False)
        
        # Оновлюємо картку фільму
        watched = get_user_watched(user_id)
        status = "✅ Переглянуто" if film_id in watched else "⬜ Не переглянуто"
        has_trailer = film.get("trailer") and len(film["trailer"]) > 20
        
        text = (
            f"{film['emoji']} *{film['title']}*\n"
            f"📅 Рік: {film['year']}\n"
            f"🎭 Фаза: {film['phase']}\n"
            f"👁️ Статус: {status}\n"
        )
        if has_trailer:
            text += "\n🎬 Трейлер доступний!"
        
        await query.edit_message_text(
            text,
            parse_mode="Markdown",
            reply_markup=film_keyboard(film_id, user_id)
        )
    
    # ── Прогрес ──
    elif data == "progress":
        log_activity(user_id, username, "view_progress")
        watched = get_user_watched(user_id)
        total_all = len(ALL_FILMS)
        watched_all = len(watched)
        pct = int(watched_all / total_all * 100) if total_all else 0
        
        # Прогрес-бар
        filled = pct // 10
        bar = "█" * filled + "░" * (10 - filled)
        
        lines = [
            f"📊 *Твій прогрес Marvel MCU*\n",
            f"Загалом: {watched_all}/{total_all} ({pct}%)",
            f"`[{bar}]`\n",
        ]
        for phase, films in MCU_FILMS.items():
            count = sum(1 for f in films if f["id"] in watched)
            total = len(films)
            phase_pct = int(count / total * 100) if total else 0
            stars = "⭐" * (count // max(1, total // 3)) if count > 0 else ""
            lines.append(f"• {phase}: {count}/{total} {stars}")
        
        if watched_all == total_all:
            lines.append("\n🏆 Ти подивився всі фільми Marvel! Легенда!")
        elif watched_all >= total_all * 0.8:
            lines.append("\n🔥 Майже фінал! Ще трохи!")
        elif watched_all >= total_all * 0.5:
            lines.append("\n💪 Вже половина! Так тримати!")
        elif watched_all > 0:
            lines.append("\n🚀 Гарний початок! Продовжуй!")
        else:
            lines.append("\n👋 Ще жодного фільму — починай прямо зараз!")
        
        await query.edit_message_text(
            "\n".join(lines),
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("⬅️ Назад", callback_data="main_menu")]
            ])
        )
    
    # ── Підтвердження скидання ──
    elif data == "confirm_reset":
        log_activity(user_id, username, "confirm_reset")
        await query.edit_message_text(
            "⚠️ *Ти впевнений?*\n\nВсі позначки переглянутих фільмів будуть видалені!",
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup([
                [
                    InlineKeyboardButton("🗑️ Так, скинути", callback_data="reset_confirmed"),
                    InlineKeyboardButton("❌ Ні, назад", callback_data="main_menu"),
                ]
            ])
        )
    
    # ── Скидання підтверджено ──
    elif data == "reset_confirmed":
        log_activity(user_id, username, "reset_all")
        data_all = load_data()
        uid = str(user_id)
        if uid in data_all:
            data_all[uid]["watched"] = []
            save_data(data_all)
        await query.edit_message_text(
            "✅ Всі позначки скинуто!\n\nПочинай марафон знову 🎬",
            reply_markup=main_menu_keyboard()
        )

# ──────────────────────────────────────────────
#  Команда для отримання ID
# ──────────────────────────────────────────────
# ──────────────────────────────────────────────
#  Команда для отримання ID (виправлена)
# ──────────────────────────────────────────────
async def get_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда для отримання свого Telegram ID"""
    user_id = update.effective_user.id
    # Використовуємо простий текст без Markdown
    await update.message.reply_text(
        f"🆔 Ваш Telegram ID: {user_id}\n\n"
        f"Скопіюйте цей ID та вставте його в змінну ADMIN_ID в коді бота."
    )

# ──────────────────────────────────────────────
#  Запуск (виправлений)
# ──────────────────────────────────────────────
def main():
    """Головна функція запуску бота"""
    try:
        # Створюємо додаток
        app = Application.builder().token(BOT_TOKEN).build()
        
        # Додаємо обробники
        app.add_handler(CommandHandler("start", start))
        app.add_handler(CommandHandler("getid", get_id))
        app.add_handler(CallbackQueryHandler(handle_callback))
        
        # Якщо встановлено ADMIN_ID, додаємо адмін команди
        if ADMIN_ID:
            app.add_handler(CommandHandler("stats", admin_stats))
            app.add_handler(CommandHandler("export", admin_export))
            app.add_handler(CommandHandler("user_progress", admin_user_progress))
            print("✅ Адмін команди активовано!")
        else:
            print("⚠️ Адмін команди не активовано (ADMIN_ID = None)")
        
        print("🦸 Marvel Bot запущено!")
        print("👇 Використайте команду /getid щоб дізнатись свій Telegram ID")
        
        # Запускаємо бота
        app.run_polling(drop_pending_updates=True)
        
    except Exception as e:
        print(f"❌ Помилка: {e}")
        print("\nМожливі рішення:")
        print("1. Перевірте підключення до інтернету")
        print("2. Переконайтесь що токен бота правильний")
        print("3. Спробуйте через 5-10 секунд")
        print("4. Перевірте чи не заблоковано Telegram API")

if __name__ == "__main__":
    main()