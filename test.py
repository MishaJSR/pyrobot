import asyncio
from asyncio import Queue

class AsyncQueue:
    def __init__(self):
        self.queue = Queue()
        self.processing = False

    async def add_to_queue(self, item):
        await self.queue.put(item)
        # if not self.processing:
        #     self.processing = True
        #     await self.process_queue()

    async def process_queue(self):
        while self.queue:
            item = await self.queue.get()
            await self.work(item)

        self.processing = False

    @staticmethod
    async def work(item):
        print("start working")
        print(item)
        print("end working")
        await asyncio.sleep(5)

# Usage
async def main():
    queue = AsyncQueue()
    task = asyncio.create_task(queue.process_queue())

    await queue.add_to_queue("sds")
    print("add 1")
    await queue.add_to_queue("sdfsdf")
    print("add 2")
    await queue.add_to_queue("sdfsfdds")
    print("add 3")
    await queue.add_to_queue("sdfsdf")
    print("add 4")
    await task

# Run the main function
asyncio.run(main())
