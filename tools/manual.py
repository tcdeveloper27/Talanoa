#!/usr/bin/env python3
"""Build the staff guide (manual/index.html) from tools/manual-template.html.

The page list, tile counts and voice table come straight from library.js and
tools/build.py, so the guide stays correct when the words change. Screenshot
callout positions come from manual/boxes.json (measured when the screenshots
were taken). Run by tools/build.py; can also be run on its own.
"""
import math, html, json, os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, 'tools'))
APP_URL = 'https://tcdeveloper27.github.io/Talanoa/'


def pct(v, total):
    return f'{100 * v / total:.2f}%'


def badge(n, x, y):
    return f'<span class="badge" style="left:{x};top:{y}">{n}</span>'


def readable(hexc):
    """The page colour darkened just enough for white writing (4.6 : 1), as the app does."""
    def lum(h):
        c = [int(h[i:i + 2], 16) / 255 for i in (1, 3, 5)]
        c = [v / 12.92 if v <= 0.03928 else ((v + 0.055) / 1.055) ** 2.4 for v in c]
        return 0.2126 * c[0] + 0.7152 * c[1] + 0.0722 * c[2]
    a = 0.0
    while a <= 0.6:
        rgb = [round(int(hexc[i:i + 2], 16) * (1 - a)) for i in (1, 3, 5)]
        out = '#' + ''.join(f'{v:02x}' for v in rgb)
        if 1.05 / (lum(out) + 0.05) >= 4.6:
            return out
        a += 0.02
    return out


def qr_svg(url):
    try:
        import qrcode, qrcode.image.svg
    except ImportError:
        sys.exit('The staff guide needs the qrcode package: pip install qrcode')
    img = qrcode.make(url, image_factory=qrcode.image.svg.SvgPathImage, box_size=10, border=2)
    svg = img.to_string(encoding='unicode')
    svg = re.sub(r'<\?xml[^>]*\?>', '', svg)
    return re.sub(r'width="[^"]*" height="[^"]*"', 'class="qr" role="img" aria-label="QR code for the Talanoa link"', svg, count=1)


def main():
    import build
    lib = build.load_library()
    assets_src = open(os.path.join(ROOT, 'assets.js'), encoding='utf-8').read()
    assets = json.loads(assets_src[assets_src.index('{'):assets_src.rindex('}') + 1])
    img = assets['img']
    boxes = json.load(open(os.path.join(ROOT, 'manual', 'boxes.json')))

    def pic(emoji, photo=None):
        src = photo or img.get(emoji)
        return f'<img src="../{src}" alt="">' if src else f'<span class="em">{html.escape(emoji)}</span>'

    def tiles(p):
        return [t for t in p['tiles'] if not build.blank(t)]

    # page gallery
    cards = []
    for i, p in enumerate(lib['pages'], 1):
        if p.get('keyboard'):
            body = 'The alphabet: spell a word, then Speak'
        else:
            sample = ', '.join(html.escape(t['label']) for t in tiles(p)[:4])
            body = f'{len(tiles(p))} tiles: {sample}…'
        cards.append(
            f'<div class="pagecard" style="--pc:{p["color"]};--pcs:{readable(p["color"])}"><div class="pc-top">{pic(p["icon"], p.get("img"))}'
            f'<b>{html.escape(p["name"])}</b><span class="n">{i}</span></div>'
            f'<div class="pc-body">{body}</div></div>')

    # voices
    rows = []
    for i, v in enumerate(build.VOICES):
        tag = ' <span class="tag">default</span>' if i == 0 else ''
        rows.append(f'<tr><td><b>{html.escape(v["name"])}</b>{tag}</td><td>{html.escape(v["desc"])}</td></tr>')
    rows.append('<tr><td><b>Built-in voice</b></td><td>the voice built into the phone or tablet (sound depends on the device)</td></tr>')

    # core row
    core = ''.join(f'<span class="corechip" style="--c:{readable(c["color"])}">{pic(c["icon"])}{html.escape(c["label"])}</span>'
                   for c in lib['core'])

    # callouts on the main screenshot (its size in CSS pixels is in boxes.json)
    W, H = boxes['shot']['width'], boxes['shot']['height']
    def at(name, ax, ay, dx=0, dy=0):
        """A point on a measured box: ax, ay = 0 for its left/top edge, .5 middle, 1 right/bottom."""
        r = boxes[name]
        return pct(r['x'] + r['width'] * ax + dx, W), pct(r['y'] + r['height'] * ay + dy, H)
    main_badges = ''.join([
        badge(1, *at('banner', 0, .5, 26)),
        badge(2, *at('core', 0, 0, 18, 16)),
        badge(3, *at('prev', 0, 0, 14, 12)),
        badge(4, *at('title', 0, 0, 14, 12)),
        badge(5, *at('next', 1, 0, -14, 12)),
        badge(6, *at('snack', 0, 0, 16, 16)),
        badge(7, *at('gear', 0, .5, -16)),
        badge(8, *at('lit', 1, 0, -14, 14)),
    ])

    # callouts on the three settings crops (each cut halfway between two sections, as tools/guide-pictures.js does)
    sw = boxes['s_voice']['sheetW']
    def mid(a, b):
        return math.floor((boxes[a]['y'] + boxes[a]['height'] + boxes[b]['y']) / 2 + 0.5)   # JavaScript's Math.round
    cuts = [0, mid('s_vol', 's_pages'), mid('s_screen', 's_own'), boxes['s_pages']['sheetH']]
    def sat(name, part):
        r = boxes[name]
        y = r['y'] + min(r['height'] / 2, 22) - cuts[part]
        return pct(sw - 16, sw), pct(y, cuts[part + 1] - cuts[part])
    def row(part, *pairs):
        return ''.join(badge(letter, *sat(name, part)) for letter, name in pairs)
    top_badges = row(0, ('A', 's_voice'), ('B', 's_speed'), ('C', 's_vol'))
    mid_badges = row(1, ('D', 's_pages'), ('E', 's_swipe'), ('F', 's_fx'), ('G', 's_calm'), ('H', 's_big'), ('I', 's_strong'),
                     ('J', 's_screen'))
    bottom_badges = row(2, ('K', 's_ownbtn'), ('L', 's_backup'), ('M', 's_counts'), ('N', 's_counton'),
                        ('O', 's_status'), ('P', 's_update'), ('Q', 's_links'))

    # the Talk page, About me and the Tongan words, straight from library.js
    talk = next((p for p in lib['pages'] if p['name'] == 'Talk'), {'tiles': []})
    talk_rows = '\n'.join(f'<tr><td><b>{pic(t["icon"])}{html.escape(t["label"])}</b></td><td>“{html.escape(t.get("say") or t["label"])}”</td></tr>'
                          for t in tiles(talk))
    about = next((t for t in lib['core'] + [t for p in lib['pages'] for t in tiles(p)] if t.get('card')), None)
    tongan = next((p for p in lib['pages'] if p['name'] == 'Tongan'), {'tiles': []})
    tongan_list = ', '.join(f'<b>{html.escape(t["label"])}</b> ({html.escape(t.get("means", ""))})' for t in tiles(tongan))

    # the Body and Sick pages, side by side
    def health_cell(t):
        if not t:
            return '<td></td><td></td>'
        return f'<td><b>{pic(t["icon"], t.get("img"))}{html.escape(t["label"])}</b></td><td>“{html.escape(t.get("say") or t["label"])}”</td>'
    body, sick = (tiles(next((p for p in lib['pages'] if p['name'] == n), {'tiles': []})) for n in ('Body', 'Sick'))
    health_rows = '\n'.join(f'<tr>{health_cell(body[i] if i < len(body) else None)}{health_cell(sick[i] if i < len(sick) else None)}</tr>'
                            for i in range(max(len(body), len(sick))))

    tpl = open(os.path.join(ROOT, 'tools', 'manual-template.html'), encoding='utf-8').read()
    out = (tpl.replace('{{PAGE_CARDS}}', '\n'.join(cards))
              .replace('{{PAGE_COUNT}}', str(len(lib['pages'])))
              .replace('{{TILE_COUNT}}', str(sum(len(tiles(p)) for p in lib['pages'])))
              .replace('{{VOICE_ROWS}}', '\n'.join(rows))
              .replace('{{VOICE_COUNT}}', str(len(build.VOICES)))
              .replace('{{CORE_CHIPS}}', core)
              .replace('{{MAIN_BADGES}}', main_badges)
              .replace('{{SET_TOP_BADGES}}', top_badges)
              .replace('{{SET_MID_BADGES}}', mid_badges)
              .replace('{{SET_BOTTOM_BADGES}}', bottom_badges)
              .replace('{{TALK_ROWS}}', talk_rows)
              .replace('{{HEALTH_ROWS}}', health_rows)
              .replace('{{ABOUT_ME}}', html.escape(about['say']) if about else '')
              .replace('{{TONGAN_LIST}}', tongan_list)
              .replace('{{QR}}', qr_svg(APP_URL))
              .replace('{{APP_URL}}', APP_URL))
    left = re.findall(r'\{\{[A-Z_]+\}\}', out)
    if left:
        sys.exit('manual template has unfilled fields: ' + ', '.join(left))
    open(os.path.join(ROOT, 'manual', 'index.html'), 'w', encoding='utf-8').write(out)
    print('  staff guide: manual/index.html')


if __name__ == '__main__':
    main()
