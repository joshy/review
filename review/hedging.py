import re

def highlight_hedging(text):
    # Define a list of regex patterns
    regex_patterns = [
        r'prominent\w{0,2}',
        r'akzentuiert\w{0,2}',
        r'angedeutet\w{0,2}',
        r'imponier\w{0,3}',
        r'(nicht\s(\w+\W+){0,5}aus(zu)?schliessen)',
        r'(kein\w{0,2}\s(?:eindeutig|gr\össer|sicher)\w{0,2})',
        r'(mit\sletzter\ssicherheit)'
    ]

    # Find matches for each regex pattern using re.findall
    highlighted_string = text
    score = 0
    for pattern in regex_patterns:
        matches = re.findall(pattern, highlighted_string)
        for match in matches:
            if type(match) is tuple:
                highlighted_string = highlighted_string.replace(match[0], '<mark>' + match[0] + '</mark>')
            else:
                highlighted_string = highlighted_string.replace(match, '<mark>' + match + '</mark>')
            score = score +  1
    return highlighted_string,score  