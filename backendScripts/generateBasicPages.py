import os
from operator import itemgetter
from generateIndexPage import make_env, load_json, MODS_METADATA_PATH, WAGO_METADATA_PATH, OTHER_PROJECTS_PATH


TEMPLATES = {
    'credits': os.path.join('Templates', 'credits.html'),
    'imprint': os.path.join('Templates', 'imprint.html'),
    '404': os.path.join('Templates', '404.html'),
}


def main():

    # Load metadata
    mods_metadata = load_json(MODS_METADATA_PATH)
    wago_metadata = load_json(WAGO_METADATA_PATH)
    other_projects_data = load_json(OTHER_PROJECTS_PATH)
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
    for item in mods_metadata:
            item['file_name'] = item.get('name', 'unknown').replace(' ', '-').lower()
    for item in wago_metadata:
        item['file_name'] = item.get('slug', 'unknown').replace(' ', '-').lower()
    for item in other_projects_data:
        for project in item.get('projects', []):
            project['file_name'] = project.get('name', 'unknown').replace(' ', '-').lower()


    for lang in ['en_US', 'de_DE']:
        env      = make_env(lang)

        for name, template_path in TEMPLATES.items():
            template = env.get_template(os.path.basename(template_path))
            print(f"Generating page {name} in {lang}")
            output_html = template.render(
                item=item,
                topAddons=topAddons,
                topMods=topMods,
                topWeakAuras=topWeakAuras,
                other_projects_data=other_projects_data
            )
            if lang == 'de_DE':
                out_path = f"{name}.html"
            else:
                out_path = os.path.join(env.globals.get('lang_code'), f"{name}.html")
            with open(out_path, "w", encoding="utf-8") as f:
                f.write(output_html)
            print(f"Generated {out_path}")


if __name__ == "__main__":
    main()
