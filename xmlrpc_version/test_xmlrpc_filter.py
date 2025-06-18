
import unittest, time, xmlrpc.client

class TestXMLRPCFilter(unittest.TestCase):
    FILTER_URL = "http://localhost:8100" #Probamos el filter del localhost 8001

    @classmethod
    def setUpClass(cls): #Proxi representando el servidor
        cls.proxy = xmlrpc.client.ServerProxy(cls.FILTER_URL, allow_none=True) 

    def test_update_and_submit(self):
        insults = ["insult1", "insult2", "insult3", "insult4"]
        self.assertTrue(self.proxy.update_insults(insults))
        out = self.proxy.submit_text("hola insult1 i intult2 insult3")
        self.assertIn("CENSORED", out) #Se espera que el texto contenga la palabra CENSORED
        self.assertNotIn("insult1", out)
        self.assertNotIn("insult3", out)
        self.assertIn("hola", out)
        self.assertIn("i", out)
    
        res = self.proxy.get_filtered_results() #Devuelve la lista 
        self.assertIsInstance(res, list) #Es una lista
        self.assertEqual(res[-1], out)

if __name__=="__main__":
    unittest.main(verbosity=2)
