import asyncio
from aiogram import Bot, Dispatcher, Router, types
import ai

import os
from dotenv import load_dotenv

load_dotenv()



# Initialize bot and dispatcher
TOKEN = os.getenv("BOT_TOKEN")
bot = Bot(token=TOKEN)
dp = Dispatcher()

# Create a router for handling messages
router = Router(name=__name__)

@router.message()
async def handle_group_messages(message: types.Message):
    if message.chat.type in ["group", "supergroup"]:
        if 'venom' in message.text.lower() or 'веном' in message.text.lower():
            print(message.text)
            ans =  await ai.create_answer(ai.history, message.text)
            await message.reply(ans, parse_mode='Markdown')
# Add the router to the dispatcher
dp.include_router(router)

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    print('bot started!')
    asyncio.run(main())

