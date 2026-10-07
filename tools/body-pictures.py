#!/usr/bin/env python3
"""Draw the pictures for the health pages that no emoji covers (a back, a knee, a throat...).

One friendly figure, the same on every Body picture, with the sore spot glowing red, so he learns
to read them the same way. The skin is the emoji yellow of the Ouch page's arm, leg and foot. On
the Sick page, Itchy (bumps and scratches) and Fell (the figure falling) use the same figure; Pee
hurts and Can't poop are the toilet emoji with a red glow or a no-entry sign.

Writes pictures/<name>.webp at 256 x 256, like the emoji pictures. Needs rsvg-convert, Pillow and
the Fluent Emoji files tools/build.py downloads into ~/.cache/tilertalker (run the build once first):
    python3 tools/body-pictures.py
"""
import base64, io, os, re, subprocess, sys

from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, 'pictures')
EMOJI = os.path.expanduser('~/.cache/tilertalker/fluent-emoji-3d/package/assets')
SIZE = 256
W = 600                                           # the figure is drawn on a 600 x 1200 sheet

DEFS = '''
<radialGradient id="skin" cx=".36" cy=".3" r=".8">
  <stop offset="0" stop-color="#FFE47A"/><stop offset=".5" stop-color="#FFC83D"/>
  <stop offset=".85" stop-color="#F5A623"/><stop offset="1" stop-color="#E38B14"/></radialGradient>
<linearGradient id="neck" x1="0" y1="0" x2="0" y2="1">
  <stop offset="0" stop-color="#E0911A"/><stop offset=".55" stop-color="#F7B42C"/><stop offset="1" stop-color="#FFC83D"/></linearGradient>
<radialGradient id="shirt" cx=".34" cy=".22" r=".95">
  <stop offset="0" stop-color="#86BBFF"/><stop offset=".45" stop-color="#4A8BF0"/>
  <stop offset=".85" stop-color="#2F69D6"/><stop offset="1" stop-color="#2454B4"/></radialGradient>
<radialGradient id="shorts" cx=".34" cy=".2" r=".95">
  <stop offset="0" stop-color="#77819A"/><stop offset=".5" stop-color="#4C5568"/><stop offset="1" stop-color="#323846"/></radialGradient>
<radialGradient id="hair" cx=".4" cy=".25" r=".85">
  <stop offset="0" stop-color="#A2714B"/><stop offset=".55" stop-color="#6E462B"/><stop offset="1" stop-color="#4A2E1B"/></radialGradient>
<radialGradient id="halo">
  <stop offset="0" stop-color="#FF2A2A" stop-opacity=".75"/><stop offset=".55" stop-color="#FF2A2A" stop-opacity=".35"/>
  <stop offset="1" stop-color="#FF2A2A" stop-opacity="0"/></radialGradient>
<radialGradient id="core" cx=".4" cy=".35" r=".7">
  <stop offset="0" stop-color="#FF8A7A"/><stop offset=".55" stop-color="#F0262A"/><stop offset="1" stop-color="#B80F18"/></radialGradient>
'''

# Left-hand parts (as you look at him); the right-hand ones are mirrored. Absolute commands only,
# so every pair of numbers is an x, y point.
LEG = 'M 207 712 C 201 820 209 930 214 1062 L 272 1062 C 277 940 290 830 296 712 Z'
ARM = 'M 152 418 C 137 510 129 600 129 690 L 183 690 C 185 600 195 520 207 438 Z'
SHORTS = 'M 196 598 L 404 598 C 410 670 414 740 410 796 L 306 796 L 300 742 L 294 796 L 190 796 C 186 740 190 670 196 598 Z'
SHIRT_FRONT = ('M 258 294 Q 300 338 342 294 L 398 308 Q 446 320 460 370 L 478 452 L 418 472 L 404 430 L 404 634 '
               'L 196 634 L 196 430 L 182 472 L 122 452 L 140 370 Q 154 320 202 308 Z')
SHIRT_BACK = ('M 258 294 Q 300 310 342 294 L 398 308 Q 446 320 460 370 L 478 452 L 418 472 L 404 430 L 404 634 '
              'L 196 634 L 196 430 L 182 472 L 122 452 L 140 370 Q 154 320 202 308 Z')
HAIR_FRONT = 'M 186 170 C 180 70 246 38 300 40 C 356 38 422 70 414 170 C 404 124 366 98 300 100 C 236 98 196 124 186 170 Z'
HAIR_BACK = ('M 186 172 C 180 70 246 38 300 40 C 354 38 420 70 414 172 C 414 214 396 246 364 256 '
             'C 330 262 270 262 236 256 C 204 246 186 214 186 172 Z')


def mirror(d):
    nums = iter(re.findall(r'[A-Za-z]|-?\d+(?:\.\d+)?', d))
    out = []
    for tok in nums:
        if tok.isalpha():
            out.append(tok)
        else:
            out += [str(W - float(tok)).rstrip('0').rstrip('.'), next(nums)]
    return ' '.join(out)


def both(d, fill):
    return f'<path d="{d}" fill="{fill}"/><path d="{mirror(d)}" fill="{fill}"/>'


def figure(view, shadow=True):
    """The whole figure, from the front ('front') or from behind ('back')."""
    s = ['<ellipse cx="300" cy="1112" rx="150" ry="16" fill="#000" opacity=".12"/>' if shadow else '']
    s.append(both(LEG, 'url(#skin)'))
    if view == 'front':
        s.append('<ellipse cx="234" cy="1084" rx="50" ry="27" fill="url(#skin)"/>'
                 '<ellipse cx="366" cy="1084" rx="50" ry="27" fill="url(#skin)"/>')
    else:
        s.append('<ellipse cx="242" cy="1078" rx="34" ry="24" fill="url(#skin)"/>'
                 '<ellipse cx="358" cy="1078" rx="34" ry="24" fill="url(#skin)"/>')
    s.append(f'<path d="{SHORTS}" fill="url(#shorts)"/>'
             '<path d="M 196 598 L 404 598 L 405 622 L 195 622 Z" fill="#1E232D" opacity=".45"/>')   # waistband
    if view == 'front':                                       # the fly and its button: this is the front
        s.append('<path d="M 300 624 Q 306 664 300 704" stroke="#1E232D" stroke-width="6" stroke-linecap="round" fill="none"/>'
                 '<circle cx="300" cy="611" r="8" fill="#D5DAE3"/>')
    else:                                                     # back pockets and the seam: this is the back
        s.append('<rect x="218" y="640" width="64" height="56" rx="12" fill="#000" fill-opacity=".14" '
                 'stroke="#1E232D" stroke-opacity=".55" stroke-width="5"/>'
                 '<rect x="318" y="640" width="64" height="56" rx="12" fill="#000" fill-opacity=".14" '
                 'stroke="#1E232D" stroke-opacity=".55" stroke-width="5"/>'
                 '<path d="M 300 624 L 300 742" stroke="#1E232D" stroke-opacity=".5" stroke-width="5" fill="none"/>')
    s.append(both(ARM, 'url(#skin)'))
    for x in (155, 445):                                      # hands, with four fingers
        s.append(''.join(f'<ellipse cx="{x + dx}" cy="{750 + abs(dx) * -.25:.0f}" rx="10" ry="17" fill="url(#skin)"/>'
                         for dx in (-24, -8, 8, 24)))
        s.append(f'<ellipse cx="{x}" cy="716" rx="37" ry="39" fill="url(#skin)"/>')
    if view == 'front':                                       # thumbs, on the inner side
        s.append('<ellipse cx="184" cy="700" rx="13" ry="20" fill="url(#skin)" transform="rotate(-20 184 700)"/>'
                 '<ellipse cx="416" cy="700" rx="13" ry="20" fill="url(#skin)" transform="rotate(20 416 700)"/>')
    s.append('<rect x="266" y="246" width="68" height="76" rx="22" fill="url(#neck)"/>')
    s.append(f'<path d="{SHIRT_FRONT if view == "front" else SHIRT_BACK}" fill="url(#shirt)"/>')
    s.append('<ellipse cx="189" cy="174" rx="20" ry="27" fill="url(#skin)"/>'
             '<ellipse cx="411" cy="174" rx="20" ry="27" fill="url(#skin)"/>')
    if view == 'front':
        s.append('<circle cx="300" cy="162" r="112" fill="url(#skin)"/>')
        s.append(f'<path d="{HAIR_FRONT}" fill="url(#hair)"/>')
        s.append('<ellipse cx="236" cy="206" rx="19" ry="11" fill="#FF7A59" opacity=".3"/>'
                 '<ellipse cx="364" cy="206" rx="19" ry="11" fill="#FF7A59" opacity=".3"/>'
                 '<ellipse cx="262" cy="172" rx="12" ry="16" fill="#3A2618"/><circle cx="266" cy="165" r="4" fill="#fff"/>'
                 '<ellipse cx="338" cy="172" rx="12" ry="16" fill="#3A2618"/><circle cx="342" cy="165" r="4" fill="#fff"/>'
                 '<path d="M 240 146 Q 258 132 281 133" stroke="#5C3A24" stroke-width="7" stroke-linecap="round" fill="none"/>'
                 '<path d="M 360 146 Q 342 132 319 133" stroke="#5C3A24" stroke-width="7" stroke-linecap="round" fill="none"/>'
                 '<path d="M 279 232 Q 300 217 321 232" stroke="#7A3A1E" stroke-width="7" stroke-linecap="round" fill="none"/>')
    else:
        s.append(f'<path d="{HAIR_BACK}" fill="url(#hair)"/>')
    return ''.join(s)


def ouch(cx, cy, r):
    """The sore spot: a red glow with short rays around it."""
    s = [f'<circle cx="{cx}" cy="{cy}" r="{r * 1.7:.0f}" fill="url(#halo)"/>',
         f'<circle cx="{cx}" cy="{cy}" r="{r * .5:.0f}" fill="url(#core)" stroke="#fff" stroke-width="{r * .1:.1f}"/>']
    import math
    for i in range(8):
        a = math.radians(i * 45 + 22.5)
        r1, r2 = r * .82, r * (1.28 if i % 2 else 1.12)
        s.append(f'<line x1="{cx + r1 * math.cos(a):.1f}" y1="{cy + r1 * math.sin(a):.1f}" '
                 f'x2="{cx + r2 * math.cos(a):.1f}" y2="{cy + r2 * math.sin(a):.1f}" stroke="#E3141C" '
                 f'stroke-width="{r * .16:.1f}" stroke-linecap="round"/>')
    return ''.join(s)


def svg(body, x, y, size):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" '
            f'viewBox="{x} {y} {size} {size}" width="512" height="512"><defs>{DEFS}</defs>{body}</svg>')


def emoji(code, x, y, size):
    png = io.BytesIO()
    Image.open(os.path.join(EMOJI, code + '.webp')).convert('RGBA').save(png, 'PNG')
    data = base64.b64encode(png.getvalue()).decode()
    return f'<image x="{x}" y="{y}" width="{size}" height="{size}" xlink:href="data:image/png;base64,{data}"/>'


def itchy():
    """A forearm with red bumps and scratch marks."""
    bumps = [(146, 520), (166, 566), (140, 600), (168, 640), (150, 668), (138, 556)]
    s = [figure('front')]
    for x, y in bumps:
        s.append(f'<circle cx="{x}" cy="{y}" r="11" fill="#E53935"/><circle cx="{x - 3}" cy="{y - 3}" r="4" fill="#FF8A80"/>')
    for dx in (0, 24, 48):
        d = f'M {98 + dx} 548 Q {128 + dx} 584 {140 + dx} 636'
        s.append(f'<path d="{d}" stroke="#D84343" stroke-width="11" stroke-linecap="round" fill="none"/>'
                 f'<path d="{d}" stroke="#FFE3E0" stroke-width="4" stroke-linecap="round" fill="none"/>')
    return ''.join(s)


def fell():
    """Lying on the floor after a fall: head to the left, a floor line, and lines where he landed."""
    s = ['<path d="M 280 1018 L 1180 1018" stroke="#8D6E63" stroke-width="18" stroke-linecap="round" opacity=".55"/>',
         '<g transform="translate(600 640) rotate(-45) translate(-300 -640)">', figure('front', shadow=False), '</g>']
    for x, y in ((400, 190), (452, 240), (504, 290)):        # moving lines, behind his head as he goes down
        s.append(f'<path d="M {x} {y} l 62 -56" stroke="#E3141C" stroke-width="16" stroke-linecap="round" opacity=".85"/>')
    return ''.join(s)


# name: (what it shows, x, y, size of the square that's cut out of the 600 x 1200 sheet)
PICTURES = {
    'body':     (lambda: figure('front') + ouch(300, 420, 50),       40, 40, 520),
    'back':     (lambda: figure('back') + ouch(300, 470, 62),        100, 200, 400),
    'chest':    (lambda: figure('front') + ouch(300, 410, 56),       110, 205, 380),
    'throat':   (lambda: figure('front') + ouch(300, 302, 34),       150, 105, 300),
    'neck':     (lambda: figure('back') + ouch(300, 274, 38),        150, 95, 300),
    'shoulder': (lambda: figure('front') + ouch(412, 332, 42),       195, 150, 320),
    'hand':     (lambda: figure('front') + ouch(150, 708, 26),        50, 600, 210),
    'knee':     (lambda: figure('front') + ouch(250, 905, 40),       120, 774, 300),
    'bottom':   (lambda: figure('back') + ouch(300, 724, 54),        140, 560, 320),
    'privates': (lambda: figure('front') + ouch(300, 744, 40),       140, 560, 320),
    'itchy':    (itchy,                                               15, 470, 260),
    'fell':     (fell,                                               130, 150, 900),
}
EMOJI_PICTURES = {
    'pee-hurts': lambda: emoji('1f6bd', 6, 40, 210) + ouch(196, 74, 40),
    'cant-poop': lambda: emoji('1f6bd', 6, 40, 210) + emoji('1f6ab', 150, 8, 100),
}


def render(name, text):
    png = subprocess.run(['rsvg-convert', '-w', '512', '-h', '512'], input=text.encode(), capture_output=True, check=True).stdout
    im = Image.open(io.BytesIO(png)).convert('RGBA').resize((SIZE, SIZE), Image.LANCZOS)
    im.save(os.path.join(OUT, name + '.webp'), 'WEBP', quality=92, method=6)


def main():
    os.makedirs(OUT, exist_ok=True)
    for name, (draw, x, y, size) in PICTURES.items():
        render(name, svg(draw(), x, y, size))
    for name, draw in EMOJI_PICTURES.items():
        render(name, svg(draw(), 0, 0, 256))
    print(f'{len(PICTURES) + len(EMOJI_PICTURES)} pictures in {os.path.relpath(OUT, ROOT)}/')


if __name__ == '__main__':
    main()
