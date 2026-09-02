# -*- coding: utf-8 -*-
"""Nitya Sankalpa - image hosting + Instagram carousel publishing."""
import base64
import json
import os
import time
import urllib.parse
import urllib.request

IG_API = "https://graph.instagram.com/v25.0"
GH_API = "https://api.github.com"


def _post(url, data, retries=3):
    body = urllib.parse.urlencode(data).encode()
    last = None
    for i in range(retries):
        try:
            req = urllib.request.Request(url, data=body, method="POST")
            with urllib.request.urlopen(req, timeout=90) as r:
                return json.loads(r.read().decode())
        except urllib.error.HTTPError as e:
            detail = e.read().decode()[:400]
            last = RuntimeError(f"HTTP {e.code} {url.split('?')[0]}: {detail}")
            if e.code < 500 and e.code != 429:
                raise last
        except Exception as e:                       # noqa: BLE001
            last = e
        time.sleep(3 * (i + 1))
    raise last


def _get(url, retries=3):
    last = None
    for i in range(retries):
        try:
            with urllib.request.urlopen(url, timeout=60) as r:
                return json.loads(r.read().decode())
        except urllib.error.HTTPError as e:
            last = RuntimeError(f"HTTP {e.code}: {e.read().decode()[:300]}")
            if e.code < 500:
                raise last
        except Exception as e:                       # noqa: BLE001
            last = e
        time.sleep(2 * (i + 1))
    raise last


# ---------------- image hosting ----------------
def upload_github(paths, repo, token, branch="main", prefix="cards"):
    """Commit each file to a public GitHub repo; return raw.githubusercontent URLs."""
    urls = []
    for p in paths:
        name = os.path.basename(p)
        day = name.split("_")[1] if "_" in name else "misc"
        dest = f"{prefix}/{day}/{name}"
        with open(p, "rb") as f:
            content = base64.b64encode(f.read()).decode()

        url = f"{GH_API}/repos/{repo}/contents/{urllib.parse.quote(dest)}"
        sha = None
        try:
            req = urllib.request.Request(
                url + f"?ref={branch}",
                headers={"Authorization": f"Bearer {token}",
                         "Accept": "application/vnd.github+json"})
            with urllib.request.urlopen(req, timeout=45) as r:
                sha = json.loads(r.read().decode()).get("sha")
        except Exception:                            # noqa: BLE001
            pass                                     # not there yet

        payload = {"message": f"panchang {dest}", "content": content, "branch": branch}
        if sha:
            payload["sha"] = sha
        req = urllib.request.Request(
            url, data=json.dumps(payload).encode(), method="PUT",
            headers={"Authorization": f"Bearer {token}",
                     "Accept": "application/vnd.github+json",
                     "Content-Type": "application/json"})
        with urllib.request.urlopen(req, timeout=90) as r:
            json.loads(r.read().decode())
        urls.append(
            f"https://raw.githubusercontent.com/{repo}/{branch}/{urllib.parse.quote(dest)}")
    return urls


def upload_imgbb(paths, api_key):
    """Fallback host. Returns direct image URLs."""
    urls = []
    for p in paths:
        with open(p, "rb") as f:
            b64 = base64.b64encode(f.read()).decode()
        res = _post("https://api.imgbb.com/1/upload",
                    {"key": api_key, "image": b64, "name": os.path.basename(p)})
        urls.append(res["data"]["url"])
    return urls


# ---------------- Instagram ----------------
def _wait_ready(container_id, token, tries=20, delay=5):
    """Poll a container until Meta finishes fetching/processing the image."""
    for _ in range(tries):
        st = _get(f"{IG_API}/{container_id}?fields=status_code,status"
                  f"&access_token={urllib.parse.quote(token)}")
        code = st.get("status_code")
        if code == "FINISHED":
            return True
        if code == "ERROR":
            raise RuntimeError(f"Container {container_id} failed: {st.get('status')}")
        time.sleep(delay)
    raise RuntimeError(f"Container {container_id} not ready in time")


def publish_carousel(ig_user_id, token, image_urls, caption):
    """Create item containers, group into a carousel, publish. Returns media id."""
    if not 2 <= len(image_urls) <= 10:
        raise ValueError("Instagram carousels take 2-10 images")

    children = []
    for u in image_urls:
        r = _post(f"{IG_API}/{ig_user_id}/media",
                  {"image_url": u, "is_carousel_item": "true", "access_token": token})
        children.append(r["id"])
    for c in children:
        _wait_ready(c, token)

    r = _post(f"{IG_API}/{ig_user_id}/media",
              {"media_type": "CAROUSEL", "children": ",".join(children),
               "caption": caption, "access_token": token})
    parent = r["id"]
    _wait_ready(parent, token)

    r = _post(f"{IG_API}/{ig_user_id}/media_publish",
              {"creation_id": parent, "access_token": token})
    return r["id"]


def refresh_token(token):
    """Long-lived Instagram tokens last 60 days; refresh keeps them alive."""
    return _get(f"{IG_API}/refresh_access_token?grant_type=ig_refresh_token"
                f"&access_token={urllib.parse.quote(token)}")


def quota_left(ig_user_id, token):
    try:
        r = _get(f"{IG_API}/{ig_user_id}/content_publishing_limit"
                 f"?fields=quota_usage,config&access_token={urllib.parse.quote(token)}")
        d = r["data"][0]
        return d.get("config", {}).get("quota_total", 100) - d.get("quota_usage", 0)
    except Exception:                                # noqa: BLE001
        return None
