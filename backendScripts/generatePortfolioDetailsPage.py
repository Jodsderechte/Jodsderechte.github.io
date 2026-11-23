import os
from jinja2 import Environment, FileSystemLoader, select_autoescape, StrictUndefined
from datetime import datetime, timezone, date, timedelta
from dateutil.parser import parse as parse_date
from babel.dates import format_date
from operator import itemgetter
from generateIndexPage import make_env, load_json, MODS_METADATA_PATH, WAGO_METADATA_PATH, OTHER_PROJECTS_PATH
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import re
import markdown  

TEMPLATE_PATH = os.path.join('Templates', 'portfolio-details.html')
CATEGORY_LOOKUP_PATH = os.path.join('data', 'category_i18n_lookup.json')
LOCALES_DIR = 'locales'

WAGO_BASE_URL = "https://wago.io"


def strip_ads_filter(html: str) -> str:
    """Remove description images/badges, preserving prose and text links."""
    soup = BeautifulSoup(html, 'html.parser')
    # CurseForge sometimes splits a Markdown banner across HTML links instead
    # of rendering an image. Only remove paragraphs consisting of that image.
    for p in soup.find_all('p'):
        if re.fullmatch(r'!\[[^\]]*\]\(.+\)', p.get_text().strip(), re.DOTALL):
            p.decompose()

    image_links = [a for a in soup.find_all('a') if a.find('img')]
    for img in soup.find_all('img'):
        img.decompose()
    for a in image_links:
        # Keep captions/text in mixed links, but remove empty badge wrappers.
        if not a.get_text(strip=True) and not a.find(['svg', 'video', 'audio']):
            a.decompose()

    for a in soup.find_all('a', href=True):
        href = a['href']
        if href.startswith('/') and not href.startswith('//'):
            a['href'] = urljoin(WAGO_BASE_URL, href)
    return str(soup)

def load_text(path):
    with open(path, encoding='utf-8') as f:
        return f.read()
def main():

        # Load metadata
    mods_metadata = load_json(MODS_METADATA_PATH)
    wago_metadata = load_json(WAGO_METADATA_PATH)
    other_projects_data = load_json(OTHER_PROJECTS_PATH)
    category_lookup = load_json(CATEGORY_LOOKUP_PATH)

    for item in mods_metadata:
        item['file_name'] = item.get('name', 'unknown').replace(' ', '-').lower()
        item['domain'] = "Curseforge.com"
        if item.get('game') == 1:
            item['type'] = 'addon'
        elif item.get('game') == 83374:
            item['type'] = 'mod'
            raw = item.get('latestVersion', '')
            item['latestVersion'] = re.sub(r'[^0-9\.]+', '', raw)
        else:
            raise ValueError(f"Unsupported game ID: {item.get('game')}")
        for screenshot in item.get('screens', []):
            screenshot['path'] = f"/logos/{screenshot.get('path', '')}"

    for item in wago_metadata:
        item['domain'] = "Wago.io"
        item['file_name'] = item.get('slug', 'unknown').replace(' ', '-').lower()
        item['type'] = 'weakaura'
        for screenshot in item.get('screens', []):
            screenshot['path'] = f"/logos/{screenshot.get('path', '')}"

    other_projects = []
    for item in other_projects_data:
        project_type = item.get('title', 'other')
        for project in item.get('projects', []):
            project['domain'] = project.get('name', 'unknown')
            project['file_name'] = project.get('name', 'unknown').replace(' ', '-').lower()
            project['type'] = project_type
            project['skipAutoImportExplanation'] = True
            project['translatedDescription'] = True
            other_projects.append(project)

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

    for lang in ['en_US', 'de_DE']:
        env      = make_env(lang)
        env.filters["strip_ads"] = lambda text: strip_ads_filter(text)
        env.globals['load_text'] = lambda path: load_text(path)
        env.filters['markdown'] = lambda text: markdown.markdown(
            text or '',
            extensions=['fenced_code', 'tables', 'smarty']
        )
        template = env.get_template(os.path.basename(TEMPLATE_PATH))

        for item in topAddons + topMods + topWeakAuras + other_projects:
            output_html = template.render(
                item=item,
                category_lookup=category_lookup,
                topAddons=topAddons,
                topMods=topMods,
                topWeakAuras=topWeakAuras,
                other_projects=other_projects,
                other_projects_data=other_projects_data,
                last_updated=datetime.now(timezone.utc),
            )
            if lang == 'de_DE':
                out_path = os.path.join("portfolio", f"{item.get('file_name')}.html")
            else:
                out_path = os.path.join(env.globals.get('lang_code'), "portfolio", f"{item.get('file_name')}.html")
            with open(out_path, "w", encoding="utf-8") as f:
                f.write(output_html)
            print(f"Generated {out_path}")


if __name__ == "__main__":
    main()
