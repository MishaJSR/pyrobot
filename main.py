import asyncio
import threading
import time
from concurrent.futures.thread import ThreadPoolExecutor

from pyrogram import Client, filters, idle
import yt_dlp

from AsyncQueue import AsyncQueue
from base_settings import base_settings
from utils import ProgressTracker

API_ID = base_settings.get_id()
API_HASH = base_settings.get_hash()
bot_name = base_settings.get_bot_name()
pwd = base_settings.get_pwd()
static_status = base_settings.get_status()
static_reg = base_settings.get_reg()

app = Client("teletoon_userbot", api_id=API_ID, api_hash=API_HASH)

ydl_opts = {
    'outtmpl': f'{pwd}/media/%(title)s.%(ext)s',
    'cookiesfrombrowser': ("chrome",),
    'format' : 'bestvideo[height=720][ext=mp4]+bestaudio',
    'merge_output_format' : 'mp4',
    'progress_hooks': [],
    'quiet': True,
}
progress_tracker = ProgressTracker(client=app, bot_name=bot_name, static_key=static_status+static_reg)
stub = progress_tracker.stub
ydl_opts['progress_hooks'].append(progress_tracker.progress_hook)
static_ydl = yt_dlp.YoutubeDL(ydl_opts)
queue = AsyncQueue(stub=stub, static_ydl=static_ydl, progress_tracker=progress_tracker)

def dome():
    loop = asyncio.new_event_loop()
    loop.run_until_complete(my_async_function())

async def my_async_function():
    await queue.worker()


@app.on_message(filters.chat(bot_name))
async def reply_with_video(client, message):
    print("get message")
    if not queue.is_start:
        thread = threading.Thread(target=dome)
        thread.start()
        queue.is_start = True
    await queue.add_to_queue(client, message)

app.run()


