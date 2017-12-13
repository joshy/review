import re
from typing import Dict, Tuple

import pydiff

from repo.converter import rtf_to_text

_word_split_re = re.compile(r'(\s+|[^\w\s]+)', re.UNICODE)


def _words_deleted_filter(change: Dict[str, str]) -> Dict[str, str]:
    return change if 'removed' in change and change['removed']==True else None


def _words_added_filter(change: Dict[str, str]) -> Dict[str, str]:
    return change if 'added' in change and change['added']==True else None


def _flatten(l):
    return [item for sublist in l for item in sublist]


def _tokenize(string):
    return [token for token in _word_split_re.split(string) if token]


def _all_deletions(changes):
    deletions = [x for x in [_words_deleted_filter(y) for y in changes]
                 if x is not None]
    values = [_tokenize(entry['value']) for entry in deletions]
    v = list(filter(str.strip, _flatten(values)))
    return len(v)


def _all_additions(changes):
    additions = [x for x in [_words_added_filter(y) for y in changes]
                 if x is not None]
    values = [_tokenize(entry['value']) for entry in additions]
    v = list(filter(str.strip, _flatten(values)))
    return len(v)


def _jaccard(before, after):
    before=before.split()
    after=after.split()
    union = list(set(after+before))
    intersection = list(set(before) - (set(before)-set(after)))
    jaccard = round(float(len(intersection))/len(union), 3)
    return jaccard


def _diff(before, after):
    j = _jaccard(before, after)
    changes = pydiff.diff_words(before, after)
    deletions = _all_deletions(changes)
    additions = _all_additions(changes)
    return {'jaccard': j, 'additions': additions, 'deletions': deletions}


def diffs(row) -> Tuple[Dict[str, str], Dict[str, str]]:
    befund_s = rtf_to_text(row['befund_s'])
    befund_g = rtf_to_text(row['befund_g'])
    befund_f = rtf_to_text(row['befund_f'])
    compare_s_g = _diff(befund_s, befund_g)
    compare_f_g = _diff(befund_g, befund_f)
    return compare_s_g, compare_f_g
