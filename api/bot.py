import os
import json
import logging
import asyncio
from urllib.request import Request, urlopen
from urllib.parse import urlencode

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Токен бота
BOT_TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN')

def send_telegram_message_sync(chat_id, text):
    """Синхронная отправка сообщения в Telegram"""
    try:
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
        data = {
            'chat_id': chat_id,
            'text': text,
            'parse_mode': 'HTML'
        }
        
        request = Request(
            url,
            data=urlencode(data).encode(),
            headers={'Content-Type': 'application/x-www-form-urlencoded'}
        )
        
        with urlopen(request) as response:
            return json.loads(response.read().decode())
    except Exception as e:
        logger.error(f"Error sending message: {e}")
        return None

async def send_telegram_message(chat_id, text):
    """Асинхронная обертка для отправки сообщения"""
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, send_telegram_message_sync, chat_id, text)

async def process_update(update_data):
    """Обрабатывает обновление от Telegram"""
    try:
        if 'message' in update_data:
            message = update_data['message']
            chat_id = message['chat']['id']
            text = message.get('text', '')
            
            if text == '/start':
                response_text = "🕉️ Бот Бхагавад-Гиты запущен! Используйте /quote для получения цитаты."
            elif text == '/quote':
                response_text = """
🕉️ Бхагавад-Гита, Глава 2, Стих 47

Шлока:
кармаṇy-evādhikāras te mā phaleṣhu kadāchana
mā karma-phala-hetur bhūr mā te saṅgo 'stvakarmaṇi

Перевод:
Ты имеешь право только на действие, но никогда на его плоды.
Пусть плоды действия не будут твоим мотивом, и не будь привязан к бездействию.
                """
            elif text == '/help':
                response_text = "Помощь: /start, /quote, /help"
            else:
                response_text = "Неизвестная команда. Используйте /help для списка команд."
            
            await send_telegram_message(chat_id, response_text)
            
        return True
    except Exception as e:
        logger.error(f"Error processing update: {e}")
        return False

# Основной обработчик для Vercel
async def app(request):
    try:
        # GET запрос - проверка работоспособности
        if request.method == 'GET':
            return {
                'statusCode': 200,
                'headers': {'Content-Type': 'application/json'},
                'body': json.dumps({
                    'status': 'Bot is running', 
                    'ok': True,
                    'token_set': bool(BOT_TOKEN)
                })
            }
        
        # POST запрос от Telegram
        elif request.method == 'POST':
            # Получаем тело запроса
            body = await request.body()
            body_str = body.decode('utf-8')
            data = json.loads(body_str)
            
            logger.info(f"Received update from Telegram")
            
            # Обрабатываем обновление
            result = await process_update(data)
            
            return {
                'statusCode': 200,
                'headers': {'Content-Type': 'application/json'},
                'body': json.dumps({'status': 'ok' if result else 'error'})
            }
            
    except Exception as e:
        logger.error(f"Error in handler: {e}")
        return {
            'statusCode': 200,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({'status': 'error', 'message': str(e)})
        }
