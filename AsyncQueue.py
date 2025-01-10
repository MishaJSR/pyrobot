import asyncio
from asyncio import Queue
from concurrent.futures import ThreadPoolExecutor

from base_settings import base_settings
from grpc_utils.proto import message_pb2


class AsyncQueue:
    def __init__(self, stub=None, progress_tracker=None, static_ydl=None):
        self.queue = Queue()
        self.stub = stub
        self.progress_tracker = progress_tracker
        self.static_ydl = static_ydl
        self.static_status = base_settings.get_status()
        self.static_reg = base_settings.get_reg()
        self.bot_name = base_settings.get_bot_name()
        self.is_start = False

    async def add_to_queue(self, client=None, message=None):
        await self.queue.put((client, message))
        print(f"Item {(client, message)} added to queue")

    async def worker(self):
        print("worker start")
        while True:
            item = await self.queue.get()
            if item is None:  # Если получен сигнал для остановки, выходим из цикла
                break
            await self.work(item)
            self.queue.task_done()
        print("worker stop")

    async def work(self, item):
        client, message = item
        url, chat = message.text.split("`")
        self.stub.SendMessage(message_pb2.Message(text=f"{url}",
                                                  tg_user_id=chat,
                                                  type_mess="url"))
        self.progress_tracker.set_cur_id(chat)
        try:
            with self.static_ydl as ydl:
                time_dict = ydl.extract_info(url, download=False)
                file_path = ydl.prepare_filename(time_dict)
                video_duration = time_dict.get('duration', None)
                ydl.download(url)
        except:
            self.stub.SendMessage(message_pb2.Message(text=f"Ошибка загрузки",
                                                      tg_user_id=chat,
                                                      type_mess="error_load"))
            return
        try:
            with open(file_path, "rb") as _:
                pass
        except FileNotFoundError:
            self.stub.SendMessage(message_pb2.Message(text=f"Ошибка на стороне сервера",
                                                      tg_user_id=chat,
                                                      type_mess="error_server"))
            return
        self.stub.SendMessage(message_pb2.Message(text=f"{video_duration}",
                                                  tg_user_id=chat,
                                                  type_mess="send_video"))
        await client.send_video(chat_id=self.bot_name, video=file_path,
                                caption=f"Вот ваше видео!{self.static_reg}{chat}")
        self.stub.SendMessage(message_pb2.Message(text=f"{video_duration}",
                                                  tg_user_id=chat,
                                                  type_mess="video_delivered"))
        print(f"Start working on {item}")
        await asyncio.sleep(5)
        print(f"End working on {item}")
