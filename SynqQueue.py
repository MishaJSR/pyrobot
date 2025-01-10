import asyncio
from asyncio import Queue


class AsyncQueue:
    def __init__(self):
        self.queue = Queue()

    async def add_to_queue(self, item):
        await self.queue.put(item)
        print(f"Item {item} added to queue")

    async def worker(self):
        while True:
            item = await self.queue.get()
            await self.work(item)
            self.queue.task_done()

    @staticmethod
    async def work(item):
        print(f"Start working on {item}")
        await asyncio.sleep(5)  # Симуляция длительной работы
        print(f"End working on {item}")


async def main():
    async_queue = AsyncQueue()

    # Запуск рабочего процесса
    worker_task = asyncio.create_task(async_queue.worker())

    # Добавление элементов в очередь
    await async_queue.add_to_queue(("Task 1", "sdsada"))
    await async_queue.add_to_queue("Task 2")
    await async_queue.add_to_queue("Task 3")

    # Ожидание обработки всех задач
    await async_queue.queue.join()

    # Завершение рабочего процесса (опционально)
    worker_task.cancel()


if __name__ == "__main__":
    asyncio.run(main())
