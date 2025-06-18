import pika
import json

def start_subscriber():
    connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
    channel = connection.channel()

    # Declarar la cola donde se reciben los textos filtrados
    channel.queue_declare(queue='filtered_texts')

    def callback(ch, method, properties, body):
        try:
            message = json.loads(body.decode())
            filtered_text = message.get('filtered_text', '')
            if filtered_text:
                print(f"[Subscriber] Texto filtrado recibido: {filtered_text}")
            else:
                print("[Subscriber] Mensaje sin texto filtrado.")
        except json.JSONDecodeError:
            print("[Subscriber] Error decodificando JSON.")
        ch.basic_ack(delivery_tag=method.delivery_tag)

    channel.basic_consume(queue='filtered_texts', on_message_callback=callback)

    print("[Subscriber] Escuchando en la cola 'filtered_texts'...")
    try:
        channel.start_consuming()
    except KeyboardInterrupt:
        print("[Subscriber] Detenido por usuario.")
        connection.close()

if __name__ == '__main__':
    start_subscriber()
