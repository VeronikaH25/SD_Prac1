
import unittest, threading, time, xmlrpc.client
from xmlrpc.server import SimpleXMLRPCServer

class DummySubscriber:
    def __init__(self):
        self.received = []
    def receive_insult(self, insult):
        self.received.append(insult)
        return True

class TestXMLRPCService(unittest.TestCase):
    SERVICE_URL = "http://localhost:8000"

    @classmethod
    def setUpClass(cls):
        cls.proxy = xmlrpc.client.ServerProxy(cls.SERVICE_URL, allow_none=True) #Proxi representando el servidor

    def test_add_and_get(self): #Prueba de añadir y obtener insultos
        tag = f"test_{time.time()}" #crea un insulto con un tag tiempo
        added_ins = self.proxy.add_insult(tag)
        self.assertTrue(added_ins) #verifica que se haya añadido correctamente
        list = self.proxy.get_insults() #lista de insultos
        self.assertIn(tag, list) #verifica que este en la lista

    def test_broadcast(self): # Prueba de broadcast
        sub = DummySubscriber()
        sub_server = SimpleXMLRPCServer(("localhost", 0), allow_none=True, logRequests=False) #crea un server en puerto aleatorio (0)
        port = sub_server.server_address[1] # obtenemos el puerto aleatorio                   #logRequests=False para no mostrar logs
        sub_server.register_instance(sub) #registra el DummySubscriber
        threading.Thread(target=sub_server.serve_forever, daemon=True).start() #lanza server

        self.proxy.register_subscriber(f"http://localhost:{port}")
        self.proxy.add_insult("insult1")
        self.proxy.add_insult("insult2")
        self.proxy.add_insult("insult3")
        time.sleep(5)
        sub_server.shutdown()

        self.assertGreaterEqual(len(sub.received), 1, "No broadcast received")

if __name__=="__main__":
    unittest.main(verbosity=2)
