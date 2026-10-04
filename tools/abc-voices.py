#!/usr/bin/env python3
"""Make the ABC page's letters and words in every natural voice, so the ABC page talks in the
same voice as the rest of the board.

Run from the repo root after the words on the board change (it is NOT run by GitHub; until it
is re-run, a new word is simply spelled out letter by letter on the ABC page):

    python3 tools/abc-voices.py                 # make what's missing
    python3 tools/abc-voices.py michael heart   # only these voices (the others are kept as they are)
    TALANOA_ASR="node /path/to/asr.js --model=small.en" python3 tools/abc-voices.py   # and check by ear

What it makes, for each voice in tools/build.py:
  voices/<voice>/abc/letter-a.mp3 ... letter-z.mp3   each letter's name ("ay", "bee", ...)
  voices/<voice>/abc/w-<word>.mp3                    every word that appears on the board
  voices/abc.json                                    the list the app reads (via assets.js)

Why it's more than "say the letter": Kokoro's voices put a stray sound in front of a very short
utterance that starts with a vowel (Michael says E as "Lee", S as "Yes"). Full sentences are
fine. So each word is made a few ways (on its own; as the first word of a longer sentence, cut
out at the pause; with the stray start trimmed) and, if TALANOA_ASR names a speech recogniser,
the first version it hears correctly is kept. Without one, the sentence-cut version is kept.
"""
import hashlib, io, json, os, re, subprocess, sys, tempfile

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import build  # noqa: E402

ROOT = build.ROOT
SR = 24000
CARRIER = '. tˈɛn kˈæts ɑːɹ ɪn ðə bˈɑːks.'     # "<word>. Ten cats are in the box."
METHOD = 'abc-v1'                                # change to make everything again

# What a recogniser may write for each letter's name
LETTER_OK = {
    'A': ['a', 'ay'], 'B': ['b', 'be', 'bee'], 'C': ['c', 'see', 'sea'], 'D': ['d', 'dee'], 'E': ['e', 'ee'],
    'F': ['f', 'ef', 'eff'], 'G': ['g', 'gee'], 'H': ['h', 'aitch'], 'I': ['i', 'eye', 'aye'], 'J': ['j', 'jay'],
    'K': ['k', 'kay'], 'L': ['l', 'el', 'ell', 'elle'], 'M': ['m', 'em'], 'N': ['n', 'en'], 'O': ['o', 'oh', 'owe'],
    'P': ['p', 'pee', 'pea'], 'Q': ['q', 'cue', 'queue'], 'R': ['r', 'are', 'ar'], 'S': ['s', 'es', 'ess'],
    'T': ['t', 'tea', 'tee'], 'U': ['u', 'you'], 'V': ['v', 'vee'], 'W': ['w', 'double u', 'double you'],
    'X': ['x', 'ex'], 'Y': ['y', 'why'], 'Z': ['z', 'zee', 'zed']}
# Words that sound alike: either spelling counts as heard right
SOUNDS_ALIKE = [('to', 'too', 'two'), ('for', 'four'), ('no', 'know'), ('i', 'eye'), ('be', 'bee'),
                ('see', 'sea'), ('right', 'write'), ('there', 'their'), ('here', 'hear'), ('one', 'won'),
                ('by', 'buy', 'bye'), ('ate', 'eight'), ('our', 'hour'), ('new', 'knew'), ('read', 'red'),
                ('wait', 'weight'), ('son', 'sun'), ('night', 'knight'), ('hi', 'high'), ('mom', 'mum')]


def norm(s):
    return ' '.join(re.sub(r"[^a-z0-9' ]+", ' ', s.lower().replace('-', ' ')).split()).replace("'", '')


def key(word):
    """How a typed word is looked up: letters only, lower case (the keyboard has no apostrophe)."""
    return re.sub(r'[^a-z]', '', word.lower())


def board_words(lib):
    """Every English word on the board (labels and sentences), plus the page names."""
    found = {}
    texts = [p['name'] for p in lib['pages']]
    for t in build.all_tiles(lib):
        if t.get('means'):
            continue                                  # the Tongan page: the keyboard can't type it
        texts += [t['label'], t.get('say') or '']
    for text in texts:
        for w in re.findall(r"[A-Za-z][A-Za-z']*", text):
            k = key(w)
            if k and k not in found:
                found[k] = w.lower()
    return found                                      # key -> spoken form ("dont" -> "don't")


def heard_ok(item, kind, text):
    t = norm(text)
    if kind == 'letter':
        return t.replace(' ', '') in [x.replace(' ', '') for x in LETTER_OK[item]]
    want = key(item)
    if t.replace(' ', '') == want:
        return True
    return any(want in group and t in group for group in SOUNDS_ALIKE)


# ------------------------------------------------------------------ making one clip several ways
def envelope(s):
    w = int(SR * 0.005)
    n = len(s) // w
    return np.array([np.sqrt(np.mean(s[i * w:(i + 1) * w] ** 2)) for i in range(n)]), w


def first_word(s):
    """The first word of "<word>. Ten cats are in the box.", cut at the pause after it."""
    e, w = envelope(s)
    if not len(e):
        return None
    m = e.max()
    loud = np.where(e > m * 0.15)[0]
    if not len(loud):
        return None
    i, n = loud[0], len(e)
    while i < n:
        if e[i] < m * 0.03:
            j = i
            while j < n and e[j] < m * 0.03:
                j += 1
            if j - i >= 8:                             # 40 ms of quiet: the word has ended
                out = s[:i * w + int(SR * 0.03)].copy()
                st = np.where(np.abs(out) > m * 0.02)[0]
                out = out[max(0, st[0] - int(SR * 0.015)):] if len(st) else out
                f = min(len(out), int(SR * 0.025))
                out[-f:] *= np.linspace(1, 0, f)
                return out if len(out) < SR * 1.3 else None
            i = j
        else:
            i += 1
    return None


def trimmed(s, frac=0.3):
    e, w = envelope(s)
    if not len(e):
        return s
    first = int(np.argmax(e > e.max() * frac))
    out = s[max(0, first * w - int(SR * 0.004)):].copy()
    f = int(SR * 0.010)
    out[:f] *= np.linspace(0, 1, f) ** 2
    return out


def versions(kokoro, phonemes, voice, lang, vowel_first):
    """Ways to make one word, best first (for words that start with a vowel, the sentence cut first).
    Each is a (name, function) so a version is only made if the ones before it weren't heard right."""
    def make(text, speed=build.SPEED):
        a, _ = kokoro.create(text, voice=voice, speed=speed, lang=lang, is_phonemes=True)
        return np.asarray(a, dtype=np.float32)
    ways = [('cut', lambda: first_word(make(phonemes + CARRIER))), ('plain', lambda: make(phonemes))]
    if not vowel_first:
        ways.reverse()
    ways += [('trim', lambda: trimmed(make(phonemes))), ('slow', lambda: make(phonemes, 0.85))]
    return ways


def mp3(audio, dest):
    import soundfile as sf
    import imageio_ffmpeg
    buf = io.BytesIO()
    sf.write(buf, build.finish(audio, SR), SR, format='WAV', subtype='PCM_16')
    subprocess.run([imageio_ffmpeg.get_ffmpeg_exe(), '-loglevel', 'error', '-y', '-f', 'wav', '-i', 'pipe:0',
                    '-ac', '1', '-ar', '24000', '-codec:a', 'libmp3lame', '-b:a', '48k', dest],
                   input=buf.getvalue(), check=True)


def listen(files):
    """Ask the recogniser what each file says: {path: text}. Empty if there's no recogniser."""
    cmd = os.environ.get('TALANOA_ASR')
    if not cmd or not files:
        return {}
    res = subprocess.run(cmd.split() + files, capture_output=True, text=True)
    heard = {}
    for line in res.stdout.splitlines():
        if '\t' in line:
            f, t = line.split('\t', 1)
            heard[f] = t
    return heard


def main():
    import soundfile as sf
    from kokoro_onnx import Kokoro
    lib = build.load_library()
    words = board_words(lib)
    model = [build.download(build.KOKORO_BASE + f, os.path.join(build.CACHE, 'kokoro', f)) for f in build.KOKORO_FILES]
    kokoro = Kokoro(*model)
    tok = kokoro.tokenizer
    man_path = os.path.join(ROOT, 'voices', 'abc.json')
    old = json.load(open(man_path)) if os.path.exists(man_path) else {}
    only = [a for a in sys.argv[1:] if not a.startswith('-')]
    todo_voices = [v for v in build.VOICES if not only or v['id'] in only]
    out = {'method': METHOD, 'letters': dict(old.get('letters', {})), 'words': dict(old.get('words', {})),
           'unsure': dict(old.get('unsure', {})), 'stamps': dict(old.get('stamps', {}))}
    print(f'ABC page: 26 letters and {len(words)} board words in {", ".join(v["name"] for v in todo_voices)}')
    for v in todo_voices:
        lang = 'en-gb' if v['kokoro'].startswith('b') else 'en-us'
        vdir = os.path.join(ROOT, 'voices', v['id'], 'abc')
        os.makedirs(vdir, exist_ok=True)
        items = [('letter', c, 'letter-' + c.lower(), tok.phonemize(c, 'en-us')) for c in LETTER_OK]
        items += [('word', k, 'w-' + k, tok.phonemize(spoken, lang)) for k, spoken in words.items()]
        letters, wmap, unsure = {}, {}, []
        with tempfile.TemporaryDirectory() as tmp:
            todo = []
            for kind, item, name, ph in items:
                stamp = hashlib.sha1(f'{METHOD}|{v["kokoro"]}|{build.SPEED}|{ph}'.encode()).hexdigest()[:10]
                dest = os.path.join(vdir, name + '.mp3')
                prev = (old.get('stamps') or {}).get(v['id'], {}).get(name)
                if prev == stamp and os.path.exists(dest):
                    (letters if kind == 'letter' else wmap)[item] = f'voices/{v["id"]}/abc/{name}.mp3?v={stamp}'
                    continue
                todo.append((kind, item, name, ph, stamp, dest))
            # round by round: make the next version of every clip not yet heard right, listen to them all
            ways = {t[2]: versions(kokoro, t[3], v['kokoro'], lang, bool(re.match(r'^[ˈˌ]?[aeiouæɑɐɒɔəɛɜɪʊʌ]', t[3])))
                    for t in todo}
            made, picked, left = {t[2]: [] for t in todo}, {}, list(todo)
            asr = bool(os.environ.get('TALANOA_ASR'))
            for rnd in range(4):
                batch = []
                for kind, item, name, ph, stamp, dest in left:
                    while ways[name]:
                        cname, fn = ways[name].pop(0)
                        a = fn()
                        if a is not None and len(a) > SR * 0.08:
                            p = os.path.join(tmp, f'{name}__{cname}.wav')
                            sf.write(p, a, SR)
                            made[name].append((cname, p, a))
                            batch.append(p)
                            break
                if not asr:
                    break                              # no recogniser: keep the first version of each
                heard = listen(batch)
                still = []
                for t in left:
                    kind, item, name = t[0], t[1], t[2]
                    last = made[name][-1] if made[name] else None
                    if last and heard_ok(item, kind, heard.get(last[1], '')):
                        picked[name] = last
                    else:
                        if last:
                            made[name][-1] = last + (heard.get(last[1], '?'),)
                        if ways[name]:
                            still.append(t)
                left = still
                if not left:
                    break
            for kind, item, name, ph, stamp, dest in todo:
                pick = picked.get(name)
                if pick is None:
                    if not made[name]:
                        continue
                    pick = made[name][0]
                    if asr:
                        unsure.append(f'{item} (heard: {", ".join(m[3] if len(m) > 3 else "?" for m in made[name])})')
                mp3(pick[2], dest)
                (letters if kind == 'letter' else wmap)[item] = f'voices/{v["id"]}/abc/{name}.mp3?v={stamp}'
                out['stamps'].setdefault(v['id'], {})[name] = stamp
        # forget clips of words no longer on the board
        keep = {os.path.basename(u.split('?')[0]) for u in list(letters.values()) + list(wmap.values())}
        for f in os.listdir(vdir):
            if f.endswith('.mp3') and f not in keep:
                os.remove(os.path.join(vdir, f))
        out.setdefault('stamps', {})[v['id']] = {n: s for n, s in out['stamps'].get(v['id'], {}).items() if n + '.mp3' in keep}
        out['letters'][v['id']], out['words'][v['id']] = letters, dict(sorted(wmap.items()))
        out['unsure'][v['id']] = unsure
        print(f'  {v["name"]}: {len(letters)} letters, {len(wmap)} words'
              + (f'; not confirmed by ear: {len(unsure)}' if unsure else ''), flush=True)
        # save after every voice, re-reading the file so voices made side by side don't overwrite each other
        cur = json.load(open(man_path)) if os.path.exists(man_path) else {}
        for part in ('letters', 'words', 'unsure', 'stamps'):
            cur.setdefault(part, {})[v['id']] = out[part][v['id']]
        cur['method'] = METHOD
        json.dump(cur, open(man_path, 'w'), indent=0, ensure_ascii=False, sort_keys=True)
    print('  wrote voices/abc.json; now run tools/build.py so the app picks them up')


if __name__ == '__main__':
    main()
