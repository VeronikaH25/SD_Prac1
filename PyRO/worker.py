import redis
import Pyro4
import json
import time
import os

R = redis.Redis(host='localhost', port=6379, decode_responses=True)

FILTER_NAME = os.getenv("FILTER_NAME", "insult_filter")

def main():
    try:
        filter_server = Pyro4.Proxy(f"PYRONAME:{FILTER_NAME}")
    except Exception as e:
        print(f"[Worker] Error conectando a Pyro4: {e}")
        return

    print("[Worker] Esperando textos a la cola Redis...")

    while True:
        # Espera bloqueante hasta que llega mensaje a la cola "texts"
        _, raw = R.blpop("texts")

        start = time.time()  

        msg = json.loads(raw)
        text = msg.get("text", "")

        # Filtra el texto
        filtered = filter_server.submit_text(text)

        # Pone el texto filtrado a la cola "filtered_texts"
        R.rpush("filtered_texts", filtered)

        end = time.time()  # tiempo final de processamiento
        processing_time = end - start

        # Guarda el tiempo
        R.rpush("metrics:times", processing_time)
        # Mantiene los últimos 100 tiempos para estadísticas
        R.ltrim("metrics:times", -100, -1)

        # print(f"[Worker] Processat: {filtered}")

if __name__ == "__main__":
    main()
