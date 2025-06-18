# insult_broadcaster.py
import pika
import json
import random
import time
import argparse

texts = [
    "You are so stupid",
    "What a loser you are",
    "You are an idiot",
    "Such a moron",
    "You're so dumb"
]

def send_message(channel, silent=False):
    text = random.choice(texts)
    if not silent:
        print(f"Broadcasting text: {text}")
    channel.basic_publish(
        exchange='',
        routing_key='texts',
        body=json.dumps({"text": text})
    )

def start_broadcast(count=None, silent=False):
    connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
    channel = connection.channel()
    channel.queue_declare(queue='texts')

    if count is not None:
        for _ in range(count):
            send_message(channel, silent)
            time.sleep(0.001)  # Pequeño delay para evitar congestión
    else:
        print("Modo periódico activado: enviando un mensaje cada 5 segundos (Ctrl+C para parar).")
        try:
            while True:
                send_message(channel, silent)
                time.sleep(5)
        except KeyboardInterrupt:
            print("Broadcast detenido por el usuario.")

    connection.close()

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--count', type=int, help="Número de mensajes a enviar (si no se pasa, se activa modo periódico)")
    parser.add_argument('--silent', action='store_true', help="No imprimir los mensajes enviados")
    args = parser.parse_args()

    start_broadcast(count=args.count, silent=args.silent)