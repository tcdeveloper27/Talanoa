#!/usr/bin/env python3
"""Build Talanoa's pictures, natural voices and offline file list.

Run from the repo root after changing library.js:

    python3 tools/build.py

What it does
  1. Pictures: copies the 3D Fluent Emoji image for every icon in
     library.js into img/ (downloaded once from npm, MIT licence).
  2. Voices:   records every phrase with each natural voice below using
     Kokoro (open-source, Apache 2.0), saved as small MP3s in voices/.
     Only new or changed phrases are recorded again.
  3. Writes assets.js (what the app loads) and sw.js (the offline cache).

One-time setup (about 400 MB of downloads, into ~/.cache/tilertalker):
    pip install kokoro-onnx soundfile pillow imageio-ffmpeg
"""
import hashlib, io, json, os, re, subprocess, sys, tarfile, tempfile, urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CACHE = os.path.expanduser('~/.cache/tilertalker')

# The natural voices offered in Settings. First one is the default.
VOICES = [
    {'id': 'michael', 'kokoro': 'am_michael', 'name': 'Michael', 'desc': 'calm man'},
    {'id': 'fenrir',  'kokoro': 'am_fenrir',  'name': 'Fenrir',  'desc': 'deeper man'},
    {'id': 'heart',   'kokoro': 'af_heart',   'name': 'Heart',   'desc': 'warm woman'},
    {'id': 'bella',   'kokoro': 'af_bella',   'name': 'Bella',   'desc': 'bright young woman'},
    {'id': 'sarah',   'kokoro': 'af_sarah',   'name': 'Sarah',   'desc': 'friendly woman'},
    {'id': 'george',  'kokoro': 'bm_george',  'name': 'George',  'desc': 'British man'},
    {'id': 'emma',    'kokoro': 'bf_emma',    'name': 'Emma',    'desc': 'British woman'},
]
SPEED = 0.92            # a touch slower than normal speech, easier to follow
SAMPLE_TEXT = 'Hi! This is my voice.'
SPEED_TEXT = 'This is how fast I talk'

EMOJI_PKG = 'https://registry.npmjs.org/@lobehub/fluent-emoji-3d/-/fluent-emoji-3d-1.1.0.tgz'
KOKORO_BASE = 'https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/'
KOKORO_FILES = ['kokoro-v1.0.onnx', 'voices-v1.0.bin']


def slug(s):
    return re.sub(r'^-+|-+$', '', re.sub(r'[^a-z0-9]+', '-', str(s).lower()))


def load_library():
    src = open(os.path.join(ROOT, 'library.js'), encoding='utf-8').read()
    start = src.index('{', src.index('window.TT_LIBRARY'))
    try:
        return json.loads(src[start:src.rindex('}') + 1])
    except json.JSONDecodeError as e:
        line = src[:start].count('\n') + e.lineno
        sys.exit(f'library.js has a typo on or just before line {line}: {e.msg}. '
                 'Check for a missing comma or quote mark. (The last tile in a list has no comma after it.)')


def check_mom_under_dad(lib):
    """Family rule: wherever a Dad tile appears, the same tile for Mom must sit
    directly underneath it (one row down in the 4-wide grid)."""
    problems = []
    for p in lib['pages']:
        tiles = p['tiles']
        for i, t in enumerate(tiles):
            if not re.search(r'\bdad\b', t['label'] + ' ' + (t.get('say') or ''), re.I):
                continue
            want = re.sub(r'\bDad\b', 'Mom', t['label']), re.sub(r'\bdad\b', 'mom', re.sub(r'\bDad\b', 'Mom', t.get('say') or ''))
            below = tiles[i + 4] if i + 4 < len(tiles) and i % 12 < 8 else None
            if not below or (below['label'], below.get('say') or '') != want:
                problems.append(f'  page "{p["name"]}": "{t["label"]}" needs "{want[0]}" directly underneath it')
    if problems:
        sys.exit('Every Dad tile must have the matching Mom tile directly below it:\n' + '\n'.join(problems))


def all_tiles(lib):
    """Every speakable tile (core + pages) with its id, checking ids are unique."""
    tiles, seen = [], {}
    for t in lib['core'] + [t for p in lib['pages'] for t in p['tiles']]:
        tid = slug(t['label'])
        if tid in seen and seen[tid] != (t.get('say') or t['label']):
            sys.exit(f'Two different tiles are both labelled "{t["label"]}". Give one a different label.')
        seen[tid] = t.get('say') or t['label']
        tiles.append((tid, t))
    return tiles


def download(url, dest):
    if os.path.exists(dest):
        return dest
    os.makedirs(os.path.dirname(dest), exist_ok=True)
    print('  downloading', url.split('/')[-1], '...')
    tmp = dest + '.part'
    urllib.request.urlretrieve(url, tmp)
    os.replace(tmp, dest)
    return dest


# ---------------------------------------------------------------- pictures
def emoji_dir():
    d = os.path.join(CACHE, 'fluent-emoji-3d')
    if not os.path.isdir(d):
        tgz = download(EMOJI_PKG, os.path.join(CACHE, 'fluent-emoji-3d.tgz'))
        with tarfile.open(tgz) as tf:
            tf.extractall(d)
    return os.path.join(d, 'package', 'assets')


def emoji_file(src_dir, emoji):
    cps = [f'{ord(c):x}' for c in emoji]
    bare = [c for c in cps if c != 'fe0f']
    for name in ('-'.join(cps), '-'.join(bare), '-'.join(bare) + '-fe0f'):
        if os.path.exists(os.path.join(src_dir, name + '.webp')):
            return name + '.webp'
    return None


def build_pictures(lib):
    src_dir = emoji_dir()
    icons = [t['icon'] for t in lib['core']] + [p['icon'] for p in lib['pages']]
    icons += [t['icon'] for p in lib['pages'] for t in p['tiles']]
    out, missing = {}, []
    os.makedirs(os.path.join(ROOT, 'img'), exist_ok=True)
    for e in dict.fromkeys(icons):
        name = emoji_file(src_dir, e)
        if not name:
            missing.append(e)
            continue
        data = open(os.path.join(src_dir, name), 'rb').read()
        dest = os.path.join(ROOT, 'img', name)
        if not os.path.exists(dest) or open(dest, 'rb').read() != data:
            open(dest, 'wb').write(data)
        out[e] = 'img/' + name
    # drop pictures no tile uses any more
    used = {os.path.basename(v) for v in out.values()}
    for f in os.listdir(os.path.join(ROOT, 'img')):
        if f.endswith('.webp') and f not in used:
            os.remove(os.path.join(ROOT, 'img', f))
    if missing:
        print('  no 3D picture for', ' '.join(missing), '(the emoji itself will show)')
    print(f'  {len(out)} pictures')
    return out


def build_app_icons():
    """Home-screen icons: the cowboy on a warm rounded square."""
    from PIL import Image, ImageDraw
    face = Image.open(os.path.join(emoji_dir(), '1f920.webp')).convert('RGBA')
    os.makedirs(os.path.join(ROOT, 'icons'), exist_ok=True)
    for size, maskable in ((192, False), (512, False), (512, True)):
        im = Image.new('RGBA', (size, size), (0, 0, 0, 0))
        bg = Image.new('RGBA', (size, size), (232, 163, 23, 255))
        if maskable:
            im = bg
        else:
            mask = Image.new('L', (size, size), 0)
            ImageDraw.Draw(mask).rounded_rectangle([0, 0, size - 1, size - 1], radius=size // 5, fill=255)
            im.paste(bg, (0, 0), mask)
        inner = int(size * (0.62 if maskable else 0.78))
        f = face.resize((inner, inner), Image.LANCZOS)
        off = (size - inner) // 2
        im.alpha_composite(f, (off, off))
        name = f'icon-{size}{"-maskable" if maskable else ""}.png'
        im.save(os.path.join(ROOT, 'icons', name), optimize=True)


# ---------------------------------------------------------------- voices
PROCESS = 'trim-start+level-v2'   # change this to force every clip to be recorded again


def finish(s, sr):
    """Cut the quiet lead-in so a tap speaks straight away (the ending is left
    whole so final sounds like the k in "snack" survive), then bring every clip
    to the same loudness so no tile is suddenly louder than another."""
    import numpy as np
    win = max(1, int(sr * 0.01))
    env = np.convolve(np.abs(s), np.ones(win) / win, mode='same')
    loud = np.where(env > 10 ** (-48 / 20))[0]
    if len(loud):
        s = s[max(0, loud[0] - int(sr * 0.04)):]
    voiced = s[env[-len(s):] > 10 ** (-40 / 20)] if len(s) else s
    rms = float(np.sqrt(np.mean(voiced ** 2))) if len(voiced) else 0.0
    if rms > 0:
        gain = min(0.12 / rms, 0.89 / max(1e-6, float(np.max(np.abs(s)))))
        s = s * gain
    return np.concatenate([np.zeros(int(sr * 0.02), dtype=s.dtype), s])


def build_voices(tiles):
    import numpy as np, soundfile as sf, imageio_ffmpeg
    from kokoro_onnx import Kokoro
    model = [download(KOKORO_BASE + f, os.path.join(CACHE, 'kokoro', f)) for f in KOKORO_FILES]
    ffmpeg = imageio_ffmpeg.get_ffmpeg_exe()
    kokoro = None
    result = {}
    jobs = [('_sample', SAMPLE_TEXT), ('_speed', SPEED_TEXT)] + [(tid, t.get('say') or t['label']) for tid, t in tiles]
    jobs = list(dict(jobs).items())
    for v in VOICES:
        vdir = os.path.join(ROOT, 'voices', v['id'])
        os.makedirs(vdir, exist_ok=True)
        man_path = os.path.join(vdir, 'manifest.json')
        manifest = json.load(open(man_path)) if os.path.exists(man_path) else {}
        made = 0
        clips = {}
        for tid, text in jobs:
            key = hashlib.sha1(f'{v["kokoro"]}|{SPEED}|{PROCESS}|{text}'.encode()).hexdigest()[:10]
            dest = os.path.join(vdir, tid + '.mp3')
            if manifest.get(tid) != key or not os.path.exists(dest):
                if kokoro is None:
                    kokoro = Kokoro(*model)
                samples, sr = kokoro.create(text, voice=v['kokoro'], speed=SPEED,
                                            lang='en-gb' if v['kokoro'].startswith('b') else 'en-us')
                audio = finish(np.asarray(samples, dtype=np.float32), sr)
                buf = io.BytesIO()
                sf.write(buf, audio, sr, format='WAV', subtype='PCM_16')
                subprocess.run([ffmpeg, '-loglevel', 'error', '-y', '-f', 'wav', '-i', 'pipe:0',
                                '-ac', '1', '-ar', '24000', '-codec:a', 'libmp3lame',
                                '-b:a', '48k', dest], input=buf.getvalue(), check=True)
                manifest[tid] = key
                made += 1
            clips[tid] = f'voices/{v["id"]}/{tid}.mp3?v={key}'
        # forget clips for tiles that no longer exist
        for tid in list(manifest):
            if tid not in clips:
                del manifest[tid]
                p = os.path.join(vdir, tid + '.mp3')
                if os.path.exists(p):
                    os.remove(p)
        json.dump(manifest, open(man_path, 'w'), indent=0, sort_keys=True)
        result[v['id']] = clips
        print(f'  voice {v["name"]}: {len(clips)} clips ({made} new)')
    return result


# ---------------------------------------------------------------- output
def file_hash(paths):
    h = hashlib.sha1()
    for p in sorted(paths):
        h.update(p.encode())
        h.update(open(os.path.join(ROOT, p.split('?')[0]), 'rb').read())
    return h.hexdigest()[:12]


def write_outputs(pictures, clips):
    assets = {
        'voices': [{k: v[k] for k in ('id', 'name', 'desc')} for v in VOICES],
        'img': pictures,
        'clips': clips,
    }
    js = ('/* Generated by tools/build.py: do not edit by hand. */\n'
          'window.TT_ASSETS = ' + json.dumps(assets, ensure_ascii=False, indent=0) + ';\n')
    open(os.path.join(ROOT, 'assets.js'), 'w', encoding='utf-8').write(js)

    shell = ['index.html', 'credits.html', 'library.js', 'assets.js', 'manifest.webmanifest',
             'icons/icon-192.png', 'icons/icon-512.png', 'icons/icon-512-maskable.png']
    precache = shell + sorted(set(pictures.values()))
    version = file_hash(precache + ['tools/sw-template.js'])
    tpl = open(os.path.join(ROOT, 'tools', 'sw-template.js'), encoding='utf-8').read()
    sw = tpl.replace('__VERSION__', version).replace('__PRECACHE__', json.dumps(['./'] + precache, indent=1))
    open(os.path.join(ROOT, 'sw.js'), 'w', encoding='utf-8').write(sw)
    print(f'  offline cache version {version}: {len(precache)} files + voice clips')


def main():
    lib = load_library()
    check_mom_under_dad(lib)
    tiles = all_tiles(lib)
    print(f'{len(lib["pages"])} pages, {len(tiles)} tiles')
    pictures = build_pictures(lib)
    build_app_icons()
    clips = build_voices(tiles)
    write_outputs(pictures, clips)
    import manual
    manual.main()
    print('Done.')


if __name__ == '__main__':
    main()
