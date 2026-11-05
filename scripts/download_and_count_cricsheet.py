"""
Download and Count Official CricSheet IPL Dataset (2008-2026)
--------------------------------------------------------------
Fetches the authoritative ipl_csv2.zip archive from cricsheet.org,
inspects match metadata across all years, and prints verified season counts.
"""

import io
import ssl
import sys
import zipfile
import urllib.request
from collections import defaultdict

sys.stdout.reconfigure(encoding='utf-8')

CRICSHEET_URL = "https://cricsheet.org/downloads/ipl_csv2.zip"


def download_and_count():
    print(f"Connecting to CricSheet at {CRICSHEET_URL}...")
    ctx = ssl.create_default_context()
    req = urllib.request.Request(CRICSHEET_URL, headers={'User-Agent': 'Mozilla/5.0'})

    with urllib.request.urlopen(req, context=ctx, timeout=60) as resp:
        zip_bytes = resp.read()

    print(f"Successfully downloaded archive ({len(zip_bytes):,} bytes).")

    with zipfile.ZipFile(io.BytesIO(zip_bytes)) as z:
        info_files = [f for f in z.namelist() if f.endswith('_info.csv')]
        print(f"Total match info files found: {len(info_files):,}\n")

        matches_by_season = defaultdict(int)
        matches_by_year = defaultdict(int)
        match_details_2026 = []

        for f in info_files:
            match_id = f.replace('_info.csv', '')
            content = z.read(f).decode('utf-8', errors='ignore')
            season = None
            date_val = None

            for line in content.splitlines():
                parts = [p.strip() for p in line.split(',')]
                if len(parts) >= 3 and parts[0] == 'info':
                    if parts[1] == 'season':
                        season = parts[2]
                    elif parts[1] == 'date' and date_val is None:
                        date_val = parts[2]

            year = str(date_val)[:4] if date_val else "Unknown"
            matches_by_season[season] += 1
            matches_by_year[year] += 1

            if year == '2026' or str(season) == '2026':
                match_details_2026.append((match_id, date_val))

    print("==================================================")
    print("      OFFICIAL CRICSHEET MATCH COUNTS BY YEAR     ")
    print("==================================================")
    total_matches = 0
    for y in sorted(matches_by_year.keys()):
        count = matches_by_year[y]
        total_matches += count
        print(f"  Year {y}: {count:>3} matches")

    print("--------------------------------------------------")
    print(f"  TOTAL MATCHES (2008-2026): {total_matches:,} matches")
    print("==================================================\n")

    print(f"2026 Season Check: Exactly {len(match_details_2026)} matches found for 2026.")
    return total_matches, matches_by_year


if __name__ == "__main__":
    download_and_count()
