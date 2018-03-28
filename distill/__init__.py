from distill.calcium import execute

def process(report, meta_data):
    if meta_data['Untersuchung'] == 'CT Herz':
        return execute(report, meta_data)
    else:
        return {}