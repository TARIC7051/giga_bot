import os
import json
import logging
import asyncio

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Токен бота
BOT_TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN')

async def send_telegram_message(chat_id, text):
    """Отправляет сообщение в Telegram"""
    try:
        import aiohttp
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
        payload = {
            'chat_id': chat_id,
            'text': text,
            'parse_mode': 'HTML'
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=payload) as response:
                return await response.json()
    except Exception as e:
        logger.error(f"Error sending message: {e}")
        return None

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
🕉️ <b>Бхагавад-Гита, Глава 2, Стих 47</b>

<b>Шлока:</b>
кармаṇy-evādhikāras te mā phaleṣhu kadāchana
mā karma-phala-hetur bhūr mā te saṅgo 'stvakarmaṇi

<b>Перевод:</b>
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
