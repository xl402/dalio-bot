import re
import difflib
from testprompts import stuff
import json


def process_lines(lines):
    pattern = r'\d{1,20}\.\d{1,20} '
    regexp = re.compile(pattern)
    indices = []
    for idx, line in enumerate(lines):
        if regexp.search(line):
            indices.append(idx)
    out = {}
    for idx0, idx1 in zip(indices[:-1], indices[1:]):
        title = lines[idx0].split('\n')[0]
        title = re.sub(pattern, '', title)
        out[title] = [title + '\n'] + lines[idx0+1:idx1]
    return out


if __name__ == '__main__':
    with open('ray-principles-cleanish.txt') as f:
        raw_lines = f.readlines()

    lines = [l for l in raw_lines if len(l) > 1]
    out = process_lines(lines)
    principles_json = json.dumps(out)
    with open("principles_to_chapter.json", "w") as f:
        f.write(principles_json)
        f.close()
    # testlines = stuff.split('\n')

    # errors = []
    # for t in testlines:
    #     meh = difflib.get_close_matches(t, list(out.keys()))
    #     if len(meh) == 0:
    #         errors.append(t)
