import os
import json
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Токен бота
BOT_TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN')
if not BOT_TOKEN:
    logger.error("TELEGRAM_BOT_TOKEN not found in environment variables")
    # Для отладки - создаем фейковый токен если не установлен
    BOT_TOKEN = "fake_token_for_debug"

# Создаем приложение
application = Application.builder().token(BOT_TOKEN).build()

# Простые обработчики команд
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🕉️ Бот Бхагавад-Гиты запущен! Используйте /quote для получения цитаты.")

async def quote(update: Update, context: ContextTypes.DEFAULT_TYPE):
    quote_text = """
🕉️ **Бхагавад-Гита, Глава 2, Стих 47**

**Шлока:**
кармаṇy-evādhikāras te mā phaleṣhu kadāchana
mā karma-phala-hetur bhūr mā te saṅgo 'stvakarmaṇi

**Перевод:**
Ты имеешь право только на действие, но никогда на его плоды.
Пусть плоды действия не будут твоим мотивом, и не будь привязан к бездействию.
    """
    await update.message.reply_text(quote_text)

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Помощь: /start, /quote, /help")

# Регистрируем обработчики
application.add_handler(CommandHandler("start", start))
application.add_handler(CommandHandler("quote", quote))
application.add_handler(CommandHandler("help", help_command))

# Инициализируем приложение при импорте
async def initialize():
    await application.initialize()
    await application.start()
    logger.info("Bot application initialized")

# Запускаем инициализацию
import asyncio
try:
    asyncio.get_event_loop().run_until_complete(initialize())
except RuntimeError:
    # Если уже есть running loop (например, в Vercel)
    asyncio.create_task(initialize())

# Обработчик для Vercel
async def app(request):
    try:
        # GET запрос
        if request.method == 'GET':
            return {
                'statusCode': 200,
                'headers': {'Content-Type': 'application/json'},
                'body': json.dumps({
                    'status': 'Bot is running', 
                    'ok': True,
                    'token_set': bool(BOT_TOKEN and BOT_TOKEN != "fake_token_for_debug")
                })
            }
        
        # POST запрос от Telegram
        elif request.method == 'POST':
            # Получаем тело запроса
            body = await request.body()
            body_str = body.decode('utf-8')
            data = json.loads(body_str)
            
            logger.info(f"Received update: {data}")
            
            # Создаем объект Update
            update = Update.de_json(data, application.bot)
            
            # Обрабатываем обновление
            await application.process_update(update)
            
            return {
                'statusCode': 200,
                'headers': {'Content-Type': 'application/json'},
                'body': json.dumps({'status': 'ok'})
            }
            
    except Exception as e:
        logger.error(f"Error in handler: {e}")
        return {
            'statusCode': 200,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({'status': 'error', 'message': str(e)})
        }
