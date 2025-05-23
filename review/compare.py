import logging
import re
import time
from typing import Dict, Tuple

import pydiff
from review.hedging import highlight_hedging
from striprtf.striprtf import rtf_to_text

_word_split_re = re.compile(r"(\s+|[^\w\s]+)", re.UNICODE)


def _words_deleted_filter(change: Dict[str, str]) -> Dict[str, str]:
    return change if "removed" in change and change["removed"] == True else None


def _words_added_filter(change: Dict[str, str]) -> Dict[str, str]:
    return change if "added" in change and change["added"] == True else None


def _flatten(l):
    return [item for sublist in l for item in sublist]


def _tokenize(string):
    return [token for token in _word_split_re.split(string) if token]


def _total_length(report) -> int:
    if report is None:
        return 0
    return len(list(filter(str.strip, report.split(" "))))


def _all_deletions(changes):
    deletions = [
        x for x in [_words_deleted_filter(y) for y in changes] if x is not None
    ]
    values = [_tokenize(entry["value"]) for entry in deletions]
    v = list(filter(str.strip, _flatten(values)))
    return len(v)


def _all_additions(changes):
    additions = [x for x in [_words_added_filter(y) for y in changes] if x is not None]
    values = [_tokenize(entry["value"]) for entry in additions]
    v = list(filter(str.strip, _flatten(values)))
    return len(v)


def _jaccard(before, after):
    before = before.split()
    after = after.split()
    union = list(set(after + before))
    intersection = list(set(before) - (set(before) - set(after)))
    try:
        jaccard = round(float(len(intersection)) / len(union), 3)
        return jaccard
    except ZeroDivisionError:
        return 0


def _diff(before, after):
    j = _jaccard(before, after)
    changes = pydiff.diff_words(before, after)
    deletions = _all_deletions(changes)
    additions = _all_additions(changes)
    return {"jaccard": j, "additions": additions, "deletions": deletions}


def _extract_section(befund):
    keyword = "Befund"
    if keyword in befund:
        parts = befund.partition(keyword)
        befund = "".join([parts[1], parts[2]])
    return befund


def diffs(row) -> Tuple[Dict[str, str], Dict[str, str], Dict[str, int], str]:
    s = time.time()
    try:
        report_s = (
            rtf_to_text(row["report_s"], encoding="iso8859-1", errors="ignore")
            if row["report_s"] is not None
            else ""
        )
        report_v = (
            rtf_to_text(row["report_v"], encoding="iso8859-1", errors="ignore")
            if row["report_v"] is not None
            else ""
        )
        report_f = (
            rtf_to_text(row["report_f"], encoding="iso8859-1", errors="ignore")
            if row["report_f"] is not None
            else ""
        )
        report_s = _extract_section(report_s)
        report_v = _extract_section(report_v)
        report_f = _extract_section(report_f)
        compare_s_f = _diff(report_s, report_f)
        compare_v_f = _diff(report_v, report_f)
        total_lengths = {
            "total_words_s": _total_length(report_s),
            "total_words_v": _total_length(report_v),
            "total_words_f": _total_length(report_f),
        }
        e = time.time()
        logging.debug("Single row diff calculation took %s", e - s)
        return compare_s_f, compare_v_f, total_lengths, row["accession_number"]
    except UnicodeDecodeError:
        logging.error(f"Can't decode row with acc: {row['accession_number']}")
        return None


def hedgings(row):
    s = time.time()
    try:
        report_s = (
            rtf_to_text(row["report_s"], encoding="iso8859-1", errors="ignore")
            if row["report_s"] is not None
            else ""
        )
        report_v = (
            rtf_to_text(row["report_v"], encoding="iso8859-1", errors="ignore")
            if row["report_v"] is not None
            else ""
        )
        report_f = (
            rtf_to_text(row["report_f"], encoding="iso8859-1", errors="ignore")
            if row["report_f"] is not None
            else ""
        )
        _, hedging_count_s = highlight_hedging(report_s)
        _, hedging_count_v = highlight_hedging(report_v)
        _, hedging_count_f = highlight_hedging(report_f)
        e = time.time()
        logging.debug("Single row hedging calculation took %s", e - s)
        return {
            "hedging_count_s": hedging_count_s,
            "hedging_count_v": hedging_count_v,
            "hedging_count_f": hedging_count_f,
            "acc": row["accession_number"],
        }
    except UnicodeDecodeError:
        logging.error(
            f"Can't calculate hedging count on acc: {row['accession_number']}"
        )
        return None
