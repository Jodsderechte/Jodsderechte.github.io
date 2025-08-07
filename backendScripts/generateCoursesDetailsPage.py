import os
from operator import itemgetter
from generateIndexPage import make_env, load_json, MODS_METADATA_PATH, WAGO_METADATA_PATH, OTHER_PROJECTS_PATH, ADDITIONAL_COURSES_PATH
from generatePortfolioDetailsPage import load_text
import markdown
TEMPLATE_PATH = os.path.join('Templates', 'courses-details.html')




def main():

        # Load metadata
    additional_courses_raw = load_json(ADDITIONAL_COURSES_PATH)
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

    additional_courses = []
    for type in additional_courses_raw:
        for course in type.get('courses', []):
            course['file_name'] = f"{course.get('title')}.html"
            course['category'] = type.get('type', 'Other')
            additional_courses.append(course)

    for lang in ['en_US', 'de_DE']:
        env      = make_env(lang)
        template = env.get_template(os.path.basename(TEMPLATE_PATH))
        env.globals['load_text'] = lambda path: load_text(path)
        env.filters['markdown'] = lambda text: markdown.markdown(
            text or '',
            extensions=['fenced_code', 'tables', 'smarty']
        )

        for item in additional_courses:
            print(f"Generating page for {item.get('title')} in {lang}")
            output_html = template.render(
                item=item,
                additional_courses_raw=additional_courses_raw,
                topAddons=topAddons,
                topMods=topMods,
                topWeakAuras=topWeakAuras,
                other_projects_data=other_projects_data
            )
            if lang == 'de_DE':
                out_path = os.path.join("courses", item.get('file_name'))
            else:
                out_path = os.path.join(env.globals.get('lang_code'), "courses", item.get('file_name'))
            with open(out_path, "w", encoding="utf-8") as f:
                f.write(output_html)
            print(f"Generated {out_path}")


if __name__ == "__main__":
    main()
