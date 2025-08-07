import os
from datetime import datetime, timezone
from operator import itemgetter
from generateIndexPage import make_env, load_json, MODS_METADATA_PATH, WAGO_METADATA_PATH, OTHER_PROJECTS_PATH, ADDITIONAL_COURSES_PATH
from markupsafe import Markup, escape
import re

TEMPLATE_PATH = os.path.join('Templates', 'final-project-details.html')

def render_bullets(text):
    """
    Parses text into prose paragraphs, ordered and unordered lists with nesting based on indentation.
    """
    lines = text.split('\n')
    html = []
    stack = []  # list of (list_tag, indent)

    def open_list(tag, indent):
        html.append(f'<{tag}>')
        stack.append((tag, indent))

    def close_list():
        tag, _ = stack.pop()
        html.append(f'</{tag}>')

    def close_to_indent(target):
        while stack and stack[-1][1] >= target:
            close_list()

    for ln in lines:
        raw = ln.rstrip()
        if not raw.strip():
            continue
        # detect ordered or unordered
        m_ord = re.match(r'^(?P<space>\s*)(?P<num>\d+)\.\s*(?P<txt>.*)$', raw)
        m_uno = re.match(r'^(?P<space>\s*)-\s*(?P<txt>.*)$', raw)
        if m_ord or m_uno:
            indent = len((m_ord or m_uno).group('space'))
            if m_ord:
                tag = 'ol'
                content = m_ord.group('txt').strip()
            else:
                tag = 'ul'
                content = m_uno.group('txt').strip()
            # manage list nesting
            if not stack:
                open_list(tag, indent)
            else:
                cur_tag, cur_indent = stack[-1]
                if indent > cur_indent:
                    open_list(tag, indent)
                elif indent < cur_indent:
                    close_to_indent(indent)
                    if not stack or stack[-1][0] != tag:
                        open_list(tag, indent)
                elif tag != cur_tag:
                    close_list()
                    open_list(tag, indent)
            # emit list item
            if tag == 'ul':
                html.append(f'<li><span>{escape(content)}</span></li>')
            else:
                html.append(f'<li><span>{escape(content)}</span></li>')
            continue
        # prose: close all lists and emit paragraph
        close_to_indent(0)
        html.append(f'<p>{escape(raw.strip())}</p>')

    close_to_indent(0)
    return Markup('\n'.join(html))

def main():

    # Load metadata
    mods_metadata = load_json(MODS_METADATA_PATH)
    wago_metadata = load_json(WAGO_METADATA_PATH)
    other_projects_data = load_json(OTHER_PROJECTS_PATH)
    additional_courses_data = load_json(ADDITIONAL_COURSES_PATH)

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

    projects = []
    for category in additional_courses_data:
        category_name = category.get('type', 'unknown')
        for course in category.get('courses', []):
            if course.get('project'):
                project = course
                project['file_name'] = project.get('title', 'unknown').replace(' ', '-').lower()
                project['category'] = category_name
                projects.append(project)

    for lang in ['en_US', 'de_DE']:
        env      = make_env(lang)
        env.filters['render_bullets'] = render_bullets
        template = env.get_template(os.path.basename(TEMPLATE_PATH))

        for item in projects:
            output_html = template.render(
                item=item,
                topAddons=topAddons,
                topMods=topMods,
                topWeakAuras=topWeakAuras,
                other_projects=other_projects,
                other_projects_data=other_projects_data,
                last_updated=datetime.now(timezone.utc),
            )
            if lang == 'de_DE':
                out_path = os.path.join("projects", f"{item.get('file_name')}.html")
            else:
                out_path = os.path.join(env.globals.get('lang_code'), "projects", f"{item.get('file_name')}.html")
            with open(out_path, "w", encoding="utf-8") as f:
                f.write(output_html)
            print(f"Generated {out_path}")


if __name__ == "__main__":
    main()
