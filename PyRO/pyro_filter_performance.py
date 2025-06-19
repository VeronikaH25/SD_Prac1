import time
import multiprocessing
import itertools
import Pyro4
import sys

def discover_filter_names(prefix="insult_filter_pyro"): #devuelve una lista de nombres de filters 
    ns = Pyro4.locateNS()
    all_names = ns.list().keys() # filtrar por prefijo "insult_filter_pyro"
    names = [n for n in all_names if n.startswith(prefix)]
    return sorted(names)

def send_filter_requests(filter_names, num_requests): #reparte peticiones a los filters
    ns = Pyro4.locateNS() #conectar al Name Server de Pyro
    proxies = [Pyro4.Proxy(ns.lookup(name)) for name in filter_names] # Crear proxies para cada filtro
    rr = itertools.cycle(proxies) #round-robin para distribuir peticiones
    for _ in range(int(num_requests)):
        next(rr).submit_text("This is an example to test performance.")

def pyro_filter_test_single_node(num_requests, filter_name):
    start = time.time()
    send_filter_requests([filter_name], num_requests)
    elapsed = time.time() - start
    print(f"[Pyro Single Node] {num_requests} reqs en {elapsed:.4f} s → {num_requests/elapsed:.1f} req/s")
    return elapsed

def pyro_filter_test_multiple_nodes(num_requests, filter_names):
    num_nodes = len(filter_names)
    requests_per_node = int(num_requests) // num_nodes

    procs = []
    start = time.time()
    for _ in range(num_nodes):
        p = multiprocessing.Process(
            target=send_filter_requests,
            args=(filter_names, requests_per_node)
        )
        p.start()
        procs.append(p)

    for p in procs: # espera a que terminen
        p.join()

    elapsed = time.time() - start
    print(f"[Pyro {num_nodes} Nodes] {num_requests} reqs en {elapsed:.4f} s → {num_requests/elapsed:.1f} req/s")
    return elapsed

if __name__ == "__main__":
    # Leer parámetros de línea de comandos
    NUM_REQUESTS = int(sys.argv[1]) if len(sys.argv) > 1 else 10000
    MAX_NODES = int(sys.argv[2]) if len(sys.argv) > 2 else 1

    # Descubrir filtros registrados
    filter_names = discover_filter_names(prefix="insult_filter_pyro")
    if not filter_names:
        print("No se han encontrado filtros registrados en Pyro NS.")
        exit(1)

    filter_names = filter_names[:MAX_NODES]  # limitar al número de nodos deseado
    print("Filtros encontrados:", filter_names)
    print("=== Pyro Filter Performance Test ===")

    # Ejecutar prueba con un único nodo
    t_single = pyro_filter_test_single_node(NUM_REQUESTS, filter_names[0])

    # Solo ejecutar prueba multi-node si hay más de uno
    if len(filter_names) > 1:
        t_multi = pyro_filter_test_multiple_nodes(NUM_REQUESTS, filter_names)
        speedup = t_single / t_multi
        print(f"→ Speedup {len(filter_names)}-node vs single: {speedup:.2f}")