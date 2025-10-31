#!/usr/bin/env python3
"""
DXCC Country List Scraper
Fetches the official ARRL DXCC list and exports to text and JSON formats.
Source: http://www.arrl.org/files/file/dxcclist.txt
"""

import requests
import json
import re
from typing import List, Dict, Optional


def fetch_dxcc_list() -> str:
    """Fetch the DXCC list from ARRL website."""
    url = "http://www.arrl.org/files/file/dxcclist.txt"
    print(f"Fetching DXCC data from {url}...")

    try:
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        print("Successfully fetched DXCC data")
        return response.text
    except requests.RequestException as e:
        print(f"Error fetching data: {e}")
        raise


def clean_whitespace(text: str) -> str:
    """Remove all extraneous whitespace from text."""
    return ' '.join(text.split())


def parse_dxcc_entry(line: str) -> Optional[Dict[str, str]]:
    """Parse a single DXCC entity line into a dictionary."""
    parts = []
    parts.append(r'^\s*(\S+)\s+')
    parts.append(r'(.+?)\s+')
    parts.append(r'(AF|AN|AS|EU|NA|OC|SA)\s+')
    parts.append(r'(\S+)\s+')
    parts.append(r'(\S+)\s+')
    parts.append(r'(\d+)\s*$')
    pattern = ''.join(parts)

    match = re.match(pattern, line)
    if match:
        prefix = match.group(1).strip()
        entity = match.group(2).strip()
        continent = match.group(3).strip()
        itu_zone = match.group(4).strip()
        cq_zone = match.group(5).strip()
        code = match.group(6).strip()

        qsl_service = '*' in prefix
        third_party = '#' in prefix

        prefix_clean = re.sub(r'\([^)]*\)', '', prefix)
        prefix_clean = prefix_clean.replace('*', '').replace('#', '').replace('^', '')
        prefix_clean = clean_whitespace(prefix_clean)

        entity = clean_whitespace(entity)
        itu_zone = clean_whitespace(itu_zone)
        cq_zone = clean_whitespace(cq_zone)

        # Remove trailing commas from zones
        itu_zone = itu_zone.rstrip(',')
        cq_zone = cq_zone.rstrip(',')

        return {
            'prefix': prefix_clean,
            'entity': entity,
            'continent': continent,
            'itu_zone': itu_zone,
            'cq_zone': cq_zone,
            'code': code,
            'qsl_service': qsl_service,
            'third_party': third_party
        }

    return None


def parse_dxcc_data(content: str) -> tuple:
    """Parse the DXCC list content into current and deleted entities."""
    current_entities = []
    deleted_entities = []
    parsing_deleted = False

    lines = content.split('\n')
    i = 0

    while i < len(lines):
        line = lines[i]

        if 'DELETED ENTITIES' in line:
            parsing_deleted = True
            i += 1
            continue

        if (not line.strip() or
            line.strip().startswith('Prefix') or
            line.strip().startswith('Entity') or
            line.strip().startswith('---') or
            line.strip().startswith('NOTE:') or
            line.strip().startswith('ZONE') or
            line.strip().startswith('Copyright') or
            line.strip().startswith('NOTES:') or
            line.strip().startswith('Continent') or
            'Total:' in line or
            'Edition' in line):
            i += 1
            continue

        entry = parse_dxcc_entry(line)
        if entry:
            if i + 1 < len(lines):
                next_line = lines[i + 1].strip()
                cont_parts = []
                cont_parts.append(r'^[A-Z0-9,\s\-#*\^]+$')
                continuation_pattern = ''.join(cont_parts)
                continents_check = ['AF', 'AN', 'AS', 'EU', 'NA', 'OC', 'SA']
                if (next_line and
                    not any(c in next_line for c in continents_check) and
                    re.match(continuation_pattern, next_line) and
                    len(next_line) < 30):
                    cont_prefix = next_line.replace('*', '').replace('#', '').replace('^', '')
                    cont_prefix = clean_whitespace(cont_prefix)
                    entry['prefix'] = entry['prefix'] + ', ' + cont_prefix
                    i += 1

            if parsing_deleted:
                deleted_entities.append(entry)
            else:
                current_entities.append(entry)

        i += 1

    return current_entities, deleted_entities


def write_text_file(current: List[Dict], deleted: List[Dict], filename: str):
    """Write DXCC data to a formatted text file."""
    print(f"Writing text file: {filename}")

    with open(filename, 'w', encoding='utf-8') as f:
        f.write("ARRL DXCC ENTITY LIST\n")
        f.write("=" * 80 + "\n\n")

        f.write(f"CURRENT ENTITIES ({len(current)} total)\n")
        f.write("-" * 80 + "\n\n")

        f.write(f"{'Prefix':<15} {'Entity':<30} {'Cont':<6} {'ITU':<6} {'CQ':<6} {'Code':<6}\n")
        f.write("-" * 80 + "\n")

        for entity in current:
            prefix = entity['prefix']
            if entity['qsl_service']:
                prefix += '*'
            if entity['third_party']:
                prefix += '#'

            f.write(f"{prefix:<15} {entity['entity']:<30} "
                   f"{entity['continent']:<6} {entity['itu_zone']:<6} "
                   f"{entity['cq_zone']:<6} {entity['code']:<6}\n")

        f.write("\n\n")
        f.write(f"DELETED ENTITIES ({len(deleted)} total)\n")
        f.write("-" * 80 + "\n\n")

        f.write(f"{'Prefix':<15} {'Entity':<30} {'Cont':<6} {'ITU':<6} {'CQ':<6} {'Code':<6}\n")
        f.write("-" * 80 + "\n")

        for entity in deleted:
            f.write(f"{entity['prefix']:<15} {entity['entity']:<30} "
                   f"{entity['continent']:<6} {entity['itu_zone']:<6} "
                   f"{entity['cq_zone']:<6} {entity['code']:<6}\n")

        f.write("\n")
        f.write("Legend:\n")
        f.write("  * = QSL service available\n")
        f.write("  # = Third-party traffic allowed\n")

    print(f"Text file written successfully: {len(current)} current, {len(deleted)} deleted entities")


def write_json_file(current: List[Dict], deleted: List[Dict], filename: str):
    """Write DXCC data to a Python file."""
    print(f"Writing Python file: {filename}")

    with open(filename, 'w', encoding='utf-8') as f:
        f.write('dxcc = ')
        json_str = json.dumps(current, indent=2, ensure_ascii=False)
        json_str = json_str.replace('true', 'True').replace('false', 'False')
        f.write(json_str)
        f.write('\n')

    print(f"Python file written successfully")


def main():
    """Main function to scrape and save DXCC data."""
    try:
        content = fetch_dxcc_list()

        print("Parsing DXCC data...")
        current_entities, deleted_entities = parse_dxcc_data(content)

        if not current_entities:
            print("Warning: No current entities parsed!")
            return

        print(f"Parsed {len(current_entities)} current entities")
        print(f"Parsed {len(deleted_entities)} deleted entities")

        write_text_file(current_entities, deleted_entities, 'dxcc_list.txt')
        write_json_file(current_entities, deleted_entities, 'dxcc_list.py')

        print("\n" + "=" * 80)
        print("SUCCESS: DXCC data exported successfully!")
        print("=" * 80)
        print(f"Text file: dxcc_list.txt")
        print(f"Python file: dxcc_list.py")
        print(f"\nTotal entities: {len(current_entities)} current, {len(deleted_entities)} deleted")

    except Exception as e:
        print(f"\nERROR: {e}")
        raise


if __name__ == "__main__":
    main()
