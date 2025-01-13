import asyncio
from asyncio import Queue
import validators

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

    async def add_to_queue(self, client=None, message=None):
        url, chat = message.text.split("`")
        if not validators.url(url):
            self.stub.SendMessage(message_pb2.Message(text=f"URL не определен",
                                                      tg_user_id=chat,
                                                      type_mess="error_load"))
            return
        await self.queue.put((client, url, chat))
        position = self.queue.qsize()
        self.stub.SendMessage(message_pb2.Message(text=f"Позиция в очереди: {position}",
                                                  tg_user_id=chat,
                                                  type_mess="position"))
        print(f"Item added to queue")
        return position

    async def worker(self):
        print("worker start")
        while True:
            if not self.queue.empty():
                item = await self.queue.get()
                print("start work with")
                await self.work(item)
                self.queue.task_done()
            await asyncio.sleep(1)

    async def work(self, item):
        print(f"Start working on {item}")
        client, url, chat = item
        self.progress_tracker.set_cur_id(chat)
        try:
            with self.static_ydl as ydl:
                info = ydl.extract_info(url, download=False)
                file_path = ydl.prepare_filename(info)
                img_url = info.get('thumbnail')
                description = info.get('title')
                self.stub.SendMessage(message_pb2.Message(text=f"{url}`{img_url}`{description}",
                                                          tg_user_id=chat,
                                                          type_mess="url"))
                video_duration = info.get('duration', None)
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
        print(f"End working on {item}")
