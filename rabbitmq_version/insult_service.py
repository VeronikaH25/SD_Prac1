import pika
import json
import threading
import time
import random
import os

INSULTS_FILE = 'insults.json'
NEW_INSULT_QUEUE = 'new_insult'
TEXT_QUEUE = 'text_queue'

texts_with_insults = [
    "You are a moron",
    "What a lovely day",
    "Such a stupid idea",
    "Hello friend",
    "You loser",
    "Have a nice time",
    "Don't be dumb"
]

class InsultService:
    def __init__(self):
        self.insults = set()
        self.load_insults()

    def load_insults(self):
        if os.path.exists(INSULTS_FILE):
            with open(INSULTS_FILE, 'r', encoding='utf-8') as f:
                try:
                    data = json.load(f)
                    self.insults = set(data.get('insults', []))
                    print(f"Loaded {len(self.insults)} insults from file.")
                except json.JSONDecodeError:
                    print("Error reading insults.json, starting with empty set.")
        else:
            self.save_insults()

    def save_insults(self):
        with open(INSULTS_FILE, 'w', encoding='utf-8') as f:
            json.dump({'insults': list(self.insults)}, f, indent=2)

    def add_insult(self, insult):
        insult = insult.strip()
        if insult and insult not in self.insults:
            self.insults.add(insult)
            self.save_insults()
            print(f"New insult added: {insult}")
            return True
        else:
            print(f"Insult already exists or empty: {insult}")
            return False

def listen_for_new_insults(insult_service):
    connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
    channel = connection.channel()
    channel.queue_declare(queue=NEW_INSULT_QUEUE)

    def callback(ch, method, properties, body):
        insult = body.decode()
        insult_service.add_insult(insult)
        ch.basic_ack(delivery_tag=method.delivery_tag)

    channel.basic_consume(queue=NEW_INSULT_QUEUE, on_message_callback=callback)
    print("Listening for new insults on RabbitMQ...")
    channel.start_consuming()

def broadcast_texts():
    connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
    channel = connection.channel()
    channel.queue_declare(queue=TEXT_QUEUE)

    correlation_id = 0
    while True:
        text = random.choice(texts_with_insults)
        message = json.dumps({"text": text, "correlation_id": str(correlation_id)})
        channel.basic_publish(exchange='', routing_key=TEXT_QUEUE, body=message)
        correlation_id += 1
        time.sleep(5)  # El sleep para no saturar

def start_service():
    insult_service = InsultService()

    # Thread para escuchar nuevos insultos
    listener_thread = threading.Thread(target=listen_for_new_insults, args=(insult_service,), daemon=True)
    listener_thread.start()

    # Thread para broadcast de textos
    broadcaster_thread = threading.Thread(target=broadcast_texts, daemon=True)
    broadcaster_thread.start()

    connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
    channel = connection.channel()

    # Consola para añadir insultos manualmente
    while True:
        insult = input("Enter insult to add (or 'exit'): ").strip()
        if insult.lower() == 'exit':
            print("Exiting service.")
            break
        if insult:
            channel.basic_publish(exchange='', routing_key=NEW_INSULT_QUEUE, body=insult)

if __name__ == '__main__':
    start_service()
