from pyrogram import Client, filters
import yt_dlp

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
ydl_opts['progress_hooks'].append(progress_tracker.progress_hook)
static_ydl = yt_dlp.YoutubeDL(ydl_opts)

@app.on_message(filters.chat(bot_name))
async def reply_with_video(client, message):
    url, chat = message.text.split("`")
    sent_message = await client.send_message(chat_id=bot_name, text=f'Видео загружается{static_reg}{chat}')
    progress_tracker.set_cur_id(chat)
    progress_tracker.set_last_message_id(sent_message.id)
    try:
        with static_ydl as ydl:
            info_dict = ydl.extract_info(url, download=True)
            file_path = ydl.prepare_filename(info_dict)
    except:
        await client.send_message(chat_id=bot_name, text=f'Ошибка загрузки{static_reg}{chat}')
        return
    try:
        with open(file_path, "rb") as _:
            pass
    except FileNotFoundError:
        await client.send_message(chat_id=bot_name, text=f'Видео не найдено. Проверьте путь!{static_reg}{chat}')
        return
    await client.send_message(chat_id=bot_name, text=f'Отправляю видео{static_reg}{chat}')
    await client.send_video(chat_id=bot_name, video=file_path, caption=f"Вот ваше видео!{static_reg}{chat}")


if __name__ == "__main__":
    print("Userbot запущен. Нажмите Ctrl+C для остановки.")
    app.run()
