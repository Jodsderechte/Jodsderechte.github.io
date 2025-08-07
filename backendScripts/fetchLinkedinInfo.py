#!/usr/bin/env python3
"""
LinkedIn Member Snapshot Data Fetcher

This script retrieves all positions and education entries from the LinkedIn Member Snapshot API
and writes them to a JSON file (`linkedin_snapshot.json`) with two top-level fields:

- `positions`: list of position entries
- `education`: list of education entries

Usage:
1. Set your LinkedIn OAuth2 access token in the environment variable `LINKEDIN_ACCESS_TOKEN`.
2. Run the script: `python linkedin_snapshot_fetcher.py`
"""
import os
import sys
import requests
import json
from datetime import datetime, timezone

# Base URL for the LinkedIn Member Snapshot API
API_URL = 'https://api.linkedin.com/rest/memberSnapshotData'

# Read the OAuth2 token from an environment variable
ACCESS_TOKEN = os.getenv('LINKEDIN_ACCESS_TOKEN')
if not ACCESS_TOKEN:
    sys.stderr.write('Error: Please set the LINKEDIN_ACCESS_TOKEN environment variable.\n')
    sys.exit(1)

HEADERS = {
    'Authorization': f'Bearer {ACCESS_TOKEN}',
    'Accept': 'application/json',
    'Linkedin-Version': '202312'
}


def fetch_snapshot(domain: str) -> list:
    """
    Fetches all snapshot entries for a given domain (e.g., POSITIONS or EDUCATION) by paging through results.

    Args:
        domain: One of 'POSITIONS' or 'EDUCATION'.

    Returns:
        A list of snapshotData dictionaries.
    """
    start = 0
    all_entries = []

    while True:
        params = {
            'q': 'criteria',
            'start': start,
            'domain': domain
        }
        response = requests.get(API_URL, headers=HEADERS, params=params)
        try:
            response.raise_for_status()
        except requests.HTTPError as e:
            sys.stderr.write(f'HTTP error when fetching {domain} at start={start}: {e}\n')
            raise

        data = response.json()
        paging = data.get('paging', {})
        elements = data.get('elements', [])

        # Extract snapshotData from each page element
        for element in elements:
            entries = element.get('snapshotData', [])
            all_entries.extend(entries)

        total = paging.get('total', 0)
        count = paging.get('count', len(elements))
        start += count

        # Break if we've retrieved all available entries
        if start >= total:
            break

    return all_entries


def main():
    # Fetch all positions and education entries
    print('Fetching positions...')
    positions = fetch_snapshot('POSITIONS')
    print(f'    Retrieved {len(positions)} positions')

    print('Fetching education...')
    education = fetch_snapshot('EDUCATION')
    print(f'    Retrieved {len(education)} education entries')

    print('Fetching profile...')
    profile = fetch_snapshot('PROFILE')
    print(f'    Retrieved {len(profile)} PROFILE entries')

    # Combine into output structure
    output = {
        'positions': positions,
        'education': education,
        'profile': profile[0] if profile else None,
        'last_updated': {
            'timestamp': datetime.now(timezone.utc).isoformat(),
        }
    }

    # Write to JSON file
    out_file = os.path.join("data", 'linkedin_snapshot.json')

    with open(out_file, 'w', encoding='utf-8') as f:
        json.dump(output, f, ensure_ascii=False, indent=4)

    print(f'Data saved to {out_file}')


if __name__ == '__main__':
    main()
