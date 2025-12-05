#!/usr/bin/env python3
from pathlib import Path

p = Path('report.txt')
text = p.read_text(encoding='utf-8')
lines = text.splitlines(keepends=True)

# locate WEB Pages heading and Tools heading
start_idx = None
end_idx = None
for i,l in enumerate(lines):
    if 'WEB Pages/URLS' in l or 'WEB Pages/URLS &amp; Why' in l or 'WEB Pages/URLS & Why' in l:
        start_idx = i
        break
for j in range(start_idx+1, len(lines)):
    if '<span>Tools</span>' in lines[j]:
        end_idx = j
        break

if start_idx is None or end_idx is None:
    print('Could not locate section boundaries; aborting')
    raise SystemExit(1)

# Keep the heading line itself
heading_line = lines[start_idx]

new_block = []
new_block.append('<div class="report-block report-assistant"><div class="report-label">ASSISTANT</div><pre>')
new_block.append('https://databayou.com/usofa/colleges.html\n')
new_block.append('-needed locations of where each university/college is located.\n\n')
new_block.append('https://www.steelers.com/team/players-roster/\n')
new_block.append('-needed names of the current roster, along with where they attended each university.\n\n')
new_block.append('https://en.wikipedia.org/wiki/2025_Pittsburgh_Steelers_season\n')
new_block.append('-needed names of all the current draft picks and free agents, along with where they attended each university.\n\n')
new_block.append('https://orientation.stanford.edu/moving-stanford/traveling-campus\n')
new_block.append('-needed the exact location of this specific institution because it showed up null in a previous query.\n')
new_block.append('</pre></div>\n')

# build new lines
new_lines = lines[:start_idx+1] + new_block + lines[end_idx:]

p.write_text(''.join(new_lines), encoding='utf-8')
print('Updated report.txt')
