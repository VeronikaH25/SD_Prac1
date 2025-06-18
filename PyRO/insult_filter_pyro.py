import Pyro4
import argparse
import json
import os
from threading import Lock

@Pyro4.expose
class InsultFilter:
    JSON_FILE = "insults.json"

    def __init__(self, name):
        self._lock = Lock()
        self._name = name
        self.results = []
        if os.path.exists(self.JSON_FILE):  # carga insultos del archivo JSON
            try:
                with open(self.JSON_FILE, "r") as f:
                    data = json.load(f)
                self.insults = set(data.get("insults", []))
                print(f"[{self._name}] Loaded insults from JSON: {self.insults}")
            except json.JSONDecodeError:
                print(f"[{self._name}] Error decoding {self.JSON_FILE}")
                self.insults = set()
        else:
            print(f"[{self._name}] No {self.JSON_FILE} found")
            self.insults = set()

    def update_insults(self, insult_list):  # actualiza insultos
        with self._lock:
            self.insults = set(insult_list)
            print(f"[{self._name}] Insult list updated: {self.insults}")
        return True

    def submit_text(self, text):  # filtra insultos
        with self._lock:
            filtered = ' '.join(
                "CENSORED" if w in self.insults else w
                for w in text.split()
            )
            self.results.append(filtered)
            print(f"[{self._name}] Filtered text: {filtered}")
        return filtered

    def get_filtered_results(self):  # devuelve resultados filtrados
        with self._lock:
            print(f"[{self._name}] Filtered results: {self.results}")
            return list(self.results)

def run_filter(host, port, name):
    daemon = Pyro4.Daemon(host=host, port=port)
    uri = daemon.register(InsultFilter(name))  #  pasamos el name 
    #uri = daemon.register(InsultFilter(name), name)  #nou

    ns = Pyro4.locateNS()
    ns.register(name, uri)
    print(f"[Server] {name} running at {uri}")
    daemon.requestLoop()

if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--host", default="localhost")
    p.add_argument("--port", type=int, required=True)
    p.add_argument("--name", required=True)
    args = p.parse_args()
    run_filter(args.host, args.port, args.name)
