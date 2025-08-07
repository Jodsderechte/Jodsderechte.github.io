#!/usr/bin/env python3
import os
import re
import json
import requests
from fetchWagoInfo import download_file
from pathlib import Path

# ——— CONFIG ———
GITHUB_REPO   = "methodgg/wago.io"
GITHUB_BRANCH = "master"
RAW_BASE      = f"https://raw.githubusercontent.com/{GITHUB_REPO}/{GITHUB_BRANCH}"
API_BASE      = f"https://api.github.com/repos/{GITHUB_REPO}/contents"

JS_PATH       = "frontend/src/components/libs/categories2.js"
I18N_DIR      = "frontend/static/i18n"
OUTPUT_PATH   = os.path.join('data',"category_i18n_lookup.json")
IMG_PATH     = os.path.join('images',"categories")

LANGS = ["en-US", "de-DE"]


def fetch_text(path):
    url = f"{RAW_BASE}/{path}"
    r = requests.get(url)
    r.raise_for_status()
    return r.text


def list_i18n_files(lang):
    url = f"{API_BASE}/{I18N_DIR}/{lang}"
    r = requests.get(url)
    r.raise_for_status()
    return [e for e in r.json() if e["name"].endswith(".json")]


def fetch_json_from_api(item):
    r = requests.get(item["download_url"])
    r.raise_for_status()
    return r.json()


def main():
    js = fetch_text(JS_PATH)
    body_m = re.search(r"this\.categories\s*=\s*\{([\s\S]*?)\};", js)
    if not body_m:
        raise RuntimeError("Couldn't find this.categories block")
    body = body_m.group(1)

    # Matches 'catKey': { … }
    entry_re = re.compile(r"'(?P<key>[^']+)'\s*:\s*\{(?P<body>[^}]+)\}", re.MULTILINE)
    cats = []
    for em in entry_re.finditer(body):
        k = em.group("key")
        b = em.group("body")
        img    = re.search(r"image\s*:\s*['\"]([^'\"]+)['\"]", b)
        col    = re.search(r"color\s*:\s*['\"]([^'\"]+)['\"]", b)
        i18    = re.search(r"i18n\s*:\s*['\"]([^'\"]+)['\"]", b)
        parent = re.search(r"parent\s*:\s*['\"]([^'\"]+)['\"]", b)

        cats.append({
            "key":    k,
            "image":  img.group(1) if img else None,
            "color":  col.group(1) if col else None,
            "i18n":   i18.group(1) if i18 else None,
            "parent": parent.group(1) if parent else None,
        })


    # Load i18n JSON for each lang & namespace
    i18n_data = {lang: {} for lang in LANGS}
    for lang in LANGS:
        for item in list_i18n_files(lang):
            ns = os.path.splitext(item["name"])[0]
            i18n_data[lang][ns] = fetch_json_from_api(item)

        lookup = {}


    for cat in cats:
        lbls = {}

        raw_i18n = cat["i18n"]
        if raw_i18n and ":" in raw_i18n:
            # namespaced lookup exactly as before
            ns, path = raw_i18n.split(":", 1)
            keys = path.split(".")
            for lang in LANGS:
                data = i18n_data[lang].get(ns, {})
                try:
                    val = data
                    for p in keys:
                        val = val[p]
                except (KeyError, TypeError):
                    val = None
                lbls[lang] = val

        elif raw_i18n:
            # no namespace → it's already the literal label!
            for lang in LANGS:
                lbls[lang] = raw_i18n

        else:
            # missing entirely
            for lang in LANGS:
                lbls[lang] = None

        if cat["image"] and not cat["image"].startswith("ffxiv"):
            # Convert relative image paths to absolute URLs
            url = f"https://wago.io/static/image/menu/{cat['image']}"
            download_file(url, Path(os.path.join(IMG_PATH)), cat["image"])

        lookup[cat["key"]] = {
            "image": cat["image"],
            "color": cat["color"],
            "label": lbls
        }


    # inherit image/color from parent when missing 
    for cat in cats:
        p = cat.get("parent")
        if not p:
            continue
        child = lookup[cat["key"]]
        parent = lookup.get(p)
        if not parent:
            continue
        # only overwrite if the child has no explicit image/color
        if child["image"] is None:
            child["image"] = parent["image"]
        if child["color"] is None:
            child["color"] = parent["color"]

    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(lookup, f, ensure_ascii=False, indent=2)

    print(f"Wrote {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
