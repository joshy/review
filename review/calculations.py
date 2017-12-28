def relative(df):
    df['words_added_g_f_relative'] = df.apply(
        lambda row: _relative(row['total_words_f'], row['words_added_g_f']), axis=1)
    df['words_deleted_g_f_relative'] = df.apply(
        lambda row: _relative(row['total_words_f'], row['words_deleted_g_f']), axis=1)
    return df


def _relative(total, changes):
    if total == 0:
        return 0
    print(total, changes)
    return (changes) / total