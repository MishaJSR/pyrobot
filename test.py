import asyncio


async def async_function(w):
    # Время работы функции (w / 3 секунд)
    duration = w / 3

    # Количество значений, которые нужно вывести
    num_values = 10

    # Интервал между выводами значений
    interval = duration / num_values

    # Асинхронный цикл для вывода значений
    for i in range(num_values):
        # Ждем между выводами значений
        await asyncio.sleep(interval)

        # Рассчитываем процент времени выполнения
        progress = (i + 1) * (100 / num_values)

        # Выводим процент времени
        print(f"Progress {i + 1}: {progress:.2f}%")


# Пример вызова функции
w = 45  # Параметр, определяющий время работы функции
asyncio.run(async_function(w))
