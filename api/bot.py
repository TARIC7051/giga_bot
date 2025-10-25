import os
import logging
import random
import requests
import json
import html
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

# --- Настройка логирования ---
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# --- Получение токена из переменной окружения ---
TELEGRAM_BOT_TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN')
if not TELEGRAM_BOT_TOKEN:
    raise ValueError("Не установлена переменная окружения TELEGRAM_BOT_TOKEN")

# --- Константы API Гиты ---
GITA_API_BASE_URL = "https://api.bhagavadgita.io/v2"

# --- Создание Application ---
application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

# --- Функции для получения цитат ---
def fetch_random_verse_from_api():
    """Получает случайный стих из API."""
    verses_per_chapter = [47, 72, 43, 42, 29, 47, 30, 28, 34, 42, 55, 20, 18, 24, 20, 24, 28, 78]
    
    try:
        random_chapter = random.randint(1, 18)
        max_verse_in_chapter = verses_per_chapter[random_chapter - 1]
        random_verse_in_chapter = random.randint(1, max_verse_in_chapter)
        
        api_url = f"{GITA_API_BASE_URL}/chapter/{random_chapter}/verse/{random_verse_in_chapter}"
        
        headers = {
            'accept': 'application/json',
        }
        
        response = requests.get(api_url, headers=headers, params={'language': 'english'})
        response.raise_for_status()
        data = response.json()
        
        if 'chapter' not in data:
            data['chapter'] = random_chapter
        if 'verse' not in data:
            data['verse'] = random_verse_in_chapter
            
        return data
    except Exception as e:
        logger.error(f"Ошибка при запросе к API Гиты: {e}")
        return None

def load_quotes_from_file():
    """Загружает цитаты из локального файла."""
    try:
        with open('api/quotes.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Ошибка загрузки quotes.json: {e}")
        return []

def fetch_random_verse_from_file():
    """Получает случайный стих из локального JSON-файла."""
    try:
        local_quotes = load_quotes_from_file()
        if not local_quotes:
            return None
        selected_verse = random.choice(local_quotes)
        if 'chapter' not in selected_verse:
            selected_verse['chapter'] = 'N/A'
        if 'verse' not in selected_verse:
            selected_verse['verse'] = 'N/A'
        return selected_verse
    except Exception as e:
        logger.error(f"Ошибка при получении цитаты из файла: {e}")
        return None

async def fetch_random_verse():
    """Получает случайный стих."""
    logger.info("Попытка получить цитату из API...")
    
    import asyncio
    verse_data = await asyncio.get_event_loop().run_in_executor(None, fetch_random_verse_from_api)
    
    if verse_data is not None:
        logger.info("Цитата успешно получена из API.")
        return verse_data
    else:
        logger.warning("API недоступно. Используем запасной файл.")
        file_verse = await asyncio.get_event_loop().run_in_executor(None, fetch_random_verse_from_file)
        return file_verse

def format_verse_message(verse_data):
    """Форматирует данные стиха в строку для отправки."""
    if not verse_data:
        return "❌ Не удалось получить цитату."

    chapter = verse_data.get('chapter', 'N/A')
    verse_num = verse_data.get('verse', 'N/A')
    slok = verse_data.get('slok', '')
    translation = verse_data.get('translation', '')

    slok = html.escape(slok)
    translation = html.escape(translation)

    message_parts = [
        f"🕉️ <b>Бхагавад-Гита, Глава {chapter}, Стих {verse_num}</b>",
        "",
    ]
    if slok:
        message_parts.append(f"<b>Шлока (Санскрит):</b>\n{slok}")
    if translation:
        message_parts.append(f"\n<b>Перевод:</b>\n{translation}")
    
    return "\n".join(message_parts).strip()

# --- Обработчики команд ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    welcome_text = (
        "🕉️ Приветствую тебя в боте Бхагавад-гиты!\n\n"
        "Я буду делиться с тобой мудрыми цитатами (шлоками) из священного писания.\n\n"
        "Доступные команды:\n"
        "/start - показать это сообщение\n"
        "/quote - получить случайную цитату (шлоку)\n"
        "/help - помощь по командам\n"
        "/about - о боте\n\n"
        "Пусть эти знания принесут тебе мир и ясность! 🙏"
    )
    await update.message.reply_text(welcome_text)

async def get_quote(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text("⏳ Получаю мудрость из Гиты...")
    
    verse_data = await fetch_random_verse()
    message_text = format_verse_message(verse_data)
    await update.message.reply_text(message_text, parse_mode='HTML')

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    help_text = (
        "📖 ДОСТУПНЫЕ КОМАНДЫ:\n\n"
        "/start - начать работу с ботом\n"
        "/quote - случайная цитата (шлока) из Бхагавад-гиты\n"
        "/help - показать это сообщение\n"
        "/about - информация о боте"
    )
    await update.message.reply_text(help_text)

async def about(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    about_text = (
        "🤖 О ЭТОМ БОТЕ\n\n"
        "Этот бот создан для распространения мудрости Бхагавад-гиты.\n\n"
        "Используй команды бота для получения вдохновляющих цитат и мудрости на каждый день."
    )
    await update.message.reply_text(about_text)

# --- Регистрация обработчиков команд ---
application.add_handler(CommandHandler("start", start))
application.add_handler(CommandHandler("quote", get_quote))
application.add_handler(CommandHandler("help", help_command))
application.add_handler(CommandHandler("about", about))

# --- Vercel Serverless Function Handler ---
async def handler(request):
    """
    Vercel Serverless Function handler.
    """
    try:
        # Для GET запросов
        if request.method == 'GET':
            return {
                "statusCode": 200,
                "headers": {"Content-Type": "application/json"},
                "body": json.dumps({"status": "Bot is running", "ok": True})
            }
        
        # Для POST запросов от Telegram
        elif request.method == 'POST':
            body = await request.body()
            body_text = body.decode('utf-8')
            update_data = json.loads(body_text)
            
            update = Update.de_json(update_data, application.bot)
            
            await application.initialize()
            await application.process_update(update)
            await application.shutdown()
            
            return {
                "statusCode": 200,
                "headers": {"Content-Type": "application/json"},
                "body": json.dumps({"status": "ok"})
            }
        
        else:
            return {
                "statusCode": 405,
                "headers": {"Content-Type": "application/json"},
                "body": json.dumps({"error": "Method not allowed"})
            }
            
    except Exception as e:
        logger.error(f"Ошибка в handler: {e}")
        return {
            "statusCode": 200,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({"status": "error", "message": str(e)})
        }

# Vercel требует эту переменную
app = handler