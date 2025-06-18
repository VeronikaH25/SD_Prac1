# insult_broadcaster.py
import redis
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

def send_message(r, silent=False):
    text = random.choice(texts)
    if not silent:
        print(f"Broadcasting text: {text}")
    r.publish('texts', json.dumps({"text": text}))

def start_broadcast(count=None, silent=False):
    r = redis.Redis(host='localhost', port=6379, decode_responses=True)

    if count is not None:
        for _ in range(count):
            send_message(r, silent)
            # Puedes ajustar el delay si ves congestión en tests
            time.sleep(0.001)
    else:
        print("Modo periódico activado: enviando un mensaje cada 5 segundos (Ctrl+C para parar).")
        try:
            while True:
                send_message(r, silent)
                time.sleep(5)
        except KeyboardInterrupt:
            print("Broadcast detenido por el usuario.")

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--count', type=int, help="Número de mensajes a enviar (modo test)")
    parser.add_argument('--silent', action='store_true', help="No imprimir los mensajes enviados")
    args = parser.parse_args()

    start_broadcast(count=args.count, silent=args.silent)
