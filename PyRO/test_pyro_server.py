
import time, threading, unittest, Pyro4

def discover_services(prefix="insult_service_pyro"):
    ns = Pyro4.locateNS()
    return sorted(name for name in ns.list().keys() if name.startswith(prefix))

class TestInsultService(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        services = discover_services()
        if not services:
            raise unittest.SkipTest("No s'han trobat serveis 'insult_service_pyro' registrats")
        cls.service_names = services
        cls.service = Pyro4.Proxy("PYRONAME:" + services[0])  

    def test_add_and_get(self):
        tag = f"test_{time.time()}"
        ok = self.service.add_insult(tag)
        self.assertTrue(ok)
        lst = self.service.get_insults()
        self.assertIn(tag, lst)
        ok2 = self.service.add_insult(tag)
        self.assertFalse(ok2)

    def test_broadcast(self):
        received = []

        @Pyro4.expose
        class DummySub:
            def receive_insult(self, insult):
                received.append(insult)
                return True

        daemon = Pyro4.Daemon(host="localhost", port=0)
        uri = daemon.register(DummySub())
        ns = Pyro4.locateNS()
        ns.register("dummy_sub", uri)

        t = threading.Thread(target=daemon.requestLoop, daemon=True)
        t.start()

        self.service.register_subscriber("PYRONAME:dummy_sub")
        self.service.add_insult("insult1")
        self.service.add_insult("insult2")
        time.sleep(6)

        self.assertGreaterEqual(len(received), 1, "No s'ha rebut cap broadcast")
        daemon.shutdown()

if __name__ == "__main__":
    unittest.main(verbosity=2)
