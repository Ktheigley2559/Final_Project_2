#!/usr/bin/env python3
from docx import Document
from pathlib import Path

DOCX_PATH = Path('Final_Project2.docx')
OUT_PATH = Path('report.txt')

if not DOCX_PATH.exists():
    print(f"{DOCX_PATH} not found")
    raise SystemExit(1)

# Read document
doc = Document(DOCX_PATH)

parts = []  # list of html blocks

for para in doc.paragraphs:
    if not para.text.strip():
        # preserve paragraph break
        parts.append('<pre>\n</pre>')
        continue
    # build paragraph HTML from runs, preserving color
    spans = []
    for run in para.runs:
        text = run.text.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
        color = None
        try:
            if run.font.color and run.font.color.rgb:
                color = str(run.font.color.rgb)  # 'RRGGBB'
        except Exception:
            color = None
        if color:
            spans.append(f'<span style="color:#{color};">{text}</span>')
        else:
            spans.append(f'<span>{text}</span>')
    para_html = ''.join(spans)
    # wrap in pre so whitespace preserved
    parts.append(f'<pre>{para_html}</pre>')

# Now classify each <pre> block as USER if its inner text color is #FFFFFF (or contains span with that color), else ASSISTANT.
html_blocks = []
for block in parts:
    # find color occurrences
    if '#FFFFFF' in block.upper() or '#FFF' in block.upper():
        role = 'USER'
    else:
        role = 'ASSISTANT'
    # create labeled block
    html_blocks.append(f'<div class="report-block report-{role.lower()}"><div class="report-label">{role}</div>{block}</div>')

html = '<div class="report-root">' + '\n'.join(html_blocks) + '</div>'
# Prepend marker so frontend knows it's safe HTML
marker = '<!-- HTML_REPORT -->\n'
OUT_PATH.write_text(marker + html, encoding='utf-8')
print(f'Wrote {OUT_PATH} ({len(html)} bytes)')
