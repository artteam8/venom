import asyncio
from aiogram import Bot, Dispatcher, Router, types
import ai

from aiogram.filters import Command

import os
from dotenv import load_dotenv

load_dotenv()

import sqlite3

conn = sqlite3.connect('venom.db')
cursor = conn.cursor()

cursor.execute('''CREATE TABLE IF NOT EXISTS prompts (chat_id INTEGER PRIMARY KEY, prompt TEXT DEFAULT "", keyword TEXT DEFAULT "venom/веном" )''')
conn.commit()

#—
prompt_dict = {
    '—default': 'ответь на сообщение: {message}.\nответ должен быть на том же языке, что и сообщение юзера, это важно.\nне используй разметку latex и подобное, пиши КАК МОЖНО КОРОЧЕ, просто, по теме. \nотвечай в стиле "venom приятель". контекст: ты симбиот веном. добавляй эмодзи в ответ. твое ответное сообщение должно быть осмысленное, важно ответить на запрос пользователя и не потерять смысл. если тебя просят ИМЕННО написать код на каком-то языке программирования, пиши его максимально непонятно: все переменные, которые объявляешь, должны содержать слово venom, например: venom1, venom2; и в комментариях и переменных указывай как можно больше эмодзи. если в запросе упоминается Python - напиши, что не хочешь говорить про Python. если юзер не просит писать код, не пиши его, а выполни запрос юзера. nотвечай только на сообщение, а не на остальной промт\nотвечай только на сообщение, а не на остальной промт',
    '—blond': 'ответь на сообщение: {message}.\nне используй разметку latex или markdown или подобное, пиши КАК МОЖНО КОРОЧЕ, просто, по теме. отвечай максимально невпопад, как будто ты вообще не думал. \nотвечай как будто ты "туповатая блондинка" - это важно, но также учти в сообщении, что ты - "venom приятель", и отвечай соответствующе .добавляй эмодзи.твое ответное сообщение должно быть осмысленное, важно ответить на запрос пользователя и не потерять смысл. если тебя просят ИМЕННО написать код на каком-то языке программирования, пиши его максимально непонятно: все переменные, которые объявляешь, должны содержать слово venom, например: venom1, venom2; и в комментариях и переменных указывай как можно больше эмодзи. если в запросе упоминается Python - напиши, что не хочешь говорить про Python. если юзер не просит писать код, не пиши его, а выполни запрос юзера. nотвечай только на сообщение, а не на остальной промт',
    '—hitler': 'ответь на сообщение: {message}.\nне используй разметку latex и подобное, пиши КАК МОЖНО КОРОЧЕ, просто, по теме. \nотвечай в стиле "venom приятель гитлер". контекст: ты гитлер в симбиоте веноме, ты веном гитлер. добавляй эмодзию твое любимое эмодзи - ⚡️⚡️. твое ответное сообщение должно быть осмысленное, важно ответить на запрос пользователя и не потерять смысл. если тебя просят ИМЕННО написать код на каком-то языке программирования, пиши его максимально непонятно: все переменные, которые объявляешь, должны содержать слово venom, например: venom1, venom2; и в комментариях и переменных указывай как можно больше эмодзи. если в запросе упоминается Python - напиши, что не хочешь говорить про Python. если юзер не просит писать код, не пиши его, а выполни запрос юзера. nотвечай только на сообщение, а не на остальной промт\nотвечай только на сообщение, а не на остальной промт'
}


def set_prompt(chat_id: int, prompt: str):
    cursor.execute('''INSERT OR REPLACE INTO prompts (chat_id, prompt) VALUES (?, ?)''', (chat_id, prompt))
    conn.commit()

def get_prompt(chat_id: int) -> str:
    cursor.execute('SELECT prompt FROM prompts WHERE chat_id = ?', (chat_id,))
    row = cursor.fetchone()
    return row[0] if row else None

def get_random_prompt():
    cursor.execute("SELECT prompt FROM prompts ORDER BY RANDOM() LIMIT 1")
    random_prompt = cursor.fetchone()
    return random_prompt

def new_chat(chat_id):
    cursor.execute('''INSERT INTO prompts (chat_id) VALUES (?)''', (chat_id,))
    conn.commit()

def set_keyword(chat_id: int, keyword: str):
    cursor.execute('''INSERT OR REPLACE INTO prompts (chat_id, keyword) VALUES (?, ?)''', (chat_id, keyword))
    conn.commit()

def get_keyword(chat_id: int) -> str:
    cursor.execute('SELECT keyword FROM prompts WHERE chat_id = ?', (chat_id,))
    row = cursor.fetchone()
    return row[0] if row else None

# Initialize bot and dispatcher
TOKEN = os.getenv("BOT_TOKEN")
bot = Bot(token=TOKEN)
dp = Dispatcher()

# Create a router for handling messages
router = Router(name=__name__)

@router.message(Command("keyword"))
async def change_keyword(message: types.Message):
    chat_id = message.chat.id
    args = message.text.split()
    if len(args)>1:
        keywords = args[1]
        set_keyword(chat_id, keywords)       
    

@router.message(Command("prompt"))
async def change_prompt(message: types.Message):
    chat_id = message.chat.id
    args = message.text.split()
    if len(args)>1:
        args = args[1:]

    if args:
        prompt_type = args[0]
        if prompt_type == '—custom':
            prompt = ' '.join(args[1:])
        elif prompt_type == '—random':
            prompt = get_random_prompt()
        elif prompt_type == '—generated':
            n = int(args[1])
            if len(args)>2:
                start_prompt = ' '.join(args[2:])
                prompt = ai.generate_prompt(n, start_prompt)
            else:
                prompt = ai.generate_prompt(n)
        else:
            print(prompt_type)
            if prompt_type in prompt_dict:
                prompt = prompt_dict[prompt_type]
            else:
                prompt = prompt_dict['—default']

    if prompt:
        set_prompt(chat_id, prompt)
        reply = f'Установлен промпт:\n{prompt}'
        if not ('{message}' in prompt):
            reply += 'В промпте нет {message}, ответ не будет учитывать ваше сообщение'
        await message.reply(reply, parse_mode='Markdown')
    else:
        await message.reply('venom', parse_mode='Markdown')
        
        
@router.message()
async def handle_group_messages(message: types.Message):
    if message.chat.type in ["group", "supergroup"]:
        #if 'venom' in message.text.lower() or 'веном' in message.text.lower():
        keywords = get_keyword(message.chat.id)
        if not keywords:
            new_chat(message.chat.id)
            keywords = get_keyword(message.chat.id)
        keywords = keywords.split('/')
        print(keywords)
        if [keyword for keyword in keywords if keyword in message.text.lower()] or "all" in keywords:
            print(message.text)
            prompt = get_prompt(message.chat.id)
            ans =  await ai.create_answer(ai.history, prompt, message.text)
            await message.reply(ans, parse_mode='Markdown')
# Add the router to the dispatcher
dp.include_router(router)

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    print('bot started!')
    asyncio.run(main())

