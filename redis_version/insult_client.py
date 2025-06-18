import redis
import json
import uuid
import threading

def main():
    r = redis.Redis(host='localhost', port=6379, decode_responses=True)
    pubsub = r.pubsub()

    # Input del usuario
    text = input("Enter text to filter: ")
    correlation_id = str(uuid.uuid4())
    reply_channel = f"reply_{correlation_id}"

    # Función que espera la respuesta
    def listen_for_reply():
        pubsub.subscribe(reply_channel)
        for message in pubsub.listen():
            if message['type'] == 'message':
                try:
                    data = json.loads(message['data'])
                    print("Filtered text:", data.get("filtered_text", "No result"))
                except:
                    print("Invalid response")
                break

    threading.Thread(target=listen_for_reply, daemon=True).start()

    r.publish('texts', json.dumps({
        "text": text,
        "reply_to": reply_channel,
        "correlation_id": correlation_id
    }))

    input("Press Enter to exit...\n")

if __name__ == '__main__':
    main()