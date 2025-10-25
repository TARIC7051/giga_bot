import os
import json
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Токен бота
BOT_TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN')

# Создаем приложение
application = Application.builder().token(BOT_TOKEN).build()

# Простые обработчики команд
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🕉️ Бот Бхагавад-Гиты запущен! Используйте /quote для получения цитаты.")

async def quote(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Временная простая цитата вместо API
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

# Инициализируем приложение один раз при запуске
async def initialize_app():
    await application.initialize()
    await application.start()
    await application.updater.start_polling()

# Обработчик для Vercel
async def handler(request):
    try:
        # GET запрос - проверка работоспособности
        if request.method == 'GET':
            return {
                'statusCode': 200,
                'headers': {'Content-Type': 'application/json'},
                'body': json.dumps({'status': 'Bot is running', 'ok': True})
            }
        
        # POST запрос - обновление от Telegram
        elif request.method == 'POST':
            body = await request.body()
            data = json.loads(body)
            
            update = Update.de_json(data, application.bot)
            await application.process_update(update)
            
            return {
                'statusCode': 200,
                'headers': {'Content-Type': 'application/json'},
                'body': json.dumps({'status': 'ok'})
            }
            
    except Exception as e:
        logger.error(f"Error: {e}")
        return {
            'statusCode': 200,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({'status': 'error', 'message': str(e)})
        }

app = handler
