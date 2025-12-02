#!/usr/bin/env python3
"""
Insert source URLs into transcript.txt (plain text) and report.txt (HTML-marked).
This script is idempotent: it will not insert duplicate source blocks if they already exist.
"""
from pathlib import Path

SRC_URLS = [
    'https://databayou.com/usofa/colleges.html',
    'https://www.steelers.com/team/players-roster/',
    'https://en.wikipedia.org/wiki/2025_Pittsburgh_Steelers_season',
    'https://orientation.stanford.edu/moving-stanford/traveling-campus',
]

TRANSCRIPT = Path('transcript.txt')
REPORT = Path('report.txt')

SOURCES_HEADER_TEXT = 'Source URLs (plain text):\n' + '\n'.join(SRC_URLS) + '\n\n'

# Update transcript.txt
if TRANSCRIPT.exists():
    txt = TRANSCRIPT.read_text(encoding='utf-8')
    if 'Source URLs (plain text):' not in txt.splitlines()[:10]:
        TRANSCRIPT.write_text(SOURCES_HEADER_TEXT + txt, encoding='utf-8')
        print('Prepended source URLs to transcript.txt')
    else:
        print('transcript.txt already contains source header; skipping')
else:
    print('transcript.txt not found; skipping')

# Update report.txt (HTML-marked)
if REPORT.exists():
    rpt = REPORT.read_text(encoding='utf-8')
    if '<div class="report-root">' in rpt and 'SOURCES' not in rpt.splitlines()[:20]:
        insert_after = '<div class="report-root">'
        idx = rpt.find(insert_after)
        if idx != -1:
            idx_end = idx + len(insert_after)
            source_block = '\n<div class="report-block report-assistant"><div class="report-label">SOURCES</div><pre>' + '\n'.join(SRC_URLS) + '</pre></div>\n'
            new_rpt = rpt[:idx_end] + source_block + rpt[idx_end:]
            REPORT.write_text(new_rpt, encoding='utf-8')
            print('Inserted SOURCES block into report.txt')
        else:
            print('Could not find insertion point in report.txt; skipping')
    else:
        print('report.txt already contains SOURCES or missing report-root; skipping')
else:
    print('report.txt not found; skipping')
