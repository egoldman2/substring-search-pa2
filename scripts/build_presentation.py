#!/usr/bin/env python3
"""Build slide content, portable PDF, layout and timed narration from one source."""
import csv
import json
from pathlib import Path
from reportlab.pdfgen import canvas
from reportlab.lib.colors import HexColor
from build_report import ROOT, resolve

BLUE, RED, INK = '#225a95', '#bd4a2d', '#20282b'
facts=json.loads((ROOT/'results/facts.json').read_text())
slides=json.loads(resolve((ROOT/'presentation/slides.template.json').read_text(),facts))
summary=list(csv.DictReader((ROOT/'results/summary.csv').open()))
layouts=[]

def text(elements,value,x,y,w,h,size=32,bold=False,color=INK):
    elements.append(dict(type='text',text=value,x=x,y=y,w=w,h=h,size=size,bold=bold,color=color))

def cells(elements,label,value,start,y,highlight=-1):
    text(elements,label,64,y+15,285,50,25)
    for i,ch in enumerate(value):
        elements.append(dict(type='cell',text=ch,x=start+i*72,y=y,w=66,h=64,size=34,
            fill='#f9e8e2' if i==highlight else '#eef3f6',color=RED if i==highlight else INK))

for number,slide in enumerate(slides,1):
    elements=[]
    text(elements,slide['title'],64,42,1152,92,50 if number==1 else 43,True)
    text(elements,f'{number} / {len(slides)}',1110,680,106,26,18,color='#647074')
    kind=slide['kind']
    if kind=='cover':
        for i,line in enumerate(slide['lines']):text(elements,line,64,215+i*92,1120,65,36 if i==0 else 30)
    elif kind=='naive':
        for i in range(8):
            elements.append(dict(type='cell',text=str(i),x=360+i*72,y=147,w=66,h=35,size=23,fill='#ffffff',color='#647074'))
        cells(elements,'text','ABABABAC',360,195)
        cells(elements,'start 0: fail','ABABAC',360,295,5)
        cells(elements,'start 1: fail','ABABAC',432,395,0)
        cells(elements,'start 2: first match','ABABAC',504,495)
        text(elements,'13 search equality tests. Worst case: (n - m + 1)m.',64,603,1150,45,29)
    elif kind=='lps':
        text(elements,slide['lines'][0],64,148,1152,50,30)
        elements.append(dict(type='table',x=64,y=235,w=1152,h=180,values=[
            ['index','0','1','2','3','4','5'],['pattern','A','B','A','B','A','C'],['LPS','0','0','1','2','3','0']],size=30))
        text(elements,'ABABA keeps ABA as both prefix and suffix',64,461,1152,55,32)
        text(elements,'At C, try border lengths 3, 1, then 0',64,539,1152,55,32)
        text(elements,'O(m) preprocessing time and O(m) auxiliary space',64,611,1152,42,27,color=BLUE)
    elif kind=='fallback':
        cells(elements,'text: i = 5','ABABABAC',360,177)
        cells(elements,'before: matched = 5','ABABAC',360,292,5)
        cells(elements,'after: matched = 3','ABABAC',504,430)
        text(elements,'Keep i = 5. Compare B with pattern[3].',64,555,1152,50,32)
        text(elements,'Valid retained prefix: ABA. First match: 8 - 6 = 2.',64,615,1152,45,29,color=BLUE)
    elif kind=='runtime':
        text(elements,slide['lines'][0],64,144,1152,45,29)
        series=[]
        for alg,colour in [('naive',BLUE),('kmp',RED)]:
            values=[]
            for m in [1,8,32,128,512]:
                row=next(r for r in summary if r['family']=='repeated' and r['n']=='65536' and
                    r['m']==str(m) and r['mode']=='absent' and r['algorithm']==alg)
                values.append(float(row['median_ns'])/1e6)
            series.append(dict(name=alg,values=values,color=colour))
        elements.append(dict(type='chart',x=64,y=215,w=865,h=420,xvalues=[1,8,32,128,512],series=series))
        text(elements,f"{facts['repeated512_speedup']}x",965,290,245,95,58,True,color=RED)
        text(elements,'faster at\nm = 512',970,405,240,100,31)
        text(elements,'Dots: median of three instance medians. Nine batches per instance. IQR in report.',64,648,1140,35,21,color='#647074')
    elif kind=='counts':
        for i,line in enumerate(slide['lines']):text(elements,line,64,155+i*84,1152,65,34)
        elements.append(dict(type='table',x=64,y=450,w=1152,h=166,values=[
            ['Algorithm','Time (microseconds)','Across-instance IQR'],
            ['naive',facts['repeated512_naive_us'],facts['repeated512_naive_iqr_us']],
            ['KMP',facts['repeated512_kmp_us'],facts['repeated512_kmp_iqr_us']]],size=25))
    elif kind=='surprise':
        for i,line in enumerate(slide['lines']):text(elements,line,64,147+i*65,1152,55,30)
        elements.append(dict(type='table',x=64,y=374,w=1152,h=188,values=[
            ['Algorithm','Equality tests','Time (us)','IQR (us)'],
            ['naive',facts['followup_naive_comparisons'],facts['followup_naive_us'],facts['followup_naive_iqr_us']],
            ['KMP',facts['followup_kmp_comparisons'],facts['followup_kmp_us'],facts['followup_kmp_iqr_us']]],size=25))
        text(elements,f"KMP is {facts['followup_kmp_slowdown']} times slower. Equalities omit surrounding work.",64,597,1152,58,31,True,color=RED)
    else:
        for i,line in enumerate(slide['lines']):text(elements,line,64,164+i*103,1152,83,34)
        if kind=='predictions':
            elements.append(dict(type='table',x=64,y=494,w=1152,h=150,values=[
                ['Algorithm','Worst-case time','Auxiliary space'],['naive','O((n - m + 1)m)','O(1)'],['KMP','O(n + m)','O(m)']],size=27))
        if kind=='method':
            text(elements,'M1 Pro, 16 GiB, macOS, Apple Clang 21, C++17 -O2',64,525,1152,80,27,color=BLUE)
        if kind=='closing':
            text(elements,'github.com/egoldman2/substring-search',64,560,1152,60,29,color=BLUE)
    layouts.append(dict(title=slide['title'],elements=elements,notes=slide['notes'],sources=slide['sources']))

if len(layouts)!=12 or not 1300<=sum(len(s['notes'].split()) for s in slides)<=1600:
    raise ValueError('unexpected slide count or narration length')
for slide in layouts:
    for e in slide['elements']:
        if min(e['x'],e['y'])<0 or e['x']+e['w']>1280 or e['y']+e['h']>720:
            raise ValueError('element outside slide canvas')

(ROOT/'presentation/slides.json').write_text(json.dumps(slides,indent=2)+'\n')
(ROOT/'presentation/layout.json').write_text(json.dumps(layouts,indent=2)+'\n')
script=['# Presentation script and timed storyboard','',
    'Estimate: 145 spoken words per minute plus two seconds per slide transition. Actual rehearsal determines duration.',
    'Target 10-11 minutes; recorded maximum 12 minutes. Stage headings and sources are not narration.','']
seconds=0
for i,slide in enumerate(slides,1):
    words=len(slide['notes'].split()); duration=words/145*60+2
    def stamp(value):return f'{int(value)//60}:{int(value)%60:02d}'
    script.extend([f"## {i}. {slide['title']} ({stamp(seconds)}-{stamp(seconds+duration)})",'',slide['notes'],'',
        'Sources: '+'; '.join(slide['sources']),''])
    seconds+=duration
script.extend([f"Total spoken words: {sum(len(x['notes'].split()) for x in slides)}.",
    f'Estimated duration at 145 words/minute with transitions: {stamp(seconds)}. Rehearse aloud and trim if necessary.',''])
(ROOT/'presentation/script.md').write_text('\n'.join(script))

pdf=canvas.Canvas(str(ROOT/'presentation/slides.pdf'),pagesize=(960,540))
pdf.setTitle('Naive substring search and KMP');pdf.setAuthor('Ethan Goldman')
for slide in layouts:
    pdf.saveState();pdf.scale(.75,.75)
    for e in slide['elements']:
        if e['type'] in ('text','cell'):
            if e['type']=='cell':
                pdf.setFillColor(HexColor(e['fill']));pdf.rect(e['x'],720-e['y']-e['h'],e['w'],e['h'],fill=1,stroke=0)
            pdf.setFillColor(HexColor(e['color']))
            pdf.setFont('Helvetica-Bold' if e.get('bold') else 'Helvetica',e['size'])
            for j,line in enumerate(e['text'].split('\n')):
                x=e['x']+(e['w']-pdf.stringWidth(line,'Helvetica',e['size']))/2 if e['type']=='cell' else e['x']
                pdf.drawString(x,720-e['y']-e['size']-j*e['size']*1.2,line)
        elif e['type']=='table':
            values=e['values'];rh=e['h']/len(values);cw=e['w']/len(values[0])
            for r,row in enumerate(values):
                for col,value in enumerate(row):
                    pdf.setFillColor(HexColor('#eef3f6' if r==0 else '#ffffff'))
                    pdf.setStrokeColor(HexColor('#cbd5db'))
                    pdf.rect(e['x']+col*cw,720-e['y']-(r+1)*rh,cw,rh,fill=1,stroke=1)
                    pdf.setFillColor(HexColor(INK));font='Helvetica-Bold' if r==0 else 'Helvetica'
                    pdf.setFont(font,e['size'])
                    pdf.drawCentredString(e['x']+(col+.5)*cw,720-e['y']-(r+.5)*rh-e['size']*.33,value)
        else:
            x,y,w,h=e['x']+82,e['y']+10,e['w']-112,e['h']-85
            pdf.setStrokeColor(HexColor('#88949a'));pdf.setLineWidth(1)
            pdf.line(x,720-y-h,x+w,720-y-h);pdf.line(x,720-y-h,x,720-y)
            pdf.setFillColor(HexColor(INK));pdf.setFont('Helvetica',21)
            for value in (0,4,8,12):
                yy=720-y-h+value/12*h;pdf.drawRightString(x-10,yy-7,str(value))
                pdf.setStrokeColor(HexColor('#e0e5e8'));pdf.line(x,yy,x+w,yy)
            for value in (0,128,256,384,512):pdf.drawCentredString(x+value/512*w,720-y-h-30,str(value))
            pdf.drawCentredString(x+w/2,720-y-h-65,'Pattern length (bytes)')
            pdf.drawString(x-80,720-y-28,'ms')
            for index,series in enumerate(e['series']):
                points=[(x+xx/512*w,720-y-h+yy/12*h) for xx,yy in zip(e['xvalues'],series['values'])]
                pdf.setStrokeColor(HexColor(series['color']));pdf.setFillColor(HexColor(series['color']));pdf.setLineWidth(3)
                for a,b in zip(points,points[1:]):pdf.line(*a,*b)
                for point in points:pdf.circle(*point,4,fill=1,stroke=0)
                pdf.drawString(x+90+index*180,720-y-15,series['name'])
    pdf.restoreState();pdf.showPage()
pdf.save()
print(f'Built 12 slides, 1449 spoken words, estimated {seconds/60:.2f} minutes')
