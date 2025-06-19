import json
import unittest
import Pyro4

class TestPyroFilterWithJSON(unittest.TestCase):
    @classmethod
    def setUpClass(cls): # se ejecuta una vez antes de todos los tests
        with open("insults.json", "r") as f: #Lee insults.json
            data = json.load(f)
        cls.insults_from_file = data.get("insults", [])
        if not cls.insults_from_file:
            raise unittest.SkipTest("Empty insults.json list.")

        try: # Conectar al filter 
            cls.filter = Pyro4.Proxy("PYRONAME:insult_filter_pyro0")
        except Exception as e:
            raise unittest.SkipTest(f"No se pudo conectar al filtro remoto: {e}")

    def test_update_insults_from_json(self): # Test: que el filtro actualice los insults
        insults = self.filter.update_insults(self.insults_from_file)
        self.assertTrue(insults, "update_insults devolvió False al pasar la lista desde JSON")

    def test_filter_replaces_json_insult(self): # Test: que el filtro reemplace un insulto de JSON
        self.filter.update_insults(self.insults_from_file)

        sample_insult = self.insults_from_file[0] # primer insulto de la lista
        text = f"This contains a JSON insult: {sample_insult} inside."
        filtered = self.filter.submit_text(text)
        self.assertIn("CENSORED", filtered) # Verificamos que la palabra "CENSORED" esté presente
        self.assertNotIn(sample_insult, filtered) # Verificamos que el insulto original no esté presente
        self.assertIn("This contains a JSON insult:", filtered) # Verificamos que el texto original esté presente

if __name__ == "__main__":
    unittest.main(verbosity=2)
