import unittest

from repo.parse import parse

class TestParse(unittest.TestCase):
    def test_a(self):
        a = """
            Anamnese\n
            A\n
            Technik\n
            B\n
            """
        t = [x.strip() for x in a.splitlines()]
        result = parse(t)
        self.assertEqual(result['anamnese'], 'A')
        self.assertEqual(result['technik'], 'B')

    def test_aa(self):
        a = """
            Anamnese\n
            A\n
            A\n
            Technik\n
            B\n
            """
        t = [x.strip() for x in a.splitlines()]
        result = parse(t)
        self.assertEqual(result['anamnese'], 'AA')
        self.assertEqual(result['technik'], 'B')

    def test_empty_lines(self):
        a = """
            Anamnese\n
            A\n
            \n
            A\n
            Technik\n
            B\n
            """
        t = [x.strip() for x in a.splitlines()]
        result = parse(t)
        self.assertEqual(result['anamnese'], 'AA')
        self.assertEqual(result['technik'], 'B')

    def test_empty_lines_1(self):
        a = """
            Anamnese\n
            A\n
            \n
            A\n
            Technik\n
            B\n
            \n
            \n
            """
        t = [x.strip() for x in a.splitlines()]
        result = parse(t)
        self.assertEqual(result['anamnese'], 'AA')
        self.assertEqual(result['technik'], 'B')


    def test_datenimport(self):
        a = """
            Bilder wurden auf Wunsch des Auftraggebers eingescannt\n
            """
        t = [x.strip() for x in a.splitlines()]
        result = parse(t)
        self.assertEqual(result['datenimport'],
                         'Bilder wurden auf Wunsch des Auftraggebers eingescannt')
