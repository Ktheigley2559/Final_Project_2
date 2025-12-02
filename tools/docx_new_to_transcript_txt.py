#!/usr/bin/env python3
from docx import Document
from pathlib import Path

DOCX_CANDIDATES = [Path('transcript_NEW.docx'), Path('Transcript_NEW.docx'), Path('transcript_new.docx')]
DOCX_PATH = None
for p in DOCX_CANDIDATES:
    if p.exists():
        DOCX_PATH = p
        break
OUT_PATH = Path('transcript_from_docx.txt')

if DOCX_PATH is None:
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
                color = str(run.font.color.rgb)
        except Exception:
            color = None
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
