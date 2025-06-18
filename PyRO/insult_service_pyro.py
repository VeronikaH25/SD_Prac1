
import json
import Pyro4
import random
import time
import argparse
from threading import Thread, Lock

@Pyro4.expose
class InsultService:
    JSON_FILE = "insults.json"

    def __init__(self):
        self._lock = Lock()
        try:
            with open(self.JSON_FILE, "r") as f:
                data = json.load(f)
            self.insults = set(data.get("insults", []))
        except (FileNotFoundError, json.JSONDecodeError):
            self.insults = set()
        self.subscribers = []

    def _save(self): # Guarda insultos en el archivo JSON
        with open(self.JSON_FILE, "w") as f:
            json.dump({"insults": list(self.insults)}, f, indent=2)

    def add_insult(self, insult): # Añade insulto
        with self._lock:
            if insult not in self.insults:
                self.insults.add(insult)
                self._save()
                print(f"[{self._name}] Added insult: {insult}")
                return True
            else:
                print(f"[{self._name}] Insult already present: {insult}")
                return False

    def get_insults(self): # Devuelve insultos
        with self._lock:
            return list(self.insults)

    def register_subscriber(self, subscriber_uri): # Registra suscriptor
        with self._lock:
            if subscriber_uri not in self.subscribers:
                self.subscribers.append(subscriber_uri)
                print(f"[{self._name}] Subscriber registered: {subscriber_uri}")
        return True

    def broadcast_loop(self): #Difunde insultos a los suscriptores
        while True:
            time.sleep(5)
            with self._lock:
                insults = list(self.insults)
                subs = list(self.subscribers)
            if insults and subs:
                insult = random.choice(insults)
                for uri in subs:
                    try:
                        Pyro4.Proxy(uri).receive_insult(insult)
                    except:
                        pass

def run_service(host, port, name):
    InsultService._name = name
    service = InsultService()
    daemon = Pyro4.Daemon(host=host, port=port)
    uri = daemon.register(service)
    ns = Pyro4.locateNS()
    ns.register(name, uri)
    print(f"[Server] {name} running at {uri}")
    Thread(target=service.broadcast_loop, daemon=True).start()
    daemon.requestLoop()

if __name__=="__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--host", default="localhost")
    p.add_argument("--port", type=int, required=True)
    p.add_argument("--name", required=True)
    args = p.parse_args()
    run_service(args.host, args.port, args.name)
