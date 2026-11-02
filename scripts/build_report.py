#!/usr/bin/env python3
"""Resolve measured facts in the editable source and typeset the report PDF."""
import html
import json
from pathlib import Path
import re
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, KeepTogether, PageBreak

ROOT = Path(__file__).resolve().parents[1]


def resolve(text, facts):
    return re.sub(r'\{\{([a-zA-Z0-9_]+)\}\}', lambda match: str(facts[match[1]]), text)


def render(text, output, title):
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle('Body', fontName='Times-Roman', fontSize=10.5, leading=14.1,
        spaceAfter=8, splitLongWords=True))
    styles.add(ParagraphStyle('ReportTitle',fontName='Helvetica-Bold',fontSize=23,leading=28,spaceAfter=16))
    styles.add(ParagraphStyle('Section',fontName='Helvetica-Bold',fontSize=14,leading=18,spaceBefore=15,spaceAfter=9,keepWithNext=True))
    styles.add(ParagraphStyle('Subsection',fontName='Helvetica-Bold',fontSize=11.5,leading=15,spaceBefore=9,spaceAfter=7,keepWithNext=True))
    styles.add(ParagraphStyle('Caption',fontName='Helvetica',fontSize=8.5,leading=11,spaceAfter=12))
    blocks = text.split('\n\n')
    story = []
    for block in blocks:
        block = block.strip()
        if not block:
            continue
        if block.startswith('!['):
            match = re.fullmatch(r'!\[([^]]*)\]\(([^)]+)\)',block)
            if not match:
                raise ValueError('invalid image block')
            path = (ROOT/'report'/match[2]).resolve()
            image = Image(str(path))
            scale = min(495/image.imageWidth,610/image.imageHeight)
            image.drawWidth=image.imageWidth*scale; image.drawHeight=image.imageHeight*scale
            image.hAlign='CENTER'
            story.extend([Spacer(1,8),image,Spacer(1,6)])
        else:
            style='Body'
            if block=='## References':
                story.append(PageBreak())
            for prefix,name in [('### ','Subsection'),('## ','Section'),('# ','ReportTitle')]:
                if block.startswith(prefix):
                    block=block[len(prefix):]; style=name; break
            if block.startswith('Figure '):
                style='Caption'
            paragraph=Paragraph(html.escape(block).replace('\n',' '),styles[style])
            if style=='Caption' and len(story)>=3 and isinstance(story[-2],Image):
                story[-3:]=[KeepTogether(story[-3:]+[paragraph])]
            else:
                story.append(paragraph)
    def footer(canvas, doc):
        canvas.setFont('Helvetica',8)
        canvas.setFillColor(colors.HexColor('#606060'))
        canvas.drawString(50,25,'Naive substring search and KMP')
        canvas.drawRightString(A4[0]-50,25,str(doc.page))
    document=SimpleDocTemplate(str(output),pagesize=A4,leftMargin=50,rightMargin=50,topMargin=47,bottomMargin=43,
        title=title,author='Ethan Goldman')
    document.build(story,onFirstPage=footer,onLaterPages=footer)


if __name__=='__main__':
    facts=json.loads((ROOT/'results/facts.json').read_text())
    source=(ROOT/'report/report.template.md').read_text()
    final=resolve(source,facts)
    if '{{' in final:
        raise ValueError('unresolved measured fact')
    words=len(final.split())
    if not 4000 <= words <= 6000:
        raise ValueError(f'report word count outside target: {words}')
    (ROOT/'report/report.md').write_text(final)
    render(final,ROOT/'report/report.pdf','First-occurrence byte search: naive search and KMP')
    print(f'Report built: {words} whitespace-delimited words including references and captions')
