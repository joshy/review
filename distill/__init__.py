from distill.calcium import extract_score
from distill.ventricle_function import extract_ventricle_function

def process(report, meta_data):
    if meta_data['Untersuchung'] == 'CT Herz':
        return extract_score(report, meta_data)
    elif meta_data['Untersuchung'] == 'MRI Herz':
        return extract_ventricle_function(report, meta_data)
    else:
        return {}