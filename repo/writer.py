import os
from typing import Optional

def write(accession_number, report):
    # str, str -> Optional[str]
    """
    Writes the report to the file system and gives back the full path.
    """
    if report is not None:
        file_dir = "reports"
        file_name = "ris-report-" + str(accession_number) + ".rtf"
        dest = os.path.join(file_dir, file_name)
        with open(dest, 'w') as report_file:
            report_file.write(report)
        return dest
    else:
        return None
