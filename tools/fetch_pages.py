#!/usr/bin/env python3
import requests
from pathlib import Path

pages = {
    'raw_databayou.html': 'https://databayou.com/usofa/colleges.html',
    'raw_steelers.html': 'https://www.steelers.com/team/players-roster/',
    'raw_wikipedia.html': 'https://en.wikipedia.org/wiki/2025_Pittsburgh_Steelers_season',
    'raw_stanford.html': 'https://orientation.stanford.edu/moving-stanford/traveling-campus'
}

Path('raw_pages').mkdir(exist_ok=True)

session = requests.Session()
session.headers.update({'User-Agent': 'FinalProject2-Fetcher/1.0 (+https://github.com/Ktheigley2559/Final_Project_2)'})

for fname, url in pages.items():
    out = Path(fname)
    try:
        print(f'Fetching {url} -> {out}')
        r = session.get(url, timeout=20)
        r.raise_for_status()
        out.write_text(r.text, encoding='utf-8')
        # also copy into raw_pages dir
        (Path('raw_pages')/fname).write_text(r.text, encoding='utf-8')
    except Exception as e:
        print(f'Failed to fetch {url}: {e}')

print('Done')
