import os
import json
import logging
import asyncio
from http.server import BaseHTTPRequestHandler

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Токен бота
BOT_TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN')

async def process_telegram_update(update_data):
    """Обрабатывает обновление от Telegram"""
    try:
        from telegram import Update
        from telegram.ext import Application, CommandHandler, ContextTypes
        
        # Создаем приложение
        application = Application.builder().token(BOT_TOKEN).build()
        
        # Обработчики команд
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
        
        # Обрабатываем обновление
        update = Update.de_json(update_data, application.bot)
        await application.initialize()
        await application.process_update(update)
        await application.shutdown()
        
        return True
    except Exception as e:
        logger.error(f"Error processing update: {e}")
        return False

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        """Обработчик GET запросов"""
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        response = json.dumps({"status": "Bot is running", "ok": True})
        self.wfile.write(response.encode())
    
    def do_POST(self):
        """Обработчик POST запросов от Telegram"""
        try:
            # Читаем тело запроса
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length)
            update_data = json.loads(post_data.decode('utf-8'))
            
            # Обрабатываем обновление асинхронно
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            result = loop.run_until_complete(process_telegram_update(update_data))
            loop.close()
            
            # Отправляем ответ
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            response = json.dumps({"status": "ok" if result else "error"})
            self.wfile.write(response.encode())
            
        except Exception as e:
            logger.error(f"Error in POST handler: {e}")
            self.send_response(200)  # Всегда 200 для Telegram
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            response = json.dumps({"status": "error", "message": str(e)})
            self.wfile.write(response.encode())

# Vercel ищет эту переменную
def app(environ, start_response):
    """WSGI приложение для совместимости"""
    handler = Handler(environ, start_response)
    return handler
