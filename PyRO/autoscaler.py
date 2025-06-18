import redis
import subprocess
import time

MAX_WORKERS = 10
MIN_WORKERS = 1
UMBRAL_SUBIDA = 2
UMBRAL_BAJADA = 0
INTERVAL_ESCALAT = 3
INTERVAL_MONITOREIG = 1

workers = []

r = redis.Redis(host='localhost', port=6379, decode_responses=True)

def contar_mensajes():
    try:
        return r.llen("texts")  #Cola Redis "texts"
    except Exception as e:
        print(f"Error al consultar la cola Redis: {e}")
        return 0

def lanzar_worker():
    proceso = subprocess.Popen(["python", "worker.py"]) 
    workers.append(proceso)
    r.set("workers:active", len(workers)) #para el data_capturer.py
    print(f"Worker lanzado")

def terminar_worker():
    if workers:
        proceso = workers.pop()
        proceso.terminate()
        r.set("workers:active", len(workers))
        print(f"Worker terminado")

def main():
    # Lanzamos los workers iniciales
    for _ in range(MIN_WORKERS):
        lanzar_worker()

    segundos = 0
    try:
        while True:
            mensajes = contar_mensajes()
            print(f"Mensajes en cola: {mensajes} | Workers activos: {len(workers)}")

            if segundos % INTERVAL_ESCALAT == 0:
                if mensajes > UMBRAL_SUBIDA and len(workers) < MAX_WORKERS:
                    lanzar_worker()
                elif mensajes <= UMBRAL_BAJADA and len(workers) > MIN_WORKERS:
                    terminar_worker()

            time.sleep(INTERVAL_MONITOREIG)
            segundos += INTERVAL_MONITOREIG

    except KeyboardInterrupt:
        print("\nFinalizando todos los workers...")
        while workers:
            terminar_worker()

if __name__ == "__main__":
    main()
