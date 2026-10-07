#!/usr/bin/env python3
"""Make the ABC page's letters and words in every natural voice, so the ABC page talks in the
same voice as the rest of the board.

Run from the repo root after the words on the board or in the word lists change (it is NOT run
by GitHub; until it is re-run, a new word is simply spelled out letter by letter on the ABC page):

    python3 tools/abc-voices.py                 # make what's missing
    python3 tools/abc-voices.py michael heart   # only these voices (the others are kept as they are)
    python3 tools/abc-voices.py --side-by-side=3   # every voice, three at a time, one process each (GPU)
    TALANOA_ASR="node /path/to/asr.js --model=small.en" python3 tools/abc-voices.py   # and check by ear

A voice in LIST_VOICES (Michael) is thousands of clips, so run it on a GPU, with the recogniser kept
loaded (on VM 100: normandy-gpu, one line):
    normandy-gpu run -e TALANOA_WHISPER=small.en -e TALANOA_WHISPER_DIR=W:/gpu-worker/models/whisper -- python tools/abc-voices.py michael
Then run tools/build.py, so the app picks up the new words (GitHub doesn't run this script).

What it makes, for each voice in tools/build.py:
  voices/<voice>/abc/letter-a.mp3 ... letter-z.mp3   each letter's name ("ay", "bee", ...)
  voices/<voice>/abc/w-<word>.mp3                    every word on the board; for the voices in LIST_VOICES
                                                     (Michael) also every word in tools/abc-common-words.txt
                                                     (everyday words, made by tools/abc-vocab.py) and in
                                                     tools/abc-added-words.txt (names and words of your own)
  voices/abc.json                                    the list tools/build.py turns into what the app reads

Why it's more than "say the letter": Kokoro's voices put a stray sound in front of a very short
utterance that starts with a vowel (Michael says E as "Lee", S as "Yes"). Full sentences are
fine. So each word is made a few ways (as a one-word sentence; on its own; as the first word of a
longer sentence, cut out at the pause; with the stray start trimmed; slower). With a recogniser
(TALANOA_WHISPER=<model>, kept loaded, or TALANOA_ASR=<command>), the first version heard
correctly is kept; if none is, the closest one for a word, the first one for a letter. Without
a recogniser, the first version is kept.
"""
import hashlib, io, json, os, re, subprocess, sys, tempfile, time

import numpy as np
from concurrent.futures import ThreadPoolExecutor

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


# The recogniser writes numbers as digits ("4th" for "fourth")
NUMBERS = dict(zip('0 1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 16 17 18 19 20 30 40 50 100'.split(),
                   'zero one two three four five six seven eight nine ten eleven twelve thirteen fourteen fifteen '
                   'sixteen seventeen eighteen nineteen twenty thirty forty fifty hundred'.split()))
NUMBERS.update(zip('1st 2nd 3rd 4th 5th 6th 7th 8th 9th 10th'.split(),
                   'first second third fourth fifth sixth seventh eighth ninth tenth'.split()))


def norm(s):
    words = re.sub(r"[^a-z0-9' ]+", ' ', s.lower().replace('-', ' ')).split()
    return ' '.join(NUMBERS.get(w, w) for w in words).replace("'", '')


key = build.abc_key
WORD_LISTS = ['tools/abc-common-words.txt', 'tools/abc-added-words.txt']
# Voices that also say the lists' ~9,000 everyday words; the others say the board's words and spell the rest.
# Each list voice is ~45 min on NORMANDY's GPU and ~54 MB on the website, so Tim keeps it to Michael (2026-10-05).
LIST_VOICES = ['michael']


def list_words():
    """The words in the word lists (one per line, # starts a note): key -> spoken form."""
    found = {}
    for rel in WORD_LISTS:
        path = os.path.join(ROOT, rel)
        if not os.path.exists(path):
            continue
        for line in open(path, encoding='utf-8'):
            w = line.split('#', 1)[0].strip()
            k = key(w)
            if k and k not in found:
                found[k] = w
    return found


def all_words(lib):
    """The board's words first (they say it the board's way), then the lists'."""
    words = build.abc_board_words(lib)
    for k, w in list_words().items():
        words.setdefault(k, w)
    return words


def distance(a, b):
    """How many letters differ (edit distance)."""
    prev = list(range(len(b) + 1))
    for i, ca in enumerate(a, 1):
        cur = [i]
        for j, cb in enumerate(b, 1):
            cur.append(min(prev[j] + 1, cur[j - 1] + 1, prev[j - 1] + (ca != cb)))
        prev = cur
    return prev[-1]


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
    Each is a (name, function) so a version is only made if the ones before it weren't heard right.
    "dot" is the word with a full stop after it, said as a sentence: it fixes most words that get a
    stray sound in front ("space" heard as "a space"), so it comes first (2026-10-05)."""
    def make(text, speed=build.SPEED):
        a, _ = kokoro.create(text, voice=voice, speed=speed, lang=lang, is_phonemes=True)
        return np.asarray(a, dtype=np.float32)
    cut = ('cut', lambda: first_word(make(phonemes + CARRIER)))
    said = [('dot', lambda: make(phonemes + '.')), ('plain', lambda: make(phonemes))]
    ways = [cut] + said if vowel_first else said + [cut]
    return ways + [('trim', lambda: trimmed(make(phonemes))), ('slow', lambda: make(phonemes, 0.85))]


def mp3(audio, dest):
    import soundfile as sf
    import imageio_ffmpeg
    buf = io.BytesIO()
    sf.write(buf, build.finish(audio, SR), SR, format='WAV', subtype='PCM_16')
    subprocess.run([imageio_ffmpeg.get_ffmpeg_exe(), '-loglevel', 'error', '-y', '-f', 'wav', '-i', 'pipe:0',
                    '-ac', '1', '-ar', '24000', '-codec:a', 'libmp3lame', '-b:a', '48k', dest],
                   input=buf.getvalue(), check=True)


_whisper = None
_LOWPASS = None


def to_16k(a):
    """24 kHz -> 16 kHz for the recogniser: up 2, low-pass at 7.6 kHz, down 3 (numpy only)."""
    global _LOWPASS
    if _LOWPASS is None:
        n = np.arange(-64, 65)
        fc = 7600 / 48000
        _LOWPASS = (np.sinc(2 * fc * n) * 2 * fc * np.hamming(len(n))).astype(np.float32)
    up = np.zeros(len(a) * 2, dtype=np.float32)
    up[::2] = a * 2
    return np.convolve(up, _LOWPASS, mode='same')[::3].astype(np.float32)


def listen(files):
    """Ask the recogniser what each file says: {path: text}. Empty if there's no recogniser.
    TALANOA_WHISPER=<model> (e.g. small.en, with faster-whisper on the GPU) keeps one recogniser loaded
    for the whole run, which is far faster for thousands of words than starting TALANOA_ASR (a
    program given the file names) again and again; TALANOA_WHISPER_DIR is where its models are kept."""
    global _whisper
    if os.environ.get('TALANOA_WHISPER') and files:
        import soundfile as sf
        from faster_whisper import WhisperModel
        name = os.environ['TALANOA_WHISPER']
        if _whisper is None:
            try:
                _whisper = WhisperModel(name, device='cuda', compute_type='float16',
                                        download_root=os.environ.get('TALANOA_WHISPER_DIR'))
            except Exception as e:                     # the GPU is full: slower, but carry on
                print(f'  (recogniser on the CPU: {e})', flush=True)
                _whisper = WhisperModel(name, device='cpu', compute_type='int8',
                                        download_root=os.environ.get('TALANOA_WHISPER_DIR'))
        pad, heard = np.zeros(8000, dtype=np.float32), {}   # half a second each side: short clips are heard better
        for f in files:
            try:
                a, sr = sf.read(f, dtype='float32')
                assert sr == SR, sr
                segs, _ = _whisper.transcribe(np.concatenate([pad, to_16k(a), pad]),
                                              language=None if name.endswith('.en') else 'en', beam_size=1, vad_filter=False)
                heard[f] = ' '.join(x.text.strip() for x in segs).strip()
            except Exception as e:
                heard[f] = 'ERROR ' + str(e)
        return heard
    cmd = os.environ.get('TALANOA_ASR')
    if not cmd or not files:
        return {}
    heard, i = {}, 0
    while i < len(files):
        # a few hundred at a time: a command line has a length limit (about 32,000 characters on Windows)
        part, size = [], 0
        while i < len(files) and (not part or size + len(files[i]) < 24000):
            part.append(files[i])
            size += len(files[i]) + 3
            i += 1
        res = subprocess.run(cmd.split() + part, capture_output=True, text=True)
        for line in res.stdout.splitlines():
            if '\t' in line:
                f, t = line.split('\t', 1)
                heard[f] = t
    return heard


def locked(path):
    """A lock file, so voices made side by side don't write voices/abc.json at the same moment."""
    lock = path + '.lock'
    for _ in range(1200):
        try:
            os.close(os.open(lock, os.O_CREAT | os.O_EXCL | os.O_WRONLY))
            return lock
        except FileExistsError:
            time.sleep(0.1)
    sys.exit(f'{lock} is stuck (a run that crashed?): delete it and run again')


def main():
    only = [a for a in sys.argv[1:] if not a.startswith('-')]
    side = next((a for a in sys.argv if a.startswith('--side-by-side')), None)
    if side:
        # one process per voice, a few at a time (--side-by-side=3; more than the GPU's memory holds is
        # much slower, not faster); each saves its own voice
        at_once = int(side.split('=')[1]) if '=' in side else 3
        names, running, worst = only or [v['id'] for v in build.VOICES], [], 0
        while names or running:
            while names and len(running) < at_once:
                running.append(subprocess.Popen([sys.executable, os.path.abspath(__file__), names.pop(0)]))
            time.sleep(2)
            for p in [p for p in running if p.poll() is not None]:
                worst = max(worst, p.returncode)
                running.remove(p)
        sys.exit(worst)
    import soundfile as sf
    from kokoro_onnx import Kokoro
    lib = build.load_library()
    words, board = all_words(lib), build.abc_board_words(lib)
    model = [build.download(build.KOKORO_BASE + f, os.path.join(build.CACHE, 'kokoro', f)) for f in build.KOKORO_FILES]
    if os.environ.get('ONNX_PROVIDER') == 'CUDAExecutionProvider':
        # on the GPU, take memory only as needed: by default each run grabs several GB, and a few voices
        # side by side then fill the card and crawl
        import onnxruntime as rt
        sess = rt.InferenceSession(model[0], providers=[('CUDAExecutionProvider', {'arena_extend_strategy': 'kSameAsRequested'}),
                                                        'CPUExecutionProvider'])
        kokoro = Kokoro.from_session(sess, model[1])
    else:
        kokoro = Kokoro(*model)
    tok = kokoro.tokenizer
    man_path = os.path.join(ROOT, 'voices', 'abc.json')
    old = json.load(open(man_path)) if os.path.exists(man_path) else {}
    todo_voices = [v for v in build.VOICES if not only or v['id'] in only]
    out = {'method': METHOD, 'letters': dict(old.get('letters', {})), 'words': dict(old.get('words', {})),
           'unsure': dict(old.get('unsure', {})), 'stamps': dict(old.get('stamps', {}))}
    print(f'ABC page: 26 letters and {len(board)} board words in {", ".join(v["name"] for v in todo_voices)}; '
          f'{len(words)} words in all for {", ".join(v["name"] for v in todo_voices if v["id"] in LIST_VOICES) or "none of them"}',
          flush=True)
    for v in todo_voices:
        lang = 'en-gb' if v['kokoro'].startswith('b') else 'en-us'
        vdir = os.path.join(ROOT, 'voices', v['id'], 'abc')
        os.makedirs(vdir, exist_ok=True)
        items = [('letter', c, 'letter-' + c.lower(), tok.phonemize(c, 'en-us')) for c in LETTER_OK]
        vwords = words if v['id'] in LIST_VOICES else board
        items += [('word', k, 'w-' + k, tok.phonemize(spoken, lang)) for k, spoken in vwords.items()]
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
            asr = bool(os.environ.get('TALANOA_WHISPER') or os.environ.get('TALANOA_ASR'))
            for rnd in range(5):
                t_round = time.time()
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
                t_made = time.time()
                heard = listen(batch)
                print(f'  {v["name"]}: round {rnd + 1}: made {len(batch)} in {t_made - t_round:.0f} s, '
                      f'checked them by ear in {time.time() - t_made:.0f} s', flush=True)
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
            encode = []
            for kind, item, name, ph, stamp, dest in todo:
                pick = picked.get(name)
                if pick is None:
                    if not made[name]:
                        continue
                    pick = made[name][0]
                    if asr and kind == 'word':
                        # nothing heard exactly right (the recogniser often drops a final s on its own):
                        # keep the version heard closest to the word, the earlier one if it's a tie
                        heard_as = [key(norm(m[3])) if len(m) > 3 else '' for m in made[name]]
                        best = min(range(len(made[name])), key=lambda i: (distance(heard_as[i], key(item)), i))
                        pick = made[name][best]
                    if asr:
                        unsure.append(f'{item} (heard: {", ".join(m[3] if len(m) > 3 else "?" for m in made[name])}; kept: {pick[0]})')
                encode.append((pick[2], dest))
                (letters if kind == 'letter' else wmap)[item] = f'voices/{v["id"]}/abc/{name}.mp3?v={stamp}'
                out['stamps'].setdefault(v['id'], {})[name] = stamp
            t_enc = time.time()
            with ThreadPoolExecutor(8) as pool:                # 8 encoders at once: each is its own program
                list(pool.map(lambda job: mp3(*job), encode))
            print(f'  {v["name"]}: saved {len(encode)} mp3s in {time.time() - t_enc:.0f} s', flush=True)
        # forget clips of words no longer on the board or in the lists
        keep = {os.path.basename(u.split('?')[0]) for u in list(letters.values()) + list(wmap.values())}
        for f in os.listdir(vdir):
            if f.endswith('.mp3') and f not in keep:
                os.remove(os.path.join(vdir, f))
        out.setdefault('stamps', {})[v['id']] = {n: s for n, s in out['stamps'].get(v['id'], {}).items() if n + '.mp3' in keep}
        out['letters'][v['id']], out['words'][v['id']] = letters, dict(sorted(wmap.items()))
        # doubtful clips: this run's, plus the earlier notes for clips kept as they were (not remade, still used)
        remade, kept = {t[1] for t in todo}, set(letters) | set(wmap)
        unsure = [u for u in (old.get('unsure') or {}).get(v['id'], [])
                  if u.split(' (heard')[0] not in remade and u.split(' (heard')[0] in kept] + unsure
        out['unsure'][v['id']] = unsure
        print(f'  {v["name"]}: {len(letters)} letters, {len(wmap)} words'
              + (f'; not confirmed by ear: {len(unsure)}' if unsure else ''), flush=True)
        # save after every voice, re-reading the file so voices made side by side don't overwrite each other
        lock = locked(man_path)
        try:
            cur = json.load(open(man_path)) if os.path.exists(man_path) else {}
            for part in ('letters', 'words', 'unsure', 'stamps'):
                cur.setdefault(part, {})[v['id']] = out[part][v['id']]
            cur['method'] = METHOD
            json.dump(cur, open(man_path, 'w'), indent=0, ensure_ascii=False, sort_keys=True)
        finally:
            os.remove(lock)
    print('  wrote voices/abc.json; now run tools/build.py so the app picks them up')


if __name__ == '__main__':
    main()
