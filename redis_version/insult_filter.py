# insult_filter_queue.py
import redis
import json
import re
import time

INSULTS_KEY = "insult:list"

class InsultFilter:
    def __init__(self):
        self.redis = redis.Redis(host='localhost', port=6379, decode_responses=True)

    def load_insults_from_redis(self):
        try:
            insults = self.redis.smembers(INSULTS_KEY)
            return insults
        except Exception as e:
            print("Error loading insults from Redis:", e)
            return []

    def filter_text(self, text):
        insults = self.load_insults_from_redis()
        filtered = text
        for insult in insults:
            filtered = re.sub(re.escape(insult), "CENSORED", filtered, flags=re.IGNORECASE)
        return filtered

def start_worker():
    r = redis.Redis(host='localhost', port=6379, decode_responses=True)
    f = InsultFilter()

    print("Worker listening on text:queue (BLPOP)...")
    while True:
        try:
            _, raw = r.blpop("text:queue")  # bloquea hasta que haya algo
            data = json.loads(raw)
            original_text = data.get("text", "")
            correlation_id = data.get("correlation_id")
            print(f"[Worker] Processing text: {original_text}")

            filtered = f.filter_text(original_text)

            result = {
                "filtered_text": filtered,
                "correlation_id": correlation_id
            }

            # Enviar al canal de resultados
            r.publish("filtered:results", json.dumps(result))
            print(f"[Worker] Published filtered text: {filtered}")

        except Exception as e:
            print("[Worker] Error:", e)
            time.sleep(1)  # para evitar bucles en error

if __name__ == '__main__':
    start_worker()
