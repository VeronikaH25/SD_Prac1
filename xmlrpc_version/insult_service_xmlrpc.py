from xmlrpc.server import SimpleXMLRPCServer
from xmlrpc.server import SimpleXMLRPCRequestHandler
from threading import Lock, Thread
import json, time, random

class InsultService:
    def __init__(self):
        self._lock = Lock()
        self.insults = set()
        self.subscribers = []
        try:
            with open("insults.json", "r") as f:
                self.insults = set(json.load(f).get("insults", []))
        except:
            pass

    def add_insult(self, insult): #Añadir insulto
        with self._lock:
            if insult not in self.insults:
                self.insults.add(insult)
                with open("insults.json", "w") as f:
                    json.dump({"insults": list(self.insults)}, f)
                return True
            return False

    def get_insults(self): #Devolver insultos
        with self._lock:
            return list(self.insults)

    def register_subscriber(self, url): #Registrar subscriber
        with self._lock:
            if url not in self.subscribers:
                self.subscribers.append(url)
        return True

    def broadcast_loop(self):
        import xmlrpc.client
        while True:
            time.sleep(5)
            with self._lock:
                if not self.insults or not self.subscribers: #No hay insultos o subscribers
                    continue
                insult = random.choice(list(self.insults))
                for sub in self.subscribers:
                    try: #Crea un proxi para que apunte a la url del subscriber y lo llama
                        xmlrpc.client.ServerProxy(sub).receive_insult(insult)
                    except:
                        pass

def run_service(port):
    service = InsultService() #Crea la instancia del servicio
    server = SimpleXMLRPCServer(("localhost", port), allow_none=True) #Crea el servidor en el puerto 
    server.register_instance(service) #Registra la instancia y las funciones se pueden llamar
    Thread(target=service.broadcast_loop, daemon=True).start() #funcion en paralelo demon=true se cierra al cerrar el programa
    print(f"[XMLRPC] InsultService running on port {port}")
    server.serve_forever()

if __name__ == "__main__":
    import sys
    run_service(int(sys.argv[1]))
