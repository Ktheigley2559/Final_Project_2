#!/usr/bin/env python3
from pathlib import Path

p = Path('report.txt')
text = p.read_text(encoding='utf-8')

marker = 'Final Project'
idx = text.find(marker)
if idx == -1:
    print('Marker not found; aborting')
    raise SystemExit(1)

# find the start of the enclosing <div class="report-block report-assistant"> before marker
start_div = text.rfind('<div class="report-block report-assistant">', 0, idx)
if start_div == -1:
    # fallback: start at marker position
    start_div = idx

# preserve the HTML_REPORT header and opening report-root
header = '<!-- HTML_REPORT -->\n'
root_open = '<div class="report-root">\n'
new_content = header + root_open + text[start_div:]

p.write_text(new_content, encoding='utf-8')
print('Trimmed report.txt; starts at Final Project block')
