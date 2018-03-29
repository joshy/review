LVEF = 'Linksventrikuläre Auswurffraktion (LVEF)'
EDV = 'Enddiastolisches Volumen (EDV)'
EDVI = 'Enddiastolisches Volumen indexiert (EDVI)'
ESV = 'Endsystolisches Volumen (ESV)'
SV = 'Schlagvolumen (SV)'
ED = 'Myokardmasse (ED)'
EDI = 'Myokardmasse indexiert (ED)'


def extract_volume(report, meta_data):
    result = {}
    lines = [s.strip() for s in report.splitlines()]
    for l in lines:
        result = _extract(l, LVEF, result)
        result = _extract(l, EDV, result)
        result = _extract(l, EDVI, result)
        result = _extract(l, ESV, result)
        result = _extract(l, SV, result)
        result = _extract(l, ED, result)
        result = _extract(l, EDI, result)
    return {'heart_volume': result}


def _extract(line, start, result):
    if line.startswith(start):
        parts = line.split('|')
        result[parts[0].strip()] = {'norm': parts[1].strip(), 'gemessen': parts[2].strip()}
        return result
    else:
        return result