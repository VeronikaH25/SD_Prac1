import xmlrpc.client, time, multiprocessing, sys

def send_requests(host, num_requests, result_dict, idx): #peticiones al InsultFilter
    proxy = xmlrpc.client.ServerProxy(f"http://{host}")
    start = time.time() #tiempo de inicio
    for i in range(num_requests):
        proxy.submit_text("you are a stupid idiot") #envia el mismo texto al filtro
        if (i + 1) % 10 == 0: #cada 10 peticiones printamos el tiempo transcurrido
            print(f"[{host}] Sent {i+1} at {time.time() - start:.2f}s")
    elapsed = time.time() - start #tiempo total
    result_dict[idx] = (host, num_requests, elapsed)

def generate_hosts(base_port, count): # base y num_nodes
    return [f"localhost:{base_port + i}" for i in range(count)]

def run_parallel_test(hosts, total_requests):
    manager = multiprocessing.Manager() # Compartir datos entre procesos
    result_dict = manager.dict()

    requests_per_host = total_requests // len(hosts) # reparte requests entre hosts
    processes = []
    global_start = time.time() # tiempo de inicio
    for i, host in enumerate(hosts):
        p = multiprocessing.Process(
            target=send_requests, args=(host, requests_per_host, result_dict, i)
        )
        p.start()
        processes.append(p)

    for p in processes: # espera a que terminen
        p.join()
    global_elapsed = time.time() - global_start

    print("\n=== Times ===")
    for i in sorted(result_dict.keys()):
        host, count, elapsed = result_dict[i]

    print(f"\n[TOTAL] {total_requests} requests in {global_elapsed:.2f}s -> {total_requests/global_elapsed:.1f} req/s")

if __name__ == "__main__":
    num_nodes = int(sys.argv[1]) if len(sys.argv) > 1 else 3 # Default 3 nodes
    num_requests = int(sys.argv[2]) if len(sys.argv) > 2 else 100 # Default 100 

    hosts = generate_hosts(8100, num_nodes)
    print(f"[INFO] Running test with hosts: {hosts}")
    run_parallel_test(hosts, num_requests)
