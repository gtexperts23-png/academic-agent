import re

def estimate_names(text):
    lines = text.split("\n")

    names = []

    for l in lines:
        l = l.strip()

        if len(l.split()) == 2:
            if re.match(r"^[A-Z][a-z]+ [A-Z][a-z]+$", l):
                names.append(l)

    return len(set(names))
