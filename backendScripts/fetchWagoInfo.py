import os
import requests
import json
from pathlib import Path
import time
LOGOS_DIR = Path('logos')

# HTTP status codes that indicate a transient problem worth retrying.
# 429/403 are rate-limiting; 5xx are upstream outages (e.g. wago.io 503).
RETRYABLE_STATUS = {403, 429, 500, 502, 503, 504}
DEFAULT_TIMEOUT = 30.0


def request_with_retries(url, *, max_retries: int = 5, backoff: float = 10.0, **kwargs):
    """
    GET `url` with retries on transient failures (retryable HTTP statuses and
    connection/timeout errors), using linear backoff. Adds a default request
    timeout so a hung connection can't stall the run. Raises the last error if
    every attempt fails.
    """
    kwargs.setdefault("timeout", DEFAULT_TIMEOUT)
    last_exc = None
    for attempt in range(1, max_retries + 1):
        try:
            r = requests.get(url, **kwargs)
            if r.status_code in RETRYABLE_STATUS and attempt < max_retries:
                wait = backoff * attempt
                print(f"{r.status_code} received for {url}, sleeping {wait}s before retry {attempt}/{max_retries}")
                time.sleep(wait)
                continue
            r.raise_for_status()
            return r
        except requests.exceptions.RequestException as exc:
            last_exc = exc
            if attempt >= max_retries:
                break
            wait = backoff * attempt
            print(f"Request error for {url} ({exc}), sleeping {wait}s before retry {attempt}/{max_retries}")
            time.sleep(wait)

    if last_exc is not None:
        raise last_exc
    # Exhausted retries on a retryable status: re-issue once to surface the HTTPError.
    r = requests.get(url, **kwargs)
    r.raise_for_status()
    return r


def download_file(url: str, save_dir: Path, filename: str):
    save_dir.mkdir(parents=True, exist_ok=True)
    path = save_dir / filename
    try:
        r = request_with_retries(url, stream=True)
    except requests.exceptions.RequestException as exc:
        # Logos/screens are committed under logos/, so a failed download must
        # not abort the run; keep whatever is already on disk.
        print(f"WARNING: failed to download {url}: {exc}")
        return None
    with open(path, "wb") as f:
        for chunk in r.iter_content(8192):
            f.write(chunk)
    return path


def fetch_wago_lookup(slug: str, max_retries: int = 5, backoff: float = 10.0):
    """
    Fetches the detailed lookup for a given Wago slug, retrying on transient
    failures (rate limiting and upstream 5xx such as a 503). Raises if every
    attempt fails so the caller can fall back to previously stored data.
    """
    url = "https://data.wago.io/lookup/wago"
    params = {"id": slug}
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
        "Accept":     "application/json",
    }
    print(f"Fetching Wago lookup for {slug}...")
    r = request_with_retries(url, params=params, headers=headers,
                             max_retries=max_retries, backoff=backoff)
    return r.json()



def fetch_all_wago_imports(user: str):
    """
    Paginate through Wago imports for `user` and return a list of dicts:
      { "name": ..., "slug": ..., "thumbnail": ... }
    """
    base = "https://data.wago.io/search/es"
    page = 0
    all_hits = []

    # Use a browser‐style UA so Wago doesn’t block us
    headers = {
        "User-Agent":   "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
        "Accept":       "application/json",
    }

    while True:
        params = {
            # Pass raw User:"username" — let requests do the encoding
            "q":         f'User:"{user}"',
            "mode":      "imports",
            "game":      "all",
            "expansion": "all",
            "type":      "all",
            "page":      str(page),
        }
        print(f"Fetching Wago imports for {user}, page {page}...")
        r = request_with_retries(base, params=params, headers=headers)
        js = r.json()

        hits  = js.get("hits", [])
        total = js.get("total", 0)

        if not hits:
            break

        all_hits.extend(hits)
        if len(all_hits) >= total:
            break

        page += 1

    # Return only the fields we care about
    return [
        {"name": h["name"], "id": h["id"], "slug": h["slug"], "installs": h["installs"],    "versionString": h["versionString"], "stars": h["stars"], "views": h["views"], "thumbnail": h["thumbnail"]}
        for h in all_hits
    ]

OUTPUT_PATH = os.path.join('data', 'wago_metadata.json')


def load_previous_metadata():
    """Load the last committed metadata keyed by slug, for fallback on failure."""
    try:
        with open(OUTPUT_PATH, encoding="utf-8") as f:
            return {entry["slug"]: entry for entry in json.load(f) if entry.get("slug")}
    except (FileNotFoundError, json.JSONDecodeError, KeyError, TypeError) as exc:
        print(f"No usable previous metadata to fall back on ({exc})")
        return {}


def build_meta_entry(item, slug):
    """Download assets and fetch the lookup for one import, returning its entry.

    Raises requests.exceptions.RequestException if the lookup can't be fetched.
    """
    thumb_url = item.get("thumbnail")
    if thumb_url:
        ext = os.path.splitext(thumb_url)[1] or ".png"
        download_file(thumb_url, LOGOS_DIR, slug + ext)
    print(f"Sleeping 20s before fetching lookup for {slug} to avoid hitting rate limits...")
    time.sleep(20)
    print(f"Processing Wago item: {item['name']} (slug: {slug})")
    lookup = fetch_wago_lookup(slug)
    versions_total    = lookup.get("versions", {}).get("total", 0)
    view_count        = lookup.get("viewCount", item.get("views", 0))
    comment_count     = lookup.get("commentCount", 0)
    install_count     = lookup.get("installCount", item.get("installs", 0))
    favorite_count    = lookup.get("favoriteCount", 0)
    modified          = lookup.get("date", {}).get("modified")
    html_description = lookup.get("description", {}).get("html", "")
    versions = lookup.get("versions", [])
    if versions and versions.get("versions"):
        changelog = versions.get("versions", [])[0].get("changelog", {}).get("text", "")
    else:
        changelog = ""
    categories = lookup.get("categories", [])
    if lookup.get("screens"):
        for img in lookup.get("screens", []):
            url = img.get("src")
            id = img.get("_id")
            ext       = os.path.splitext(url)[1] or ".png"
            download_file(url, LOGOS_DIR, id + ext)
            img["path"] = id + ext
    else:
        lookup["screens"] = []

    return {
        "name":           item["name"],
        "slug":           slug,
        "installs":       install_count,
        "stars":          item.get("stars", favorite_count),
        "views":          view_count,
        "hasThumbnail":   bool(thumb_url),
        "latestVersion":  item.get("versionString", ""),
        "versionsTotal":  versions_total,
        "commentCount":   comment_count,
        "dateModified":   modified,
        "description": html_description,
        "categories": categories,
        "changelog": changelog,
        "url": lookup.get("url", f"https://wago.io/{slug}"),
        "screens" : [
            {
                "path": img.get("path"),
            }
            for img in lookup.get("screens", [])
        ],
    }


def main():
    wago_user = os.getenv("WAGO_USER")
    if not wago_user:
        raise RuntimeError(f"Set WAGO_USER environment variable to the Wago user whose imports you want to fetch.")
    wago_items = fetch_all_wago_imports(wago_user)
    prev_by_slug = load_previous_metadata()

    wago_meta = []
    for item in wago_items:
        slug      = item["slug"]
        if not slug:
            print(f"Found item without slug: {item}")
            slug = item["id"]
        try:
            wago_meta.append(build_meta_entry(item, slug))
        except requests.exceptions.RequestException as exc:
            # Transient outage after all retries: never drop data — reuse the
            # last-known entry if we have one, otherwise skip this new item.
            prev = prev_by_slug.get(slug)
            if prev is not None:
                print(f"WARNING: lookup failed for {slug} ({exc}); reusing previous data")
                wago_meta.append(prev)
            else:
                print(f"WARNING: lookup failed for {slug} ({exc}); skipping new item")

    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(wago_meta, f, indent=2, ensure_ascii=False)
    print(f"Fetched {len(wago_meta)} Wago imports and downloaded thumbnails")

if __name__ == "__main__":
    main()
