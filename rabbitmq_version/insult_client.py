import pika
import json
import uuid

# Conexión a RabbitMQ
connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
channel = connection.channel()

# Crear cola temporal exclusiva para recibir respuesta
result = channel.queue_declare(queue='', exclusive=True)
callback_queue = result.method.queue

# Leer texto desde consola
text = input("Enter text to filter: ")

# Generar ID único para esta petición
correlation_id = str(uuid.uuid4())
message = {"text": text}

# Publicar en la cola 'texts', indicando reply_to
channel.basic_publish(
    exchange='',
    routing_key='texts',
    properties=pika.BasicProperties(
        reply_to=callback_queue,
        correlation_id=correlation_id
    ),
    body=json.dumps(message).encode()
)
print("Sent text to be filtered. Waiting for response...")

# Función para recibir y filtrar solo nuestra respuesta
def on_response(ch, method, properties, body):
    if properties.correlation_id == correlation_id:
        try:
            response = json.loads(body.decode())
            print("Filtered text:", response.get("filtered_text", "No result"))
        except json.JSONDecodeError:
            print("Received non-JSON response:", body.decode())
        ch.stop_consuming()

# Escuchar en nuestra cola exclusiva
channel.basic_consume(queue=callback_queue, on_message_callback=on_response, auto_ack=True)

try:
    channel.start_consuming()
except KeyboardInterrupt:
    print("Operation interrupted by user.")
finally:
    connection.close()