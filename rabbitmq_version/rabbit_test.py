import pika
import json
import threading
import time
import subprocess

NEW_INSULT_QUEUE = 'new_insult'
TEXT_QUEUE = 'text_queue'
FILTERED_QUEUE = 'filtered_texts'

texts_to_filter = [
    "You are a moron",
    "What a lovely day",
    "Such a stupid idea",
    "Hello friend",
    "You loser",
    "Have a nice time",
    "Don't be dumb"
]

NUM_REQUESTS = 500
FILTER_WORKER_SCRIPT = "insult_filter.py"
SERVICE_SCRIPT = "insult_service.py"

# ---------- Test InsultService -------------
def test_insult_service(num_requests=NUM_REQUESTS, num_publishers=1):
    connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
    channel = connection.channel()
    channel.queue_declare(queue=NEW_INSULT_QUEUE)

    # Para evitar que los threads usen el mismo canal (no es thread-safe), cada thread abre su canal
    def publisher(start_index, count):
        # Abrir conexión y canal dentro del thread
        conn = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
        ch = conn.channel()
        ch.queue_declare(queue=NEW_INSULT_QUEUE)
        for i in range(start_index, start_index + count):
            insult = f"insult_{i}"
            ch.basic_publish(exchange='', routing_key=NEW_INSULT_QUEUE, body=insult)
        conn.close()

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

    duration = end_time - start_time
    print(f"[InsultService] Publishers: {num_publishers} Sent {num_requests} insults in {duration:.2f}s")
    return duration

# ----------- Test InsultFilter -------------

def run_filter_workers(num_workers):
    procs = []
    for _ in range(num_workers):
        p = subprocess.Popen(['python', FILTER_WORKER_SCRIPT], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        procs.append(p)
    return procs

def stop_filter_workers(procs):
    for p in procs:
        p.terminate()
    for p in procs:
        try:
            p.wait(timeout=5)
        except subprocess.TimeoutExpired:
            p.kill()

def listener(results, stop_event, expected):
    connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
    channel = connection.channel()
    channel.queue_declare(queue=FILTERED_QUEUE)

    def callback(ch, method, properties, body):
        data = json.loads(body.decode())
        results.append(data)
        if len(results) >= expected:
            stop_event.set()
        ch.basic_ack(delivery_tag=method.delivery_tag)

    channel.basic_consume(queue=FILTERED_QUEUE, on_message_callback=callback, auto_ack=False)
    print("[Listener] Listening for filtered results...")
    while not stop_event.is_set():
        connection.process_data_events(time_limit=1)
    connection.close()

def test_insult_filter(num_requests=NUM_REQUESTS, num_workers=1):
    # Lanzar workers
    procs = run_filter_workers(num_workers)
    time.sleep(2)  # esperar que arranquen

    connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
    channel = connection.channel()
    channel.queue_declare(queue=TEXT_QUEUE)

    results = []
    stop_event = threading.Event()
    listener_thread = threading.Thread(target=listener, args=(results, stop_event, num_requests), daemon=True)
    listener_thread.start()

    start_time = time.time()
    for i in range(num_requests):
        text = texts_to_filter[i % len(texts_to_filter)]
        msg = {"text": text, "correlation_id": str(i)}
        channel.basic_publish(exchange='', routing_key=TEXT_QUEUE, body=json.dumps(msg).encode())
    stop_event.wait(timeout=60)
    end_time = time.time()

    # Parar workers
    stop_filter_workers(procs)

    duration = end_time - start_time
    print(f"[InsultFilter] Workers: {num_workers} Sent and received {len(results)}/{num_requests} filtered texts in {duration:.2f}s")

    return duration

def main():
    print("=== RABBITMQ InsultService & InsultFilter Performance Test ===")
    print(f"Number of requests per test: {NUM_REQUESTS}\n")

    service_times = []
    filter_times = []

    print("Testing InsultService with 1 publisher...")
    t = test_insult_service(num_requests=NUM_REQUESTS, num_publishers=1)
    service_times.append(t)

    print("Testing InsultFilter with 1 worker...")
    t = test_insult_filter(num_requests=NUM_REQUESTS, num_workers=1)
    filter_times.append(t)

    for nodes in [2, 3]:
        print(f"\nTesting InsultService with {nodes} publishers...")
        t = test_insult_service(num_requests=NUM_REQUESTS, num_publishers=nodes)
        service_times.append(t)

        print(f"Testing InsultFilter with {nodes} workers...")
        t = test_insult_filter(num_requests=NUM_REQUESTS, num_workers=nodes)
        filter_times.append(t)

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