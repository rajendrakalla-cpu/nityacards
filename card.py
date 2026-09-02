# -*- coding: utf-8 -*-
"""Nitya Sankalpa - panchang card renderer (HTML -> JPEG via headless Chromium)."""
import base64
import html
import os

import emblems as EM
import names as N

W, H = 1080, 1350
HERE = os.path.dirname(os.path.abspath(__file__))

# ---- themes --------------------------------------------------------------
# "brand" is the Nitya Sankalpa warm palette, sampled from the logo.
# "night" is the deep alternative; same layout, dark ground.
THEMES = {
    "brand": {
        "serif": False,
        "ground": ("#FCF4CF", "#FBEFDC", "#EED8C3"),   # cream -> sand
        "panel": "#FFFDF9",
        "panel_line": "rgba(175,65,20,.13)",
        "ink": "#28211B",          # headings
        "body": "#6A5A4C",         # labels
        "value": "#3A2E24",        # values
        "saffron": "#F09B1F",
        "orange": "#E78225",
        "terracotta": "#D35525",
        "deep": "#AF4114",         # wordmark colour
        "good": "#2F7A55",
        "bad": "#C0392B",
        "hair": "rgba(175,65,20,.14)",
        "tile": "rgba(240,155,31,.10)",
        "tile_line": "rgba(215,85,37,.22)",
        "wm_op": ".085",
        "shadow": "0 10px 34px rgba(140,80,30,.10)",
    },
    "night": {
        "serif": True,
        "ground": ("#12233D", "#0A1729", "#06101C"),
        "panel": "rgba(255,255,255,.03)",
        "panel_line": "rgba(217,180,91,.20)",
        "ink": "#F3DFA6",
        "body": "rgba(234,224,200,.80)",
        "value": "#F3DFA6",
        "saffron": "#D9B45B",
        "orange": "#D9B45B",
        "terracotta": "#D9B45B",
        "deep": "#D9B45B",
        "good": "#8FC9A0",
        "bad": "#E0806B",
        "hair": "rgba(217,180,91,.13)",
        "tile": "rgba(217,180,91,.07)",
        "tile_line": "rgba(217,180,91,.26)",
        "wm_op": ".05",
        "shadow": "none",
    },
}
THEME = os.environ.get("NP_THEME", "brand")

DEITY_DIR = os.path.join(HERE, "assets", "deities")
LOGO_FULL = os.path.join(HERE, "assets", "logo.png")
LOGO_MARK = os.path.join(HERE, "assets", "logo_mark.png")
BRAND = "Nitya Sankalpa"
HANDLE = "@nityasankalpa"

_cache = {}


def deity_img(weekday):
    """Painted portrait for the weekday's deity, or None if the asset is missing."""
    if not os.path.isdir(DEITY_DIR):
        return None
    for f in sorted(os.listdir(DEITY_DIR)):
        if f.startswith(f"{weekday}_"):
            p = os.path.join(DEITY_DIR, f)
            if p not in _cache:
                with open(p, "rb") as fh:
                    _cache[p] = "data:image/jpeg;base64," + base64.b64encode(fh.read()).decode()
            return _cache[p]
    return None


def _img(path):
    if path not in _cache:
        if not os.path.exists(path):
            _cache[path] = None
        else:
            with open(path, "rb") as f:
                _cache[path] = "data:image/png;base64," + base64.b64encode(f.read()).decode()
    return _cache[path]


def t(x):
    return x.strftime("%I:%M %p").lstrip("0") if x else "—"


def rng(pair):
    return f"{t(pair[0])} – {t(pair[1])}" if pair else "—"


RISE_SVG = """<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7"
 stroke-linecap="round" stroke-linejoin="round"><path d="M3 19h18"/><path d="M6.5 14.2a5.5 5.5 0 0 1 11 0"/>
 <path d="M12 2.4v4.2M9.4 5l2.6-2.6L14.6 5"/><path d="M2.6 11.4h1.8M19.6 11.4h1.8M5 6.2l1.3 1.3M17.7 7.5L19 6.2"/></svg>"""

SET_SVG = """<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7"
 stroke-linecap="round" stroke-linejoin="round"><path d="M3 19h18"/><path d="M6.5 14.2a5.5 5.5 0 0 1 11 0"/>
 <path d="M12 6.8V2.6M9.4 4.2L12 6.8l2.6-2.6"/><path d="M2.6 11.4h1.8M19.6 11.4h1.8M5 6.2l1.3 1.3M17.7 7.5L19 6.2"/></svg>"""

MOON_SVG = """<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7"
 stroke-linecap="round" stroke-linejoin="round"><path d="M20.5 14.6A8.6 8.6 0 1 1 9.4 3.5
 a6.8 6.8 0 0 0 11.1 11.1z"/></svg>"""


def _rows(items):
    return "".join(
        f'<div class="row {c}"><span class="lbl">{html.escape(l)}</span>'
        f'<span class="dots"></span><span class="val">{html.escape(v)}</span></div>'
        for l, v, c in items)


def build_html(p, lang, theme=None):
    T = THEMES[theme or THEME]
    L, wd = N.L, p["weekday"]
    up = L["upto"][lang]
    paksha, tithi = N.tithi_name(lang, p["tithi"])
    font = (N.FONT if T["serif"] else N.FONT_SANS)[lang]
    num_font = "'Noto Serif',serif" if T["serif"] else "'Noto Sans',sans-serif"

    tithi_val = tithi + (f" {up} {t(p['tithi_end'])}" if p["tithi_end"] else "")
    if p["tithi_next"] is not None:
        tithi_val += " · " + N.tithi_name(lang, p["tithi_next"])[1]

    nak_val = N.NAKSHATRA[lang][p["nakshatra"]]
    if p["nakshatra_end"]:
        nak_val += f" {up} {t(p['nakshatra_end'])}"
    if p["nakshatra_next"] is not None:
        nak_val += " · " + N.NAKSHATRA[lang][p["nakshatra_next"]]

    panchanga = _rows([
        (L["tithi"][lang], tithi_val, ""),
        (L["nakshatra"][lang], nak_val, ""),
        (L["yoga"][lang], N.YOGA[lang][p["yoga"]] +
         (f" {up} {t(p['yoga_end'])}" if p["yoga_end"] else ""), ""),
        (L["karana"][lang], N.KARANA[lang][p["karana"]] +
         (f" {up} {t(p['karana_end'])}" if p["karana_end"] else ""), ""),
        (L["chandra"][lang], N.RASHI[lang][p["chandra_rashi"]], ""),
    ])
    ausp = _rows([
        (L["brahma"][lang], rng(p["brahma"]), ""),
        (L["abhijit"][lang], rng(p["abhijit"]) if p["abhijit"] else L["none"][lang], ""),
        (L["amrit"][lang], rng(p["amrit"]), ""),
        (L["vijaya"][lang], rng(p["vijaya"]), ""),
    ])
    inausp = _rows([
        (L["rahu"][lang], rng(p["rahu"]), "hot"),
        (L["yamaganda"][lang], rng(p["yamaganda"]), ""),
        (L["gulika"][lang], rng(p["gulika"]), ""),
        (L["durmuhurtam"][lang], " · ".join(rng(d) for d in p["durmuhurtam"]) or "—", ""),
        (L["varjyam"][lang], rng(p["varjyam"]), ""),
    ])

    hindu = (f'{N.month_name(lang, p)} · {paksha} · '
             f'{N.SAMVATSARA[p["samvatsara"]]} {L["samvatsara"][lang]}')
    day_line = f'{N.WEEKDAY[lang][wd]} · {N.DEITY[lang][wd]}'

    dimg = deity_img(wd)
    if dimg:
        portrait = (f'<div class="deity"><img src="{dimg}" alt=""></div>')
        wm = f'<img class="wmimg" src="{dimg}" alt="">'
    else:
        portrait = f'<div class="medal">{EM.svg(wd, 42, 2.2)}</div>'
        wm = EM.svg(wd, 540, 1.2)

    mark, full = _img(LOGO_MARK), _img(LOGO_FULL)
    badge = (f'<img class="mark" src="{mark}" alt="">' if mark
             else f'<div class="mark-fallback">ॐ</div>')
    pill = (f'<img class="pill-logo" src="{mark or full}" alt="">' if (mark or full) else "")

    g0, g1, g2 = T["ground"]

    return f"""<!doctype html><html><head><meta charset="utf-8"><style>
* {{ margin:0; padding:0; box-sizing:border-box; }}
body {{ width:{W}px; height:{H}px; overflow:hidden; font-family:{font};
  color:{T["value"]}; -webkit-font-smoothing:antialiased; }}
.card {{ position:relative; width:100%; height:100%; overflow:hidden;
  background:linear-gradient(170deg, {g0} 0%, {g1} 52%, {g2} 100%);
  padding:34px 44px 26px; display:flex; flex-direction:column; }}
/* soft brand blobs */
.card::before {{ content:""; position:absolute; width:900px; height:640px; left:-160px; top:-330px;
  border-radius:50%; background:radial-gradient(circle, rgba(240,155,31,.20), transparent 68%); }}
.card::after {{ content:""; position:absolute; width:1000px; height:620px; right:-260px; bottom:-320px;
  border-radius:50%; background:radial-gradient(circle, rgba(211,85,37,.14), transparent 68%); }}

.wm {{ position:absolute; left:50%; top:56%; transform:translate(-50%,-50%);
  color:{T["terracotta"]}; opacity:{T["wm_op"]}; z-index:1; }}
.inner {{ position:relative; z-index:3; display:flex; flex-direction:column; height:100%; }}

.top {{ display:flex; align-items:center; justify-content:space-between; gap:14px; }}
.badge {{ width:64px; height:64px; border-radius:50%; background:#fff; display:flex;
  align-items:center; justify-content:center; box-shadow:{T["shadow"]};
  border:1px solid {T["panel_line"]}; }}
.mark {{ width:44px; height:44px; object-fit:contain; }}
.mark-fallback {{ font-size:30px; color:{T["deep"]}; }}
.date {{ font-family:{num_font}; font-size:23px; font-weight:700; letter-spacing:.13em;
  color:{T["ink"]}; text-transform:uppercase; text-align:right; }}
.date span {{ display:block; font-size:15px; font-weight:600; letter-spacing:.16em;
  color:{T["terracotta"]}; margin-top:3px; }}

.deity {{ width:112px; height:142px; flex:none; border-radius:12px; overflow:hidden;
  border:2px solid {T["tile_line"]}; box-shadow:{T["shadow"]}; background:{T["tile"]}; }}
.deity img {{ width:100%; height:100%; object-fit:cover; display:block; }}
.wmimg {{ width:720px; height:720px; object-fit:contain;
  filter:grayscale(.45) sepia(.55) saturate(1.05);
  -webkit-mask-image:radial-gradient(ellipse at 50% 50%, #000 26%, rgba(0,0,0,.55) 48%, transparent 70%);
  mask-image:radial-gradient(ellipse at 50% 50%, #000 26%, rgba(0,0,0,.55) 48%, transparent 70%); }}
.medal {{ width:66px; height:66px; border-radius:50%; display:flex; align-items:center;
  justify-content:center; color:{T["terracotta"]};
  border:1.5px solid {T["tile_line"]}; background:{T["tile"]}; }}

h1 {{ text-align:center; font-size:53px; line-height:1.12; color:{T["ink"]}; font-weight:800;
  margin:16px 0 0; letter-spacing:-.005em; }}
.accent {{ width:76px; height:5px; flex:none; border-radius:3px; margin:11px auto 0;
  background:linear-gradient(90deg, {T["saffron"]}, {T["terracotta"]}); }}
.top, .suns, .foot, h1 {{ flex:none; }}
.wd {{ text-align:center; font-size:28px; color:{T["terracotta"]}; margin-top:10px; font-weight:700; }}
.hindu {{ text-align:center; font-size:20px; color:{T["body"]}; margin-top:4px; line-height:1.36; }}

.suns {{ display:flex; gap:13px; margin-top:14px; }}
.sun {{ flex:1; background:{T["tile"]}; border:1px solid {T["tile_line"]};
  border-radius:14px; padding:9px 6px; text-align:center; }}
.sun svg {{ width:25px; height:25px; color:{T["terracotta"]}; }}
.sun .k {{ font-size:17px; color:{T["body"]}; margin-top:1px; }}
.sun .v {{ font-family:{num_font}; font-size:32px; color:{T["ink"]}; font-weight:800; margin-top:2px; }}

.sec {{ margin-top:12px; }}
.sec > .h {{ font-size:19px; letter-spacing:.17em; text-transform:uppercase; font-weight:700;
  display:flex; align-items:center; gap:11px; margin-bottom:4px; }}
.sec > .h i {{ flex:1; height:1px; background:{T["hair"]}; }}
.h.gold {{ color:{T["deep"]}; }} .h.grn {{ color:{T["good"]}; }} .h.red {{ color:{T["bad"]}; }}

.row {{ display:flex; align-items:baseline; gap:9px; padding:4.5px 0; font-size:25px;
  line-height:1.26; }}
.row + .row {{ border-top:1px solid {T["hair"]}; }}
.lbl {{ color:{T["body"]}; white-space:nowrap; }}
.dots {{ flex:1; border-bottom:1px dotted {T["hair"]}; transform:translateY(-6px); }}
.val {{ color:{T["value"]}; font-weight:700; text-align:right; max-width:64%; }}
.row.hot .val {{ color:{T["bad"]}; }}

.foot {{ margin-top:auto; padding-top:11px; display:flex; flex-direction:column;
  align-items:center; gap:6px; }}
.pill {{ display:flex; align-items:center; gap:11px; background:{T["panel"]};
  border:1px solid {T["panel_line"]}; border-radius:999px; padding:7px 24px 7px 14px;
  box-shadow:{T["shadow"]}; }}
.pill-logo {{ height:34px; width:auto; object-fit:contain; }}
.pill b {{ font-size:24px; font-weight:800; color:{T["ink"]}; letter-spacing:.005em; }}
.loc {{ font-size:17px; color:{T["body"]}; letter-spacing:.03em; }}
.lang {{ display:none; }}
</style></head><body><div class="card">
<div class="wm">{wm}</div>
<div class="inner">
  <div class="top">
    <div class="badge">{badge}</div>
    {portrait}
    <div class="date">{p["date"].strftime("%d %b %Y")}<span>{html.escape(N.CITY_LOCAL[lang])}</span></div>
  </div>

  <h1>{html.escape(N.TITLE[lang])}</h1>
  <div class="accent"></div>
  <div class="wd">{html.escape(day_line)}</div>
  <div class="hindu">{html.escape(hindu)}</div>

  <div class="suns">
    <div class="sun">{RISE_SVG}<div class="k">{html.escape(N.L["sunrise"][lang])}</div>
      <div class="v">{t(p["sunrise"])}</div></div>
    <div class="sun">{SET_SVG}<div class="k">{html.escape(N.L["sunset"][lang])}</div>
      <div class="v">{t(p["sunset"])}</div></div>
    <div class="sun">{MOON_SVG}<div class="k">{html.escape(N.L["moonrise"][lang])}</div>
      <div class="v">{t(p["moonrise"])}</div></div>
  </div>

  <div class="sec"><div class="h gold">{html.escape(N.L["panchanga"][lang])}<i></i></div>{panchanga}</div>
  <div class="sec"><div class="h grn">{html.escape(N.L["auspicious"][lang])}<i></i></div>{ausp}</div>
  <div class="sec"><div class="h red">{html.escape(N.L["inauspicious"][lang])}<i></i></div>{inausp}</div>

  <div class="foot">
    <div class="pill">{pill}<b>{html.escape(BRAND)}</b></div>
    <div class="loc">{html.escape(HANDLE)} · {html.escape(N.LANG_NAME[lang])} · IST</div>
  </div>
</div></div></body></html>"""


def _shoot(pg, p, lang, path, theme=None):
    pg.set_content(build_html(p, lang, theme), wait_until="load")
    pg.wait_for_timeout(300)
    over = pg.evaluate(
        "() => {const c=document.querySelector('.inner');"
        "return c.scrollHeight - c.clientHeight;}")
    pg.screenshot(path=path, type="jpeg", quality=94)
    return over


def render_all(panchangs, outdir, langs=None, theme=None, suffix=""):
    """panchangs: {lang: computed panchang dict}. Returns (paths, overflow warnings)."""
    from playwright.sync_api import sync_playwright
    langs = langs or N.LANGS
    paths, warn = [], []
    with sync_playwright() as pw:
        b = pw.chromium.launch()
        pg = b.new_page(viewport={"width": W, "height": H}, device_scale_factor=1)
        for lg in langs:
            p = panchangs[lg]
            fp = os.path.join(outdir, f"panchang_{p['date']}_{lg}{suffix}.jpg")
            over = _shoot(pg, p, lg, fp, theme)
            if over > 0:
                warn.append(f"{lg}: content overflows by {over}px")
            paths.append(fp)
        b.close()
    return paths, warn


# ---------------------------------------------------------------- verse card
def build_verse_html(v, lang, date, theme=None, scale=1.0):
    """The scripture slide. `v` is a dict from verses.VERSES."""
    import verses as VS
    T = THEMES[theme or THEME]
    font = (N.FONT if T["serif"] else N.FONT_SANS)[lang]
    num_font = "'Noto Serif',serif" if T["serif"] else "'Noto Sans',sans-serif"
    dev = "'Noto Serif Devanagari', serif"

    mark, full = _img(LOGO_MARK), _img(LOGO_FULL)
    badge = (f'<img class="mark" src="{mark}" alt="">' if mark
             else '<div class="mark-fallback">ॐ</div>')
    pill = (f'<img class="pill-logo" src="{mark or full}" alt="">' if (mark or full) else "")
    om = _img(LOGO_MARK)
    g0, g1, g2 = T["ground"]
    s = lambda px: round(px * scale, 1)

    sa = html.escape(v["sa"]).replace("\n", "<br>")

    return f"""<!doctype html><html><head><meta charset="utf-8"><style>
* {{ margin:0; padding:0; box-sizing:border-box; }}
body {{ width:{W}px; height:{H}px; overflow:hidden; font-family:{font};
  color:{T["value"]}; -webkit-font-smoothing:antialiased; }}
.card {{ position:relative; width:100%; height:100%; overflow:hidden;
  background:linear-gradient(170deg, {g0} 0%, {g1} 52%, {g2} 100%);
  padding:34px 44px 26px; display:flex; flex-direction:column; }}
.card::before {{ content:""; position:absolute; width:900px; height:640px; left:-160px; top:-330px;
  border-radius:50%; background:radial-gradient(circle, rgba(240,155,31,.20), transparent 68%); }}
.card::after {{ content:""; position:absolute; width:1000px; height:620px; right:-260px; bottom:-320px;
  border-radius:50%; background:radial-gradient(circle, rgba(211,85,37,.14), transparent 68%); }}
.inner {{ position:relative; z-index:3; display:flex; flex-direction:column; height:100%; }}

.top {{ display:flex; align-items:center; justify-content:space-between; flex:none; }}
.badge {{ width:64px; height:64px; border-radius:50%; background:#fff; display:flex;
  align-items:center; justify-content:center; box-shadow:{T["shadow"]};
  border:1px solid {T["panel_line"]}; }}
.mark {{ width:44px; height:44px; object-fit:contain; }}
.mark-fallback {{ font-size:30px; color:{T["deep"]}; }}
.date {{ font-family:{num_font}; font-size:23px; font-weight:700; letter-spacing:.13em;
  color:{T["ink"]}; text-transform:uppercase; text-align:right; }}

h1 {{ text-align:center; font-size:{s(52)}px; line-height:1.12; color:{T["ink"]};
  font-weight:800; margin:20px 0 0; flex:none; }}
.accent {{ width:76px; height:5px; flex:none; border-radius:3px; margin:13px auto 0;
  background:linear-gradient(90deg, {T["saffron"]}, {T["terracotta"]}); }}

.panel {{ margin:auto 0; background:{T["panel"]}; border:1px solid {T["panel_line"]};
  border-radius:26px; box-shadow:{T["shadow"]}; padding:34px 38px 30px; text-align:center; }}
.omrow {{ display:flex; justify-content:center; margin-bottom:16px; }}
.omrow img {{ height:52px; width:auto; object-fit:contain; opacity:.95; }}
.sa {{ font-family:{dev}; font-size:{s(37)}px; line-height:1.62; color:{T["ink"]};
  font-weight:600; }}
.iast {{ font-family:{num_font}; font-size:{s(21)}px; color:{T["body"]}; font-style:italic;
  margin-top:14px; letter-spacing:.01em; }}
.sep {{ width:120px; height:1px; background:{T["hair"]}; margin:22px auto; }}
.mlabel {{ font-size:{s(18)}px; letter-spacing:.22em; text-transform:uppercase;
  color:{T["terracotta"]}; font-weight:700; }}
.tr {{ font-size:{s(27)}px; line-height:1.5; color:{T["value"]}; margin-top:11px; }}
.cite {{ font-size:{s(21)}px; letter-spacing:.10em; color:{T["deep"]}; font-weight:700;
  margin-top:24px; text-transform:uppercase; }}

.foot {{ padding-top:14px; display:flex; flex-direction:column;
  align-items:center; gap:6px; flex:none; }}
.pill {{ display:flex; align-items:center; gap:11px; background:{T["panel"]};
  border:1px solid {T["panel_line"]}; border-radius:999px; padding:7px 24px 7px 14px;
  box-shadow:{T["shadow"]}; }}
.pill-logo {{ height:34px; width:auto; object-fit:contain; }}
.pill b {{ font-size:24px; font-weight:800; color:{T["ink"]}; }}
.loc {{ font-size:17px; color:{T["body"]}; letter-spacing:.03em; }}
</style></head><body><div class="card"><div class="inner">
  <div class="top">
    <div class="badge">{badge}</div>
    <div class="date">{date.strftime("%d %b %Y")}</div>
  </div>
  <h1>{html.escape(VS.TITLE[lang])}</h1>
  <div class="accent"></div>
  <div class="panel">
    {'<div class="omrow"><img src="' + om + '" alt=""></div>' if om else ''}
    <div class="sa">{sa}</div>
    <div class="iast">{html.escape(v["iast"])}</div>
    <div class="sep"></div>
    <div class="mlabel">{html.escape(VS.MEANING[lang])}</div>
    <div class="tr">{html.escape(v["tr"][lang])}</div>
    <div class="cite">{html.escape(VS.citation(v, lang))}</div>
  </div>
  <div class="foot">
    <div class="pill">{pill}<b>{html.escape(BRAND)}</b></div>
    <div class="loc">{html.escape(HANDLE)} · {html.escape(N.LANG_NAME[lang])}</div>
  </div>
</div></div></body></html>"""


def render_verses(v, date, outdir, langs=None, theme=None, suffix=""):
    """One verse slide per language. Shrinks type until each card fits."""
    from playwright.sync_api import sync_playwright
    langs = langs or N.LANGS
    paths, warn = [], []
    with sync_playwright() as pw:
        b = pw.chromium.launch()
        pg = b.new_page(viewport={"width": W, "height": H}, device_scale_factor=1)
        for lg in langs:
            fp = os.path.join(outdir, f"verse_{date}_{lg}{suffix}.jpg")
            for scale in (1.0, 0.95, 0.9, 0.85, 0.8, 0.75, 0.7):
                pg.set_content(build_verse_html(v, lg, date, theme, scale), wait_until="load")
                pg.wait_for_timeout(220)
                over = pg.evaluate(
                    "() => {const c=document.querySelector('.inner');"
                    "return c.scrollHeight - c.clientHeight;}")
                if over <= 0:
                    break
            if over > 0:
                warn.append(f"verse {lg}: overflows by {over}px even at smallest size")
            pg.screenshot(path=fp, type="jpeg", quality=94)
            paths.append(fp)
        b.close()
    return paths, warn
