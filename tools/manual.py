#!/usr/bin/env python3
"""Build the staff guide (manual/index.html) from tools/manual-template.html.

The page list, tile counts and voice table come straight from library.js and
tools/build.py, so the guide stays correct when the words change. Screenshot
callout positions come from manual/boxes.json (measured when the screenshots
were taken). Run by tools/build.py; can also be run on its own.
"""
import html, json, os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, 'tools'))
APP_URL = 'https://tcdeveloper27.github.io/Talanoa/'


def pct(v, total):
    return f'{100 * v / total:.2f}%'


def badge(n, x, y):
    return f'<span class="badge" style="left:{x};top:{y}">{n}</span>'


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

    def pic(emoji):
        src = img.get(emoji)
        return f'<img src="../{src}" alt="">' if src else f'<span class="em">{html.escape(emoji)}</span>'

    # page gallery
    cards = []
    for i, p in enumerate(lib['pages'], 1):
        sample = ', '.join(html.escape(t['label']) for t in p['tiles'][:4])
        cards.append(
            f'<div class="pagecard" style="--pc:{p["color"]}"><div class="pc-top">{pic(p["icon"])}'
            f'<b>{html.escape(p["name"])}</b><span class="n">{i}</span></div>'
            f'<div class="pc-body">{len(p["tiles"])} tiles: {sample}…</div></div>')

    # voices
    rows = []
    for i, v in enumerate(build.VOICES):
        tag = ' <span class="tag">default</span>' if i == 0 else ''
        rows.append(f'<tr><td><b>{html.escape(v["name"])}</b>{tag}</td><td>{html.escape(v["desc"])}</td></tr>')
    rows.append('<tr><td><b>Tablet voice</b></td><td>the voice built into the tablet (sound depends on the tablet)</td></tr>')

    # core row
    core = ''.join(f'<span class="corechip" style="--c:{c["color"]}">{pic(c["icon"])}{html.escape(c["label"])}</span>'
                   for c in lib['core'])

    # callouts on the main screenshot (1280 x 800 CSS pixels)
    W, H = 1280, 800
    def at(name, dx=0, dy=0, where='tl'):
        r = boxes[name]
        x = r['x'] + (r['width'] / 2 if where == 'c' else 0) + dx
        y = r['y'] + (r['height'] / 2 if where == 'c' else 0) + dy
        return pct(x, W), pct(y, H)
    main_badges = ''.join([
        badge(1, *at('banner', 330, 28)),
        badge(2, *at('core', 18, 14)),
        badge(3, *at('prev', 14, 14)),
        badge(4, *at('title', 14, 14)),
        badge(5, *at('next', 14, 14)),
        badge(6, *at('snack', 16, 16)),
        badge(7, *at('gear', -22, 18)),
    ])

    # callouts on the two settings crops (sheet is 600 CSS px wide, cut 44px above "Pages to show")
    sw = boxes['s_voice']['sheetW']
    cut = boxes['s_pages']['y'] - 44
    total = boxes['s_pages']['sheetH']
    def sat(name, top):
        r = boxes[name]
        h = cut if top else total - cut
        y = r['y'] + min(r['height'] / 2, 22) - (0 if top else cut)
        return pct(sw - 16, sw), pct(y, h)
    top_badges = ''.join([badge('A', *sat('s_voice', True)), badge('B', *sat('s_speed', True)),
                          badge('C', *sat('s_vol', True))])
    bottom_badges = ''.join([badge('D', *sat('s_pages', False)), badge('E', *sat('s_status', False)),
                             badge('F', *sat('s_update', False)), badge('G', *sat('s_about', False))])

    tpl = open(os.path.join(ROOT, 'tools', 'manual-template.html'), encoding='utf-8').read()
    out = (tpl.replace('{{PAGE_CARDS}}', '\n'.join(cards))
              .replace('{{PAGE_COUNT}}', str(len(lib['pages'])))
              .replace('{{TILE_COUNT}}', str(sum(len(p['tiles']) for p in lib['pages'])))
              .replace('{{VOICE_ROWS}}', '\n'.join(rows))
              .replace('{{VOICE_COUNT}}', str(len(build.VOICES)))
              .replace('{{CORE_CHIPS}}', core)
              .replace('{{MAIN_BADGES}}', main_badges)
              .replace('{{SET_TOP_BADGES}}', top_badges)
              .replace('{{SET_BOTTOM_BADGES}}', bottom_badges)
              .replace('{{QR}}', qr_svg(APP_URL))
              .replace('{{APP_URL}}', APP_URL))
    left = re.findall(r'\{\{[A-Z_]+\}\}', out)
    if left:
        sys.exit('manual template has unfilled fields: ' + ', '.join(left))
    open(os.path.join(ROOT, 'manual', 'index.html'), 'w', encoding='utf-8').write(out)
    print('  staff guide: manual/index.html')


if __name__ == '__main__':
    main()
