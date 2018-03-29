from collections import OrderedDict

LVEF = 'Linksventrikuläre Auswurffraktion (LVEF)'
RVEF = 'Rechtsventrikuläre Auswurffraktion (RVEF)'
EDV = 'Enddiastolisches Volumen (EDV)'
EDVI = 'Enddiastolisches Volumen indexiert (EDVI)'
ESV = 'Endsystolisches Volumen (ESV)'
SV = 'Schlagvolumen (SV)'
ED = 'Myokardmasse (ED)'
EDI = 'Myokardmasse indexiert (ED)'

RESULT_KEY_VENCTRICLE_FUNCTION = 'ventricle_function'

LEFT_INDEX_START_V1 = 'Linksventrikuläre Funktion|Norm. Frau / Mann*|gemessen|'
RIGHT_INDEX_START_V1 = 'Rechtsventrikuläre Funktion| Norm. Frau / Mann*|gemessen|'

LEFT_INDEX_START_V2 = 'Linksventrikuläre Funktion|gemessen|Norm. Frau / Mann*|'
RIGHT_INDEX_START_V2 = 'Rechtsventrikuläre Funktion|gemessen|Norm. Frau / Mann*|'


def extract_ventricle_function(report, meta_data):

    lines = [s.strip() for s in report.splitlines()]
    left_index_v1 = [i for i,s in enumerate(lines) if s.startswith(LEFT_INDEX_START_V1)]
    right_index_v1 = [i for i,s in enumerate(lines) if s.startswith(RIGHT_INDEX_START_V1)]
    left_index_v2 = [i for i,s in enumerate(lines) if s.startswith(LEFT_INDEX_START_V2)]
    right_index_v2 = [i for i,s in enumerate(lines) if s.startswith(RIGHT_INDEX_START_V2)]

    left = OrderedDict()
    right = OrderedDict()

    left_index = left_index_v1 or left_index_v2
    right_index = right_index_v1 or right_index_v2
    variant = 1 if left_index_v1 else 2

    if left_index:
        for l in lines[left_index[0] : (left_index[0] + 8)]:
            left = _extract(l, LVEF, left, variant)
            left = _extract(l, EDV, left, variant)
            left = _extract(l, EDVI, left, variant)
            left = _extract(l, ESV, left, variant)
            left = _extract(l, SV, left, variant)
            left = _extract(l, ED, left, variant)
            left = _extract(l, EDI, left, variant)

    if right_index:
        for l in lines[right_index[0] : right_index[0] + 6]:
            right = _extract(l, RVEF, right, variant)
            right = _extract(l, EDV, right, variant)
            right = _extract(l, EDVI, right, variant)
            right = _extract(l, ESV, right, variant)
            right = _extract(l, SV, right, variant)

    return { RESULT_KEY_VENCTRICLE_FUNCTION : {'left': left, 'right': right}}


def _extract(line, prefix, result, variant):
    if line.startswith(prefix):
        parts = line.split('|')
        if variant == 1:
            result[parts[0].strip()] = OrderedDict({
                'norm': parts[1].strip(),
                'gemessen': parts[2].strip()
            })
        else:
            result[parts[0].strip()] = OrderedDict({
                'norm': parts[2].strip(),
                'gemessen': parts[1].strip()
            })
        return result
    else:
        return result