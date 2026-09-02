# -*- coding: utf-8 -*-
"""
Nitya Sankalpa - daily Nitya Panchang pipeline.

  python3 pipeline.py                    # the panchang carousel (8 cards)
  python3 pipeline.py --post verse       # the scripture carousel (8 cards)
  python3 pipeline.py --post both        # both, as two separate posts
  python3 pipeline.py --dry-run          # render only, publish nothing
  python3 pipeline.py --date 2026-09-05

Instagram caps a carousel at 10 slides, so the 8 panchang cards and the 8 verse
cards go out as two posts rather than one 16-slide carousel.

Config comes from environment variables (see config.env.example).
"""
import argparse
import datetime as dt
import os
import sys
import traceback

import card
import names as N
import verses as VS
import panchang as P
import publish as PUB

OUT = os.environ.get("NP_OUT", os.path.join(os.path.dirname(__file__), "out"))


def fmt(x):
    return x.strftime("%I:%M %p").lstrip("0") if x else "—"


def rng(pair):
    return f"{fmt(pair[0])}–{fmt(pair[1])}" if pair else "—"


HASHTAGS = (
    "#panchang #panchangam #nityasankalpa #hindupanchang #rahukalam "
    "#todayspanchang #sanatandharma #dailypanchang #tithi #nakshatra "
    "#muhurat #hinducalendar #telugupanchangam #tamilpanchangam "
    "#kannadapanchanga #bengalipanchang #malayalampanchangam #marathipanchang #bhakti #spirituality #vedicastrology #india"
)


def caption(p):
    d = p["date"]
    pk, ti = N.tithi_name("en", p["tithi"])
    deity = N.DEITY["en"][p["weekday"]]
    nak = N.NAKSHATRA["en"][p["nakshatra"]]
    wd = N.WEEKDAY["en"][p["weekday"]]
    ab = rng(p["abhijit"]) if p["abhijit"] else "not available today"

    return (
        f"🕉️ Nitya Panchang · {d.strftime('%d %B %Y')} · {wd}\n"
        f"Presiding deity of the day: {deity}\n"
        f"{N.MASA['en'][p['masa']]} · {pk} · {ti} · {nak} nakshatra\n\n"
        f"☀️ Sunrise {fmt(p['sunrise'])}  ·  Sunset {fmt(p['sunset'])}\n"
        f"🚫 Rahu Kalam {rng(p['rahu'])}\n"
        f"✨ Abhijit Muhurta {ab}\n"
        f"🌅 Brahma Muhurta {rng(p['brahma'])}\n"
        f"🌙 Moon in {N.RASHI['en'][p['chandra_rashi']]}\n\n"
        f"Swipe for your language and your city →\n"
        + " · ".join(f"{N.LANG_NAME[lg]} {N.CITIES[lg]['name']}" for lg in N.LANGS)
        + "\n\nEach card is calculated for its own city, so the timings are the ones "
          "that actually apply where you are. Save this for the day 🙏\n\n" + HASHTAGS
    )


VERSE_TAGS = (
    "#bhagavadgita #gita #upanishads #shloka #sanskrit #dailyverse "
    "#nityasankalpa #sanatandharma #bhakti #spirituality #vedanta #dharma "
    "#gitaquotes #shlokaoftheday #hinduism #india"
)


def verse_caption(v, day):
    return (
        f"\U0001F549\uFE0F Nitya Panchang \u00b7 Today's Verse \u00b7 "
        f"{day.strftime('%d %B %Y')}\n"
        f"{VS.BOOK[v['book']]['en']} \u00b7 {v['ref']}\n\n"
        f"{v['sa']}\n\n"
        f"{v['tr']['en']}\n\n"
        "Swipe for the same verse in your language \u2192\n"
        + " \u00b7 ".join(N.LANG_NAME[lg] for lg in N.LANGS)
        + "\n\n" + VERSE_TAGS
    )


def need(key):
    v = os.environ.get(key, "").strip()
    if not v:
        sys.exit(f"Missing required environment variable: {key}")
    return v


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--date")
    ap.add_argument("--post", choices=["panchang", "verse", "both"], default="panchang",
                    help="which carousel to build (Instagram allows max 10 slides, "
                         "so the 8 panchang cards and 8 verse cards ship as two posts)")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--no-publish", action="store_true")
    a = ap.parse_args()

    day = dt.date.fromisoformat(a.date) if a.date else \
        (dt.datetime.utcnow() + dt.timedelta(hours=5, minutes=30)).date()

    os.makedirs(OUT, exist_ok=True)
    jobs = ["panchang", "verse"] if a.post == "both" else [a.post]
    results = []

    for job in jobs:
        if job == "panchang":
            # every language card is calculated for its own city
            pn = {lg: P.compute(day, N.CITIES[lg]) for lg in N.LANGS}
            paths, warn = card.render_all(pn, OUT)
            cap = caption(pn["en"])
            label = "panchang"
            print(f"Rendered {len(paths)} panchang cards for {day}:")
            for lg, x in zip(N.LANGS, paths):
                print(f"   {lg:3} {N.CITIES[lg]['name']:15} {x}")
        else:
            v = VS.verse_for(day)
            paths, warn = card.render_verses(v, day, OUT)
            cap = verse_caption(v, day)
            label = "verse"
            print(f"Rendered {len(paths)} verse cards for {day} "
                  f"({VS.BOOK[v['book']]['en']} {v['ref']}):")
            for lg, x in zip(N.LANGS, paths):
                print(f"   {lg:3} {x}")
        for w in warn:
            print(f"   WARNING layout overflow -> {w}")

        with open(os.path.join(OUT, f"caption_{label}_{day}.txt"), "w") as f:
            f.write(cap)

        if a.dry_run or a.no_publish:
            print(f"\n--- {label} caption ---\n{cap}\n")
            results.append(paths)
            continue

        results.append(publish_set(paths, cap, label))

    return results


def publish_set(paths, cap, label):
    # host the images
    if os.environ.get("GITHUB_REPO"):
        urls = PUB.upload_github(paths, need("GITHUB_REPO"), need("GITHUB_TOKEN"),
                                 os.environ.get("GITHUB_BRANCH", "main"))
    elif os.environ.get("IMGBB_KEY"):
        urls = PUB.upload_imgbb(paths, os.environ["IMGBB_KEY"])
    else:
        sys.exit("Set GITHUB_REPO+GITHUB_TOKEN or IMGBB_KEY for image hosting")
    print("Hosted:", *urls, sep="\n  ")

    ig_id, tok = need("IG_USER_ID"), need("IG_ACCESS_TOKEN")
    left = PUB.quota_left(ig_id, tok)
    if left is not None:
        print(f"Publishing quota remaining: {left}")
        if left < 1:
            sys.exit("Daily publishing quota exhausted; skipping.")

    media_id = PUB.publish_carousel(ig_id, tok, urls, cap)
    print(f"PUBLISHED {label} carousel, media id {media_id}")

    try:
        PUB.refresh_token(tok)
        print("Access token refreshed.")
    except Exception as e:                            # noqa: BLE001
        print(f"Token refresh failed (non-fatal): {e}")
    return media_id


if __name__ == "__main__":
    try:
        main()
    except SystemExit:
        raise
    except Exception:                                 # noqa: BLE001
        traceback.print_exc()
        sys.exit(1)
