import unittest

from distill import extract_volume
from distill.heart_volume import LVEF, EDV, EDVI, ESV, SV, ED, EDI

class TestParse(unittest.TestCase):
    def test_a(self):
        sample_text = """
        Motilität/Funktion:
        Global regelrechte Pumpfunktion ohne Nachweis einer umschriebenen Motilitätsstörung. Kein Hinweis auf Klappendysfunktion. Die Volumenmessung ergab folgende Werte: Linksventrikuläre Funktion|Norm. Frau / Mann*|gemessen|
        Linksventrikuläre Auswurffraktion (LVEF)|57-77 / 57-77|61 % |
        Enddiastolisches Volumen (EDV) |86-178 / 106-214|94.67 ml |
        Enddiastolisches Volumen indexiert (EDVI)|56-96 / 57-105|56.53 ml/m² |
        Endsystolisches Volumen (ESV)|22-66 / 26-82|37.30 ml |
        Schlagvolumen (SV)|57-117 / 72-144|57.37 ml |
        Myokardmasse (ED)|56-140 / 92-176|107.48 g |
        Myokardmasse indexiert (ED) |41-81 / 49-85|64.18 g/m² |
        """
        result = extract_volume(sample_text, {'Untersuchung': 'MRI Herz'})
        self.assertEqual(result['heart_volume'][LVEF], {'norm': '57-77 / 57-77', 'gemessen': '61 %'})
        self.assertEqual(result['heart_volume'][EDV], {'norm': '86-178 / 106-214', 'gemessen': '94.67 ml'})
        self.assertEqual(result['heart_volume'][EDVI], {'gemessen': '56.53 ml/m²', 'norm': '56-96 / 57-105'})
        self.assertEqual(result['heart_volume'][ESV], {'norm': '22-66 / 26-82', 'gemessen': '37.30 ml'})
        self.assertEqual(result['heart_volume'][SV], {'gemessen': '57.37 ml', 'norm': '57-117 / 72-144'})
        self.assertEqual(result['heart_volume'][ED], {'norm': '56-140 / 92-176', 'gemessen': '107.48 g'})
        self.assertEqual(result['heart_volume'][EDI], {'gemessen': '64.18 g/m²', 'norm': '41-81 / 49-85'})