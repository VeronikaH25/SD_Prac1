import pika
import json
import re
import os
import threading

INSULTS_FILE = 'insults.json'
TEXT_QUEUE = 'text_queue'
FILTERED_QUEUE = 'filtered_texts'
NEW_INSULT_QUEUE = 'new_insult'

class InsultFilter:
    def __init__(self):
        self.insults = self.load_insults_from_file()

    def load_insults_from_file(self):
        if os.path.exists(INSULTS_FILE):
            try:
                with open(INSULTS_FILE, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    insults = data.get("insults", [])
                    print(f"[Filter] Cargados insultos iniciales desde archivo.")
                    return insults
            except json.JSONDecodeError:
                print("[Filter] Error leyendo insults.json")
        return []

    def add_insult(self, insult):
        insult_lower = insult.lower()
        if insult_lower not in [i.lower() for i in self.insults]:
            self.insults.append(insult)
            print(f"[Filter] Insulto añadido: {insult}")

    def filter_text(self, text):
        filtered_text = text
        for insult in self.insults:
            pattern = re.compile(re.escape(insult), re.IGNORECASE)
            filtered_text = pattern.sub("CENSORED", filtered_text)
        return filtered_text

def listen_new_insults(filter_obj):
    connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
    channel = connection.channel()
    channel.queue_declare(queue=NEW_INSULT_QUEUE)

    def new_insult_callback(ch, method, properties, body):
        insult = body.decode().strip()
        if insult:
            print(f"[Filter] Nuevo insulto recibido: {insult}")
            filter_obj.add_insult(insult)
        ch.basic_ack(delivery_tag=method.delivery_tag)

    channel.basic_consume(queue=NEW_INSULT_QUEUE, on_message_callback=new_insult_callback)
    print(f"[Filter] Escuchando nuevos insultos en '{NEW_INSULT_QUEUE}'...")
    channel.start_consuming()

def start_insult_filter():
    insult_filter = InsultFilter()

    # Hilo para escuchar nuevos insultos con conexión independiente
    thread_insults = threading.Thread(target=listen_new_insults, args=(insult_filter,), daemon=True)
    thread_insults.start()

    # Conexión principal para consumir textos a filtrar
    connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
    channel = connection.channel()
    channel.queue_declare(queue=TEXT_QUEUE)
    channel.queue_declare(queue=FILTERED_QUEUE)

    def text_callback(ch, method, properties, body):
        try:
            message = json.loads(body.decode())
        except json.JSONDecodeError:
            print("[Filter] Error decodificando mensaje JSON")
            ch.basic_ack(delivery_tag=method.delivery_tag)
            return

        text = message.get('text', '')
        if not text:
            print("[Filter] Mensaje sin campo 'text'")
            ch.basic_ack(delivery_tag=method.delivery_tag)
            return

        print(f"[Filter] Texto original: {text}")
        filtered = insult_filter.filter_text(text)
        print(f"[Filter] Texto filtrado: {filtered}")

        response = json.dumps({"filtered_text": filtered})

        channel.basic_publish(exchange='', routing_key=FILTERED_QUEUE, body=response.encode())
        ch.basic_ack(delivery_tag=method.delivery_tag)

    channel.basic_consume(queue=TEXT_QUEUE, on_message_callback=text_callback)

    print(f"[Filter] En ejecución, esperando mensajes en '{TEXT_QUEUE}'...")
    try:
        channel.start_consuming()
    except KeyboardInterrupt:
        print("[Filter] Detenido por usuario")
        connection.close()

if __name__ == '__main__':
    start_insult_filter()
