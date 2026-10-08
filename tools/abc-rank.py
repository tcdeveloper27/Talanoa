#!/usr/bin/env python3
"""Rank the ABC page's words by how common they are, for the word suggestions (Settings → Talking in
sentences → Word suggestions on the ABC page). Writes abc-rank.txt: one word per line, most
common first. The app only suggests words the chosen voice says whole, and words he has spoken before
come first anyway, so this only decides the order of the rest.

Needs wordfreq (in the GPU worker's Python on NORMANDY; on VM 100: normandy-gpu, one line):
    normandy-gpu run -- python tools/abc-rank.py
Re-run it after the word lists change (tools/abc-vocab.py, tools/abc-added-words.txt, new tiles), then
tools/build.py. Never print the list in a session.
"""
import json, os, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import build  # noqa: E402
from wordfreq import zipf_frequency

ROOT = build.ROOT


def main():
    lib = build.load_library()
    words = set(build.abc_board_words(lib))
    for v in build.VOICES:                             # every word any voice can say whole
        path = os.path.join(ROOT, 'voices', v['id'], 'abc', 'words.json')
        if os.path.exists(path):
            words |= set(json.load(open(path, encoding='utf-8')))
    ranked = sorted(words, key=lambda w: (-zipf_frequency(w, 'en'), w))
    out = os.path.join(ROOT, 'abc-rank.txt')
    with open(out, 'w', encoding='utf-8', newline='\n') as f:
        f.write('# Made by tools/abc-rank.py (wordfreq): the ABC page words, most common first. Do not edit by hand.\n')
        f.write('\n'.join(ranked) + '\n')
    print(f'wrote {out}: {len(ranked)} words')


if __name__ == '__main__':
    main()
