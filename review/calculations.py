from math import floor

def relative(df):
    df['words_added_g_f_relative'] = df.apply(
        lambda row: _relative(row['total_words_f'], row['words_added_g_f']), axis=1)
    df['words_deleted_g_f_relative'] = df.apply(
        lambda row: _relative(row['total_words_f'], row['words_deleted_g_f']), axis=1)
    return df

def _relative(total, changes):
    t = total or 1.0
    return (changes) / t

def calculate_median(values):
    if (len(values) == 0):
        return 0

    values = sorted(values)
    half = int(floor(len(values) / 2))

    if(len(values) % 2):
        return values[half]
    else:
        return (values[half - 1] + values[half]) / 2.0
