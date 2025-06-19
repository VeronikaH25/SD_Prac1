from xmlrpc.server import SimpleXMLRPCServer
from xmlrpc.server import SimpleXMLRPCRequestHandler
from threading import Lock
import json, os

class InsultFilter: 
    def __init__(self):
        self._lock = Lock() #Usamos threading
        self.results = [] #Guardaremos textos filtrados
        try:
            with open("insults.json", "r") as f: #Cargamos insultos desde un archivo JSON
                self.insults = set(json.load(f).get("insults", []))
        except:
            self.insults = set()

    def submit_text(self, text): #Reemplaza insultos por CENSORED
        with self._lock:
            filtered = ' '.join("CENSORED" if word in self.insults else word for word in text.split())
            self.results.append(filtered)
        return filtered

    def get_filtered_results(self): #Devuelve los resultados filtrados
        with self._lock:
            return list(self.results)

def run_filter(port):
    server = SimpleXMLRPCServer(("localhost", port), allow_none=True)
    server.register_instance(InsultFilter()) #Registrar la instancia del filtro
    print(f"[XMLRPC] InsultFilter running on port {port}")
    server.serve_forever() 

if __name__ == "__main__":
    import sys
    run_filter(int(sys.argv[1])) # python insult_filter_xmlrpc.py 8100(port)
