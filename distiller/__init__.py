from distiller.calcium import extract_score
from distiller.aorta import extract_table
from distiller.ventricle_function import extract_ventricle_function

def process(report, meta_data):
    if meta_data is None:
        return {}
    elif meta_data['Untersuchung'] == 'CT Herz':
        x = extract_score(report, meta_data)
        y = extract_table(report, meta_data)
        return {**x, **y}
    elif meta_data['Untersuchung'] == 'MRI Herz':
        return extract_ventricle_function(report, meta_data)
    else:
        return {}