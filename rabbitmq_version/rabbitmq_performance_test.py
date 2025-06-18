# test_broadcaster_stress.py
import time
import subprocess
import multiprocessing

# Lanza una instancia de broadcaster con N mensajes
def run_broadcaster_instance(num_requests_per_process):
    subprocess.run([
        "python", "insult_broadcaster.py",
        "--count", str(num_requests_per_process),
        "--silent"
    ])

# Test con un solo broadcaster
def rabbitmq_stress_test_single_node(num_requests):
    start_time = time.time()
    run_broadcaster_instance(num_requests)
    end_time = time.time()

    total_time = end_time - start_time
    print(f"[RabbitMQ Single Node] Procesados {num_requests} mensajes en {total_time:.4f} segundos.")
    return total_time

# Test con múltiples broadcasters
def rabbitmq_stress_test_multiple_nodes(num_requests, num_nodes):
    processes = []
    requests_per_node = num_requests // num_nodes

    start_time = time.time()

    for _ in range(num_nodes):
        p = multiprocessing.Process(target=run_broadcaster_instance, args=(requests_per_node,))
        p.start()
        processes.append(p)

    for p in processes:
        p.join()

    end_time = time.time()

    total_time = end_time - start_time
    print(f"[RabbitMQ Multiple Nodes] Procesados {num_requests} mensajes con {num_nodes} nodos en {total_time:.4f} segundos.")
    return total_time

if __name__ == "__main__":
    num_requests = 10000

    # Prueba con un solo nodo
    rabbitmq_single_node_time = rabbitmq_stress_test_single_node(num_requests)

    # Prueba con múltiples nodos
    num_nodes = 2
    rabbitmq_multiple_nodes_time = rabbitmq_stress_test_multiple_nodes(num_requests, num_nodes)

    # Cálculo de Speedup
    speedup = rabbitmq_single_node_time / rabbitmq_multiple_nodes_time
    print(f"Speedup: {speedup:.2f}")

    # Escalado dinámico
    lambda_rate = 500  # mensajes por segundo
    avg_processing_time = 0.01  # segundos por mensaje
    capacity_per_worker = 50  # mensajes por segundo

    dynamic_workers = int((lambda_rate * avg_processing_time) / capacity_per_worker)
    dynamic_workers = max(dynamic_workers, 1)  # Al menos un worker

    print(f"[RabbitMQ Dynamic Scaling] Calculados {dynamic_workers} broadcasters dinámicamente.")
    rabbitmq_dynamic_time = rabbitmq_stress_test_multiple_nodes(num_requests, dynamic_workers)