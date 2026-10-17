#!/usr/bin/env python3
"""Build the six brand-manual diagrams (SVG + PNG) from the derived logo vectors and
globals-brand-tokens.json. Every number drawn here is read from the tokens file or the
manual; see VALUES below. Run: python3 build_diagrams.py  (renders PNG with Chromium)."""
import json, pathlib, re, html, sys

HERE = pathlib.Path(__file__).parent
LOGOS = HERE.parent / 'logos' / 'derived'
TOK = json.loads((HERE.parent.parent / 'globals-brand-tokens.json').read_text())

# ---- values (all from the tokens file / manual) --------------------------------------
GOLD, CITRIC, BABY, DUCK, SKY, GREEN = '#C69300', '#FC611E', '#F2C7CA', '#FFCB3F', '#6FCBF1', '#96E7BE'
GREY, INK, INK500, CTEXT, BLACK, WHITE = '#EAEBEA', '#16171B', '#686A6B', '#C03C03', '#000000', '#FFFFFF'
assert TOK['color']['global_gold']['hex'] == GOLD and TOK['color']['citric_text']['hex'] == CTEXT
KA = TOK['logo']['knot_alone']            # min 16 px / 5 mm, favicons 16..512
FAV = KA['favicon_px']                    # [16, 32, 48, 180, 192, 512]
FLOOR_PX = TOK['logo']['scale_range']['floor_screen_px']   # 120
FLOOR_MM = TOK['logo']['scale_range']['floor_print_mm']    # 30
GSTF = TOK['logo']['sub_brands']['gstf']  # 40 px / 10 mm
ONTOUR = TOK['logo']['sub_brands']['on_tour']  # 30 px min, 50 native
MS = TOK['logo']['min_size']
assert KA['min_screen_px'] == 16 and KA['min_print_mm'] == 5 and FLOOR_PX == 120 and FLOOR_MM == 30
assert FAV == [16, 32, 48, 180, 192, 512] and GSTF['min_height_px'] == 40 and GSTF['min_height_mm'] == 10
MM = 96 / 25.4   # px per mm at 96 dpi (true-scale canvas)

# ---- lockup geometry, measured on the derived vectors ---------------------------------
# viewBox of the GLOBALS lockup: -0.0009 1.6797 343.6880 78.8428; the knot spans the full
# height; the wordmark cap height (flat letters, after the group transform) is 37.0 units.
LVB = '-0.0009 1.6797 343.6880 78.8428'
LW, LH = 343.6880, 78.8428
CAP = 37.0                      # G in lockup units
G_OF_H = CAP / LH               # G as a fraction of the lockup height (0.469)
KNOT_W_OF_W = 79.0645 / LW      # knot width as a fraction of the lockup width (0.230)
WM_TOP, WM_BOT = 19.08 / LH, 56.07 / LH   # wordmark cap top/bottom as fractions of height
KVB = '-0.0009 1.6797 79.0645 78.8428'
CVB = '-0.0009 0.0000 316.4270 83.4453'   # Club GLOBALS stacked lockup

def inner(name):
    s = (LOGOS / f'{name}.svg').read_text()
    s = re.sub(r'<\?xml[^>]*\?>', '', s)
    s = re.sub(r'<title>.*?</title>|<desc>.*?</desc>', '', s, flags=re.S)
    m = re.search(r'<svg[^>]*>(.*)</svg>', s, re.S)
    return m.group(1).strip()

SYMS = {
    'lk-gk-black': ('globals-wordmark-goldknot-black', LVB),
    'lk-gk-white': ('globals-wordmark-goldknot-white', LVB),
    'lk-black': ('globals-wordmark-black', LVB),
    'lk-white': ('globals-wordmark-white', LVB),
    'knot-gold': ('globals-knot-gold', KVB),
    'knot-white': ('globals-knot-white', KVB),
    'knot-black': ('globals-knot-black', KVB),
    'knot-colour': ('globals-knot-colour', KVB),
    'club-colour': ('club-globals-lockup-colour', CVB),
}

FONT_CSS = """
@font-face{font-family:'Urbanist';font-weight:500;src:url('../fonts/urbanist-latin-500-normal.woff2') format('woff2');}
@font-face{font-family:'Urbanist';font-weight:600;src:url('../fonts/urbanist-latin-600-normal.woff2') format('woff2');}
@font-face{font-family:'Urbanist';font-weight:700;src:url('../fonts/urbanist-latin-700-normal.woff2') format('woff2');}
text{font-family:'Urbanist','DejaVu Sans',sans-serif;font-weight:500;fill:#000;font-variant-numeric:tabular-nums}
.t{font-size:30px;font-weight:600;letter-spacing:-0.01em}
.s{font-size:16px;fill:#686A6B}
.l{font-size:15px}.lb{font-size:15px;font-weight:600}.lw{font-size:15px;fill:#FFFFFF}.lbw{font-size:15px;font-weight:600;fill:#FFFFFF}
.cap{font-size:13px;fill:#686A6B}.capw{font-size:13px;fill:#B9BDC4}
.h{font-size:20px;font-weight:600}
.dim{stroke:#C03C03;stroke-width:1.5;fill:none}.dimt{font-size:14px;font-weight:600;fill:#C03C03}
.dash{stroke:#C03C03;stroke-width:2;stroke-dasharray:8 6;fill:none}
.dashw{stroke:#FFFFFF;stroke-width:2;stroke-dasharray:8 6;fill:none}
.axis{stroke:#686A6B;stroke-width:1;stroke-dasharray:4 4;fill:none}
.no{stroke:#C03C03;stroke-width:6;stroke-linecap:round;fill:none}
.frame{fill:none;stroke:#D6D8D6;stroke-width:1}
.eyebrow{font-size:11px;font-weight:600;letter-spacing:0.2em;text-transform:uppercase}
"""

class SVG:
    def __init__(self, title, w=1600, h=1000):
        self.w, self.h, self.title = w, h, title
        self.defs, self.body = [], []
        self.used = set()
    def sym(self, key):
        if key not in self.used:
            name, vb = SYMS[key]
            self.defs.append(f'<symbol id="{key}" viewBox="{vb}" overflow="visible">{inner(name)}</symbol>')
            self.used.add(key)
    def use(self, key, x, y, w, h, extra=''):
        self.sym(key)
        self.body.append(f'<use href="#{key}" x="{x:.2f}" y="{y:.2f}" width="{w:.2f}" height="{h:.2f}" {extra}/>')
    def add(self, s): self.body.append(s)
    def text(self, x, y, s, cls='l', anchor='start', extra=''):
        self.body.append(f'<text x="{x:.1f}" y="{y:.1f}" class="{cls}" text-anchor="{anchor}" {extra}>{html.escape(s)}</text>')
    def lines(self, x, y, items, cls='l', lh=22):
        for i, s in enumerate(items): self.text(x, y + i * lh, s, cls)
    def rect(self, x, y, w, h, fill='none', extra=''):
        self.body.append(f'<rect x="{x:.2f}" y="{y:.2f}" width="{w:.2f}" height="{h:.2f}" fill="{fill}" {extra}/>')
    def dim_h(self, x1, x2, y, label, above=True, cls='dim', tcls='dimt'):
        t = 6
        self.add(f'<path class="{cls}" d="M{x1:.1f} {y-t:.1f}V{y+t:.1f}M{x2:.1f} {y-t:.1f}V{y+t:.1f}M{x1:.1f} {y:.1f}H{x2:.1f}"/>')
        self.text((x1 + x2) / 2, y - 9 if above else y + 19, label, tcls, 'middle')
    def dim_v(self, x, y1, y2, label, left=True, cls='dim', tcls='dimt'):
        t = 6
        self.add(f'<path class="{cls}" d="M{x-t:.1f} {y1:.1f}H{x+t:.1f}M{x-t:.1f} {y2:.1f}H{x+t:.1f}M{x:.1f} {y1:.1f}V{y2:.1f}"/>')
        ax = x - 10 if left else x + 10
        self.text(ax, (y1 + y2) / 2 + 5, label, tcls, 'end' if left else 'start')
    def footer(self, s='GLOBALS brand manual · v1.0 · diagram · 2026-10-17'):
        self.text(64, self.h - 32, s, 'cap')
    def write(self, name):
        out = (f'<svg xmlns="http://www.w3.org/2000/svg" width="{self.w}" height="{self.h}" viewBox="0 0 {self.w} {self.h}">'
               f'<title>{html.escape(self.title)}</title><style>{FONT_CSS}</style><defs>{"".join(self.defs)}</defs>'
               f'<rect width="{self.w}" height="{self.h}" fill="#FFFFFF"/>{"".join(self.body)}</svg>')
        (HERE / f'{name}.svg').write_text(out)
        print(name, len(out), 'bytes')

def lockup_h(w): return w * LH / LW
def times(s): return s.replace('x', '×')

# ======================================================================================
def clear_space():
    d = SVG('GLOBALS clear space')
    d.text(64, 64, 'Clear space', 't')
    d.text(64, 94, 'One unit, G, is the cap height of GLOBALS in the lockup in use. Keep 1 G clear on all four sides, measured from the outermost ink.', 's')
    d.text(64, 116, 'Nothing enters the clear space: no type, no partner mark, no rule line, no edge of a photograph that is not the lockup\'s own background.', 's')
    # lockup, full colour on light (this sheet is white)
    W = 700; H = lockup_h(W); G = G_OF_H * H
    x0, y0 = 64 + G + 60, 320
    d.rect(x0 - G, y0 - G, W + 2 * G, H + 2 * G, CITRIC, 'fill-opacity="0.06"')
    d.rect(x0 - G, y0 - G, W + 2 * G, H + 2 * G, 'none', 'class="dash"')
    d.use('lk-gk-black', x0, y0, W, H)
    d.dim_v(x0 + W * 0.56, y0 - G, y0, '1 G', True)
    d.dim_v(x0 + W * 0.56, y0 + H, y0 + H + G, '1 G', True)
    d.dim_h(x0 - G, x0, y0 + H * 0.5, '1 G', True)
    d.dim_h(x0 + W, x0 + W + G, y0 + H * 0.5, '1 G', True)
    # cap-height bracket on the wordmark, outside the boundary
    bx = x0 + W + G + 28
    d.dim_v(bx, y0 + WM_TOP * H, y0 + WM_BOT * H, 'G', False)
    d.text(bx + 30, y0 + (WM_TOP + WM_BOT) / 2 * H + 5 + 18, 'cap height of GLOBALS', 'cap')
    d.text(x0 - G, y0 + H + G + 30, 'clear-space boundary: 1 G from the outermost ink, all four sides', 'cap')
    d.text(x0 - G, y0 - G - 14, 'GLOBALS lockup, full colour on light (this sheet is white). The rule is the same in every mode.', 'cap')
    # knot alone, right
    K = 190; u = K / 2
    kx, ky = 1290, 300
    d.rect(kx - u, ky - u, K + 2 * u, K + 2 * u, CITRIC, 'fill-opacity="0.06"')
    d.rect(kx - u, ky - u, K + 2 * u, K + 2 * u, 'none', 'class="dash"')
    d.use('knot-gold', kx, ky, K, K)
    d.dim_v(kx + K * 0.5, ky - u, ky, '1 unit', True)
    d.dim_h(kx + K, kx + K + u, ky + K * 0.5, '1 unit', True)
    d.dim_v(kx - u - 24, ky, ky + K / 2, '1 unit = ½ knot height', True)
    d.text(kx - u, ky + K + u + 30, 'Knot alone: the unit is half the knot height; 1 unit on all sides', 'cap')
    d.lines(64, 760, [
        'G scales with the lockup, so the rule holds at every size (A4 default lockup 50 mm wide, 10 mm tall; 1920×1080 default 320 px wide, 64 px tall).',
        'For the stacked Club GLOBALS lockup, G is the cap height of GLOBALS, the lower bold line. For a partner lock-up the clear space is 1 G around the whole pair, in addition to the 2 G gap.',
        'Do not 14: place anything inside the clear space.',
    ], 'l', 24)
    d.footer(); d.write('clear-space')

# ======================================================================================
def min_size():
    d = SVG('GLOBALS minimum sizes')
    d.text(64, 64, 'Minimum sizes', 't')
    d.text(64, 94, 'Below these sizes the three loops of the knot stop reading as separate. Screen values are CSS pixels at 1×; print values are physical. Everything on this sheet is drawn at true scale on a 96 dpi canvas.', 's')
    # ---- screen column
    sx = 64; y = 170
    d.text(sx, y, 'Screen', 'h'); y += 34
    W = FLOOR_PX; H = lockup_h(W)
    d.use('lk-gk-black', sx, y, W, H)
    d.dim_h(sx, sx + W, y + H + 14, f'{FLOOR_PX} px', False)
    d.text(sx + W + 60, y + H / 2 + 5, f'GLOBALS lockup floor: {FLOOR_PX} px wide, never narrower on any screen', 'lb')
    d.text(sx + W + 60, y + H / 2 + 25, 'Normal range: width 1/12 to 1/3 of the longest edge of the layout, default 1/6', 'cap')
    y += H + 70
    K = KA['min_screen_px']
    d.use('knot-gold', sx, y, K, K)
    d.dim_h(sx, sx + K, y + K + 14, f'{K} px', False)
    d.text(sx + W + 60, y + K / 2 + 5, f'Knot alone: {K} px minimum (the favicon size)', 'lb')
    d.text(sx + W + 60, y + K / 2 + 25, 'Default 1/12 of the longest edge: 1920×1080 → 160 px', 'cap')
    y += K + 70
    # favicon set: true-size black squares with the gold knot
    d.text(sx, y, 'Favicon and app icon: knot alone, gold on a black square, exported at', 'lb'); d.text(sx + 470, y, ', '.join(str(v) for v in FAV) + ' px', 'lb')
    y += 16; fx = sx
    for s in FAV[:4]:
        d.rect(fx, y, s, s, BLACK)
        ins = s * 0.14
        d.use('knot-gold', fx + ins, y + ins, s - 2 * ins, s - 2 * ins)
        d.text(fx + s / 2, y + 180 + 18, f'{s}', 'cap', 'middle')
        fx += s + 28
    d.text(fx + 10, y + 180 + 18, f'{FAV[4]} and {FAV[5]} px: same master, re-checked at size (not drawn)', 'cap')
    y += 180 + 50
    # sub-brand lockups
    gh = GSTF['min_height_px']; gw = round(gh * 385 / 98)
    d.rect(sx, y, gw, gh, 'none', 'class="dash"')
    d.text(sx + gw / 2, y + gh / 2 + 4, 'supplied artwork', 'cap', 'middle')
    d.dim_v(sx + gw + 12, y, y + gh, f'{gh} px', False)
    d.text(sx + gw + 90, y + gh / 2 + 5, f'GLOBALS Tech Festival lockup: minimum height {gh} px, black ground only', 'lb')
    y += gh + 40
    oh = ONTOUR['min_height_px']; ow = 150
    d.rect(sx, y, ow, oh, BLACK)
    d.text(sx + ow / 2, y + oh / 2 + 4, 'supplied artwork', 'capw', 'middle')
    d.dim_v(sx + ow + 12, y, y + oh, f'{oh} px', False)
    d.text(sx + gw + 90, y + oh / 2 + 5, f'GLOBALS On Tour lockup: minimum height {oh} px (native {ONTOUR["native_height_px"]} px), dark only', 'lb')
    # ---- print column
    px = 900; y = 170
    d.text(px, y, 'Print', 'h'); y += 34
    W = FLOOR_MM * MM; H = lockup_h(W)
    d.use('lk-gk-black', px, y, W, H)
    d.dim_h(px, px + W, y + H + 14, f'{FLOOR_MM} mm', False)
    d.text(px + W + 60, y + H / 2 + 5, f'GLOBALS lockup floor: {FLOOR_MM} mm wide (A4 and A5 sit on the floor)', 'lb')
    y += H + 70
    K = KA['min_print_mm'] * MM
    d.use('knot-gold', px, y, K, K)
    d.dim_h(px, px + K, y + K + 14, f'{KA["min_print_mm"]} mm', False)
    d.text(px + W + 60, y + K / 2 + 5, f'Knot alone: {KA["min_print_mm"]} mm minimum; default 1/12 of the longest edge (A4 25 mm)', 'lb')
    y += K + 70
    gh = GSTF['min_height_mm'] * MM; gw = gh * 385 / 98
    d.rect(px, y, gw, gh, 'none', 'class="dash"')
    d.text(px + gw / 2, y + gh / 2 + 4, 'supplied artwork', 'cap', 'middle')
    d.dim_v(px + gw + 12, y, y + gh, f'{GSTF["min_height_mm"]} mm', False)
    d.text(px + gw + 90, y + gh / 2 + 5, f'GLOBALS Tech Festival lockup: minimum height {GSTF["min_height_mm"]} mm', 'lb')
    y += gh + 60
    # size table
    d.text(px, y, 'Lockup width by format: default 1/6 of the longest edge, minimum 1/12, maximum 1/3; height = width ÷ 5', 'lb'); y += 26
    rows = [('A1 841×594', 'A1'), ('A2 594×420', 'A2'), ('A3 420×297', 'A3'), ('A4 297×210', 'A4'), ('A5 210×148', 'A5')]
    cols = [px, px + 150, px + 300, px + 450, px + 600]
    for cx, hd in zip(cols, ['Format', 'Default', 'Minimum', 'Maximum', 'Height']): d.text(cx, y, hd, 'cap')
    y += 22
    for label, k in rows:
        r = MS[k]
        vals = [label, f'{r["default_width_mm"]} mm', f'{r["min_width_mm"]} mm' + (' (floor)' if r['min_width_mm'] == 30 and k in ('A4', 'A5') else ''), f'{r["max_width_mm"]} mm', f'{r["height_mm"]} mm']
        for cx, v in zip(cols, vals): d.text(cx, y, v, 'l')
        y += 22
    r = MS['1920x1080']
    for cx, v in zip(cols, ['1920×1080 px', f'{r["default_width_px"]} px', f'{r["min_width_px"]} px', f'{r["max_width_px"]} px', f'{r["height_px"]} px']): d.text(cx, y, v, 'l')
    y += 22
    d.text(px, y + 8, 'Club GLOBALS stacked lockup: same height as the GLOBALS lockup at that format', 'cap')
    d.text(px, y + 26, '(A4 10 mm, 1920×1080 64 px); its width follows.', 'cap')
    d.text(64, 940, 'Do not 7: use the mark below its minimum size. On Tour and GLOBALS Tech Festival are supplied artwork; never rebuilt from type.', 'l')
    d.footer(); d.write('min-size')

# ======================================================================================
def partner_box(d, x, y, w, h, dark=False, label='PARTNER MARK', sub='black or white only'):
    d.rect(x, y, w, h, WHITE if dark else BLACK, 'rx="4"')
    d.text(x + w / 2, y + h / 2 - 2, label, 'lb' if dark else 'lbw', 'middle')
    d.text(x + w / 2, y + h / 2 + 16, sub, 'cap' if dark else 'capw', 'middle')

def lockup_grammar():
    d = SVG('GLOBALS partner lock-up grammar')
    d.text(64, 64, 'Partner lock-up grammar', 't')
    d.text(64, 94, 'GLOBALS × PARTNER on GLOBALS surfaces: host first. The separator is a multiplication sign (×, U+00D7) in Urbanist 500 at the cap height of the smaller mark, centred in a gap of 2 G.', 's')
    d.text(64, 116, 'G = cap height of GLOBALS in the lockup in use. The partner mark is never taller than the GLOBALS knot, and on GLOBALS surfaces it is reproduced in black or white only.', 's')
    # ---- horizontal
    d.text(64, 180, 'Horizontal (landscape formats, headers)', 'h')
    W = 400; H = lockup_h(W); G = G_OF_H * H
    x0, y0 = 64 + G + 130, 250
    pw = 190; ph = H  # partner at knot height = the maximum
    px0 = x0 + W + 2 * G
    cy = y0 + H / 2
    # clear space around the pair
    d.rect(x0 - G, y0 - G, (px0 + pw) - x0 + 2 * G, H + 2 * G, 'none', 'class="dash"')
    d.add(f'<line x1="{x0-G-30:.1f}" y1="{cy:.1f}" x2="{px0+pw+G+30:.1f}" y2="{cy:.1f}" class="axis"/>')
    d.use('lk-gk-black', x0, y0, W, H)
    d.text(x0 + W + G, cy + G * 0.36, '×', 'l', 'middle', f'style="font-size:{G:.0f}px;font-weight:500"')
    partner_box(d, px0, y0, pw, ph)
    d.dim_h(x0 + W, px0, y0 + H + G + 18, '2 G, × centred', False)
    d.dim_v(px0 + pw + G + 26, y0, y0 + ph, '≤ knot height', False)
    d.text(px0 + pw + G + 36, cy + 24, '(knot height, cap height of GLOBALS, or ¾ of either)', 'cap')
    d.text(x0 - G, y0 + H + G + 37, 'clear space 1 G around the whole pair, in addition to the gap', 'cap')
    d.text(x0 - G - 36, cy - 8, 'one centre axis', 'cap', 'end')
    # ---- stacked
    sy = 470
    d.text(64, sy, 'Stacked (portrait formats, square social)', 'h')
    W2 = 300; H2 = lockup_h(W2); G2 = G_OF_H * H2
    sx0 = 64 + 120; sy0 = sy + 60
    cx = sx0 + W2 / 2
    pw2 = 170; ph2 = H2
    py0 = sy0 + H2 + 2 * G2
    d.rect(sx0 - G2, sy0 - G2, W2 + 2 * G2, (py0 + ph2) - sy0 + 2 * G2, 'none', 'class="dash"')
    d.add(f'<line x1="{cx:.1f}" y1="{sy0-G2-24:.1f}" x2="{cx:.1f}" y2="{py0+ph2+G2+24:.1f}" class="axis"/>')
    d.use('lk-gk-black', sx0, sy0, W2, H2)
    d.text(cx, sy0 + H2 + G2 + G2 * 0.36, '×', 'l', 'middle', f'style="font-size:{G2:.0f}px;font-weight:500"')
    partner_box(d, cx - pw2 / 2, py0, pw2, ph2)
    d.dim_v(sx0 + W2 + G2 + 20, sy0 + H2, py0, '2 G, × centred', False)
    d.dim_v(sx0 - G2 - 20, py0, py0 + ph2, '≤ knot height', True)
    # ---- rules
    rx = 820; ry = 500
    d.text(rx, ry, 'Rules', 'h')
    d.lines(rx, ry + 34, [
        '• Separator: × (U+00D7), Urbanist 500, at the cap height of the smaller mark, centred in the gap.',
        '  Never x, +, and, a slash or a rule line.',
        '• Gap: 2 G in total, the × centred in it; horizontal in the horizontal version, vertical in the stacked one.',
        '• Order: host first. On GLOBALS surfaces GLOBALS × Partner; on the partner\'s surfaces its own rule applies.',
        '• Scale: on GLOBALS surfaces the partner mark is never taller than the GLOBALS knot. Size it to the',
        '  knot height, the cap height of GLOBALS, or ¾ of either, by the balance of the relationship.',
        '• Colour: on globals.co and GLOBALS black surfaces every partner mark is black or white only',
        '  (founder rule 2026-09-29). No partner colour on a GLOBALS surface.',
        '• Position: bottom-left (default) or bottom-right. Never top-centre, never centred mid-page,',
        '  never in the hero headline area.',
        '• Several partners: no chained lock-ups. A logo strip on the pure-black band, black and white,',
        '  equal cap heights, 2 G apart, no separators, ordered by tier then alphabetically.',
        '• Clear space: 1 G around the whole pair, in addition to the gap.',
        '• The partner mark is its supplied file, never its name set in Urbanist.',
    ], 'l', 24)
    d.text(64, 940, 'Co-branding with The Social Hub follows this grammar with TSH\'s own measures on TSH surfaces: see the chapter 10 diagram.', 'l')
    d.footer(); d.write('lockup-grammar')

# ======================================================================================
def margin_dim(d, x0, m, y):
    d.add(f'<path class="dim" d="M{x0-60:.1f} {y:.1f}H{x0+m:.1f}M{x0:.1f} {y-6:.1f}V{y+6:.1f}M{x0+m:.1f} {y-6:.1f}V{y+6:.1f}"/>')
    d.text(x0 - 8, y - 8, 'margin', 'dimt', 'end')
    d.text(x0 - 8, y + 20, '= lockup ÷ 4', 'dimt', 'end')

def layout_families():
    d = SVG('GLOBALS layout families')
    d.text(64, 64, 'Three layout families for print and social', 't')
    d.text(64, 94, 'Mark size per format: lockup width 1/6 of the longest edge (A4 50 mm, 1920×1080 320 px). Margin = lockup width ÷ 4 (A4 12.5 mm, 1920×1080 80 px). Print bleed 3 mm; none on screen.', 's')
    d.text(64, 116, 'Shown on an A-series portrait sheet: the lockup is 1/6 of the long edge and the margin is a quarter of the lockup width. The same numbers apply to every family.', 's')
    PW, PH = 400, 566
    lw = PH / 6; lh = lockup_h(lw); m = lw / 4
    y0 = 170
    panels = [(140, 'Black Panel'), (640, 'Photo Scrim'), (1140, 'Light Sheet')]
    for (x0, name) in panels:
        d.text(x0, y0 - 14, f'({"abc"[panels.index((x0, name))]}) {name}', 'h')
    # (a) Black Panel
    x0 = 140
    d.rect(x0, y0, PW, PH, BLACK)
    d.text(x0 + m, y0 + m + 10, 'GLOBALS ON TOUR · BARCELONA', 'eyebrow', 'start', 'style="fill:#FFFFFF"')
    d.rect(x0 + m, y0 + m + 22, lw, 2, GOLD)
    d.text(x0 + m, y0 + m + 80, 'Pitch on', 'l', 'start', 'style="font-size:52px;font-weight:700;fill:#FFFFFF;letter-spacing:-0.035em"')
    d.text(x0 + m, y0 + m + 134, 'the Bus', 'l', 'start', 'style="font-size:52px;font-weight:700;fill:#FFFFFF;letter-spacing:-0.035em"')
    d.text(x0 + m, y0 + m + 176, '14 OCTOBER · 18:30', 'eyebrow', 'start', f'style="fill:{CITRIC}"')
    d.text(x0 + m, y0 + m + 200, 'The Social Hub Poblenou', 'lw')
    d.use('lk-gk-white', x0 + m, y0 + PH - m - lh, lw, lh)
    margin_dim(d, x0, m, y0 + PH - m - lh / 2)
    d.dim_v(x0 + m + lw + 14, y0 + PH - m, y0 + PH, 'lockup ÷ 4', False)
    d.dim_h(x0 + m, x0 + m + lw, y0 + PH - m - lh - 14, 'lockup width', True)
    d.lines(x0, y0 + PH + 34, [
        'Black #000000 edge to edge. Headline white, 600 or 700,',
        'left, under eight words. Gold rule 2 pt / 2 px, one lockup',
        'width long, under the headline or eyebrow. Lockup gold on',
        'dark, bottom-left at the margin. One citric element at most.',
        'Spectrum only as one chip or strip, never a background.',
        'Use: signage, roll-ups, screens, slide covers, social cards.',
    ], 'cap', 19)
    # (b) Photo Scrim
    x0 = 640
    d.add(f'''<defs>
<linearGradient id="scrimV" x1="0" y1="0" x2="0" y2="1">
 <stop offset="0" stop-color="#08090B" stop-opacity=".62"/><stop offset=".18" stop-color="#08090B" stop-opacity=".22"/>
 <stop offset=".38" stop-color="#08090B" stop-opacity=".06"/><stop offset=".66" stop-color="#08090B" stop-opacity=".46"/>
 <stop offset=".88" stop-color="#08090B" stop-opacity=".88"/><stop offset="1" stop-color="#08090B" stop-opacity=".96"/></linearGradient>
<linearGradient id="scrimL" x1="0" y1="0" x2="1" y2="0">
 <stop offset="0" stop-color="#08090B" stop-opacity=".77"/><stop offset=".40" stop-color="#08090B" stop-opacity=".32"/>
 <stop offset=".72" stop-color="#08090B" stop-opacity="0"/></linearGradient>
<clipPath id="pclip"><rect x="{x0}" y="{y0}" width="{PW}" height="{PH}"/></clipPath></defs>''')
    d.rect(x0, y0, PW, PH, '#7A8088')
    # photo stand-in: a few soft shapes so the scrim is visible
    d.add(f'<g clip-path="url(#pclip)"><circle cx="{x0+300}" cy="{y0+200}" r="150" fill="#9AA0A6"/><circle cx="{x0+110}" cy="{y0+330}" r="110" fill="#5E646B"/><rect x="{x0}" y="{y0+380}" width="{PW}" height="{PH-380}" fill="#4A5057"/><text x="{x0+PW/2}" y="{y0+PH/2}" class="l" text-anchor="middle" fill="#2B2F34">own event photo, object-fit: cover</text></g>')
    d.rect(x0, y0, PW, PH, 'url(#scrimV)')
    d.rect(x0, y0, PW, PH, 'url(#scrimL)')
    d.use('lk-gk-white', x0 + m, y0 + m, lw, lh)
    margin_dim(d, x0, m, y0 + m + lh / 2)
    d.dim_v(x0 + m + lw + 14, y0, y0 + m, 'lockup ÷ 4', False)
    ty = y0 + PH - m
    d.rect(x0 + m, ty - 150, 64 * 0.55, 4 * 0.55 + 1, CITRIC)
    d.text(x0 + m, ty - 126, 'GLOBALS ON TOUR · 14 OCTOBER', 'eyebrow', 'start', f'style="fill:{CITRIC}"')
    d.text(x0 + m, ty - 78, 'Pitch on', 'l', 'start', 'style="font-size:44px;font-weight:700;fill:#FFFFFF;letter-spacing:-0.035em"')
    d.text(x0 + m, ty - 34, 'the Bus', 'l', 'start', 'style="font-size:44px;font-weight:700;fill:#FFFFFF;letter-spacing:-0.035em"')
    d.text(x0 + m, ty - 8, 'One context line in white at 92%', 'lw', 'start', 'style="fill-opacity:.92"')
    d.text(x0 + PW - m, ty - 8, 'SIGN-OFF 62%', 'eyebrow', 'end', 'style="fill:#FFFFFF;fill-opacity:.62;letter-spacing:.22em"')
    d.lines(x0, y0 + PH + 34, [
        'Full-bleed own photograph (never stock). Two scrim layers:',
        'vertical 180° rgba(8,9,11) .62 → .22 at 18% → .06 at 38% → .46',
        'at 66% → .88 at 88% → .96; left wash 90° .74–.80 → .30–.34 at',
        '40% → 0 at 72%. White text ≥ 4.5:1 at its worst pixel; never',
        'fades to white or grey. Lockup top-left at the margin; type',
        'block bottom-left with a 64×4 px citric tick. Use: banners,',
        'share cards, blog covers, On Tour cards, hero sections.',
    ], 'cap', 19)
    # (c) Light Sheet
    x0 = 1140
    d.rect(x0, y0, PW, PH, GREY)
    d.use('lk-gk-black', x0 + m, y0 + m, lw, lh)
    margin_dim(d, x0, m, y0 + m + lh / 2)
    d.dim_v(x0 + m + lw + 14, y0, y0 + m, 'lockup ÷ 4', False)
    ey = y0 + m + lh + 50
    d.text(x0 + m, ey, 'BARCELONA DELEGATION · 14 TO 16 OCTOBER', 'eyebrow', 'start', f'style="fill:{INK}"')
    d.rect(x0 + m, ey + 10, 40, 2, CITRIC)
    d.text(x0 + m, ey + 56, 'Three days,', 'l', 'start', f'style="font-size:40px;font-weight:600;fill:{INK}"')
    d.text(x0 + m, ey + 98, 'nine rooms', 'l', 'start', f'style="font-size:40px;font-weight:600;fill:{INK}"')
    cy = ey + 130
    for i, (t, v) in enumerate([('09:30', 'Welcome · The Social Hub Poblenou'), ('11:00', 'Investor round table · Room 2'), ('14:30', 'Pitch on the Bus · Plaça de les Glòries')]):
        d.rect(x0 + m, cy + i * 62, PW - 2 * m, 50, WHITE, 'rx="6"')
        d.text(x0 + m + 14, cy + i * 62 + 31, t, 'lb', 'start', f'style="fill:{INK}"')
        d.text(x0 + m + 70, cy + i * 62 + 31, v, 'cap', 'start', f'style="fill:{INK500}"')
    d.lines(x0, y0 + PH + 34, [
        'Light grey #EAEBEA sheet, text black #16171B or #000000,',
        'white cards at 14 px / 4 mm radius. Lockup full colour on',
        'light, top-left at the margin. Headline black 600; eyebrow',
        'with a citric rule; body 500. Citric only as fills; orange or',
        'gold that is read is #C03C03 or #876500. One accent per sheet.',
        'A4 document margins 15 mm sides, 20 mm top and bottom.',
        'Use: one-pagers, programmes, fact sheets, briefs, menus.',
    ], 'cap', 19)
    d.text(64, 915, 'Lockup width / margin per format: A1 140 / 35 mm · A2 100 / 25 · A3 70 / 18 · A4 50 / 12.5 · A5 35 / 9 · 1920×1080 320 / 80 px · 1080×1080 240 / 80 · 1080×1920 240 / 80 plus platform safe zones.', 'l')
    d.text(64, 940, 'A black panel inside a light sheet (for the On Tour lockup, which has no light variant) is a Black Panel element on a Light Sheet, with the panel\'s own margin equal to the sheet margin.', 'l')
    d.footer(); d.write('layout-families')

# ======================================================================================
def tsh_box(d, x, y, s, dark=False):
    cls = 'dashw' if dark else 'dash'
    d.rect(x, y, s, s, 'none', f'class="{cls}"')
    c1 = 'lbw' if dark else 'lb'; c2 = 'capw' if dark else 'cap'
    d.text(x + s / 2, y + s / 2 - 10, 'TSH MARK', c1, 'middle')
    d.text(x + s / 2, y + s / 2 + 10, 'official file, never redrawn', c2, 'middle')
    d.text(x + s / 2, y + s / 2 + 28, 'Solid White' if dark else 'Outlined / Solid Black', c2, 'middle')

def tsh_lockup():
    d = SVG('GLOBALS × THE SOCIAL HUB lock-up')
    d.text(64, 64, 'GLOBALS × THE SOCIAL HUB', 't')
    d.text(64, 94, 'Partner grammar on both brands\' surfaces, never "GLOBALS AT The Social Hub" (AT is reserved for TSH-owned sub-brands). GLOBALS reads first on both: TSH puts the partner first, GLOBALS puts the host first.', 's')
    d.text(64, 116, 'The TSH mark is never drawn here: it is the official file from TSH Bynder in one of its three versions (Outlined, Solid Black, Solid White), upright and unaltered. Schematic placeholders below.', 's')
    # ---- row 1: TSH surface
    y0 = 160
    d.text(64, y0 + 24, 'On The Social Hub surfaces (TSH is host): GLOBALS mark mono black on white, never taller than the TSH mark', 'h')
    PX, PY, PWd, PHt = 64, y0 + 44, 1472, 300
    d.rect(PX, PY, PWd, PHt, WHITE, 'class="frame"')
    S = 150                                  # TSH mark height
    H = S * 0.75; W = H * LW / LH; G = G_OF_H * H   # GLOBALS at ¾ (default for residency material)
    gap = 2 * G                              # = two stacked SOCIAL at matched height
    x0 = PX + 120; cy = PY + PHt / 2 - 10
    d.add(f'<line x1="{x0-40:.1f}" y1="{cy:.1f}" x2="{x0+W+gap+S+40:.1f}" y2="{cy:.1f}" class="axis"/>')
    d.use('lk-black', x0, cy - H / 2, W, H)
    # the two stacked SOCIAL measures (faint guide), then the × on top
    for i in (0, 1):
        d.rect(x0 + W + gap / 2 - 34, cy - G + i * G, 68, G, '#F4F4F4', 'class="axis"')
        d.text(x0 + W + gap / 2, cy - G + i * G + 12, 'SOCIAL', 'cap', 'middle', 'style="font-size:10px;fill:#84888F;letter-spacing:.08em"')
    d.text(x0 + W + gap / 2, cy + G * 0.36, '×', 'l', 'middle', f'style="font-size:{G:.0f}px;font-weight:500"')
    tsh_box(d, x0 + W + gap, cy - S / 2, S)
    d.dim_h(x0 + W, x0 + W + gap, cy + S / 2 + 24, 'gap = two stacked SOCIAL (TSH logotype at the size in use) = 2 G at matched height', False)
    d.dim_v(x0 + W + gap + S + 30, cy - S / 2, cy + S / 2, '1× TSH mark', False)
    d.dim_v(x0 - 30, cy - H / 2, cy + H / 2, 'GLOBALS ¾ ×', True)
    d.lines(x0 + W + gap + S + 170, cy - 90, [
        'Scale: GLOBALS ≤ TSH mark, in quarter steps of its height:',
        '½, ¾ or 1× (default ¾ for residency material, 1× for a joint event).',
        'Mode: mono black on white; mono white on a TSH colour block',
        'or photo. Never gold on white (2.77:1).',
        'Position: bottom-left, bottom-centre, bottom-right, middle-right,',
        'top-right only. The TSH mark keeps its grid position, ½ its size',
        'from the edge; the GLOBALS mark inherits that padding.',
        'Typeface: Hour (the host\'s); GLOBALS is present as its mark only.',
    ], 'l', 22)
    # ---- row 2: GLOBALS surface
    y1 = PY + PHt + 50
    d.text(64, y1 + 24, 'On GLOBALS surfaces (GLOBALS is host): the inverse. TSH mark never taller than the GLOBALS knot, black or white only', 'h')
    QX, QY, QW, QH = 64, y1 + 44, 1472, 300
    d.rect(QX, QY, QW, QH, BLACK)
    H2 = 120; W2 = H2 * LW / LH; G2 = G_OF_H * H2; gap2 = 2 * G2
    S2 = H2                                  # TSH mark at the knot height = the maximum
    x1 = QX + 120; cy2 = QY + QH / 2 - 10
    d.add(f'<line x1="{x1-40:.1f}" y1="{cy2:.1f}" x2="{x1+W2+gap2+S2+40:.1f}" y2="{cy2:.1f}" class="axis" stroke="#84888F"/>')
    d.rect(x1 - G2, cy2 - H2 / 2 - G2, W2 + gap2 + S2 + 2 * G2, H2 + 2 * G2, 'none', 'class="dashw" stroke-opacity=".5"')
    d.use('lk-gk-white', x1, cy2 - H2 / 2, W2, H2)
    d.text(x1 + W2 + gap2 / 2, cy2 + G2 * 0.36, '×', 'lw', 'middle', f'style="font-size:{G2:.0f}px;font-weight:500"')
    tsh_box(d, x1 + W2 + gap2, cy2 - S2 / 2, S2, dark=True)
    d.dim_h(x1 + W2, x1 + W2 + gap2, cy2 + H2 / 2 + 24, '2 G, × centred', False, 'dim', 'dimt')
    d.dim_v(x1 + W2 + gap2 + S2 + 30, cy2 - S2 / 2, cy2 + S2 / 2, '≤ knot height', False)
    d.text(x1 - G2, cy2 - H2 / 2 - G2 - 10, 'clear space 1 G around the pair', 'capw')
    d.lines(x1 + W2 + gap2 + S2 + 170, cy2 - 90, [
        'GLOBALS × THE SOCIAL HUB, GLOBALS first as host.',
        'TSH mark: Solid White on black, Solid Black on light grey',
        '(Outlined allowed on light grey). Never taller than the knot;',
        'never in TSH colour on a GLOBALS surface.',
        'Position bottom-left or bottom-right. Clear space 1 G.',
        'Typeface: Urbanist (the host\'s); TSH is present as its mark only.',
        'Shared surfaces: solids only, no gradient; body copy black',
        'or white; no citric beside TSH Orange or Red, no baby beside',
        'TSH Pink or Sand.',
    ], 'lw', 22)
    d.text(64, 940, 'Lock-up grammar per chapter 3; TSH measures per TSH guide slides 019, 024, 025, 028, 065, 086. Approval: GLOBALS owner checks chapter 10, TSH contact reviews against their guide.', 'l')
    d.footer(); d.write('tsh-lockup')

# ======================================================================================
def misuse():
    d = SVG('GLOBALS mark: do not')
    d.text(64, 64, 'Do not', 't')
    d.text(64, 94, 'The fourteen things never done with the mark (chapter 2), and the four modes that are the only correct ones. The supplied files are the only source; never rebuild, recolour or decorate them.', 's')
    d.add(f'''<defs>
<linearGradient id="badgrad" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="{CITRIC}"/><stop offset="1" stop-color="{BABY}"/></linearGradient>
<filter id="shadow" x="-20%" y="-20%" width="140%" height="160%"><feDropShadow dx="0" dy="6" stdDeviation="6" flood-color="#000" flood-opacity=".6"/></filter>
<pattern id="busy" width="18" height="18" patternUnits="userSpaceOnUse"><rect width="18" height="18" fill="#5B6168"/><circle cx="4" cy="4" r="4" fill="#C9CED3"/><rect x="9" y="9" width="7" height="7" fill="#2A2E33"/></pattern>
<pattern id="knotpat" width="36" height="36" patternUnits="userSpaceOnUse"><use href="#knot-gold" x="2" y="2" width="32" height="32"/></pattern>
<clipPath id="circ"><circle cx="0" cy="0" r="1"/></clipPath>
</defs>''')
    d.sym('knot-gold')
    TW, TH, GX, GY = 280, 230, 16, 16
    cols, rows = 5, 3
    ox, oy = 64, 130
    LWd = 170; LHt = lockup_h(LWd)
    items = []
    def tile(i, caption, draw, dark=False):
        c, r = i % cols, i // cols
        x, y = ox + c * (TW + GX), oy + r * (TH + GY)
        d.rect(x, y, TW, TH - 46, BLACK if dark else GREY, 'rx="6"')
        d.add(f'<clipPath id="tc{i}"><rect x="{x}" y="{y}" width="{TW}" height="{TH-46}" rx="6"/></clipPath>')
        d.add(f'<g clip-path="url(#tc{i})">')
        draw(x, y, TW, TH - 46)
        d.add('</g>')
        if caption:
            d.add(f'<line x1="{x+22}" y1="{y+TH-46-22}" x2="{x+TW-22}" y2="{y+22}" class="no"/>')
        for j, line in enumerate(caption):
            d.text(x, y + TH - 26 + j * 18, line, 'lb' if j == 0 else 'cap')
    def centre(x, y, w, h): return x + (w - LWd) / 2, y + (h - 46 - LHt) / 2 + 10
    # 1 stretch
    def t1(x, y, w, h):
        cx, cy = centre(x, y, w, h)
        d.add(f'<g transform="translate({cx-30:.1f} {cy:.1f}) scale(1.35 1)">'); d.use('lk-gk-black', 0, 0, LWd, LHt); d.add('</g>')
    tile(0, ['3. Stretch, condense or skew', 'Scale proportionally only.'], t1)
    # 2 recolour
    # simpler: draw a citric knot by recolouring the black knot symbol via CSS fill override is not possible on <use>; use a tinted copy
    def t2b(x, y, w, h):
        cx, cy = centre(x, y, w, h)
        d.use('lk-black', cx, cy, LWd, LHt)
        d.rect(cx - 2, cy - 2, LWd * KNOT_W_OF_W + 4, LHt + 4, GREY)
        knot = inner('globals-knot-black').replace('#000000', CITRIC)
        d.add(f'<svg x="{cx:.1f}" y="{cy:.1f}" width="{LWd*KNOT_W_OF_W:.1f}" height="{LHt:.1f}" viewBox="{KVB}">{knot}</svg>')
    tile(1, ['1. Recolour outside the four modes', 'No citric knot, no sky wordmark, no two-tone.'], t2b)
    # 3 gradient on the mark
    def t3(x, y, w, h):
        cx, cy = centre(x, y, w, h)
        d.use('lk-black', cx, cy, LWd, LHt)
        d.add(f'<svg x="{cx:.1f}" y="{cy:.1f}" width="{LWd*KNOT_W_OF_W:.1f}" height="{LHt:.1f}" viewBox="{KVB}">{inner("globals-knot-black").replace("#000000", "url(#badgrad)")}</svg>')
    tile(2, ['2. Gradient on the knot or wordmark', 'The meshes are for display type and strips.'], t3)
    # 4 rotate
    def t4(x, y, w, h):
        cx, cy = centre(x, y, w, h)
        d.add(f'<g transform="rotate(-12 {cx+LWd/2:.1f} {cy+LHt/2:.1f})">'); d.use('lk-gk-black', cx, cy, LWd, LHt); d.add('</g>')
    tile(3, ['4. Rotate', '0° in every static placement.'], t4)
    # 5 shadow / outline
    def t5(x, y, w, h):
        cx, cy = centre(x, y, w, h)
        d.add('<g filter="url(#shadow)">'); d.use('lk-gk-black', cx, cy, LWd, LHt); d.add('</g>')
        outl = inner('globals-knot-black').replace('fill="#000000"', 'fill="none" stroke="#000000" stroke-width="2.5"')
        d.add(f'<svg x="{cx-26:.1f}" y="{cy-30:.1f}" width="{LWd*KNOT_W_OF_W*0.6:.1f}" height="{LHt*0.6:.1f}" viewBox="{KVB}">{outl}</svg>')
    tile(4, ['5. Shadow, glow, bevel or outline', 'On a photo use a scrim, not an effect.'], t5)
    # 6 busy photo
    def t6(x, y, w, h):
        d.rect(x, y, w, h, 'url(#busy)')
        cx, cy = centre(x, y, w, h); d.use('lk-gk-white', cx, cy, LWd, LHt)
    tile(5, ['6. Busy photo without a scrim', 'Knot and wordmark ≥ 4.5:1 on any ground.'], t6)
    # 7 below min size
    def t7(x, y, w, h):
        sw = 72; sh = lockup_h(sw)
        d.use('lk-gk-black', x + (w - sw) / 2, y + (h - sh) / 2, sw, sh)
        d.text(x + w / 2, y + h / 2 + 34, f'{sw} px wide: below the {FLOOR_PX} px floor', 'cap', 'middle')
    tile(6, ['7. Below the minimum size', f'Lockup floor {FLOOR_PX} px / {FLOOR_MM} mm; knot {KA["min_screen_px"]} px / {KA["min_print_mm"]} mm.'], t7)
    # 8 retired marks
    def t8(x, y, w, h):
        cx = x + w / 2 - 60; cy = y + h / 2 - 10
        d.add(f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="34" fill="#F26322"/>')
        d.text(cx, cy + 56, '2017 symbol', 'cap', 'middle')
        d.rect(x + w / 2 + 20, cy - 34, 100, 68, WHITE, 'stroke="#D6D8D6"')
        d.text(x + w / 2 + 70, cy - 6, '2024 positive /', 'cap', 'middle'); d.text(x + w / 2 + 70, cy + 12, 'negative PNGs', 'cap', 'middle')
        d.text(x + w / 2 + 70, cy + 56, '"(OLD) DO NOT USE"', 'cap', 'middle')
    tile(7, ['8. Retired marks', '2017 symbol, 2024 PNGs, the OLD folder.'], t8)
    # 9 two lockups in one
    def t9(x, y, w, h):
        sw = 150; sh = lockup_h(sw); cw = 120; ch = cw * 83.4453 / 316.427
        d.use('lk-gk-black', x + (w - sw) / 2, y + 28, sw, sh)
        d.use('club-colour', x + (w - cw) / 2, y + 28 + sh + 18, cw, ch)
    tile(8, ['9. Two lockups as one unit', 'Never both lockups on one surface.'], t9)
    # 10 live type
    def t10(x, y, w, h):
        kh = 40; cx = x + 40; cy = y + (h - kh) / 2
        d.use('knot-gold', cx, cy, kh, kh)
        d.text(cx + kh + 14, cy + kh - 8, 'GLOBALS', 'l', 'start', 'style="font-size:34px;font-weight:700"')
        d.text(x + w / 2, cy + kh + 36, 'wordmark set in Urbanist, not the artwork', 'cap', 'middle')
    tile(9, ['10. Wordmark in live type', 'The lockup is artwork, not a word.'], t10)
    # 11 separated corners
    def t11(x, y, w, h):
        d.use('knot-gold', x + 18, y + 18, 44, 44)
        wm = ''.join(re.findall(r'<path[^>]*/>', inner('globals-wordmark-black'))[5:])
        ww = 130; wh = ww * LH / LW
        d.add(f'<svg x="{x+w-ww-18:.1f}" y="{y+h-wh-18:.1f}" width="{ww}" height="{wh:.1f}" viewBox="{LVB}"><g transform="translate(15.5512,-28.3631) scale(1.037008)">{wm}</g></svg>')
    tile(10, ['11. Knot and wordmark separated', 'Never in different corners of one surface.'], t11)
    # 12 spectrum knot on the GLOBALS wordmark
    def t12(x, y, w, h):
        cx, cy = centre(x, y, w, h)
        d.use('lk-black', cx, cy, LWd, LHt)
        d.rect(cx - 2, cy - 2, LWd * KNOT_W_OF_W + 4, LHt + 4, GREY)
        d.use('knot-colour', cx, cy, LWd * KNOT_W_OF_W, LHt)
    tile(11, ['12. Spectrum knot on GLOBALS', 'Spectrum is Club GLOBALS only.'], t12)
    # 13 crop / mask / pattern
    def t13(x, y, w, h):
        k = 110; cx = x + 40; cy = y + (h - k) / 2
        d.add(f'<clipPath id="cmask"><circle cx="{cx+k/2:.1f}" cy="{cy+k/2:.1f}" r="{k*0.38:.1f}"/></clipPath>')
        d.add(f'<circle cx="{cx+k/2:.1f}" cy="{cy+k/2:.1f}" r="{k*0.38:.1f}" fill="#FFFFFF"/>')
        d.add('<g clip-path="url(#cmask)">'); d.use('knot-gold', cx, cy, k, k); d.add('</g>')
        d.rect(x + w - 120, y + 20, 100, h - 40, 'url(#knotpat)')
    tile(12, ['13. Crop, mask or pattern fill', 'Pattern-from-logo rejected 2026-10-09.'], t13)
    # 14 clear space
    def t14(x, y, w, h):
        sw = 150; sh = lockup_h(sw); g = G_OF_H * sh
        cx = x + 24; cy = y + (h - sh) / 2 - 6
        d.rect(cx - g, cy - g, sw + 2 * g, sh + 2 * g, 'none', 'class="dash"')
        d.use('lk-gk-black', cx, cy, sw, sh)
        d.text(cx + sw + 4, cy + sh - 6, 'Partner', 'l', 'start', 'style="font-size:22px;font-weight:600"')
        d.text(cx - g, cy + sh + g + 16, 'type inside the 1 G clear space', 'cap')
    tile(13, ['14. Anything inside the clear space', '1 G on all sides, from the outermost ink.'], t14)
    # 15 the four modes (correct)
    def t15(x, y, w, h):
        hw, hh = (w - 3 * 8) / 2, (h - 3 * 8) / 2
        cells = [(BLACK, 'lk-gk-white', 'Gold on dark', 'capw'), (WHITE, 'lk-gk-black', 'Full colour on light', 'cap'),
                 (BLACK, 'lk-white', 'Mono white', 'capw'), (WHITE, 'lk-black', 'Mono black', 'cap')]
        for i, (bg, sym, lab, cls) in enumerate(cells):
            cxx = x + 8 + (i % 2) * (hw + 8); cyy = y + 8 + (i // 2) * (hh + 8)
            d.rect(cxx, cyy, hw, hh, bg, 'rx="4"')
            lw2 = hw * 0.62; lh2 = lockup_h(lw2)
            d.use(sym, cxx + (hw - lw2) / 2, cyy + (hh - lh2) / 2 - 8, lw2, lh2)
            d.text(cxx + hw / 2, cyy + hh - 8, lab, cls, 'middle')
    tile(14, [], t15)
    c, r = 14 % cols, 14 // cols
    d.text(ox + c * (TW + GX), oy + r * (TH + GY) + TH - 26, 'Do: one of the four modes, nothing else', 'lb')
    d.text(ox + c * (TW + GX), oy + r * (TH + GY) + TH - 8, 'Gold on dark is the primary mode.', 'cap')
    d.text(64, 940, 'Numbers refer to the "Do not" list in chapter 2. The list is closed: a misuse not drawn here is still a misuse when it breaks a stated rule.', 'l')
    d.footer(); d.write('misuse')

# ======================================================================================
def render():
    from playwright.sync_api import sync_playwright
    EXE = '/opt/pw-browsers/chromium-1194/chrome-linux/chrome'
    with sync_playwright() as p:
        b = p.chromium.launch(executable_path=EXE)
        ctx = b.new_context(viewport={'width': 1600, 'height': 1000}, device_scale_factor=1)
        pg = ctx.new_page()
        for name in NAMES:
            pg.goto('file://' + str(HERE / f'{name}.svg'))
            pg.wait_for_timeout(400)
            pg.evaluate('document.fonts.ready')
            pg.wait_for_timeout(200)
            pg.screenshot(path=str(HERE / f'{name}.png'), clip={'x': 0, 'y': 0, 'width': 1600, 'height': 1000})
            # 256-colour palette, dithered: a third of the size, no visible loss on flat diagram art
            from PIL import Image
            im = Image.open(HERE / f'{name}.png').convert('RGB')
            im.quantize(colors=256, method=Image.Quantize.MEDIANCUT, dither=Image.Dither.FLOYDSTEINBERG).save(HERE / f'{name}.png', optimize=True)
            print('rendered', name, (HERE / f'{name}.png').stat().st_size, 'bytes')
        b.close()

NAMES = ['clear-space', 'min-size', 'lockup-grammar', 'layout-families', 'tsh-lockup', 'misuse']
if __name__ == '__main__':
    clear_space(); min_size(); lockup_grammar(); layout_families(); tsh_lockup(); misuse()
    if '--no-render' not in sys.argv:
        render()
