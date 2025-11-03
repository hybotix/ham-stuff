#!/usr/bin/env python3
"""
Search DXCC list by country or zone
Usage: python dxcc_search.py <type> <search_term> [output_file]
       python dxcc_search.py c <country_name> [output_file]
       python dxcc_search.py z <zone_code> [output_file]
"""

import sys
from datetime import datetime
from dxcc_list import dxcc


def search_by_country(query):
    """Search for DXCC entities by country name."""
    query_lower = query.lower()
    matches = []

    for entity in dxcc:
        if query_lower in entity['entity'].lower():
            matches.append(entity)

    return matches


def search_by_zone(continent):
    """Search for DXCC entities by zone (continent)."""
    continent_upper = continent.upper()

    valid_continents = ['AF', 'AN', 'AS', 'EU', 'NA', 'OC', 'SA']
    if continent_upper not in valid_continents:
        print("Invalid zone code: " + continent)
        print("Valid codes: AF (Africa), AN (Antarctica), AS (Asia), EU (Europe),")
        print("             NA (North America), OC (Oceania), SA (South America)")
        return None

    matches = []
    for entity in dxcc:
        if continent_upper in entity['continent']:
            matches.append(entity)

    return matches


def print_results(matches, search_term, search_type, output_file=None):
    """Print search results in a formatted table."""
    if matches is None:
        return

    lines = []

    if not matches:
        msg = "\nNo matches found for '" + search_term + "'\n"
        if output_file:
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(msg)
            print("Results written to: " + output_file)
        else:
            print(msg)
        return

    if search_type == 'z':
        continent_names = {
            'AF': 'Africa',
            'AN': 'Antarctica',
            'AS': 'Asia',
            'EU': 'Europe',
            'NA': 'North America',
            'OC': 'Oceania',
            'SA': 'South America'
        }
        cont_name = continent_names.get(search_term.upper(), search_term)
        lines.append("\nFound " + str(len(matches)) + " entities in " + cont_name + " (" + search_term.upper() + "):\n")
        matches = sorted(matches, key=lambda x: x['entity'])
    else:
        lines.append("\nFound " + str(len(matches)) + " match(es) for '" + search_term + "':\n")

    if search_type == 'z':
        lines.append("-" * 99)
        lines.append("{:<25} {:<35} {:<8} {:<6} {:<6}".format('Prefix', 'Entity', 'ITU', 'CQ', 'Code'))
        lines.append("-" * 99)
    else:
        lines.append("-" * 105)
        lines.append("{:<25} {:<35} {:<6} {:<8} {:<6} {:<6}".format('Prefix', 'Entity', 'Cont', 'ITU', 'CQ', 'Code'))
        lines.append("-" * 105)

    for entity in matches:
        prefix = entity['prefix']
        prefix = prefix.rstrip(',').strip()
        markers = ''
        if entity['qsl_service']:
            markers += '*'
        if not entity['third_party']:
            markers += '#'
        if markers:
            prefix += " " + markers

        if search_type == 'z':
            line = "{:<25} {:<35} {:<8} {:<6} {:<6}".format(
                prefix,
                entity['entity'],
                entity['itu_zone'],
                entity['cq_zone'],
                entity['code']
            )
        else:
            line = "{:<25} {:<35} {:<6} {:<8} {:<6} {:<6}".format(
                prefix,
                entity['entity'],
                entity['continent'],
                entity['itu_zone'],
                entity['cq_zone'],
                entity['code']
            )
        lines.append(line)

    if search_type == 'z':
        lines.append("-" * 99)
    else:
        lines.append("-" * 105)
    lines.append("\nLegend: * = QSL service available, # = Third-party traffic NOT allowed\n")

    output = '\n'.join(lines)

    if output_file:
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(output)
        print("\nResults written to: " + output_file)
        print("Found " + str(len(matches)) + " match(es)")
    else:
        print(output)


def generate_filename(search_type, search_term):
    """Generate a unique filename based on search parameters."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    clean_term = search_term.replace(' ', '_').replace('/', '_')
    type_name = 'country' if search_type == 'c' else 'zone'
    return "dxcc_" + type_name + "_" + clean_term + "_" + timestamp + ".txt"


def show_usage():
    """Display usage information."""
    print("Usage: python dxcc_search.py <type> <search_term> [output_file]")
    print("\nSearch Types:")
    print("  c - Search by country name (partial match)")
    print("  z - Search by zone (continent code)")
    print("\nExamples:")
    print("  python dxcc_search.py c japan")
    print('  python dxcc_search.py c "united states" usa_results.txt')
    print("  python dxcc_search.py z EU")
    print("  python dxcc_search.py z AS asia_results.txt")
    print("\nIf output_file is '-', a unique filename will be auto-generated")
    print("Example: python dxcc_search.py c japan -")
    print("\nValid Zone Codes:")
    print("  AF = Africa")
    print("  AN = Antarctica")
    print("  AS = Asia")
    print("  EU = Europe")
    print("  NA = North America")
    print("  OC = Oceania")
    print("  SA = South America")


def main():
    """Main function."""
    output_file = None
    search_term = None
    search_type = None
    matches = None

    if len(sys.argv) < 2:
        show_usage()
        print("\nInteractive mode:\n")

        while True:
            search_type = input("Enter search type - [C]ountry or [Z]one [C]: ").strip().lower()
            if not search_type:
                search_type = 'c'
                break
            if search_type in ['c', 'z']:
                break
            print("Invalid search type. Must be 'c' or 'z'.")

        while True:
            if search_type == 'c':
                search_term = input("Enter country name to search: ").strip()
            else:
                search_term = input("Enter zone code (AF/AN/AS/EU/NA/OC/SA): ").strip()

            if search_term:
                break
            print("Search term cannot be empty. Please enter a value.")

        while True:
            save_choice = input("Save to file? [Y]es or [N]o [N]: ").strip().lower()
            if not save_choice:
                save_choice = 'n'
                break
            if save_choice in ['y', 'n']:
                break
            print("Invalid choice. Must be 'y' or 'n'.")

        if save_choice == 'y':
            filename = input("Enter filename (or press Enter for auto-generated): ").strip()
            if not filename:
                output_file = generate_filename(search_type, search_term)
            else:
                output_file = filename

    elif len(sys.argv) < 3:
        show_usage()
        sys.exit(1)
    else:
        search_type = sys.argv[1].lower()

        if search_type not in ['c', 'z']:
            print("Invalid search type: " + search_type)
            print("Must be 'c' (country) or 'z' (zone)")
            show_usage()
            sys.exit(1)

        if len(sys.argv) == 3:
            search_term = sys.argv[2]
        elif len(sys.argv) == 4:
            search_term = sys.argv[2]
            if sys.argv[3] == '-':
                output_file = generate_filename(search_type, search_term)
            else:
                output_file = sys.argv[3]
        else:
            if sys.argv[-1] == '-' or sys.argv[-1].endswith('.txt'):
                search_term = ' '.join(sys.argv[2:-1])
                if sys.argv[-1] == '-':
                    output_file = generate_filename(search_type, search_term)
                else:
                    output_file = sys.argv[-1]
            else:
                search_term = ' '.join(sys.argv[2:])

    if search_type == 'c':
        matches = search_by_country(search_term)
    else:
        matches = search_by_zone(search_term)

    print_results(matches, search_term, search_type, output_file)


if __name__ == "__main__":
    main()
