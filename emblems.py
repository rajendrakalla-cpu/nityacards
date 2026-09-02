# -*- coding: utf-8 -*-
"""
Gold line-art emblems, one per weekday deity (index 0 = Sunday).

  0 Sunday    Surya      sun disc on a lotus
  1 Monday    Shiva      trishul with damaru and crescent
  2 Tuesday   Hanuman    gada (mace)
  3 Wednesday Ganesha    modak on a lotus leaf
  4 Thursday  Vishnu     shankha and chakra
  5 Friday    Lakshmi    lotus rising from a kalash
  6 Saturday  Shani      deepam (oil lamp)

Each is a 100x100 viewBox, stroke-only, inheriting currentColor.
"""

_SURYA = """
<circle cx="50" cy="44" r="13"/>
<g stroke-linecap="round">
<path d="M50 22.5v-8M50 73.5v0M31.5 25.5l-5-6.2M68.5 25.5l5-6.2
M27 44h-8M81 44h8M30.5 60.5l-5.6 5.6M69.5 60.5l5.6 5.6
M38.2 25.2l-3-7.4M61.8 25.2l3-7.4M31.2 53.5l-7.4 3M68.8 53.5l7.4 3
M31.2 34.5l-7.4-3M68.8 34.5l7.4-3"/></g>
<path d="M50 62c-6 0-11 3.6-13.4 9.2C42 73.6 46 75 50 75s8-1.4 13.4-3.8C61 65.6 56 62 50 62z"/>
<path d="M36.6 71.2C30 69.6 24 71 20.4 75.6c5 3.4 11.2 4.2 16.2 2.6"/>
<path d="M63.4 71.2C70 69.6 76 71 79.6 75.6c-5 3.4-11.2 4.2-16.2 2.6"/>
<path d="M36.6 78.2C40.6 82 45 84 50 84s9.4-2 13.4-5.8"/>
"""

_SHIVA = """
<path d="M50 90V40" stroke-linecap="round"/>
<path d="M30 40h40" stroke-linecap="round"/>
<path d="M50 40V14" stroke-linecap="round"/>
<path d="M46 19l4-9 4 9" stroke-linecap="round" stroke-linejoin="round"/>
<path d="M31 40c0-9 -1-15 -1-21" stroke-linecap="round"/>
<path d="M26 24l4-9 4 9" stroke-linecap="round" stroke-linejoin="round"/>
<path d="M69 40c0-9 1-15 1-21" stroke-linecap="round"/>
<path d="M66 24l4-9 4 9" stroke-linecap="round" stroke-linejoin="round"/>
<path d="M40 56L60 70M60 56L40 70" stroke-linecap="round"/>
<path d="M39 56h22M39 70h22" stroke-linecap="round"/>
<path d="M44 63h-9M56 63h9" stroke-linecap="round" stroke-width="1.2"/>
<circle cx="34" cy="63" r="1.8" fill="currentColor" stroke="none"/>
<circle cx="66" cy="63" r="1.8" fill="currentColor" stroke="none"/>
"""

_HANUMAN = """
<path d="M50 12c-9 0-16 7-16 17s7 17 16 17 16-7 16-17-7-17-16-17z"/>
<path d="M35.5 22h29M34 34h32" />
<path d="M40 46h20l-2 6H42z"/>
<path d="M50 52v30" stroke-linecap="round"/>
<path d="M44 58h12M44 66h12" stroke-linecap="round"/>
<circle cx="50" cy="86" r="5"/>
<path d="M50 29h0.01" stroke-linecap="round" stroke-width="4"/>
"""

_GANESHA = """
<path d="M50 14c-4 9-10 14-16 20-6 7-9 14-9 22 0 8 11 12 25 12s25-4 25-12
 c0-8-3-15-9-22-6-6-12-11-16-20z" stroke-linejoin="round"/>
<path d="M50 16L34 66M50 16l16 50M50 16v50M50 16l-9 51M50 16l9 51" stroke-width="1.2"/>
<path d="M22 68h56" stroke-linecap="round"/>
<path d="M27 74c-6-1-10 1-13 4 8 5 18 7 26 6" />
<path d="M73 74c6-1 10 1 13 4-8 5-18 7-26 6" />
<path d="M36 80h28l-3 8H39z" stroke-linejoin="round"/>
"""

_VISHNU = """
<g transform="translate(-4 0)">
<path d="M40 20c-9 6-18 20-19 34-1 11 3 20 9 24 4 3 9 2 11-2 2-5-1-9-1-15
 0-9 4-15 4-24 0-8-1-14-4-17z" stroke-linejoin="round"/>
<path d="M40 20c3-3 7-5 10-4 2 1 2 4 0 6-2 2-5 3-8 3"/>
<path d="M30 78c5 4 12 5 18 3-3-4-8-6-13-6" stroke-linejoin="round"/>
<path d="M26 40c4 2 7 5 8 9M23 55c4 2 8 4 11 4"/>
</g>
<g transform="translate(6 0)">
<circle cx="70" cy="50" r="20"/>
<circle cx="70" cy="50" r="7"/>
<g stroke-linecap="round">
<path d="M70 30v-6M70 76v-6M50 50h-6M96 50h-6
M55.9 35.9l-4.3-4.3M88.4 68.4l-4.3-4.3M84.1 35.9l4.3-4.3M51.6 68.4l4.3-4.3"/></g>
<path d="M70 43v-13M70 70V57M63 50H50M90 50H77" stroke-width="1"/>
</g>
"""

_LAKSHMI = """
<path d="M50 52c-4 0-7 5-7 11s3 10 7 10 7-4 7-10-3-11-7-11z"/>
<path d="M43 63c-6-4-13-4-18 0 3 7 10 11 18 10"/>
<path d="M57 63c6-4 13-4 18 0-3 7-10 11-18 10"/>
<path d="M39 56c-8-6-16-7-23-3 3 8 12 13 21 13"/>
<path d="M61 56c8-6 16-7 23-3-3 8-12 13-21 13"/>
<path d="M50 52V40" stroke-linecap="round"/>
<path d="M50 40c-4-3-6-7-6-12 4 1 6 4 6 8 0-4 2-7 6-8 0 5-2 9-6 12z"/>
<path d="M32 78h36l-3 10H35z"/>
<path d="M30 78h40" stroke-linecap="round"/>
"""

_SHANI = """
<path d="M50 14c-6 8-9 13-9 18 0 5 4 8 9 8s9-3 9-8c0-5-3-10-9-18z"
 stroke-linejoin="round"/>
<path d="M50 26c-2 3-3 5-3 7 0 2 1.4 3.4 3 3.4s3-1.4 3-3.4c0-2-1-4-3-7z"
 fill="currentColor" stroke="none"/>
<path d="M50 40v10" stroke-linecap="round"/>
<path d="M22 54h56c0 11-13 18-28 18S22 65 22 54z" stroke-linejoin="round"/>
<path d="M18 54h64" stroke-linecap="round"/>
<path d="M50 72v8" stroke-linecap="round"/>
<path d="M34 88h32l-4-8H38z" stroke-linejoin="round"/>
<path d="M30 92h40" stroke-linecap="round"/>
"""

EMBLEM = [_SURYA, _SHIVA, _HANUMAN, _GANESHA, _VISHNU, _LAKSHMI, _SHANI]


def svg(weekday, size=100, width=1.9, opacity=1.0):
    """Inline SVG for the given weekday (0 = Sunday)."""
    return (
        f'<svg viewBox="0 0 100 100" width="{size}" height="{size}" fill="none" '
        f'stroke="currentColor" stroke-width="{width}" stroke-linejoin="round" '
        f'opacity="{opacity}">{EMBLEM[weekday]}</svg>'
    )
