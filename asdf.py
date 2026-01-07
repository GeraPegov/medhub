def decorator(func):
    def wrapper(*args, **kwargs):
        return func(3)
    return wrapper

@decorator
def get(num):
    suma = num + 2
    return suma


print(get)