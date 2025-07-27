import os
import requests
import json
from pathlib import Path
import time
LOGOS_DIR = Path('logos')

def download_file(url: str, save_dir: Path, filename: str):
    save_dir.mkdir(parents=True, exist_ok=True)
    path = save_dir / filename
    r = requests.get(url, stream=True); r.raise_for_status()
    with open(path, "wb") as f:
        for chunk in r.iter_content(8192):
            f.write(chunk)
    return path


def fetch_wago_lookup(slug: str, max_retries: int = 3, backoff: float = 1.0):
    """
    Fetches the detailed lookup for a given Wago slug, with simple retry on 429.
    """
    url = "https://data.wago.io/lookup/wago"
    params = {"id": slug}
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
        "Accept":     "application/json",
    }
    print(f"Fetching Wago lookup for {slug}...")
    for attempt in range(1, max_retries + 1):
        r = requests.get(url, params=params, headers=headers)
        if r.status_code == 429:
            # Too many requests: wait and retry
            wait = backoff * attempt
            print(f"429 received for {slug}, sleeping {wait}s before retry {attempt}/{max_retries}")
            time.sleep(wait)
            continue
        r.raise_for_status()
        return r.json()

    # If we get here, all retries failed
    r.raise_for_status()  # will raise the last HTTPError



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
        r = requests.get(base, params=params, headers=headers)
        r.raise_for_status()   # will now only raise on true errors (not bad encoding)
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

def main():
    wago_user = os.getenv("WAGO_USER")
    if not wago_user:
        raise RuntimeError(f"Set WAGO_USER environment variable to the Wago user whose imports you want to fetch.")
    wago_items = fetch_all_wago_imports(wago_user)

    wago_meta = []
    for item in wago_items:
        slug      = item["slug"]
        if not slug:
            print(f"Found item without slug: {item}")
            slug = item["id"]
        if item["thumbnail"]:
            thumb_url = item["thumbnail"]
            ext       = os.path.splitext(thumb_url)[1] or ".png"
            download_file(thumb_url, LOGOS_DIR, slug + ext)
        lookup = fetch_wago_lookup(slug)
        versions_total    = lookup.get("versions", {}).get("total", 0)
        view_count        = lookup.get("viewCount", item.get("views", 0))
        comment_count     = lookup.get("commentCount", 0)
        install_count     = lookup.get("installCount", item.get("installs", 0))
        favorite_count    = lookup.get("favoriteCount", 0)
        modified          = lookup.get("date", {}).get("modified")

        wago_meta.append({
            "name":           item["name"],
            "slug":           slug,
            "installs":       install_count,
            "stars":          item.get("stars", 0),
            "views":          view_count,
            "hasThumbnail":   bool(thumb_url),
            "versionString":  item.get("versionString", ""),
            "versionsTotal":  versions_total,
            "commentCount":   comment_count,
            "favoriteCount":  favorite_count,
            "dateModified":   modified,
        })
        
    with open(os.path.join('Data', 'wago_metadata.json'), "w", encoding="utf-8") as f:
        json.dump(wago_meta, f, indent=2, ensure_ascii=False)
    print(f"Fetched {len(wago_meta)} Wago imports and downloaded thumbnails")

if __name__ == "__main__":
    main()
