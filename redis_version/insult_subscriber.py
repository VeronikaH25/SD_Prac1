# subscriber_queue.py
import redis
import json

def start_subscriber():
    r = redis.Redis(host='localhost', port=6379, decode_responses=True)
    pubsub = r.pubsub()
    pubsub.subscribe('filtered:results')
    print("Subscriber listening on filtered:results")

    for message in pubsub.listen():
        if message['type'] != 'message':
            continue
        try:
            data = json.loads(message['data'])
            print(f"[Subscriber] Filtered text: {data.get('filtered_text')}")
        except Exception as e:
            print("Error parsing message:", e)

if __name__ == '__main__':
    start_subscriber()
