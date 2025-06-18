
import time, multiprocessing, itertools, Pyro4, sys

def discover_service_names(prefix="insult_service_pyro"):
    ns = Pyro4.locateNS()
    return sorted(n for n in ns.list().keys()
                  if n.startswith(prefix))

def send_service_requests(names, num_requests):
    ns = Pyro4.locateNS()
    prox = [Pyro4.Proxy(ns.lookup(n)) for n in names]
    rr = itertools.cycle(prox)
    for i in range(int(num_requests)):
        next(rr).add_insult(f"ins_{i}_{time.time()}")

def test_single(num_requests, name):
    start = time.time()
    send_service_requests([name], num_requests)
    dt = time.time() - start
    print(f"[Single Node] {num_requests} add_insult en {dt:.2f}s → {num_requests/dt:.1f} req/s")
    return dt

def test_multi(num_requests, names):
    per = int(num_requests) // len(names)
    procs = []
    start = time.time()
    for _ in names:
        p = multiprocessing.Process(target=send_service_requests,
                                    args=(names, per))
        p.start()
        procs.append(p)
    for p in procs:
        p.join()
    dt = time.time() - start
    print(f"[{len(names)} Nodes] {num_requests} add_insult en {dt:.2f}s → {num_requests/dt:.1f} req/s")
    return dt

if __name__ == "__main__":
    # Leer parámetros desde línea de comandos
    N = int(sys.argv[1]) if len(sys.argv) > 1 else 10000
    MAX_NODES = int(sys.argv[2]) if len(sys.argv) > 2 else 1

    names = discover_service_names("insult_service_pyro")
    if not names:
        print("No hay nodos insultservice registrados.")
        exit(1)

    names = names[:MAX_NODES]  # limitar número de nodos a usar
    print("Servicios:", names)

    t1 = test_single(N, names[0])

    if len(names) > 1:
        tN = test_multi(N, names)
        print(f"→ Speedup {len(names)}-node vs single: {t1/tN:.2f}×")