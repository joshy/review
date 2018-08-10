import unittest

from distiller.aorta import extract_table

class TestParse(unittest.TestCase):
    def test_a(self):
        sample_text = """
        Aneurysma Aorta aszendens mit folgenden Messwerten, die senkrecht zum Blutstrom gemessen wurden:
        Anulus [mm]|23.5|
        Sinus [mm]|31|
        Sinutubulärer Übergang [mm]|30|
        Aszendens Höhe rPA [mm]|40|
        Asz. vor Tr. Brachioceph. [mm]|37|
        Bogen zw. Tr. & li ACC [mm]|33|
        Bogen distal li A. subcl. [mm]|25|
        Extraaortale Strukturen:
        """
        result = extract_table(sample_text, {'Untersuchung': 'CT Herz'})
        self.assertDictEqual(result, {
            'aorta': {
                'Anulus': '23.5',
                'Asz': '37',
                'Aszendens': '40',
                'Bogen distal': '25',
                'Bogen zw': '33',
                'Sinus': '31',
                'Sinutubulärer': '30'
            }
        })
