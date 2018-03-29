import unittest

from distill.ventricle_function import LVEF, RVEF, EDV, EDVI, ESV, SV, ED, EDI, extract_ventricle_function

class TestParse(unittest.TestCase):
    def test_a(self):
        sample_text = """
        Motilität/Funktion:
        Global regelrechte Pumpfunktion ohne Nachweis einer umschriebenen Motilitätsstörung. Kein Hinweis auf Klappendysfunktion. Die Volumenmessung ergab folgende Werte:
        Linksventrikuläre Funktion|Norm. Frau / Mann*|gemessen|
        Linksventrikuläre Auswurffraktion (LVEF)|57-77 / 57-77|61 % |
        Enddiastolisches Volumen (EDV) |86-178 / 106-214|94.67 ml |
        Enddiastolisches Volumen indexiert (EDVI)|56-96 / 57-105|56.53 ml/m² |
        Endsystolisches Volumen (ESV)|22-66 / 26-82|37.30 ml |
        Schlagvolumen (SV)|57-117 / 72-144|57.37 ml |
        Myokardmasse (ED)|56-140 / 92-176|107.48 g |
        Myokardmasse indexiert (ED) |41-81 / 49-85|64.18 g/m² |

        Rechtsventrikuläre Funktion| Norm. Frau / Mann*|gemessen|
        Rechtsventrikuläre Auswurffraktion (RVEF)|52-72|61 % |
        Enddiastolisches Volumen (EDV)|77-201 / 118-250|82.29 ml |
        Enddiastolisches Volumen indexiert (EDVI)|48-112 / 61-121|47.45 ml/m² |
        Endsystolisches Volumen (ESV)|41-117|31.72 ml |
        Schlagvolumen (SV)|48-120 / 68-144| 50.57 ml |
        *Referenzwerte nach Kawel-Böhm et al., 2015
        """
        result = extract_ventricle_function(sample_text, {'Untersuchung': 'MRI Herz'})

        left = result['ventricle_function']['left']
        self.assertEqual(left[LVEF], {'norm': '57-77 / 57-77', 'gemessen': '61 %'})
        self.assertEqual(left[EDV], {'norm': '86-178 / 106-214', 'gemessen': '94.67 ml'})
        self.assertEqual(left[EDVI], {'gemessen': '56.53 ml/m²', 'norm': '56-96 / 57-105'})
        self.assertEqual(left[ESV], {'norm': '22-66 / 26-82', 'gemessen': '37.30 ml'})
        self.assertEqual(left[SV], {'gemessen': '57.37 ml', 'norm': '57-117 / 72-144'})
        self.assertEqual(left[ED], {'norm': '56-140 / 92-176', 'gemessen': '107.48 g'})
        self.assertEqual(left[EDI], {'gemessen': '64.18 g/m²', 'norm': '41-81 / 49-85'})

        right = result['ventricle_function']['right']
        self.assertEqual(right[RVEF], {'gemessen': '61 %', 'norm': '52-72'})
        self.assertEqual(right[EDV], {'norm': '77-201 / 118-250', 'gemessen': '82.29 ml'})
        self.assertEqual(right[EDVI], {'gemessen': '47.45 ml/m²', 'norm': '48-112 / 61-121'})
        self.assertEqual(right[ESV], {'gemessen': '31.72 ml', 'norm': '41-117'})
        self.assertEqual(right[SV], {'gemessen': '50.57 ml', 'norm': '48-120 / 68-144'})
