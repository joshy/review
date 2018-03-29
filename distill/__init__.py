from distill.calcium import extract_score
from distill.heart_volume import extract_volume

def process(report, meta_data):
    if meta_data['Untersuchung'] == 'CT Herz':
        return extract_score(report, meta_data)
    elif meta_data['Untersuchung'] == 'MRI Herz':
        return extract_volume(report, meta_data)
    else:
        return {}