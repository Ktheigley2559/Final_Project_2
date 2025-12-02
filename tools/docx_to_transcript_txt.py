#!/usr/bin/env python3
from docx import Document
from pathlib import Path

DOCX_PATH = Path('Transcript.docx')
OUT_PATH = Path('transcript_from_docx.txt')

if not DOCX_PATH.exists():
    print(f"{DOCX_PATH} not found")
    raise SystemExit(1)

doc = Document(DOCX_PATH)

parts = []

for para in doc.paragraphs:
    if not para.text.strip():
        parts.append('<pre>\n</pre>')
        continue
    spans = []
    for run in para.runs:
        text = run.text.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
        color = None
        try:
            if run.font.color and run.font.color.rgb:
                color = str(run.font.color.rgb)  # e.g., 'FF0000'
        except Exception:
            color = None
        # Map docx colors to UI colors: white -> user (#ffffff), red -> assistant (map to yellow #ffdf00), else keep original
        ui_color = None
        if color:
            c = color.upper()
            if c in ('FFFFFF','FFF'):
                ui_color = '#ffffff'
            elif c in ('FF0000','F00'):
                ui_color = '#ffdf00'
            else:
                ui_color = f'#{c}'
        if ui_color:
            spans.append(f'<span style="color:{ui_color};">{text}</span>')
        else:
            spans.append(f'<span>{text}</span>')
    para_html = ''.join(spans)
    parts.append(f'<pre>{para_html}</pre>')

html_blocks = []
for block in parts:
    # detect if block contains user color
    upper = block.upper()
    if '#FFFFFF' in upper or '#FFF' in upper:
        role = 'USER'
    else:
        role = 'ASSISTANT'
    html_blocks.append(f'<div class="transcript-block transcript-{role.lower()}"><div class="transcript-label">{role}</div>{block}</div>')

html = '<div class="transcript-root">' + '\n'.join(html_blocks) + '</div>'
marker = '<!-- HTML_TRANSCRIPT -->\n'
OUT_PATH.write_text(marker + html, encoding='utf-8')
print(f'Wrote {OUT_PATH} ({len(html)} bytes)')
