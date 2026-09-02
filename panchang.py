"""
Nitya Sankalpa - Panchang calculation engine
Swiss Ephemeris (Moshier), Lahiri/Chitrapaksha ayanamsa, Drik (true) system.
"""
import datetime as dt
import math
import swisseph as swe

FLAG = swe.FLG_SWIEPH | swe.FLG_MOSEPH | swe.FLG_SIDEREAL
swe.set_sid_mode(swe.SIDM_LAHIRI, 0, 0)

CITY = {"name": "Hyderabad", "lat": 17.3850, "lon": 78.4867, "tz": 5.5}


# ---------- time helpers ----------
def jd_from_local(y, m, d, hour_local, tz):
    """Julian day (UT) from local civil time."""
    ut = hour_local - tz
    return swe.julday(y, m, d, ut, swe.GREG_CAL)


def local_dt_from_jd(jd, tz):
    """datetime (naive, local) from Julian day UT."""
    y, m, d, h = swe.revjul(jd + tz / 24.0, swe.GREG_CAL)
    hh = int(h)
    mm = int((h - hh) * 60)
    ss = int(round((((h - hh) * 60) - mm) * 60))
    if ss >= 60:
        ss -= 60
        mm += 1
    if mm >= 60:
        mm -= 60
        hh += 1
    base = dt.datetime(y, m, d) + dt.timedelta(hours=hh, minutes=mm, seconds=ss)
    return base


# ---------- longitudes ----------
def sun_long(jd):
    return swe.calc_ut(jd, swe.SUN, FLAG)[0][0]


def moon_long(jd):
    return swe.calc_ut(jd, swe.MOON, FLAG)[0][0]


def elongation(jd):
    return (moon_long(jd) - sun_long(jd)) % 360.0


def sum_long(jd):
    return (moon_long(jd) + sun_long(jd)) % 360.0


# ---------- generic root finder for "angle reaches target" ----------
def _find_crossing(func, target, jd_lo, jd_hi, tol=1e-7):
    """Find jd in [lo,hi] where func(jd) (0..360, increasing mod 360) hits target."""

    def f(jd):
        return ((func(jd) - target + 180.0) % 360.0) - 180.0

    lo, hi = jd_lo, jd_hi
    flo = f(lo)
    fhi = f(hi)
    if flo * fhi > 0:
        return None
    for _ in range(80):
        mid = (lo + hi) / 2.0
        fm = f(mid)
        if flo * fm <= 0:
            hi, fhi = mid, fm
        else:
            lo, flo = mid, fm
        if hi - lo < tol:
            break
    mid = (lo + hi) / 2.0
    # Reject the +/-180 wrap discontinuity, which also flips sign but is not a crossing
    if abs(((func(mid) - target + 180.0) % 360.0) - 180.0) > 1e-3:
        return None
    return mid


def _span_end(func, jd_start, arc, max_days=3.0):
    """End time of the current segment of width `arc` degrees containing jd_start."""
    cur = func(jd_start)
    idx = int(cur / arc)
    target = ((idx + 1) * arc) % 360.0
    lo = jd_start
    hi = jd_start + 0.05
    while hi - jd_start < max_days:
        c = _find_crossing(func, target, lo, hi)
        if c is not None:
            return c
        lo = hi
        hi = hi + 0.05
    return None


def _span_start(func, jd_ref, arc, max_days=3.0):
    """Start time of the current segment of width `arc` containing jd_ref."""
    cur = func(jd_ref)
    idx = int(cur / arc)
    target = (idx * arc) % 360.0
    hi = jd_ref
    lo = jd_ref - 0.05
    while jd_ref - lo < max_days:
        c = _find_crossing(func, target, lo, hi)
        if c is not None:
            return c
        hi = lo
        lo = lo - 0.05
    return None


# ---------- rise / set ----------
def _rise_trans(jd_start, body, flag, lat, lon):
    res = swe.rise_trans(
        jd_start, body, flag,
        (lon, lat, 0.0), 0.0, 0.0, swe.FLG_MOSEPH,
    )
    if res[0] < 0:
        return None
    return res[1][0]


def sunrise_sunset(y, m, d, city):
    """Local-day sunrise and the sunset that follows it."""
    lat, lon, tz = city["lat"], city["lon"], city["tz"]
    jd_midnight = jd_from_local(y, m, d, 0.0, tz)
    sr = _rise_trans(jd_midnight, swe.SUN, swe.CALC_RISE, lat, lon)
    ss = _rise_trans(sr, swe.SUN, swe.CALC_SET, lat, lon)
    return sr, ss


def moonrise_moonset(y, m, d, city, sr=None, nxt_sr=None):
    """Moonrise/set for the Hindu day, which runs sunrise to sunrise.

    Searching the civil day instead would report no moonrise roughly once a
    month, on the days the Moon happens to rise just after midnight.
    """
    lat, lon, tz = city["lat"], city["lon"], city["tz"]
    base = sr if sr is not None else jd_from_local(y, m, d, 0.0, tz)
    # Near amavasya the Moon rises within minutes of the Sun, sometimes just
    # before it, so look back a few hours rather than starting exactly at sunrise.
    start = base - 3.0 / 24.0
    end = nxt_sr if nxt_sr is not None else base + 1.0
    mr = _rise_trans(start, swe.MOON, swe.CALC_RISE, lat, lon)
    ms = _rise_trans(start, swe.MOON, swe.CALC_SET, lat, lon)
    if mr and mr > end:
        mr = None
    if ms and ms > end:
        ms = None
    return mr, ms


# ---------- inauspicious / auspicious periods ----------
# index of the 1/8 day-part, 0-based, keyed by weekday (0=Sunday)
RAHU_PART = {0: 7, 1: 1, 2: 6, 3: 4, 4: 5, 5: 3, 6: 2}
YAMA_PART = {0: 4, 1: 3, 2: 2, 3: 1, 4: 0, 5: 6, 6: 5}
GULIKA_PART = {0: 6, 1: 5, 2: 4, 3: 3, 4: 2, 5: 1, 6: 0}
# durmuhurtam: 1-based muhurta numbers out of 15 daytime muhurtas
DURMUHURTAM = {0: [14], 1: [9, 13], 2: [4, 9], 3: [8], 4: [6, 12], 5: [4, 9], 6: [2]}


def eighth_part(sr, ss, idx):
    part = (ss - sr) / 8.0
    return sr + idx * part, sr + (idx + 1) * part


def muhurta_span(sr, ss, n):
    """n is 1-based out of 15 daytime muhurtas."""
    unit = (ss - sr) / 15.0
    return sr + (n - 1) * unit, sr + n * unit


# ---------- name indices ----------
KARANA_SEQ = [1, 2, 3, 4, 5, 6, 7]  # Bava..Vanija cycle (movable)

# Varjyam start, in ghatikas out of the nakshatra's 60, indexed by nakshatra
VARJYAM_GHATI = [50, 24, 30, 40, 14, 21, 30, 20, 32, 30, 20, 18, 21,
                 20, 14, 14, 10, 14, 20, 24, 20, 10, 10, 18, 16, 24, 30]
VARJYAM_LEN = 4.0      # ghatikas
AMRIT_OFFSET = 24.0    # ghatikas after varjyam start


def karana_index(n):
    """n = 0..59 half-tithi index -> karana name index 0..10."""
    if n == 0:
        return 7  # Kimstughna
    if n >= 57:
        return 8 + (n - 57)  # Shakuni, Chatushpada, Naga
    return (n - 1) % 7


def masa_index(jd, tz):
    """Amanta lunar month index, 0 = Chaitra."""
    amavasya = _span_start(elongation, jd, 360.0, max_days=32.0)
    if amavasya is None:
        amavasya = jd
    s = sun_long(amavasya)
    return (int(s / 30.0) + 1) % 12


# ---------- main ----------
def compute(date, city=CITY):
    y, m, d = date.year, date.month, date.day
    tz = city["tz"]

    sr, ss = sunrise_sunset(y, m, d, city)
    nxt_sr, _ = sunrise_sunset(*(date + dt.timedelta(days=1)).timetuple()[:3], city)
    mr, ms = moonrise_moonset(y, m, d, city, sr, nxt_sr)
    _, prev_ss = sunrise_sunset(*(date - dt.timedelta(days=1)).timetuple()[:3], city)

    weekday = (date.weekday() + 1) % 7  # 0 = Sunday

    def seq(func, arc, ref):
        i = int(func(ref) / arc)
        end = _span_end(func, ref, arc)
        return i, end

    t_idx, t_end = seq(elongation, 12.0, sr)
    n_idx, n_end = seq(moon_long, 360.0 / 27.0, sr)
    y_idx, y_end = seq(sum_long, 360.0 / 27.0, sr)
    k_raw = int(elongation(sr) / 6.0)
    k_end = _span_end(elongation, sr, 6.0)

    # next tithi/nakshatra if the current one ends before next sunrise
    def nxt(func, arc, end_jd):
        if end_jd is None or end_jd >= nxt_sr:
            return None, None
        i = int(func(end_jd + 1e-4) / arc)
        return i, _span_end(func, end_jd + 1e-4, arc)

    t2_idx, t2_end = nxt(elongation, 12.0, t_end)
    n2_idx, n2_end = nxt(moon_long, 360.0 / 27.0, n_end)

    rk = eighth_part(sr, ss, RAHU_PART[weekday])
    yg = eighth_part(sr, ss, YAMA_PART[weekday])
    gk = eighth_part(sr, ss, GULIKA_PART[weekday])
    abhijit = muhurta_span(sr, ss, 8) if weekday != 3 else None
    durmu = [muhurta_span(sr, ss, n) for n in DURMUHURTAM[weekday]]
    # Brahma muhurta: the two muhurtas (96 min) before sunrise, i.e. 96->48 min prior
    night_unit = (sr - prev_ss) / 15.0
    brahma = (sr - 2 * night_unit, sr - night_unit)
    vijaya = muhurta_span(sr, ss, 11)          # 11th of 15 daytime muhurtas
    godhuli = (ss - 12.0 / 1440.0, ss + 12.0 / 1440.0)

    # Varjyam / Amrit Kalam, proportional to the nakshatra's own duration
    ARC27 = 360.0 / 27.0
    nk_start = _span_start(moon_long, sr, ARC27)
    nk_end = n_end
    varj = amrit = None
    if nk_start and nk_end:
        ghati = (nk_end - nk_start) / 60.0
        vs = nk_start + VARJYAM_GHATI[n_idx] * ghati
        varj = (vs, vs + VARJYAM_LEN * ghati)
        as_ = vs + AMRIT_OFFSET * ghati
        amrit = (as_, as_ + VARJYAM_LEN * ghati)

    ml = moon_long(sr)
    sl = sun_long(sr)

    out = {
        "date": date,
        "city": city,
        "weekday": weekday,
        "sunrise": local_dt_from_jd(sr, tz),
        "sunset": local_dt_from_jd(ss, tz),
        "moonrise": local_dt_from_jd(mr, tz) if mr else None,
        "moonset": local_dt_from_jd(ms, tz) if ms else None,
        "day_length": (ss - sr) * 24.0,
        "tithi": t_idx,
        "tithi_end": local_dt_from_jd(t_end, tz) if t_end else None,
        "tithi_next": t2_idx,
        "tithi_next_end": local_dt_from_jd(t2_end, tz) if t2_end else None,
        "paksha": 0 if t_idx < 15 else 1,
        "nakshatra": n_idx,
        "nakshatra_end": local_dt_from_jd(n_end, tz) if n_end else None,
        "nakshatra_next": n2_idx,
        "nakshatra_next_end": local_dt_from_jd(n2_end, tz) if n2_end else None,
        "yoga": y_idx,
        "yoga_end": local_dt_from_jd(y_end, tz) if y_end else None,
        "karana": karana_index(k_raw),
        "karana_end": local_dt_from_jd(k_end, tz) if k_end else None,
        "chandra_rashi": int(ml / 30.0),
        "surya_rashi": int(sl / 30.0),
        "masa": masa_index(sr, tz),
        "rahu": (local_dt_from_jd(rk[0], tz), local_dt_from_jd(rk[1], tz)),
        "yamaganda": (local_dt_from_jd(yg[0], tz), local_dt_from_jd(yg[1], tz)),
        "gulika": (local_dt_from_jd(gk[0], tz), local_dt_from_jd(gk[1], tz)),
        "abhijit": (local_dt_from_jd(abhijit[0], tz), local_dt_from_jd(abhijit[1], tz)) if abhijit else None,
        "varjyam": (local_dt_from_jd(varj[0], tz), local_dt_from_jd(varj[1], tz)) if varj else None,
        "amrit": (local_dt_from_jd(amrit[0], tz), local_dt_from_jd(amrit[1], tz)) if amrit else None,
        "brahma": (local_dt_from_jd(brahma[0], tz), local_dt_from_jd(brahma[1], tz)),
        "vijaya": (local_dt_from_jd(vijaya[0], tz), local_dt_from_jd(vijaya[1], tz)),
        "godhuli": (local_dt_from_jd(godhuli[0], tz), local_dt_from_jd(godhuli[1], tz)),
        "durmuhurtam": [(local_dt_from_jd(a, tz), local_dt_from_jd(b, tz)) for a, b in durmu],
        "shaka": y - 78 if (m > 3 or (m == 3 and d > 20)) else y - 79,
        "vikram": y + 57 if (m > 3 or (m == 3 and d > 20)) else y + 56,
        "samvatsara": (y - 1987) % 60 if (m > 3 or (m == 3 and d > 20)) else (y - 1988) % 60,
    }
    return out


if __name__ == "__main__":
    import json
    p = compute(dt.date.today())
    for k, v in p.items():
        print(f"{k:20} {v}")
