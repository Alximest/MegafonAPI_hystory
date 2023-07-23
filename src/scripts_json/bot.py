import asyncio, logging
from aiogram import Bot, Dispatcher, types, executor
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from dotenv import load_dotenv, find_dotenv
from os import getenv

load_dotenv(find_dotenv())

# Create an instance of the bot
API_TOKEN = getenv("API_TOKEN")
CHAT_ID = getenv("YOUR_CHAT_ID")
bot = Bot(token=API_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)

# Variable to store the latest data from the script
latest_data = ""


async def send_data_to_chat(data: str, audio_file_path: str = None):
    if audio_file_path:
        # If there's an audio file, send it with the text message
        audio_file = types.InputFile(audio_file_path)
        await bot.send_audio(chat_id=CHAT_ID, audio=audio_file, caption=data)
    else:
        # If there's no audio file, send only the text message
        await bot.send_message(chat_id=CHAT_ID, text=data)


def update_latest_data(new_data: str, audio_file_path: str = None):
    global latest_data
    latest_data = new_data
    # Send the latest data with the audio file (if available) and the text message
    asyncio.create_task(send_data_to_chat(new_data, audio_file_path))
