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


# Human-readable instructions surfaced when the token can no longer authenticate.
# This DMA "self-serve" app has no programmatic refresh token, so a new access
# token must be minted by hand (roughly once a year) via LinkedIn's OAuth tool.
REAUTH_INSTRUCTIONS = (
    "LinkedIn access token is expired or revoked (HTTP {status}).\n"
    "The Member Snapshot data was NOT updated; the previous snapshot has been kept.\n"
    "\n"
    "To fix, regenerate the token (must be done manually ~once a year) using https://www.linkedin.com/developers/tools/oauth'.\n"
)


def _signal_auth_failed():
    """Set the `auth_failed` step output so the workflow can open an alert issue."""
    output_path = os.getenv('GITHUB_OUTPUT')
    if output_path:
        with open(output_path, 'a', encoding='utf-8') as fh:
            fh.write('auth_failed=true\n')


def main():
    # Fetch all positions and education entries. Any failure here is non-fatal:
    # we keep the last-good snapshot and let the rest of the pipeline continue.
    try:
        print('Fetching positions...')
        positions = fetch_snapshot('POSITIONS')
        print(f'    Retrieved {len(positions)} positions')

        print('Fetching education...')
        education = fetch_snapshot('EDUCATION')
        print(f'    Retrieved {len(education)} education entries')

        print('Fetching profile...')
        profile = fetch_snapshot('PROFILE')
        print(f'    Retrieved {len(profile)} PROFILE entries')
    except requests.HTTPError as e:
        status = e.response.status_code if e.response is not None else None
        if status in (401, 403):
            sys.stderr.write(REAUTH_INSTRUCTIONS.format(status=status))
            print(
                f'::warning title=LinkedIn token expired::LinkedIn access token '
                f'expired or revoked (HTTP {status}). Snapshot not updated - '
                f'regenerate it via the OAuth Token Generator Tool.'
            )
            _signal_auth_failed()
        else:
            sys.stderr.write(f'Transient HTTP error fetching LinkedIn data: {e}\n')
            print(
                f'::warning title=LinkedIn fetch failed::Could not fetch LinkedIn '
                f'data (HTTP {status}). Snapshot not updated; will retry next run.'
            )
        print('Keeping previous data/linkedin_snapshot.json unchanged.')
        sys.exit(0)
    except requests.RequestException as e:
        sys.stderr.write(f'Network error fetching LinkedIn data: {e}\n')
        print(
            '::warning title=LinkedIn fetch failed::Network error while fetching '
            'LinkedIn data. Snapshot not updated; will retry next run.'
        )
        print('Keeping previous data/linkedin_snapshot.json unchanged.')
        sys.exit(0)

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
