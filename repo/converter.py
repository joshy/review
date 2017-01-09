import subprocess


def convert(report_file):
    completed = subprocess.run(['unrtf', '--html', report_file], stdout=subprocess.PIPE)
    return completed.stdout.decode('UTF-8')

