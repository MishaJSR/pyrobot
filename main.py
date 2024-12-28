from pyrogram import Client, filters
import yt_dlp
from pyrogram.filters import video

from base_settings import base_settings
from grpc_utils.proto import message_pb2
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

@app.on_message(filters.chat(bot_name))
async def reply_with_video(client, message):
    url, chat = message.text.split("`")
    stub.SendMessage(message_pb2.Message(text=f"{url}",
                                         tg_user_id=chat,
                                         type_mess="url"))
    progress_tracker.set_cur_id(chat)
    try:
        with static_ydl as ydl:
            time_dict = ydl.extract_info(url, download=False)
            file_path = ydl.prepare_filename(time_dict)
            video_duration = time_dict.get('duration', None)
            info_dict = ydl.extract_info(url, download=True)
    except:
        stub.SendMessage(message_pb2.Message(text=f"Ошибка загрузки",
                                             tg_user_id=chat,
                                             type_mess="error_load"))
        return
    try:
        with open(file_path, "rb") as _:
            pass
    except FileNotFoundError:
        stub.SendMessage(message_pb2.Message(text=f"Ошибка на стороне сервера",
                                             tg_user_id=chat,
                                             type_mess="error_server"))
        return
    stub.SendMessage(message_pb2.Message(text=f"{video_duration}",
                                         tg_user_id=chat,
                                         type_mess="send_video"))
    await client.send_video(chat_id=bot_name, video=file_path, caption=f"Вот ваше видео!{static_reg}{chat}")


if __name__ == "__main__":
    print("Userbot запущен. Нажмите Ctrl+C для остановки.")
    app.run()
