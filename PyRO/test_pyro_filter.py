
import json
import unittest
import Pyro4

class TestPyroFilterWithJSON(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with open("insults.json", "r") as f: #Lee insults.json
            data = json.load(f)
        cls.insults_from_file = data.get("insults", [])
        if not cls.insults_from_file:
            raise unittest.SkipTest("Empty insults.json list.")

        try: # Conectar al filter 
            cls.filter = Pyro4.Proxy("PYRONAME:insult_filter_pyro0")
        except Exception as e:
            raise unittest.SkipTest(f"No se pudo conectar al filtro remoto: {e}")

    def test_update_insults_from_json(self): #Test: que el filtro actualice las insults
        insults = self.filter.update_insults(self.insults_from_file)
        self.assertTrue(insults, "update_insults devolvió False al pasar la lista desde JSON")

    def test_filter_replaces_json_insult(self):
        self.filter.update_insults(self.insults_from_file)

        sample_insult = self.insults_from_file[0]
        text = f"This contains a JSON insult: {sample_insult} inside."
        filtered = self.filter.submit_text(text)
        self.assertIn("CENSORED", filtered)
        self.assertNotIn(sample_insult, filtered)
        self.assertIn("This contains a JSON insult:", filtered)
        self.assertIn("inside.", filtered)

    def test_get_filtered_results_includes_last(self):

        # Llamamos a submit_text y guardamos el resultado
        sample_insult = self.insults_from_file[0]
        new_text = f"Edge case: {sample_insult}?"
        last_filtered = self.filter.submit_text(new_text)

        # Consultamos la lista de resultados y comparamos el último
        results = self.filter.get_filtered_results()
        self.assertIsInstance(results, list, "get_filtered_results no devolvió una lista")
        self.assertTrue(len(results) >= 1, "No hay resultados en el historial de filtrado")
        self.assertEqual(results[-1], last_filtered)

if __name__ == "__main__":
    unittest.main(verbosity=2)
