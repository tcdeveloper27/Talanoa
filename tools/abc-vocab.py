#!/usr/bin/env python3
"""Choose the everyday words the ABC page can say in the board's own voice.

The words on the board are always included (tools/abc-voices.py finds them in library.js). This
picks the rest and writes them to tools/abc-common-words.txt, one per line:

  1. the most common English words (wordfreq; its English list leans on film and TV subtitles, so
     it is everyday talk);
  2. everyday things that are a little rarer, from WordNet, if they are still fairly common words:
     foods, drinks, animals, toys, clothes, body parts, places, vehicles, games, sports, holidays...
  3. other forms of those words and of the board's words (eggs, dogs, swimming, watched), when
     they are common words in their own right.

Swearing and slurs are left out (a list of them, plus WordNet's "vulgar"/"slur" labels), so the
keyboard spells those out instead of saying them. Names and other words of your own go in
tools/abc-added-words.txt; this script never touches that file.

It needs `wordfreq` and `nltk` (the GPU worker on NORMANDY has them), WordNet's files and the
list of words to leave out:
    TALANOA_WORDNET=<folder holding corpora/wordnet/> TALANOA_LEAVE_OUT=<JSON list> python tools/abc-vocab.py
It prints only counts and a few checks, never the lists.
"""
import json, os, re, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import build  # noqa: E402

ROOT = build.ROOT
OUT = os.path.join(ROOT, 'tools', 'abc-common-words.txt')
COMMON = 4000        # how many of the most common words
FORMS_ZIPF = 3.2     # how common another form of a word must be (eggs, swimming), on wordfreq's Zipf
                     # scale: 3 = once in a million words, 4 = ten times
WORD = re.compile(r"[a-z]+(?:'[a-z]+)?")
# The everyday kinds of thing (WordNet synsets) and how common a word must be to come in with them.
# Food comes first: it's what gets asked for most.
THINGS = [
    (2.8, ['food.n.01', 'food.n.02', 'beverage.n.01', 'dish.n.02', 'edible_fruit.n.01', 'vegetable.n.01',
           'dessert.n.01', 'baked_goods.n.01', 'candy.n.01', 'sandwich.n.01', 'snack_food.n.01',
           'condiment.n.01', 'meal.n.01']),
    (3.2, ['toy.n.01', 'game.n.01', 'game.n.02', 'sport.n.01', 'clothing.n.01', 'footwear.n.02', 'headdress.n.01',
           'jewelry.n.01', 'body_part.n.01', 'room.n.01', 'mercantile_establishment.n.01', 'restaurant.n.01',
           'holiday.n.01', 'chromatic_color.n.01', 'achromatic_color.n.01', 'feeling.n.01', 'relative.n.01',
           'health_professional.n.01', 'weather.n.01', 'atmospheric_phenomenon.n.01', 'toiletry.n.01',
           'medicine.n.02', 'illness.n.01', 'symptom.n.01', 'injury.n.01', 'time_unit.n.01',
           'day_of_the_week.n.01', 'calendar_month.n.01', 'season.n.02', 'music_genre.n.01', 'dance.n.01',
           'american_state.n.01']),
    (3.5, ['animal.n.01', 'vehicle.n.01', 'building.n.01', 'facility.n.01', 'worker.n.01',
           'musical_instrument.n.01', 'furniture.n.01', 'home_appliance.n.01', 'electronic_equipment.n.01',
           'flower.n.01', 'tree.n.01', 'container.n.01', 'tableware.n.01', 'kitchen_utensil.n.01',
           'geological_formation.n.01', 'body_of_water.n.01', 'show.n.03', 'broadcast.n.02']),
]
ALSO = ['nugget', 'nuggets']          # everyday words WordNet files under something else
OFFENSIVE = ('vulgarism', 'obscenity', 'ethnic_slur', 'disparagement', 'profanity')


def forms(w):
    """Other forms of a word: plurals / -s, -ing, -ed (candidates only; wordfreq decides what's real)."""
    out = {w + 's', w + 'es', w + 'ing', w + 'ed'}
    if w.endswith('y') and len(w) > 2 and w[-2] not in 'aeiou':
        out |= {w[:-1] + 'ies', w[:-1] + 'ied'}
    if w.endswith('e'):
        out |= {w[:-1] + 'ing', w + 'd'}
    if len(w) >= 3 and w[-1] not in 'aeiouwxy' and w[-2] in 'aeiou' and w[-3] not in 'aeiou':
        out |= {w + w[-1] + 'ing', w + w[-1] + 'ed'}          # swim -> swimming, stop -> stopped
    if w.endswith('f'):
        out.add(w[:-1] + 'ves')
    if w.endswith('fe'):
        out.add(w[:-2] + 'ves')
    return out


def bases(w):
    """The words this could be a form of (so a plural of a left-out word is left out too)."""
    out = {w}
    for suf, rep in (('ies', 'y'), ('ied', 'y'), ('ves', 'f'), ('ves', 'fe'), ('es', ''), ('s', ''),
                     ('ing', ''), ('ing', 'e'), ('ed', ''), ('ed', 'e'), ('d', '')):
        if w.endswith(suf) and len(w) > len(suf) + 1:
            b = w[:len(w) - len(suf)] + rep
            out.add(b)
            if len(b) >= 3 and b[-1] == b[-2]:
                out.add(b[:-1])                                 # swimming -> swimm -> swim
    return out


def main():
    from wordfreq import top_n_list, zipf_frequency
    wn_dir = os.environ.get('TALANOA_WORDNET')
    leave_path = os.environ.get('TALANOA_LEAVE_OUT')
    if not wn_dir or not leave_path:
        sys.exit('Set TALANOA_WORDNET and TALANOA_LEAVE_OUT (see the top of this file).')
    import nltk
    nltk.data.path.insert(0, wn_dir)                  # NLTK only reads files inside its data folders
    from nltk.corpus import wordnet as wn
    leave = {x.strip().lower() for x in json.load(open(leave_path, encoding='utf-8')) if ' ' not in x.strip()}

    def zipf(w):
        return zipf_frequency(w, 'en')

    def offensive(w):
        if bases(w) & leave:
            return True
        # WordNet's labels: left out only if every meaning of the word is labelled (so "taco" stays)
        syns = [s for s in wn.synsets(w) if any(l.name().lower() == w for l in s.lemmas())]
        return bool(syns) and all(any(d.name().split('.')[0] in OFFENSIVE for d in s.usage_domains()) for s in syns)

    def ok(w):
        return bool(WORD.fullmatch(w)) and (len(w) > 1 or w in ('a', 'i')) and not offensive(w)

    board = set(build.abc_board_words(build.load_library()).values())

    # 1. the most common words
    common = []
    for w in top_n_list('en', COMMON * 3):
        if ok(w):
            common.append(w)
            if len(common) >= COMMON:
                break
    # 2. everyday things
    things = {w for w in ALSO if ok(w)}
    for least, names in THINGS:
        for name in names:
            try:
                root = wn.synset(name)
            except Exception:
                print(f'  (no WordNet kind {name})')
                continue
            for s in [root] + list(root.closure(lambda x: x.hyponyms() + x.instance_hyponyms())):
                for l in s.lemmas():
                    w = l.name().lower()
                    if '_' not in w and '-' not in w and ok(w) and zipf(w) >= least:
                        things.add(w)
    # 3. other forms
    base = set(common) | things | board
    more = set()
    for w in base:
        for f in forms(w):
            if f not in base and ok(f) and zipf(f) >= FORMS_ZIPF:
                more.add(f)

    words = sorted(set(common) | things | more)
    head = ['# Everyday words the ABC page can say in the board\'s own voice (besides the words on the',
            '# board itself). Made by tools/abc-vocab.py: do not edit by hand, re-run it. Your own words',
            '# (names, favourite things) go in tools/abc-added-words.txt.',
            '# Chosen with wordfreq (Robyn Speer; its data is CC BY-SA 4.0, so this list is too) and',
            '# WordNet 3.0 (Princeton University).']
    open(OUT, 'w', encoding='utf-8', newline='\n').write('\n'.join(head + words) + '\n')
    print(f'common {len(common)}, things {len(things)} ({len(things - set(common))} not already common), '
          f'other forms {len(more)}; total {len(words)}; not on the board {len(set(words) - board)}')
    probe = ['eggs', 'pancakes', 'waffles', 'tacos', 'nuggets', 'burrito', 'cereal', 'swimming', 'dogs', 'grandma',
             'christmas', 'utah', 'hungry', 'tired', 'bathroom']
    print('checks: ' + ', '.join(f'{p} {"yes" if p in words else "no"}' for p in probe))


if __name__ == '__main__':
    main()
