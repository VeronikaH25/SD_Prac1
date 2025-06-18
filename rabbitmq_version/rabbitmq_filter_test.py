import time
import pika
import json
import multiprocessing

# Función para enviar textos a la cola 'texts' (usada por insult_filter.py)
def send_texts_to_filter_queue(num_requests):
    connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
    channel = connection.channel()

    # Declarar la cola 'texts' (coincide con la que usa insult_filter.py)
    channel.queue_declare(queue='texts')

    for _ in range(num_requests):
        message = {"text": "You are so stupid"}  # Contiene un insulto conocido
        channel.basic_publish(
            exchange='',
            routing_key='texts',
            body=json.dumps(message),
            properties=pika.BasicProperties(
                delivery_mode=2  # Hacer que el mensaje sea persistente
            )
        )

    connection.close()

# Test de rendimiento con un solo nodo
def rabbitmq_filter_test_single_node(num_requests):
    start_time = time.time()
    send_texts_to_filter_queue(num_requests)
    end_time = time.time()

    total_time = end_time - start_time
    print(f"[RabbitMQ Filter Single Node] Procesados {num_requests} solicitudes en {total_time:.4f} segundos.")
    return total_time

# Función de trabajo para procesos en múltiples nodos
def worker(num_requests):
    send_texts_to_filter_queue(num_requests)

# Test de rendimiento con múltiples nodos
def rabbitmq_filter_test_multiple_nodes(num_requests, num_nodes):
    processes = []
    requests_per_node = num_requests // num_nodes

    start_time = time.time()

    for _ in range(num_nodes):
        p = multiprocessing.Process(target=worker, args=(requests_per_node,))
        processes.append(p)
        p.start()

    for p in processes:
        p.join()

    end_time = time.time()
    total_time = end_time - start_time
    print(f"[RabbitMQ Filter Multiple Nodes] Procesados {num_requests} solicitudes con {num_nodes} nodos en {total_time:.4f} segundos.")
    return total_time

if __name__ == "__main__":
    num_requests = 10000

    # Prueba con un solo nodo
    rabbitmq_single_node_time = rabbitmq_filter_test_single_node(num_requests)

    # Prueba con múltiples nodos
    num_nodes = 2
    rabbitmq_multiple_nodes_time = rabbitmq_filter_test_multiple_nodes(num_requests, num_nodes)

    # Cálculo de Speedup
    speedup = rabbitmq_single_node_time / rabbitmq_multiple_nodes_time
    print(f"Speedup: {speedup:.2f}")

    # Escalado dinámico
    lambda_rate = 500  # mensajes por segundo
    avg_processing_time = 0.01  # segundos por mensaje
    capacity_per_worker = 50  # mensajes por segundo

    dynamic_workers = int((lambda_rate * avg_processing_time) / capacity_per_worker)
    dynamic_workers = max(dynamic_workers, 1)

    print(f"[RabbitMQ Filter Dynamic Scaling] Calculados {dynamic_workers} workers dinámicamente.")
    rabbitmq_dynamic_time = rabbitmq_filter_test_multiple_nodes(num_requests, dynamic_workers)