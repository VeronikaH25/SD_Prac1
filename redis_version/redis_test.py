import redis
import json
import threading
import time
import subprocess
import os
import signal

INSULTS_CHANNEL = 'new_insult'
INSULTS_KEY = 'insult:list'
TEXT_QUEUE = "text:queue"
RESULT_CHANNEL = "filtered:results"

texts_to_filter = [
    "You are a moron",
    "What a lovely day",
    "Such a stupid idea",
    "Hello friend",
    "You loser",
    "Have a nice time",
    "Don't be dumb"
]

NUM_REQUESTS = 500  # ajusta para test más largo o corto
WORKER_SCRIPT = "insult_filter.py"  # ruta al worker que tienes


# ---------- Test InsultService -------------

def test_insult_service(num_requests=NUM_REQUESTS, num_publishers=1):
    """
    Simula num_publishers enviando insultos simultáneamente.
    """
    r = redis.Redis(host='localhost', port=6379, decode_responses=True)

    def publisher(start_index, count):
        for i in range(start_index, start_index + count):
            insult = f"insult_{i}"
            r.publish(INSULTS_CHANNEL, insult)

    count_per_publisher = num_requests // num_publishers

    start_time = time.time()
    threads = []
    for i in range(num_publishers):
        t = threading.Thread(target=publisher, args=(i * count_per_publisher, count_per_publisher))
        t.start()
        threads.append(t)
    for t in threads:
        t.join()
    end_time = time.time()

    # Esperamos que se procesen (listener de insultos)
    time.sleep(2)
    insults = r.smembers(INSULTS_KEY)

    duration = end_time - start_time
    print(f"[InsultService] Publishers: {num_publishers} Sent {num_requests} insults in {duration:.2f}s")
    print(f"[InsultService] Insults stored: {len(insults)} (expected {num_requests})")

    return duration


# ----------- Test InsultFilter -------------

def run_worker_processes(num_workers):
    procs = []
    for _ in range(num_workers):
        p = subprocess.Popen(['py', WORKER_SCRIPT], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        procs.append(p)
    return procs

def stop_worker_processes(procs):
    for p in procs:
        p.terminate()
    for p in procs:
        try:
            p.wait(timeout=5)
        except subprocess.TimeoutExpired:
            p.kill()

def listener(results, stop_event, expected):
    r = redis.Redis(host='localhost', port=6379, decode_responses=True)
    pubsub = r.pubsub()
    pubsub.subscribe(RESULT_CHANNEL)
    count = 0

    for message in pubsub.listen():
        if stop_event.is_set():
            break
        if message['type'] == 'message':
            data = json.loads(message['data'])
            results.append(data)
            count += 1
            if count >= expected:
                stop_event.set()

def test_insult_filter(num_requests=NUM_REQUESTS, num_workers=1):
    r = redis.Redis(host='localhost', port=6379, decode_responses=True)

    # Lanzar workers
    procs = run_worker_processes(num_workers)
    time.sleep(2)  # dar tiempo a que arranquen

    results = []
    stop_event = threading.Event()
    listener_thread = threading.Thread(target=listener, args=(results, stop_event, num_requests), daemon=True)
    listener_thread.start()

    start_time = time.time()
    for i in range(num_requests):
        text = texts_to_filter[i % len(texts_to_filter)]
        msg = {"text": text, "correlation_id": str(i)}
        r.lpush(TEXT_QUEUE, json.dumps(msg))
    stop_event.wait(timeout=60)
    end_time = time.time()

    # Parar workers
    stop_worker_processes(procs)

    duration = end_time - start_time
    print(f"[InsultFilter] Workers: {num_workers} Sent and received {len(results)}/{num_requests} filtered texts in {duration:.2f}s")

    return duration


def main():
    print("=== REDIS InsultService & InsultFilter Performance Test ===")
    print(f"Number of requests per test: {NUM_REQUESTS}\n")

    # Test single node (1 publisher / 1 worker)
    service_times = []
    filter_times = []

    print("Testing InsultService with 1 publisher...")
    t = test_insult_service(num_requests=NUM_REQUESTS, num_publishers=1)
    service_times.append(t)

    print("Testing InsultFilter with 1 worker...")
    t = test_insult_filter(num_requests=NUM_REQUESTS, num_workers=1)
    filter_times.append(t)

    # Test multi-node 2, 3
    for nodes in [2, 3]:
        print(f"\nTesting InsultService with {nodes} publishers...")
        t = test_insult_service(num_requests=NUM_REQUESTS, num_publishers=nodes)
        service_times.append(t)

        print(f"Testing InsultFilter with {nodes} workers...")
        t = test_insult_filter(num_requests=NUM_REQUESTS, num_workers=nodes)
        filter_times.append(t)

    # Mostrar speedups
    print("\n=== Speedup Analysis ===")
    print("InsultService times (seconds):", service_times)
    print("InsultFilter times (seconds):", filter_times)

    base_service = service_times[0]
    base_filter = filter_times[0]

    for i, n in enumerate([1, 2, 3]):
        speedup_service = base_service / service_times[i]
        speedup_filter = base_filter / filter_times[i]
        print(f"Nodes: {n} | InsultService Speedup: {speedup_service:.2f} | InsultFilter Speedup: {speedup_filter:.2f}")

if __name__ == "__main__":
    main()