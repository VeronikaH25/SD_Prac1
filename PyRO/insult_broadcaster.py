#  Generar textos de “insulto” y enviarlos a la cola de trabajo en Redis.
import redis, json, random, time, argparse, os

# Conexión a Redis
r = redis.Redis(host='localhost', port=6379, decode_responses=True)


TEXTS = [ #ejemplos de textos
    "You are so stupid",
    "What a loser you are",
    "You are an idiot",
    "Such a moron",
    "You're so dumb"
]


def push_text(r, silent=False):
    text = random.choice(TEXTS)
    try:
        r.rpush("texts", json.dumps({"text": text})) # Enviar texto a la cola "texts"
        r.incr("metrics:arrived") # Incrementar contador de textos recibidos
        if not silent:
            print(f"[Broadcaster] Enviado texto: {text}")
    except Exception as e:
        print(f"Error al enviar texto a Redis: {e}")

def main(count=None, silent=False):
    r = redis.Redis( #conectamos a Redis
        host=os.getenv("REDIS_HOST", "localhost"),
        port=6379,
        decode_responses=True
    )
    if count is not None: # modo ráfaga: enviar un número fijo de mensajes
        for _ in range(count):
            push_text(r, silent)
    else: # modo continuo: enviar mensajes cada 1 s
        print("Enviando un texto cada 1 s")
        try:
            while True:
                msgs_this_second = random.randint(500, 1000) # número aleatorio de mensajes a enviar cada segundo
                for _ in range(msgs_this_second):
                    push_text(r, silent)
                print(f"[Broadcaster] Enviats {msgs_this_second} missatges aquest segon")
                time.sleep(1)  # esperar 1 segon i repetir
        except KeyboardInterrupt:
            print("Broadcaster detenido.")

if __name__ == "__main__": # python insult_broadcaster.py (opcional)--count 10000 --silent
    ap = argparse.ArgumentParser()
    ap.add_argument("--count", type=int,
                    help="Número de mensajes en modo ráfaga")
    ap.add_argument("--silent", action="store_true",
                    help="No imprimir cada texto")
    args = ap.parse_args()
    main(args.count, args.silent)
