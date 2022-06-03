import time
from datetime import datetime

# вывод сообщения на экран
def print_message(msg):
    now = datetime.now()
    readable_time = time.strftime("%H.%M", time.localtime())(msg['time'])
    print(f"{msg['name']} {readable_time}") # вывести на экран имя из сообщения
    print(msg["text"])

def add_message(name, text):
    new_message = {
        "name": name,
        "text": text,
        "time": time.time()
    }
    all_messages.append(new_message) #в список добавили

all_messages = [ # хранятся все сообщение чата, внутри словарь
    {
    "text": "Привет всем в чате",
    "name": "Mike",
    "time": time.time(),
    },
    {
    "text": "И тебе привет",
    "name": "Вася",
    "time": time.time(),

    },
    {
    "text": "Как тут здорово",
    "name": "Ксения",
    "time": time.time(),
    }
]

add_message("Mike", "Всё я устал, иду спать")
add_message("Вася", "Всё я устал")


for message in all_messages: # печать всех сообщений
    print_message(message)
    print("_"*28)
