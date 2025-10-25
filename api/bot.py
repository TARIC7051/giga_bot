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
if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN not set")

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

# Обработчик для Vercel - максимально простой
async def handler(event, context):
    try:
        # GET запрос - проверка работоспособности
        if event.get('httpMethod') == 'GET':
            return {
                'statusCode': 200,
                'headers': {'Content-Type': 'application/json'},
                'body': json.dumps({'status': 'Bot is running', 'ok': True})
            }
        
        # POST запрос - обновление от Telegram
        elif event.get('httpMethod') == 'POST':
            body = event.get('body', '{}')
            
            # Декодируем base64 если нужно
            if event.get('isBase64Encoded', False):
                import base64
                body = base64.b64decode(body).decode('utf-8')
            
            data = json.loads(body)
            update = Update.de_json(data, application.bot)
            
            # Обрабатываем обновление
            await application.initialize()
            await application.process_update(update)
            await application.shutdown()
            
            return {
                'statusCode': 200,
                'headers': {'Content-Type': 'application/json'},
                'body': json.dumps({'status': 'ok'})
            }
        else:
            return {
                'statusCode': 405,
                'body': json.dumps({'error': 'Method not allowed'})
            }
            
    except Exception as e:
        logger.error(f"Error: {e}")
        return {
            'statusCode': 200,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({'status': 'error', 'message': str(e)})
        }

# Vercel требует эту переменную
app = handler
