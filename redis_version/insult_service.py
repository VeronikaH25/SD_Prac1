import redis
import json
import threading
import time
import random
import os

INSULTS_KEY = "insult:list"
TEXT_QUEUE = "text:queue"

# Textos con insultos incluidos para broadcast
texts_with_insults = [
    "You are a moron",
    "What a lovely day",
    "Such a stupid idea",
    "Hello friend",
    "You loser",
    "Have a nice time",
    "Don't be dumb"
]

def preload_insults(force_reload=False):
    r = redis.Redis(host='localhost', port=6379, decode_responses=True)
    if force_reload or r.scard(INSULTS_KEY) == 0:
        if force_reload:
            r.delete(INSULTS_KEY)
            print("Deleted existing insults, reloading from JSON...")

        json_path = os.path.join(os.path.dirname(__file__), 'insults.json')
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        insults = data.get("insults", [])
        for insult in insults:
            r.sadd(INSULTS_KEY, insult)
        print(f"Loaded {len(insults)} insults into Redis")
    else:
        print("Insults already present in Redis, skipping preload.")

def add_insults_listener():
    r = redis.Redis(host='localhost', port=6379, decode_responses=True)
    pubsub = r.pubsub()
    pubsub.subscribe('new_insult')

    print("Listening for new insults on Redis...")

    for message in pubsub.listen():
        if message['type'] != 'message':
            continue
        insult = message['data'].strip()
        if insult:
            added = r.sadd(INSULTS_KEY, insult)
            if added:
                print(f"New insult added to Redis: {insult}")
            else:
                print(f"Insult already in Redis: {insult}")

def broadcast_texts():
    r = redis.Redis(host='localhost', port=6379, decode_responses=True)
    correlation_id = 0
    while True:
        text = random.choice(texts_with_insults)
        message = {"text": text, "correlation_id": str(correlation_id)}
        r.lpush(TEXT_QUEUE, json.dumps(message))  # LPUSH a la cola de trabajo
        # Silenciar el broadcast para no imprimir
        correlation_id += 1
        time.sleep(5)

def start_service():
    preload_insults(force_reload=True)

    # Thread para escuchar nuevos insultos
    listener_thread = threading.Thread(target=add_insults_listener, daemon=True)
    listener_thread.start()

    # Thread para broadcast de textos
    broadcaster_thread = threading.Thread(target=broadcast_texts, daemon=True)
    broadcaster_thread.start()

    r = redis.Redis(host='localhost', port=6379, decode_responses=True)

    # Consola para añadir insultos manualmente
    while True:
        insult = input("Enter insult to add (or 'exit'): ").strip()
        if insult.lower() == 'exit':
            print("Exiting service.")
            break
        if insult:
            r.publish('new_insult', insult)

if __name__ == "__main__":
    start_service()
