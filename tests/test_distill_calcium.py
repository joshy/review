import unittest

from distiller import extract_score

class TestParse(unittest.TestCase):
    def test_a(self):
        sample_text = """
        Calcium-Score
        Coronararterie|Calcium-Score|RCA| 0|LM| 0|LAD/RIVA| 0|CX| 0|Gesamt Calcium-Score| 0|||
        Coronararterien
        Keine Coronarstenosen.
        Extracardiale Strukturen
        """
        result = extract_score(sample_text, {'Untersuchung': 'CT Herz'})
        self.assertDictEqual(result, {
            'calcium_score': {
                'RCA': '0',
                'LM': '0',
                'LAD/RIVA': '0',
                'CX': '0',
                'Gesamt Calcium-Score': '0'
            }
        })
