# Nitya Panchang — automated daily Instagram carousel

Publishes two Instagram carousels a day for @nityasankalpa: the **panchang** at
6:00 AM IST and a **scripture verse** in the evening. Instagram caps a carousel at
10 slides, so the 8 panchang cards and the 8 verse cards go out as two posts rather
than one 16-slide carousel.

Every panchang card is **calculated for its own city**, so followers see timings that
actually apply where they are:

| Slide | Language | City | Calendar |
|---|---|---|---|
| 1 | English | Hyderabad | lunar (amanta) |
| 2 | हिन्दी | New Delhi | lunar (amanta) |
| 3 | తెలుగు | Visakhapatnam | lunar (amanta) |
| 4 | ಕನ್ನಡ | Bengaluru | lunar (amanta) |
| 5 | தமிழ் | Chennai | **solar** |
| 6 | मराठी | Mumbai | lunar (amanta) |
| 7 | বাংলা | Kolkata | **solar** |
| 8 | മലയാളം | Kochi | **solar** |

Astronomy is computed live with the Swiss Ephemeris using the Lahiri (Chitrapaksha)
ayanamsa and the Drik (true-position) system — the same basis published panchangams use.
Nothing is hardcoded or scraped.

## The scripture carousel

Eight slides, one per language, all carrying the same verse for that day: the
Sanskrit in Devanagari, a roman transliteration, the meaning in that card's
language, and the citation. Verses rotate deterministically by date
(`verses.verse_for`), so the cycle is stable and repeats every `len(VERSES)` days.

The set in `verses.py` is 12 verses from the Bhagavad Gita and the Upanishads
(Isha, Brihadaranyaka, Mundaka, Katha). Add more by appending to `VERSES` — each
entry needs `book`, `ref`, `sa`, `iast`, and a `tr` meaning for all eight languages.
The card auto-shrinks its type until the verse fits, so length is forgiving.

> **Before the first publish:** the Sanskrit and English are standard and widely
> printed, but the regional-language meanings are working translations. Have a
> native reader check them and correct `verses.py` directly.

## What's on each panchang card

| Section | Fields |
|---|---|
| Top bar | Logo badge, the day's deity portrait, date and city |
| Header | Title, weekday and its presiding deity, month, paksha, samvatsara |
| Hero | Sunrise, sunset, moonrise |
| Panchanga | Tithi, Nakshatra, Yoga, Karana, Chandra rashi — each with end times |
| Auspicious | Brahma Muhurta, Abhijit Muhurta, Amrit Kalam, Vijaya Muhurta |
| Inauspicious | Rahu Kalam, Yamaganda, Gulika Kalam, Durmuhurtam, Varjyam |

Conventions worth knowing:

- **Abhijit Muhurta is omitted on Wednesdays** — it is traditionally void that day.
  Brahma Muhurta always appears, so there is never a card with no auspicious window.
- Samvatsara names are romanised on all cards.
- **Tamil, Bengali and Malayalam use solar months** (Aavani, Bhadro, Chingam) keyed to
  the Sun's rashi, because those calendars are solar. The other five show the amanta
  lunar month.
- Each card carries the **presiding deity of the weekday** — Sunday Surya · Monday
  Shiva · Tuesday Hanuman · Wednesday Ganesha · Thursday Vishnu · Friday Lakshmi ·
  Saturday Shani — as a framed painted portrait in the top bar and a large, feathered
  watermark behind the body. The paintings live in `assets/deities/` named `<weekday>_*.jpg`
  where weekday 0 is Sunday. Replace a file to change that day's art; if the folder is
  missing the renderer falls back to line-art emblems rather than breaking.
- **Moonrise is computed over the Hindu day** (sunrise to sunrise), with a three-hour
  lookback. Using the civil day instead leaves moonrise blank about once a month, and
  on amavasya the Moon rises minutes *before* sunrise.

## Files

| File | Purpose |
|---|---|
| `panchang.py` | Swiss Ephemeris calculations — the whole astronomical core |
| `names.py` | Name/label tables, per-language cities, weekday deities |
| `emblems.py` | Line-art deity emblems — the fallback if the paintings are missing |
| `assets/` | Logo mark and lockup; `deities/` holds the seven painted portraits |
| `card.py` | HTML/CSS card template, rendered to JPEG via headless Chromium |
| `publish.py` | Image hosting (GitHub or imgbb) + Instagram Graph API carousel publishing |
| `verses.py` | The verse corpus and the daily rotation |
| `pipeline.py` | Orchestrates compute → render → host → publish |
| `bootstrap-repo.sh` | Creates the GitHub repo and pushes, one command |
| `.github/workflows/daily-panchang.yml` | The two scheduled publishing runs |

## Setup

### 1. Instagram credentials

Your account must be a **Business or Creator** account.

1. At [developers.facebook.com](https://developers.facebook.com/apps), create an app.
2. Add the **Instagram** product → *Instagram API setup with Instagram login*.
3. Link your Instagram account and generate a token with these scopes:
   `instagram_business_basic` and `instagram_business_content_publish`.
4. Copy the **Instagram User ID** and the access token from the same panel.

Token lifecycle: the token you generate is short-lived (1 hour). Exchange it for a
long-lived token (60 days). The pipeline calls `refresh_access_token` after every
successful post, which rolls the 60 days forward — so as long as it posts at least once
every two months, the token never expires on its own.

### 2. Image hosting

Instagram will not accept an uploaded file — it fetches the image from a public URL,
and **only JPEG works**. The pipeline commits each day's cards to a public GitHub repo
and hands Instagram the `raw.githubusercontent.com` URLs. This doubles as a dated
archive of every card you've ever posted.

Create a fine-grained personal access token with **Contents: read and write** on that
repo. (imgbb is supported as an alternative — set `IMGBB_KEY` instead.)

### 3. Run it

```bash
./setup.sh                    # fonts, Python deps, Chromium
cp config.env.example config.env   # then fill it in
set -a && source config.env && set +a

python3 pipeline.py --dry-run          # render only, nothing posted
python3 pipeline.py                    # the panchang carousel
python3 pipeline.py --post verse       # the scripture carousel
python3 pipeline.py --post both        # both, as two separate posts
python3 pipeline.py --date 2026-09-05
```

### 4. Push and schedule it

```bash
./bootstrap-repo.sh          # creates the repo and pushes; needs gh or GITHUB_TOKEN
```

The repo must be **public** — Instagram fetches each card from
`raw.githubusercontent.com` and cannot authenticate to a private repo. Then add under
**Settings → Secrets and variables → Actions**:

| Kind | Name | Value |
|---|---|---|
| Secret | `IG_USER_ID` | your Instagram user ID |
| Secret | `IG_ACCESS_TOKEN` | long-lived token |
| Secret | `GH_IMAGE_TOKEN` | the fine-grained PAT from step 2 |

The workflow then runs twice daily — `20 0 * * *` publishes the panchang and
`20 13 * * *` the scripture carousel. Use **Actions → Daily Nitya Panchang → Run
workflow** to fire either by hand; it has a `post` selector and a `dry_run` checkbox.
Start with `dry_run = true` and check the uploaded artifacts before going live.

**Changing the times** — edit the two cron lines (they are UTC; IST is +5:30) and the
matching schedule string in the *Decide which carousel* step. GitHub's scheduler can
lag 5-20 minutes under load, so both fire ten minutes early.

## Changing things

**Cities** — edit `CITIES` (and `CITY_LOCAL`, the name in the local script) in
`names.py`. Everything location-dependent recomputes; tithi/nakshatra/yoga end times
stay the same, since those are absolute moments in time.

**Theme** — two palettes live in `THEMES` at the top of `card.py`:

- `brand` (default) — the warm Nitya Sankalpa palette, sampled straight from the logo:
  saffron `#F09B1F`, orange `#E78225`, terracotta `#D35525`, deep `#AF4114`, on a
  cream-to-sand ground. Uses the Noto Sans stack.
- `night` — the same layout on a deep navy ground with gold, using the Noto Serif stack.

Switch with the `NP_THEME` environment variable (`NP_THEME=night`) or
`card.render_all(pn, out, theme="night")`. To retune, edit the palette dicts — every
colour on the card is driven from them, nothing is hardcoded in the CSS.

**Logo** — `assets/logo_mark.png` (the om-flame-infinity mark) is used for the header
badge and the footer pill; `assets/logo.png` is the full lockup. Both are transparent
PNGs generated from the master logo. Replace either file and the cards follow; if the
files are missing the renderer falls back to a text badge rather than breaking.

**Card design** — everything visual is the CSS block in `card.py`.

**Fewer or more languages** — `card.render_all(pn, out, langs=["te", "en"])`.
Instagram carousels take 2-10 slides, so the current eight leaves room for two more.

**Layout safety** — the renderer measures each card after rendering and reports any
vertical or horizontal overflow rather than silently clipping. If you enlarge the type
or add rows, watch for `WARNING layout overflow` in the run output.

**Different fields** — the `ausp` and `inausp` lists in `card.build_html` are plain
`(label, value)` tuples; add or remove rows there.

## Accuracy

Verified against a published panchang for 2 Sep 2026: tithi, nakshatra, yoga and karana
end times matched within one minute; Rahu Kalam, Yamaganda, Gulika, Brahma Muhurta and
Amrit Kalam all matched after adjusting for the location's different sunrise.

Panchang traditions genuinely differ — Durmuhurtam tables and the Varjyam/Amrit
ghatika offsets vary between regional almanacs. The values used here are in
`panchang.py` (`DURMUHURTAM`, `VARJYAM_GHATI`, `AMRIT_OFFSET`) and are easy to swap
if your family or temple follows a different siddhanta.
