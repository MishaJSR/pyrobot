import asyncio
import os
from asyncio import Queue

import yt_dlp.utils

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
        if await self.check_video(chat=chat, url=url):
            position = self.queue.qsize() + 1
            self.stub.SendMessage(message_pb2.Message(text=f"Позиция в очереди: {position}",
                                                      tg_user_id=chat,
                                                      type_mess="position"))
            await self.queue.put((client, url, chat))
            print(f"Item added to queue")

    async def worker(self):
        print("worker start")
        while True:
            if not self.queue.empty():
                item = self.queue._queue[0]
                print("start work with")
                print(self.queue.qsize())
                await self.work(item)
                await self.queue.get()
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
                video_duration = info.get('duration', None)
                img_url = info.get('thumbnail')
                description = info.get('title')
                self.stub.SendMessage(message_pb2.Message(text=f"{url}`{img_url}`{description}",
                                                          tg_user_id=chat,
                                                          type_mess="url"))
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
        os.remove(file_path)
        print(f"End working on {item}")

    async def check_video(self, chat, url):
        try:
            with self.static_ydl as ydl:
                info = ydl.extract_info(url, download=False)
                video_duration = info.get('duration', None)
        except yt_dlp.utils.DownloadError:
            self.stub.SendMessage(message_pb2.Message(text=f"Качество видео слишком низкое для загрузки 720р\n",
                                                              tg_user_id=chat,
                                                              type_mess="repeat"))
            return
        if video_duration > 3599:
            self.stub.SendMessage(message_pb2.Message(text=f"Видео больше часа в данный момент не загружаем\n",
                                                              tg_user_id=chat,
                                                              type_mess="repeat"))
            return
        # for item in self.queue._queue:
        #     if item[2] == chat:
        #         self.stub.SendMessage(message_pb2.Message(text=f"Одно из Ваших видео уже находится в очереди\n"
        #                                                        f"Пожалуйста дождитесь загрузки",
        #                                                   tg_user_id=chat,
        #                                                   type_mess="repeat"))
        #         return
        return True
