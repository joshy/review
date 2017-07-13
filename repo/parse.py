import os
import sys

from typing import Dict, List

contexts = ('Anamnese', 'Technik', 'Fragestellung', 'Befund', 'Beurteilung')


def parse(text: List[str]) -> Dict[str, str]:
    """ Parses a ris report into sections.
    A few assumptions are made:
     * A new line ends any section, which holds to be true for most of the
       reports
    """
    section = ''
    values = [] # type: List[str]
    data = {}
    for line in text:
        if line and line.startswith(contexts):
            # Since we know filter(line.startswith, contexts) will get exactly
            # one hit, we just pull the hit using next
            current_section = next(filter(line.startswith, contexts))
            # if there is no empty line save the current context to data
            if section and section != current_section:
                data[section] = ''.join(values)
            section = current_section
        elif line and section:
            values.append(line)
        elif not line:
            data[section] = ''.join(values)
            section = ''
    return data