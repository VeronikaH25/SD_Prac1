import xmlrpc.client, time, multiprocessing, sys

def send_requests(host, num_requests):
    proxy = xmlrpc.client.ServerProxy(f"http://{host}")
    start = time.time()
    for i in range(num_requests):
        proxy.add_insult(f"xml_ins_{i}_{time.time()}")
        if (i + 1) % 10 == 0:
            print(f"[{host}] Sent {i+1} at {time.time() - start:.2f}s")

def generate_hosts(base_port, count):
    return [f"localhost:{base_port + i}" for i in range(count)]

def run_parallel_test(hosts, total_requests):
    requests_per_host = total_requests // len(hosts)
    processes = []

    start = time.time()
    for host in hosts:
        p = multiprocessing.Process(target=send_requests, args=(host, requests_per_host))
        p.start()
        processes.append(p)

    for p in processes:
        p.join()

    elapsed = time.time() - start
    print(f"\n[PARALLEL] {total_requests} requests in {elapsed:.2f}s → {total_requests/elapsed:.1f} req/s")

if __name__ == "__main__":
    num_nodes = int(sys.argv[1]) if len(sys.argv) > 1 else 3
    num_requests = int(sys.argv[2]) if len(sys.argv) > 2 else 100

    hosts = generate_hosts(8000, num_nodes)
    print(f"[INFO] Running test with hosts: {hosts}")
    run_parallel_test(hosts, num_requests)
