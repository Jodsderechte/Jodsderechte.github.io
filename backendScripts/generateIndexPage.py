import os
import json
from jinja2 import Environment, FileSystemLoader, select_autoescape, StrictUndefined
from datetime import datetime, timezone, date, timedelta
import gettext
import polib
import glob
from dateutil.parser import parse as parse_date
from babel.dates import format_date
from operator import itemgetter

TEMPLATE_PATH = os.path.join('Templates', 'index.html')
MODS_METADATA_PATH = os.path.join('data', 'mods_metadata.json')
WAGO_METADATA_PATH = os.path.join('data', 'wago_metadata.json')
LINKEDIN_SNAPSHOT_PATH = os.path.join('data', 'linkedin_snapshot.json')
OTHER_PROJECTS_PATH = os.path.join('data', 'other_projects.json')
ADDITIONAL_COURSES_PATH = os.path.join('data', 'additional_courses.json')
GITHUB_METRICS_PATH = 'github-metrics.json'
LOCALES_DIR = 'locales'
BIRTHDATE = os.getenv('BIRTHDATE')


def calculate_age_filter(value, fmt="%d.%m.%Y"):
    """
    Jinja filter “age”:
      • if `value` is a date, use it directly
      • if it's a string, parse with the given `fmt`
    Returns full years since that date up to today.
    """
    if isinstance(value, str):
        try:
            born = datetime.strptime(value, fmt).date()
        except ValueError:
            return ""
    elif isinstance(value, date):
        born = value
    else:
        return ""

    today = date.today()
    years = today.year - born.year
    if (today.month, today.day) < (born.month, born.day):
        years -= 1
    return years

def month_year_filter(date_str, locale):
    """
    Turn "Mar 2023" or "2017" into a datetime, then format as "MMM yyyy"
    in the given locale (e.g. "Mär 2023" in German).
    """
    dt = parse_date(date_str, default=datetime(1900, 1, 1))
    return format_date(dt, format="MMM yyyy", locale=locale)

def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)
    
def annotate_calendar(raw_calendar):
    """
    Given the JSON structure
      { "contributionCalendar": { "weeks": [ { "contributionDays": [ { "color": ... }, … ] }, … ] } }
    this will inject a `date` and `weekday` into each day, counting backwards from today.
    """
    weeks = raw_calendar["contributionCalendar"]["weeks"]
    flat_days = [day for week in weeks for day in week["contributionDays"]]

    today = date.today()
    last_index = len(flat_days) - 1

    for idx, day in enumerate(flat_days):
        # how many days ago was this cell?
        days_ago = last_index - idx
        d = today - timedelta(days=days_ago)
        day["day"] = d.day
        day["month"] = d.strftime('%B')
        # full weekday name, e.g. "Tuesday"
        day["weekday"] = d.strftime("%A")    # e.g. "Saturday"

    # because we mutated those same dicts, `weeks` now has date+weekday in each day
    return raw_calendar

def make_env(lang_code):
    """Create a Jinja Environment with a localized timeago filter."""
    locale_path = os.path.join(LOCALES_DIR, lang_code, "LC_MESSAGES")
    os.makedirs(locale_path, exist_ok=True)

    # Merge all existing .po into one in-memory POFile
    merged = polib.POFile()
    merged.metadata = {
        "Project-Id-Version": "wago.io",
        "Language": lang_code,
        "MIME-Version": "1.0",
        "Content-Type": "text/plain; charset=utf-8",
        "Content-Transfer-Encoding": "8bit",
    }

    po_paths = glob.glob(os.path.join(locale_path, "*.po"))
    print(f'building po files for paths: {po_paths}')
    for po_path in po_paths:
        if not po_path.endswith("full.po"):
            print(f'merging {po_path}')
            pool = polib.pofile(po_path)
            for entry in pool:
                existing = merged.find(entry.msgid)
                if existing:
                    # override with latest msgstr if non-empty
                    if entry.msgstr:
                        existing.msgstr = entry.msgstr
                else:
                    merged.append(entry)

    # Write out the merged catalog as full.po + .mo
    merged_po = os.path.join(locale_path, "full.po")
    merged.save(merged_po)
    merged.save_as_mofile(merged_po[:-3] + ".mo")
    print(f'Wrote merged .po to {merged_po}')

    # Load that .mo into StrictTranslations
    mo_file = os.path.join(locale_path, "full.mo")
    with open(mo_file, "rb") as f:
        translations = StrictTranslations(f)

    print(f'Loaded translations for {lang_code} from {mo_file}')

    env = Environment(
        loader=FileSystemLoader(os.path.dirname(TEMPLATE_PATH)),
        autoescape=select_autoescape(['html', 'xml']),
        extensions=['jinja2.ext.i18n'],
        undefined=StrictUndefined,   # optional: catch missing vars too
    )
    env.install_gettext_translations(translations, newstyle=True)

    env.filters['month_year'] = lambda d: month_year_filter(d, lang_code)
    env.filters["age"] = lambda age, fmt: calculate_age_filter(age, fmt)
    # also make lang_code available in templates if you need it
    env.globals['lang_code'] = lang_code
    

    return env
class StrictTranslations(gettext.GNUTranslations):
    def gettext(self, message):
        translated = super().gettext(message)
        # If nothing was found, gettext() returns the original msgid.
        # But only treat it as missing if there’s no entry in the catalog.
        if translated == message and message not in self._catalog:
            raise KeyError(f"Missing translation for: {message!r}")
        return translated

    def ngettext(self, singular, plural, n):
        translated = super().ngettext(singular, plural, n)
        # Determine which key was looked up
        key = singular if n == 1 else plural
        if translated in (singular, plural) and key not in self._catalog:
            raise KeyError(f"Missing plural translation for: {singular!r}/{plural!r}")
        return translated

def main():

    for lang in ['en_US', 'de_DE']:
        env      = make_env(lang)
        template = env.get_template(os.path.basename(TEMPLATE_PATH))

        # Load metadata
        mods_metadata = load_json(MODS_METADATA_PATH)
        wago_metadata = load_json(WAGO_METADATA_PATH)
        github_metrics = load_json(GITHUB_METRICS_PATH)
        github_metrics["user"]["calendar"] = annotate_calendar(github_metrics["user"]["calendar"])
        linkedin_snapshot = load_json(LINKEDIN_SNAPSHOT_PATH)
        other_projects_data = load_json(OTHER_PROJECTS_PATH)
        additional_courses = load_json(ADDITIONAL_COURSES_PATH)

        total_installs = sum(mod['installs'] for mod in mods_metadata) + sum(item['installs'] for item in wago_metadata)
        total_downloads = sum(mod['downloadCount'] for mod in mods_metadata) + sum(item['views'] for item in wago_metadata)
        total_stars = sum(mod.get('stars', 0) for mod in mods_metadata) + sum(item.get('stars', 0) for item in wago_metadata)
        total_comments = sum(item.get('commentCount', 0) for item in wago_metadata) # comments are disabled for all curseforge items

        for item in mods_metadata:
            item['file_name'] = item.get('name', 'unknown').replace(' ', '-').lower()
        for item in wago_metadata:
            item['file_name'] = item.get('slug', 'unknown').replace(' ', '-').lower()
        for item in other_projects_data:
            for project in item.get('projects', []):
                project['file_name'] = project.get('name', 'unknown').replace(' ', '-').lower()

        

        topAddons = sorted(
            (m for m in mods_metadata if m.get('game') == 1),
            key=itemgetter('downloadCount'),
            reverse=True
        )[:10]


        topMods = sorted(
            (m for m in mods_metadata if m.get('game') == 83374),
            key=itemgetter('downloadCount'),
            reverse=True
        )[:10]

        topWeakAuras = sorted(
            wago_metadata,
            key=itemgetter('installs'),
            reverse=True
        )[:10]

        top3Addons = sorted(
            (m for m in mods_metadata if m.get('game') == 1),
            key=itemgetter('downloadCount'),
            reverse=True
        )[:3]


        top3Mods = sorted(
            (m for m in mods_metadata if m.get('game') == 83374),
            key=itemgetter('downloadCount'),
            reverse=True
        )[:3]

        top3WeakAuras = sorted(
            wago_metadata,
            key=itemgetter('installs'),
            reverse=True
        )[:3]

        template = env.get_template(os.path.basename(TEMPLATE_PATH))
        output_html = template.render(
            linkedin_snapshot=linkedin_snapshot,
            github_metrics=github_metrics,
            topAddons=topAddons,
            topMods=topMods,
            topWeakAuras=topWeakAuras,
            top3Addons=top3Addons,
            top3Mods=top3Mods,
            top3WeakAuras=top3WeakAuras,
            other_projects_data=other_projects_data,
            total_installs=total_installs,
            total_downloads=total_downloads,
            total_stars=total_stars,
            total_comments=total_comments,
            last_updated=datetime.now(timezone.utc),
            additional_courses=additional_courses,
            birthdate=BIRTHDATE,
        )

        # Write output
        if lang == 'de_DE':
            out_path = "index.html"
        else:
            out_path = f"{lang}/index.html"
        with open(out_path, "w", encoding="utf-8") as f:
            f.write(output_html)
        print(f"Generated {out_path}")


if __name__ == "__main__":
    main()
