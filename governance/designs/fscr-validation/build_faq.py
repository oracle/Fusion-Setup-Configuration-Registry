#!/usr/bin/env python3
"""Publish FAQ Markdown to design and knowledge folders, plus HTML and Word.

Use --markdown-only for standard-library-only Markdown publication.
The full document build uses the bundled document dependencies.
"""
import argparse
import importlib.util
import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parent
STEM = 'fscr-validation-faq'
KNOWLEDGE = ROOT.parents[2] / 'knowledge/validation-rules'


def markdown_text(value):
    """Keep authored text literal, including placeholders and table cells."""
    return re.sub(r'([\\`*_\[\]<>|])', r'\\\1', str(value)).replace('\n', '<br>')


def markdown_anchor(heading):
    return re.sub(r'[^\w\- ]', '', heading.lower()).replace(' ', '-')


def render_markdown(data):
    lines = [f"# {markdown_text(data['title'])}", '',
             f"*{markdown_text(data['subtitle'])}*", '',
             f"**Version:** {markdown_text(data['version'])}", '',
             f"**Date:** {markdown_text(data['date'])}", '',
             f"**Owner:** {markdown_text(data['owner'])}", '', '## Contents', '']
    headings = [f"{index}. {section['title']}"
                for index, section in enumerate(data['sections'], 1)]
    for heading in headings:
        lines.append(f'- [{markdown_text(heading)}](#{markdown_anchor(heading)})')
    lines.append('')
    for heading, section in zip(headings, data['sections']):
        lines.extend([f'## {markdown_text(heading)}', ''])
        for block in section['blocks']:
            kind = block['type']
            if kind == 'h':
                lines.append(f"### {markdown_text(block['text'])}")
            elif kind == 'p':
                lines.append(markdown_text(block['text']))
            elif kind == 'bullets':
                lines.extend(f'- {markdown_text(item)}' for item in block['items'])
            elif kind == 'table':
                headers = block['headers']
                lines.append('| ' + ' | '.join(map(markdown_text, headers)) + ' |')
                lines.append('| ' + ' | '.join('---' for _ in headers) + ' |')
                for row in block['rows']:
                    if len(row) != len(headers):
                        raise ValueError('FAQ table row does not match its headers')
                    lines.append('| ' + ' | '.join(map(markdown_text, row)) + ' |')
            else:
                raise ValueError(f'Unsupported FAQ Markdown block: {kind}')
            lines.append('')
    return '\n'.join(lines).rstrip() + '\n'


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--dry-run', action='store_true', help='Validate source and render Markdown in memory; write nothing')
    parser.add_argument('--markdown-only', action='store_true', help='Publish both Markdown copies without rebuilding HTML or Word')
    args = parser.parse_args()
    data = json.loads((ROOT / 'faq-content.json').read_text())
    assert data['title'] and data['sections']
    markdown = render_markdown(data)
    if args.dry_run:
        print(f"FAQ source valid: {len(data['sections'])} sections; no outputs written.")
        return
    for folder in (ROOT, KNOWLEDGE):
        folder.mkdir(parents=True, exist_ok=True)
        (folder / f'{STEM}.md').write_text(markdown, encoding='utf-8')
    if args.markdown_only:
        print('Published FAQ Markdown to the design and knowledge folders.')
        return
    from docx import Document
    spec = importlib.util.spec_from_file_location('design_layout', ROOT / 'build_design.py')
    layout = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(layout)
    layout.STEM = STEM
    layout.create_html(data)
    layout.create_word(data)
    html_path = ROOT / f'{STEM}.html'
    html_text = html_path.read_text().replace(
        'A shared design for framework engineers, pillar teams, implementation partners and project owners.',
        'Practical answers and illustrative conversations for pillar teams, framework engineers and implementers.'
    ).replace(
        'FSCR Framework Team · Design version 1.0 · Diagrams have editable draw.io sources.',
        f'FSCR Framework Team · FAQ version {data["version"]} · Companion to the functional and technical design.'
    )
    html_path.write_text(html_text)
    word_path = ROOT / f'{STEM}.docx'
    doc = Document(word_path)
    for p in doc.paragraphs:
        if p.text.startswith('A common design for framework engineers'):
            p.text = 'Answers to the practical questions teams ask before adopting FSCR validation. This FAQ explains triggers, evidence sources, current limits, ownership and the human decisions required during a validation run.'
    for section in doc.sections:
        for p in section.footer.paragraphs:
            for run in p.runs:
                run.text = run.text.replace('FSCR Validation Design', 'FSCR Validation FAQ')
    doc.save(word_path)
    print('Built companion FAQ in Markdown, HTML and Word; knowledge Markdown synchronized.')


if __name__ == '__main__':
    main()
