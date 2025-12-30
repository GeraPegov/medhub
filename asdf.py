import time

# Измеряем СУММАРНОЕ время (как для пользователя)
a = list(range(10000))  # создаем список заранее

print("Начинаем поиск...")
real_start = time.time()  # или time.perf_counter() для точности
