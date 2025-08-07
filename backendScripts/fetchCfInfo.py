import os
import requests
import json
from pathlib import Path
LOGOS_DIR = Path('logos')

def fetch_mod_info(project_id: int, api_key: str) -> dict:
    """
    Fetches mod information from CurseForge API for a given project_id.
    Returns a dictionary with name, downloadCount, summary, and logo URL.
    """
    url = f"https://api.curseforge.com/v1/mods/{project_id}"
    headers = {
        'Accept': 'application/json',
        'x-api-key': api_key
    }
    response = requests.get(url, headers=headers)
    response.raise_for_status()

    data = response.json().get('data', {})
    main_file_id = data.get('mainFileId')
    latest_files = data.get('latestFiles', [])

    # find the file entry matching mainFileId
    main_file = next(
        (f for f in latest_files if f.get('id') == main_file_id),
        None
    )
    response = requests.get(f"{url}/description", headers=headers)
    response.raise_for_status()

    description = response.json().get('data', {})
    # extract the fields or fall back to None
    latest_version     = main_file.get('displayName') if main_file else None
    latest_release_date= main_file.get('fileDate')    if main_file else None
    installs           = main_file.get('downloadCount') if main_file else None
    stars = data.get('ratingDetails', {}).get('positiveRatings', 0)
    categories = []
    for category in data.get('categories', []):
        category = category.get('slug', category.get('name', ''))
        categories.append(category)

    response = requests.get(f"{url}/files/{main_file_id}/changelog", headers=headers)
    response.raise_for_status()
    changelog = response.json().get('data', {})
    return {
        'id':                data.get('id'),
        'name':              data.get('name'),
        'downloadCount':     data.get('downloadCount'),
        'summary':           data.get('summary'),
        'latestVersion':     latest_version,
        'latestReleaseDate': latest_release_date,
        'installs':          installs,
        'logoUrl':           data.get('logo', {}).get('url'),
        'stars':             stars,
        'game':              data.get('gameId', ""),
        'description':       description,
        'screenshots':       data.get('screenshots', []),
        'slug':              data.get('slug', ""),
        'categories':        categories,
        'changelog':         changelog,
    }


def download_logo(logo_url: str, save_dir: Path, filename: int) -> Path:
    """
    Downloads the logo image from the given URL and saves it to save_dir.
    Returns the path to the saved file.
    """
    save_dir.mkdir(parents=True, exist_ok=True)
    filepath = save_dir / filename

    response = requests.get(logo_url, stream=True)
    response.raise_for_status()

    with open(filepath, 'wb') as f:
        for chunk in response.iter_content(chunk_size=8192):
            f.write(chunk)

    return filepath


def main():
    project_ids = os.getenv('CURSEFORGE_PROJECT_IDS', '').split(',')

    # Your CurseForge API key (set as environment variable)
    api_key = os.getenv('CURSEFORGE_API_KEY')
    if not api_key:
        raise EnvironmentError("Please set the CURSEFORGE_API_KEY environment variable.")

    # Prepare output
    output = []

    for pid in project_ids:
        try:
            info = fetch_mod_info(pid, api_key)
            if info.get('logoUrl'):
                ext = os.path.splitext(info['logoUrl'])[1]
                filename = f"{pid}{ext}"
                download_logo(info['logoUrl'], LOGOS_DIR, filename)

            if info.get('screenshots'):
                for screenshot in info['screenshots']:
                    if screenshot.get('url'):
                        ext = os.path.splitext(screenshot['url'])[1]
                        filename = f"{screenshot['id']}{ext}"
                        download_logo(screenshot['url'], LOGOS_DIR, filename)

            output.append({
                'id':                info['id'],
                'name':              info['name'],
                'downloadCount':     info['downloadCount'],
                'summary':           info['summary'],
                'latestVersion':     info['latestVersion'],
                'dateModified':      info['latestReleaseDate'],
                'installs':          info['installs'],
                'stars':             info['stars'],
                'game':              info['game'],
                'categories':        info['categories'],
                'changelog':         info['changelog'],
                'screens': [
                    {
                        'path': f"{screenshot['id']}{os.path.splitext(screenshot['url'])[1]}",
                    } for screenshot in info.get('screenshots', [])
                ],
                'url': f"https://www.curseforge.com/wow/addons/{info['slug']}" if info['game'] == 1 else f"https://www.curseforge.com/ark-survival-ascended/mods/{info['slug']}" if info['game'] == 83374 else ValueError("Unsupported game ID"),
                'description': info['description']
            })
            print(f"Fetched and saved data for project {pid}")

        except requests.HTTPError as e:
            print(f"Failed to fetch project {pid}: {e}")

    # Save collected metadata to a JSON file
    with open(os.path.join('data', 'mods_metadata.json'), 'w', encoding='utf-8') as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    print("All done. Metadata written to mods_metadata.json and logos saved in 'logos/' directory.")


if __name__ == '__main__':
    main()
