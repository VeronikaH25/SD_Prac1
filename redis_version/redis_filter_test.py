# test_insult_filter_stress.py
import time
import redis
import multiprocessing
import json
import subprocess

# Cliente Redis
r = redis.Redis(host='localhost', port=6379, decode_responses=True)
INSULTS_KEY = "insult:list"

# Precarga de palabras ofensivas en Redis, para que el filtro pueda censurarlas luego
def preload_insults():
    insults = ["stupid", "idiot", "dumb", "loser", "moron"]
    for insult in insults:
        r.sadd(INSULTS_KEY, insult)

def send_text_and_get_response(text, correlation_id):
    pubsub = r.pubsub()
    reply_channel = f"reply_{correlation_id}"
    pubsub.subscribe(reply_channel)

    r.publish('texts', json.dumps({
        "text": text,
        "reply_to": reply_channel,
        "correlation_id": correlation_id
    }))

    for message in pubsub.listen():
        if message['type'] == 'message':
            data = json.loads(message['data'])
            if data.get("correlation_id") == correlation_id:
                pubsub.unsubscribe(reply_channel)
                return data.get("filtered_text")
    return None

def filter_worker(num_requests, base_id):
    sample_text = "You are a stupid idiot and a loser."
    for i in range(num_requests):
        send_text_and_get_response(sample_text, f"{base_id}_{i}")

# Lanza una instancia de insult_filter.py
def start_filter_process():
    return subprocess.Popen(
        ["python", "insult_filter.py"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )

# Lanza N procesos de insult_filter.py
def launch_filter_nodes(num_nodes):
    procs = []
    for _ in range(num_nodes):
        proc = start_filter_process()
        procs.append(proc)
    time.sleep(1.5)  # Esperar a que arranquen
    return procs

# Termina todos los insult_filter.py lanzados
def terminate_filter_nodes(procs):
    for proc in procs:
        proc.terminate()
    for proc in procs:
        proc.wait()

# Test con 1 nodo (1 insult_filter.py)
def redis_filter_test_single_node(num_requests):
    procs = launch_filter_nodes(1)
    start_time = time.time()
    filter_worker(num_requests, "single")
    end_time = time.time()
    terminate_filter_nodes(procs)
    total_time = end_time - start_time
    print(f"[Redis Filter Single Node] Procesados {num_requests} textos en {total_time:.4f} segundos.")
    return total_time

# Test con múltiples nodos (N insult_filter.py)
def redis_filter_test_multiple_nodes(num_requests, num_nodes):
    procs = launch_filter_nodes(num_nodes)
    processes = []
    requests_per_node = num_requests // num_nodes

    start_time = time.time()
    for i in range(num_nodes):
        p = multiprocessing.Process(target=filter_worker, args=(requests_per_node, f"multi{i}"))
        processes.append(p)
        p.start()

    for p in processes:
        p.join()

    end_time = time.time()
    terminate_filter_nodes(procs)
    total_time = end_time - start_time
    print(f"[Redis Filter Multiple Nodes] Procesados {num_requests} textos con {num_nodes} nodos en {total_time:.4f} segundos.")
    return total_time

# Main test runner
if __name__ == "__main__":
    preload_insults()
    num_requests = 10000

    single_time = redis_filter_test_single_node(num_requests)

    num_nodes = 3
    multi_time = redis_filter_test_multiple_nodes(num_requests, num_nodes)

    speedup = single_time / multi_time if multi_time > 0 else float('inf')
    print(f"Speedup: {speedup:.2f}")
