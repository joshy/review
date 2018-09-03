from distiller.calcium import extract_score
from distiller.aorta import extract_table
from distiller.ventricle_function import extract_ventricle_function


def process(report, meta_data):
    if meta_data is None:
        return {}
    elif contains_aorta(meta_data["Untersuchung"]):
        x = extract_score(report, meta_data)
        y = extract_table(report, meta_data)
        return {**x, **y}
    elif meta_data["Untersuchung"] == "MRI Herz":
        return extract_ventricle_function(report, meta_data)
    else:
        return {}


def contains_aorta(study_description):
    x =  (
        study_description.startswith("CT Herz")
        or study_description.startswith("CT Aorten")
        or study_description.startswith("CT Angio")
    )
    return x

