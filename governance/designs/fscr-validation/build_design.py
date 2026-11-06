#!/usr/bin/env python3
"""Build matching HTML, Word and editable diagrams from design-content.json.

Run with the workspace dependency Python and supply its Node and package paths.
No network access or Fusion operations are performed.
"""
import argparse
import base64
import html
import json
import re
import subprocess
import textwrap
from pathlib import Path
from xml.etree import ElementTree as ET

from docx import Document
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_CELL_VERTICAL_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.style import WD_STYLE_TYPE
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Inches, Pt, RGBColor

ROOT = Path(__file__).resolve().parent
STEM = 'fscr-validation-functional-technical-design'
PALETTE = {'framework': '#EAF0F7', 'pillar': '#EAF3EC', 'human': '#FFF2DF', 'core': '#F0EFF8'}


def diagrams():
    out = {}
    nodes = []
    labels = [
        ('Requirements and selected project', 'Project owner and implementer', 'human'),
        ('Resolve scope and prepare local plans', 'Framework and core   |   no Oracle Run Book yet', 'framework'),
        ('Run prevalidation or record explicit skip', 'Framework assesses   |   implementer chooses', 'framework'),
        ('Create Run Book and execute implementation', 'Core services and pillar workflows   |   own approval gates', 'core'),
        ('Review requirements tasks and actual setup', 'Framework assembles   |   pillars define correctness', 'framework'),
        ('Optionally run one transaction check', 'Explicit request   |   pillar procedure and operation gates', 'pillar'),
        ('Publish evidence and decide next action', 'Framework reports   |   project owner accepts gaps', 'human'),
    ]
    for i, (title, sub, color) in enumerate(labels):
        nodes.append(dict(id=f'n{i}', x=50, y=20+i*86, w=640, h=62, title=title, sub=sub, color=color))
    notes = [
        dict(id='a', x=735,y=172,w=230,h=108,title='Prevalidation scope',sub='NOT READY holds handoff\nAn explicit skip leaves\nreadiness unverified',color='human'),
        dict(id='b', x=735,y=430,w=230,h=100,title='Standalone request',sub='May enter transaction\nvalidation independently\nPrerequisites still apply',color='human'),
    ]
    edges=[(f'n{i}',f'n{i+1}',None) for i in range(6)] + [('n2','a',None),('b','n5',None)]
    out['lifecycle']=dict(name='Validation lifecycle',w=1000,h=630,nodes=nodes+notes,edges=edges)

    nodes=[
        dict(id='a',x=40,y=20,w=590,h=65,title='Discover applicable pillar checks',sub='Version and applicability   |   select exactly one',color='framework'),
        dict(id='b',x=40,y=125,w=590,h=65,title='Resolve inputs route and existing records',sub='Identity   privileges   payload limits   duplicate check',color='framework'),
        dict(id='c',x=40,y=230,w=590,h=65,title='Approve exact operation or choose manual steps',sub='Implementer approval   |   evidence and cleanup disclosed',color='human'),
        dict(id='d',x=40,y=335,w=590,h=65,title='Execute once and read back business assertions',sub='Pillar owned API route or implementer run procedure',color='pillar'),
        dict(id='e',x=40,y=440,w=590,h=65,title='Capture evidence then handle cleanup',sub='Separate cleanup approval   |   record retention or removal',color='pillar'),
        dict(id='f',x=40,y=545,w=590,h=65,title='Publish one transaction report',sub='Task summary first   |   check result and cleanup separate',color='framework'),
        dict(id='skip',x=700,y=20,w=260,h=65,title='SKIPPED',sub='Explicit user decision',color='human'),
        dict(id='blocked',x=700,y=125,w=260,h=65,title='BLOCKED',sub='Missing prerequisite or route',color='human'),
        dict(id='unknown',x=700,y=330,w=260,h=125,title='INDETERMINATE',sub='Uncertain mutation outcome\nReconcile by stable key\nDo not blindly create again\nKeep known effects in report',color='human'),
        dict(id='outcomes',x=700,y=545,w=260,h=65,title='Preserve all outcomes',sub='Skip and blockers also report',color='framework'),
    ]
    edges=[(chr(97+i),chr(98+i),None) for i in range(5)] + [('a','skip',None),('b','blocked',None),('d','unknown',None),('outcomes','f',None)]
    out['transaction']=dict(name='Single transaction flow',w=1000,h=635,nodes=nodes,edges=edges)

    nodes=[
        dict(id='router',x=245,y=15,w=510,h=64,title='Router',sub='Intent   project   stage   next action',color='framework'),
        dict(id='shared',x=245,y=128,w=510,h=90,title='Shared validation skills',sub='Prevalidation   Implementation Review\nTransaction Coordinator   Summary and Evidence',color='framework'),
        dict(id='pillar',x=20,y=274,w=445,h=86,title='Pillar definitions and execution',sub='Applicability   assertions   business procedures\nInput limits   duplicate handling   cleanup',color='pillar'),
        dict(id='core',x=535,y=274,w=445,h=86,title='Core technical services',sub='Authentication   declared adapters   Run Book\nService prerequisites and operation approval',color='core'),
        dict(id='schemas',x=20,y=425,w=445,h=74,title='Schemas and local report tools',sub='Contract checks   readiness rules   HTML and JSON',color='framework'),
        dict(id='external',x=535,y=425,w=445,h=74,title='Fusion environment',sub='Access only through a declared approved route',color='core'),
        dict(id='project',x=20,y=560,w=960,h=75,title='Project workspace',sub='Requirements and task references   sanitized evidence   immutable run outputs   decisions\nArtifact index   run records   token usage   authorized untracked exports',color='human'),
    ]
    edges=[('router','shared',None),('shared','pillar',None),('shared','core',None),('pillar','schemas',None),('core','external',None),('schemas','project',None)]
    out['architecture']=dict(name='Technical architecture',w=1000,h=655,nodes=nodes,edges=edges)
    return out


def arrow_points(a,b):
    ax,ay=a['x']+a['w']/2,a['y']+a['h']/2
    bx,by=b['x']+b['w']/2,b['y']+b['h']/2
    if abs(ay-by)<65:
        return [(a['x']+a['w'] if bx>ax else a['x'],ay),(b['x'] if bx>ax else b['x']+b['w'],by)]
    return [(ax,a['y']+a['h']), (ax,(a['y']+a['h']+b['y'])/2), (bx,(a['y']+a['h']+b['y'])/2),(bx,b['y'])]


def create_diagrams(node, modules):
    assets=ROOT/'assets'; assets.mkdir(exist_ok=True)
    mx=ET.Element('mxfile',host='app.diagrams.net',type='device')
    for key, d in diagrams().items():
        page=ET.SubElement(mx,'diagram',id=key,name=d['name'])
        model=ET.SubElement(page,'mxGraphModel',dx='1000',dy=str(d['h']),grid='1',gridSize='10',guides='1',tooltips='1',connect='1',arrows='1',fold='1',page='1',pageScale='1',pageWidth='1000',pageHeight=str(d['h']),math='0',shadow='0')
        root=ET.SubElement(model,'root'); ET.SubElement(root,'mxCell',id='0'); ET.SubElement(root,'mxCell',id='1',parent='0')
        svg=[f'<svg xmlns="http://www.w3.org/2000/svg" width="{d["w"]}" height="{d["h"]}" viewBox="0 0 {d["w"]} {d["h"]}">', '<defs><marker id="arrow" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse"><path d="M 0 0 L 10 5 L 0 10 z" fill="#5A6570"/></marker></defs>', '<rect width="100%" height="100%" fill="white"/>']
        byid={n['id']:n for n in d['nodes']}
        for i,(a,b,label) in enumerate(d['edges']):
            pts=arrow_points(byid[a],byid[b]); ps=' '.join(f'{x},{y}' for x,y in pts)
            svg.append(f'<polyline points="{ps}" fill="none" stroke="#5A6570" stroke-width="2" marker-end="url(#arrow)"/>')
            cell=ET.SubElement(root,'mxCell',id=f'e{i}',value=label or '',style='edgeStyle=orthogonalEdgeStyle;rounded=0;html=1;endArrow=block;strokeColor=#5A6570;strokeWidth=2;',edge='1',parent='1',source=a,target=b)
            ET.SubElement(cell,'mxGeometry',relative='1',attrib={'as':'geometry'})
        for n in d['nodes']:
            fill=PALETTE[n['color']]; x,y,w,h=(n[k] for k in ['x','y','w','h'])
            svg.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="8" fill="{fill}" stroke="#A8B5C1" stroke-width="1.4"/>')
            lines=n['sub'].split('\n'); total=25+20*len(lines); ty=y+(h-total)/2+18
            fs=19 if w>300 else 17
            svg.append(f'<text x="{x+w/2}" y="{ty}" text-anchor="middle" fill="#121C27" font-family="Arial,sans-serif" font-size="{fs}" font-weight="bold">{html.escape(n["title"])}</text>')
            for j,line in enumerate(lines): svg.append(f'<text x="{x+w/2}" y="{ty+24+j*20}" text-anchor="middle" fill="#303B47" font-family="Arial,sans-serif" font-size="16">{html.escape(line)}</text>')
            val=f'<b>{html.escape(n["title"])}</b><br>'+html.escape(n['sub']).replace('\n','<br>')
            cell=ET.SubElement(root,'mxCell',id=n['id'],value=val,style=f'rounded=1;whiteSpace=wrap;html=1;fillColor={fill};strokeColor=#A8B5C1;fontColor=#121C27;fontFamily=Arial;fontSize=17;spacing=8;',vertex='1',parent='1')
            ET.SubElement(cell,'mxGeometry',x=str(x),y=str(y),width=str(w),height=str(h),attrib={'as':'geometry'})
        svg.append('</svg>'); (assets/f'{key}.svg').write_text('\n'.join(svg))
        script="const sharp=require(process.argv[1]); sharp(process.argv[2],{density:240}).png().toFile(process.argv[3]).catch(e=>{console.error(e);process.exit(1)});"
        subprocess.run([node,'-e',script,str(Path(modules)/'sharp'),str(assets/f'{key}.svg'),str(assets/f'{key}.png')],check=True)
    ET.indent(mx)
    ET.ElementTree(mx).write(ROOT/'fscr-validation-diagrams.drawio',encoding='utf-8',xml_declaration=True)


def create_html(d):
    esc=html.escape
    style='''
    :root{color-scheme:light}*{box-sizing:border-box}body{margin:0;font:16px/1.65 -apple-system,BlinkMacSystemFont,"Segoe UI",Arial,sans-serif;color:#202833;background:#f6f7f9}a{color:#245986}header{background:white;padding:64px max(32px,calc((100vw - 1120px)/2));}header h1{font-size:38px;line-height:1.2;margin:0 0 18px;max-width:850px;color:#000}header p{margin:10px 0;max-width:850px}.meta{font-size:14px;color:#455262}.layout{display:grid;grid-template-columns:260px minmax(0,1fr);gap:48px;max-width:1200px;margin:auto;padding:42px 32px 80px}nav{align-self:start;position:sticky;top:20px;font-size:13px;line-height:1.45}nav ol{padding-left:22px}nav li{margin:9px 0}nav a{text-decoration:none}main{min-width:0}section{background:white;padding:34px 38px;margin:0 0 28px;border:1px solid #e2e5e9;border-radius:4px;scroll-margin-top:20px}h2{font-size:26px;line-height:1.25;color:#000;margin:0 0 22px}h3{font-size:18px;line-height:1.3;margin:28px 0 10px;color:#000}p{margin:0 0 16px}ul{padding-left:22px;margin:14px 0}li{margin:8px 0}table{width:100%;border-collapse:collapse;margin:20px 0 22px;font-size:14px;line-height:1.5;table-layout:fixed}td,th{border:1px solid #d9d9d9;padding:11px 12px;text-align:left;vertical-align:middle;overflow-wrap:anywhere}th{background:#34495e;color:white;font-weight:600}tbody tr:nth-child(even){background:#f6f8fa}pre{font:12px/1.7 ui-monospace,SFMono-Regular,Consolas,monospace;white-space:pre-wrap;overflow-wrap:anywhere;padding:16px 0;margin:18px 0;color:#152c40}figure{margin:24px 0}figure img{display:block;width:100%;height:auto}figcaption{font-size:13px;color:#4c5763;margin-top:12px}.sources a{overflow-wrap:anywhere}footer{font-size:13px;color:#5a6570;margin:24px 0} @media(max-width:950px){.layout{display:block;padding:24px 16px}nav{position:static;margin-bottom:30px}section{padding:28px 22px}header{padding:40px 26px}header h1{font-size:32px}} @media print{@page{size:A4;margin:20mm}body{background:white;font-size:10pt;line-height:1.45}header{padding:0 0 20px}header h1{font-size:25pt}.layout{display:block;padding:0}nav{position:static;break-after:page}nav li{margin:4px 0}section{border:0;padding:0;margin:0;break-before:page}h2{font-size:18pt}h3{font-size:12pt;break-after:avoid}tr,figure{break-inside:avoid}table{font-size:9pt}td,th{padding:6px}pre{font-size:8pt}a{color:inherit;text-decoration:none}footer{display:none}}
    '''
    parts=['<!DOCTYPE html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">',f'<title>{esc(d["title"])}</title><style>{style}</style></head><body>',f'<header><h1>{esc(d["title"])}</h1><p>{esc(d["subtitle"])}</p><p class="meta">Version {d["version"]} · {d["date"]} · {d["owner"]}</p><p>A shared design for framework engineers, pillar teams, implementation partners and project owners.</p></header><div class="layout"><nav aria-label="Contents"><strong>Contents</strong><ol>']
    for i,s in enumerate(d['sections'],1): parts.append(f'<li><a href="#section-{i}">{esc(s["title"])}</a></li>')
    parts.append('</ol></nav><main>')
    for i,s in enumerate(d['sections'],1):
        parts.append(f'<section id="section-{i}"><h2>{i} {esc(s["title"])}</h2>')
        for b in s['blocks']:
            t=b['type']
            if t in ['p','h']: parts.append(f'<{"p" if t=="p" else "h3"}>{esc(b["text"])}</{"p" if t=="p" else "h3"}>')
            elif t=='bullets': parts.append('<ul>'+''.join(f'<li>{esc(v)}</li>' for v in b['items'])+'</ul>')
            elif t=='code': parts.append('<pre><code>'+esc(b['text'])+'</code></pre>')
            elif t=='links': parts.append('<ul class="sources">'+''.join(f'<li><a href="{esc(url,quote=True)}">{esc(label)}</a></li>' for label,url in b['items'])+'</ul>')
            elif t=='figure':
                raw=(ROOT/'assets'/f'{b["id"]}.svg').read_bytes(); encoded=base64.b64encode(raw).decode()
                parts.append(f'<figure><img src="data:image/svg+xml;base64,{encoded}" alt="{esc(b["caption"])}"><figcaption>{esc(b["caption"])}</figcaption></figure>')
            elif t=='table':
                widths=b.get('widths',[1]*len(b['headers'])); total=sum(widths)
                parts.append('<table><colgroup>'+''.join(f'<col style="width:{w/total*100:.2f}%">' for w in widths)+'</colgroup><thead><tr>'+''.join(f'<th scope="col">{esc(h)}</th>' for h in b['headers'])+'</tr></thead><tbody>')
                parts.extend('<tr>'+''.join(f'<td>{esc(c)}</td>' for c in row)+'</tr>' for row in b['rows']); parts.append('</tbody></table>')
        parts.append('</section>')
    parts.append('<footer>FSCR Framework Team · Design version 1.0 · Diagrams have editable draw.io sources.</footer></main></div></body></html>')
    (ROOT/f'{STEM}.html').write_text('\n'.join(parts))


def cell_shading(cell,fill):
    el=OxmlElement('w:shd'); el.set(qn('w:fill'),fill); cell._tc.get_or_add_tcPr().append(el)


def add_link(p,label,target,internal=False):
    link=OxmlElement('w:hyperlink')
    if internal: link.set(qn('w:anchor'),target)
    else:
        rid=p.part.relate_to(target,'http://schemas.openxmlformats.org/officeDocument/2006/relationships/hyperlink',is_external=True)
        link.set(qn('r:id'),rid)
    r=OxmlElement('w:r'); props=OxmlElement('w:rPr'); col=OxmlElement('w:color'); col.set(qn('w:val'),'245986'); props.append(col); r.append(props)
    t=OxmlElement('w:t');t.text=label;r.append(t);link.append(r);p._p.append(link)


def add_table(doc,b):
    table=doc.add_table(rows=1, cols=len(b['headers']));table.alignment=WD_TABLE_ALIGNMENT.CENTER;table.autofit=False
    widths=b.get('widths',[6.15/len(b['headers'])]*len(b['headers']))
    for col,w in zip(table.columns,widths): col.width=Inches(w)
    pr=table._tbl.tblPr; borders=OxmlElement('w:tblBorders')
    for side in ['top','left','bottom','right','insideH','insideV']:
        e=OxmlElement('w:'+side);e.set(qn('w:val'),'single');e.set(qn('w:sz'),'4');e.set(qn('w:color'),'D9D9D9');borders.append(e)
    pr.append(borders)
    margins=OxmlElement('w:tblCellMar')
    for side,sz in [('top',85),('bottom',85),('left',95),('right',95)]:
        e=OxmlElement('w:'+side);e.set(qn('w:w'),str(sz));e.set(qn('w:type'),'dxa');margins.append(e)
    pr.append(margins)
    for idx,rowvalues in enumerate([b['headers']]+b['rows']):
        row=table.rows[0] if idx==0 else table.add_row()
        rpr=row._tr.get_or_add_trPr();rpr.append(OxmlElement('w:cantSplit'))
        if idx==0:rpr.append(OxmlElement('w:tblHeader'))
        for c,val,w in zip(row.cells,rowvalues,widths):
            c.width=Inches(w);c.vertical_alignment=WD_CELL_VERTICAL_ALIGNMENT.CENTER
            p=c.paragraphs[0];p.paragraph_format.space_after=Pt(0);p.paragraph_format.line_spacing=1.05
            r=p.add_run(val);r.font.name='Calibri';r.font.size=Pt(9.5)
            if idx==0:r.bold=True;r.font.color.rgb=RGBColor.from_string('FFFFFF');cell_shading(c,'34495E')
            elif idx%2==0:cell_shading(c,'F6F8FA')
    p=doc.add_paragraph();p.paragraph_format.space_after=Pt(0);p.paragraph_format.space_before=Pt(0);p.paragraph_format.line_spacing=1;p.add_run().font.size=Pt(3)


def create_word(d):
    doc=Document();sec=doc.sections[0]
    sec.page_width=Inches(8.27);sec.page_height=Inches(11.69)
    sec.left_margin=sec.right_margin=Inches(1.06);sec.top_margin=Inches(.72);sec.bottom_margin=Inches(.7)
    sec.header_distance=Inches(.3);sec.footer_distance=Inches(.3)
    styles=doc.styles
    for name in ['Normal','Title','Subtitle','Heading 1','Heading 2','Heading 3','Caption','List Bullet']:
        st=styles[name];st.font.name='Calibri';st.font.color.rgb=RGBColor(0,0,0)
    styles['Normal'].font.size=Pt(10.5); styles['Normal'].paragraph_format.space_after=Pt(8);styles['Normal'].paragraph_format.line_spacing=1.08
    styles['Title'].font.size=Pt(29);styles['Title'].font.bold=True;styles['Title'].paragraph_format.space_after=Pt(16)
    styles['Subtitle'].font.size=Pt(13);styles['Subtitle'].font.italic=False;styles['Subtitle'].paragraph_format.space_after=Pt(13)
    for name,size in [('Heading 1',18),('Heading 2',12),('Heading 3',11)]:
        st=styles[name];st.font.size=Pt(size);st.font.bold=True;st.paragraph_format.space_before=Pt(13);st.paragraph_format.space_after=Pt(8)
    styles['Heading 1'].paragraph_format.space_before=Pt(0)
    styles['Caption'].font.size=Pt(9);styles['Caption'].font.italic=False;styles['Caption'].paragraph_format.space_after=Pt(10)
    styles['List Bullet'].paragraph_format.space_after=Pt(5);styles['List Bullet'].paragraph_format.line_spacing=1.05
    bullet=styles.add_style('Design Bullet',WD_STYLE_TYPE.PARAGRAPH)
    bullet.base_style=styles['Normal']
    bullet.paragraph_format.left_indent=Inches(.20)
    bullet.paragraph_format.first_line_indent=Inches(-.20)
    bullet.paragraph_format.tab_stops.add_tab_stop(Inches(.20))
    bullet.paragraph_format.space_before=Pt(0)
    bullet.paragraph_format.space_after=Pt(0)
    bullet.paragraph_format.line_spacing=1.05
    # A restrained footer makes the longer design easy to navigate.
    p=sec.footer.paragraphs[0];p.alignment=WD_ALIGN_PARAGRAPH.RIGHT
    r=p.add_run('FSCR Validation Design   |   ');r.font.size=Pt(8);r.font.color.rgb=RGBColor(0,0,0)
    field=OxmlElement('w:fldSimple');field.set(qn('w:instr'),'PAGE');p._p.append(field)
    doc.add_paragraph(d['title'],'Title');doc.add_paragraph(d['subtitle'],'Subtitle')
    p=doc.add_paragraph(f'Version {d["version"]}  |  {d["date"]}\n{d["owner"]}');p.paragraph_format.space_after=Pt(16)
    doc.add_paragraph('A common design for framework engineers, pillar teams, implementation partners and project owners. Use it to assign ownership, author bounded checks, integrate supported execution routes and assess evidence consistently.')
    doc.add_paragraph('Guide contents','Heading 2')
    for i,s in enumerate(d['sections'],1):
        p=doc.add_paragraph();p.paragraph_format.space_after=Pt(4);p.paragraph_format.line_spacing=1
        add_link(p,f'{i}  {s["title"]}',f'section_{i}',True)
    for i,s in enumerate(d['sections'],1):
        p=doc.add_paragraph(f'{i}  {s["title"]}','Heading 1')
        p.paragraph_format.page_break_before=True
        bm=OxmlElement('w:bookmarkStart');bm.set(qn('w:id'),str(i));bm.set(qn('w:name'),f'section_{i}');p._p.insert(0,bm)
        end=OxmlElement('w:bookmarkEnd');end.set(qn('w:id'),str(i));p._p.append(end)
        for b in s['blocks']:
            t=b['type']
            if t=='p':doc.add_paragraph(b['text'])
            elif t=='h':doc.add_paragraph(b['text'],'Heading 2')
            elif t=='bullets':
                for item in b['items']:doc.add_paragraph('\u2022\t'+item,'Design Bullet')
            elif t=='table':add_table(doc,b)
            elif t=='code':
                p=doc.add_paragraph();p.paragraph_format.space_before=Pt(5);p.paragraph_format.space_after=Pt(9);p.paragraph_format.line_spacing=1.08
                r=p.add_run(b['text']);r.font.name='Liberation Mono';r.font.size=Pt(8)
            elif t=='links':
                for label,url in b['items']:
                    p=doc.add_paragraph();p.paragraph_format.space_after=Pt(4);add_link(p,label,url)
            elif t=='figure':
                p=doc.add_paragraph();p.paragraph_format.keep_with_next=True;p.paragraph_format.space_after=Pt(4)
                shape=p.add_run().add_picture(str(ROOT/'assets'/f'{b["id"]}.png'),width=Inches(6.15))
                shape._inline.docPr.set('descr',b['caption'])
                doc.add_paragraph(b['caption'],'Caption')
    # Remove inherited template decoration as well as direct paragraph borders.
    for tree in [doc.styles.element, doc.element]:
        for el in list(tree.iter(qn('w:pBdr'))): el.getparent().remove(el)
    doc.core_properties.title=d['title'];doc.core_properties.subject=d['subtitle'];doc.core_properties.author=d['owner'];doc.core_properties.keywords='FSCR validation prevalidation implementation design';doc.core_properties.comments=''
    doc.save(ROOT/f'{STEM}.docx')


def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--node',required=True);ap.add_argument('--node-modules',required=True);args=ap.parse_args()
    data=json.loads((ROOT/'design-content.json').read_text())
    create_diagrams(args.node,args.node_modules);create_html(data);create_word(data)
    print('Built HTML, DOCX and three editable draw.io diagrams.')


if __name__=='__main__':main()
