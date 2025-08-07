#!/usr/bin/env python3
import os
import json
import polib

# ——— CONFIG ———
LOOKUP_JSON   = os.path.join('data', "category_i18n_lookup.json")
LOCALES_DIR   = "locales"
DOMAIN        = "categories"      # we'll emit categories.po
LANGS         = {
    "en-US": "en_US",
    "de-DE": "de_DE",
}

def main():
    with open(LOOKUP_JSON, "r", encoding="utf-8") as f:
        lookup = json.load(f)

    for lang_tag, locale_dir in LANGS.items():
        # ensure the locale directory exists
        lc_path = os.path.join(LOCALES_DIR, locale_dir, "LC_MESSAGES")
        os.makedirs(lc_path, exist_ok=True)

        po_path = os.path.join(lc_path, f"{DOMAIN}.po")

        # load existing PO if present, else create new
        if os.path.isfile(po_path):
            po = polib.pofile(po_path)
        else:
            po = polib.POFile()
            po.metadata = {
                "Project-Id-Version": "wago.io categories",
                "Report-Msgid-Bugs-To": "",
                "POT-Creation-Date": "",
                "PO-Revision-Date": "",
                "Last-Translator": "",
                "Language-Team": "",
                "Language": locale_dir,
                "MIME-Version": "1.0",
                "Content-Type": "text/plain; charset=utf-8",
                "Content-Transfer-Encoding": "8bit",
            }

        # update entries
        for cat_key, data in lookup.items():
            msgid = cat_key
            msgstr = data.get("label", {}).get(lang_tag) or ""
            # find or create entry
            entry = po.find(msgid)
            if not entry:
                entry = polib.POEntry(msgid=msgid, msgstr=msgstr)
                # optional: add comment with image/color
                img = data.get("image")
                col = data.get("color")
                if img or col:
                    entry.comment = "image: {}  color: {}".format(img or "-", col or "-")
                po.append(entry)
            else:
                entry.msgstr = msgstr
                # update comment if desired
                img = data.get("image")
                col = data.get("color")
                entry.comment = "image: {}  color: {}".format(img or "-", col or "-")

        # save .po and compile .mo
        po.save(po_path)

        print(f"Wrote {po_path}")

if __name__ == "__main__":
    main()
