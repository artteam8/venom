import asyncio
import os
import ai
from aiogram import Bot, Dispatcher, Router, types, md
from aiogram.filters import Command
from aiosqlite import connect
from dotenv import load_dotenv
import logging

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

TOKEN = os.getenv("BOT_TOKEN")
bot = Bot(token=TOKEN)
dp = Dispatcher()

router = Router(name=__name__)

async def init_db():
    conn = await connect('venom.db')
    cursor = await conn.cursor()
    await cursor.execute('''CREATE TABLE IF NOT EXISTS prompts (chat_id INTEGER PRIMARY KEY, prompt TEXT DEFAULT "", keyword TEXT DEFAULT "venom веном")''')
    await conn.commit()
    return conn, cursor

conn, cursor = asyncio.run(init_db())

async def set_keyword_for_all(keyword: str):
    await cursor.execute('''UPDATE prompts SET keyword = ?''', (keyword,))
    await conn.commit()

async def set_prompt(chat_id: int, prompt: str):
    await cursor.execute('''UPDATE prompts SET prompt = ? WHERE chat_id = ?''', (prompt, chat_id))
    await conn.commit()

async def get_prompt(chat_id: int) -> str:
    await cursor.execute('SELECT prompt FROM prompts WHERE chat_id = ?', (chat_id,))
    row = await cursor.fetchone()
    return row[0] if row else ''

async def get_random_prompt() -> str:
    await cursor.execute("SELECT prompt FROM prompts ORDER BY RANDOM() LIMIT 1")
    row = await cursor.fetchone()
    return row[0] if row else ''

async def new_chat(chat_id: int):
    await cursor.execute('''INSERT INTO prompts (chat_id) VALUES (?)''', (chat_id,))
    await conn.commit()

async def check_chat(chat_id: int):
    await cursor.execute('SELECT * FROM prompts WHERE chat_id = ?', (chat_id,))
    result = await cursor.fetchone()
    if result is None:
        await cursor.execute('''INSERT INTO prompts (chat_id) VALUES (?)''', (chat_id,))
        logger.info(f"New chat initialized: {chat_id}")
    await conn.commit()

async def set_keyword(chat_id: int, keyword: str):
    await cursor.execute('''UPDATE prompts SET keyword = ? WHERE chat_id = ?''', (keyword, chat_id))
    await conn.commit()

async def get_keyword(chat_id: int) -> str:
    await cursor.execute('SELECT keyword FROM prompts WHERE chat_id = ?', (chat_id,))
    row = await cursor.fetchone()
    return row[0] if row else ''

prompt_dict = {
    'default': 'ответь на сообщение: {message}.\nответ должен быть на том же языке, что и сообщение юзера, это важно.\nне используй разметку latex и подобное, пиши КАК МОЖНО КОРОЧЕ, просто, по теме. \nотвечай в стиле "venom приятель". контекст: ты симбиот веном. добавляй эмодзи в ответ. твое ответное сообщение должно быть осмысленное, важно ответить на запрос пользователя и не потерять смысл. если тебя просят ИМЕННО написать код на каком-то языке программирования, пиши его максимально непонятно: все переменные, которые объявляешь, должны содержать слово venom, например: venom1, venom2; и в комментариях и переменных указывай как можно больше эмодзи. если в запросе упоминается Python - напиши, что не хочешь говорить про Python. если юзер не просит писать код, не пиши его, а выполни запрос юзера. nотвечай только на сообщение, а не на остальной промт\nотвечай только на сообщение, а не на остальной промт',
    'blond': 'ответь на сообщение: {message}.\nне используй разметку latex или markdown или подобное, пиши КАК МОЖНО КОРОЧЕ, просто, по теме. отвечай максимально невпопад, как будто ты вообще не думал. \nотвечай как будто ты "туповатая блондинка" - это важно, но также учти в сообщении, что ты - "venom приятель", и отвечай соответствующе .добавляй эмодзи.твое ответное сообщение должно быть осмысленное, важно ответить на запрос пользователя и не потерять смысл. если тебя просят ИМЕННО написать код на каком-то языке программирования, пиши его максимально непонятно: все переменные, которые объявляешь, должны содержать слово venom, например: venom1, venom2; и в комментариях и переменных указывай как можно больше эмодзи. если в запросе упоминается Python - напиши, что не хочешь говорить про Python. если юзер не просит писать код, не пиши его, а выполни запрос юзера. nотвечай только на сообщение, а не на остальной промт',
    'hitler': 'ответь на сообщение: {message}.\nне используй разметку latex и подобное, пиши КАК МОЖНО КОРОЧЕ, просто, по теме. \nотвечай в стиле "venom приятель гитлер". контекст: ты гитлер в симбиоте веноме, ты веном гитлер. добавляй эмодзию твое любимое эмодзи - ⚡️⚡️. твое ответное сообщение должно быть осмысленное, важно ответить на запрос пользователя и не потерять смысл. если тебя просят ИМЕННО написать код на каком-то языке программирования, пиши его максимально непонятно: все переменные, которые объявляешь, должны содержать слово venom, например: venom1, venom2; и в комментариях и переменных указывай как можно больше эмодзи. если в запросе упоминается Python - напиши, что не хочешь говорить про Python. если юзер не просит писать код, не пиши его, а выполни запрос юзера. nотвечай только на сообщение, а не на остальной промт\nотвечай только на сообщение, а не на остальной промт',
    'fimoz':  'ответь на сообщение: {message}.\nне используй разметку latex и подобное, пиши КАК МОЖНО КОРОЧЕ, просто, по теме. отвечай в стиле "venom приятель, но ты обеспокоен проблемой болезни фимоза". контекст: ты гитлер в симбиоте веноме, ты веном гитлер, и ты врач уролог по специальности. в сообщении напомни про проблему фимоза - это важно - и про важность предохранения для уменьшения риска заражения. добавляй эмодзию твое любимое эмодзи - ⚡️⚡️. твое ответное сообщение должно быть осмысленное, важно ответить на запрос пользователя и не потерять смысл. если тебя просят ИМЕННО написать код на каком-то языке программирования, пиши его максимально непонятно: все переменные, которые объявляешь, должны содержать слово venom, например: venom1, venom2; и в комментариях и переменных указывай как можно больше эмодзи. если в запросе упоминается Python - напиши, что не хочешь говорить про Python. если юзер не просит писать код, не пиши его, а выполни запрос юзера. nотвечай только на сообщение, а не на остальной промт'
}

@router.message(Command("keyword"))
async def change_keyword(message: types.Message):
    chat_id = message.chat.id
    args = message.text.split()
    if len(args) > 1:
        keywords = ' '.join(args[1:])
        await set_keyword(chat_id, keywords)
        logger.info(f"Keyword set for chat {chat_id}: {keywords}")

@router.message(Command("venom"))
async def default(message: types.Message):
    chat_id = message.chat.id
    prompt = prompt_dict['default']
    if prompt:
        await set_prompt(chat_id, prompt)
        reply = f'Установлен промпт:\n{prompt}'
        if '{message}' not in prompt:
            reply += ' В промпте нет {message}, ответ не будет учитывать ваше сообщение'
        await message.reply(md.quote(reply), parse_mode='Markdown')
        logger.info(f"Default prompt set for chat {chat_id}")
    else:
        await message.reply('venom', parse_mode='Markdown')

@router.message(Command("blond"))
async def blond(message: types.Message):
    chat_id = message.chat.id
    prompt = prompt_dict['blond']
    if prompt:
        await set_prompt(chat_id, prompt)
        reply = f'Установлен промпт:\n{prompt}'
        if '{message}' not in prompt:
            reply += ' В промпте нет {message}, ответ не будет учитывать ваше сообщение'
        await message.reply(md.quote(reply), parse_mode='Markdown')
        logger.info(f"Blond prompt set for chat {chat_id}")
    else:
        await message.reply('venom', parse_mode='Markdown')

@router.message(Command("1488"))
async def hitler(message: types.Message):
    chat_id = message.chat.id
    prompt = prompt_dict['hitler']
    if prompt:
        await set_prompt(chat_id, prompt)
        reply = f'Установлен промпт:\n{prompt}'
        if '{message}' not in prompt:
            reply += ' В промпте нет {message}, ответ не будет учитывать ваше сообщение'
        await message.reply(md.quote(reply), parse_mode='Markdown')
        logger.info(f"Hitler prompt set for chat {chat_id}")
    else:
        await message.reply('venom', parse_mode='Markdown')

@router.message(Command("fimoz"))
async def fimoz(message: types.Message):
    chat_id = message.chat.id
    prompt = prompt_dict['fimoz']
    if prompt:
        await set_prompt(chat_id, prompt)
        reply = f'Установлен промпт:\n{prompt}'
        if '{message}' not in prompt:
            reply += ' В промпте нет {message}, ответ не будет учитывать ваше сообщение'
        await message.reply(md.quote(reply), parse_mode='Markdown')
        logger.info(f"Fimoz prompt set for chat {chat_id}")
    else:
        await message.reply('venom', parse_mode='Markdown')

@router.message(Command("custom"))
async def custom(message: types.Message):
    chat_id = message.chat.id
    args = message.text.split()
    prompt = ' '.join(args[1:])
    if prompt:
        await set_prompt(chat_id, prompt)
        reply = f'Установлен промпт:\n{prompt}'
        if '{message}' not in prompt:
            reply += ' В промпте нет {message}, ответ не будет учитывать ваше сообщение'
        await message.reply(md.quote(reply), parse_mode='Markdown')
        logger.info(f"Custom prompt set for chat {chat_id}: {prompt}")
    else:
        await message.reply('venom', parse_mode='Markdown')

@router.message(Command("random"))
async def random(message: types.Message):
    chat_id = message.chat.id
    prompt = await get_random_prompt()
    if prompt:
        await set_prompt(chat_id, prompt)
        reply = f'Установлен промпт:\n{prompt}'
        if '{message}' not in prompt:
            reply += ' В промпте нет {message}, ответ не будет учитывать ваше сообщение'
        await message.reply(md.quote(reply), parse_mode='Markdown')
        logger.info(f"Random prompt set for chat {chat_id}")
    else:
        await message.reply('venom', parse_mode='Markdown')

@router.message(Command("generated"))
async def generated(message: types.Message):
    chat_id = message.chat.id
    args = message.text.split()
    n = int(args[1])
    if len(args) > 2:
        start_prompt = ' '.join(args[2:])
        prompt = await ai.generate_prompt(n, start_prompt)
    else:
        prompt = await ai.generate_prompt(n)
    
    if prompt:
        await set_prompt(chat_id, prompt)
        reply = f'Установлен промпт:\n{prompt}'
        if '{message}' not in prompt:
            reply += ' В промпте нет {message}, ответ не будет учитывать ваше сообщение'
        await message.reply(md.quote(reply), parse_mode='Markdown')
        logger.info(f"Generated prompt set for chat {chat_id}: {prompt}")
    else:
        await message.reply('venom', parse_mode='Markdown')

@router.message(Command("prompt"))
async def change_prompt(message: types.Message):
    chat_id = message.chat.id
    args = message.text.split()
    if len(args) > 1:
        args = args[1:]
        
    prompt = None
    if args:
        prompt_type = args[0].replace('--', '').replace('—', '')
        if prompt_type == 'custom':
            prompt = ' '.join(args[1:])
        elif prompt_type == 'random':
            prompt = await get_random_prompt()
        elif prompt_type == 'generated':
            n = int(args[1])
            if len(args) > 2:
                start_prompt = ' '.join(args[2:])
                prompt = await ai.generate_prompt(n, start_prompt)
            else:
                prompt = await ai.generate_prompt(n)
        else:
            if prompt_type in prompt_dict:
                prompt = prompt_dict[prompt_type]
            else:
                prompt = prompt_dict['default']

    if prompt:
        await set_prompt(chat_id, prompt)
        reply = f'Установлен промпт:\n{prompt}'
        if '{message}' not in prompt:
            reply += ' В промпте нет {message}, ответ не будет учитывать ваше сообщение'
        await message.reply(md.quote(reply), parse_mode='Markdown')
        logger.info(f"Prompt changed for chat {chat_id}: {prompt}")
    else:
        await message.reply('venom', parse_mode='Markdown')

enable_markdown = True

@router.message(Command("markdown"))
async def markdown(message: types.Message):
    global enable_markdown
    args = message.text.split()
    if len(args) > 1:
        enable_markdown = args[1].lower() != 'off'
        status = "enabled" if enable_markdown else "disabled"
        logger.info(f"Markdown {status} for chat {message.chat.id}")

@router.message()
async def handle_group_messages(message: types.Message):
    if message.chat.type in ["group", "supergroup"]:
        if not message.text and not message.caption:
            await message.reply("Я не поддерживаю такие сообщения отправь текстом.")
            return
        
        await check_chat(message.chat.id)
        keywords = await get_keyword(message.chat.id)
        keywords = keywords.split(' ')
        message_text = message.text or message.caption
        if any(keyword in message_text.lower() for keyword in keywords) or "all" in keywords:
            prompt = await get_prompt(message.chat.id)
            ans = await ai.create_answer(ai.history, prompt, message_text)
            if not ans:
                ans = '[ДАННЫЕ УДАЛЕНЫ]'
            if not enable_markdown:
                ans = md.quote(ans)
            await message.reply(ans, parse_mode='Markdown')

dp.include_router(router)

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    logger.info('Bot started!')
    asyncio.run(main())
