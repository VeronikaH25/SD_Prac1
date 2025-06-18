# redis_broadcaster_test.py
import time
import subprocess
import multiprocessing
import sys
import os

def run_broadcaster_instance(num_requests_per_process):
    # Ejecuta insult_broadcaster.py, redirigiendo su salida a /dev/null o nul
    with open(os.devnull, 'w') as devnull:
        subprocess.run(
            [sys.executable, "insult_broadcaster.py", str(num_requests_per_process)],
            stdout=devnull, stderr=devnull
        )

# Test con un solo broadcaster
def redis_broadcast_test_single_node(num_requests):
    start_time = time.time()
    run_broadcaster_instance(num_requests)
    end_time = time.time()

    total_time = end_time - start_time
    print(f"[Redis Broadcaster Single Node] Enviados {num_requests} mensajes en {total_time:.4f} segundos.")
    return total_time

# Test con múltiples broadcasters
def redis_broadcast_test_multiple_nodes(num_requests, num_nodes):
    processes = []
    requests_per_node = num_requests // num_nodes

    start_time = time.time()

    for _ in range(num_nodes):
        p = multiprocessing.Process(target=run_broadcaster_instance, args=(requests_per_node,))
        processes.append(p)
        p.start()

    for p in processes:
        p.join()

    end_time = time.time()
    total_time = end_time - start_time
    print(f"[Redis Broadcaster Multiple Nodes] Enviados {num_requests} mensajes con {num_nodes} nodos en {total_time:.4f} segundos.")
    return total_time

if __name__ == "__main__":
    num_requests = 1000  # Ajusta aquí el número total de mensajes
    num_nodes = 3         # Ajusta aquí el número de nodos para la prueba paralela

    # Prueba con un solo nodo
    single_time = redis_broadcast_test_single_node(num_requests)

    # Prueba con múltiples nodos
    multiple_time = redis_broadcast_test_multiple_nodes(num_requests, num_nodes)

    # Speedup
    speedup = single_time / multiple_time
    print(f"Speedup: {speedup:.2f}")
