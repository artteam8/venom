import asyncio
from aiogram import Bot, Dispatcher, Router, types
import ai

import os
from dotenv import load_dotenv

load_dotenv()

import sqlite3

conn = sqlite3.connect('venom.db')
cursor = conn.cursor()

cursor.execute('''CREATE TABLE IF NOT EXISTS prompts (chat_id INTEGER PRIMARY KEY, prompt TEXT DEFAULT ""''')
conn.commit()


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

# Initialize bot and dispatcher
TOKEN = os.getenv("BOT_TOKEN")
bot = Bot(token=TOKEN)
dp = Dispatcher()

# Create a router for handling messages
router = Router(name=__name__)

@router.message(Command("/prompt"))
async def change_prompt(message: types.Message):
    chat_id = message.chat.id
    args = message.get_args()
    if args:
        prompt_type = args[0]
        if prompt_type == '--custom':
            prompt = ''.join(args[1:])
        elif prompt_type == '--random':
            prompt = get_random_prompt()
        elif prompt_type == '--generated':
            n = int(args[1])
            if len(args)>2:
                start_prompt = ''.join(args[2:])
                prompt = ai.generate_prompt(n, start_prompt)
            else:
                prompt = ai.generate_prompt(n)
        else:
            if prompt_type in prompt_dict:
                prompt = prompt_dict[prompt_type]
            else:
                prompt = prompt_dict['--default']

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
        if 'venom' in message.text.lower() or 'веном' in message.text.lower():
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

