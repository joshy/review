import os


def write(accession_number, report):
    if report is not None:
        file_dir = "reports"
        file_name = "ris-report-" + str(accession_number) + ".rtf"
        dest = os.path.join(file_dir, file_name)
        report_file = open(dest, 'w')
        report_file.write(report)
        return dest
    else:
        return None

