#!/usr/bin/env python3
"""
Discovery Report Generator
Generates a beautiful, typography-focused HTML report from discovery markdown files.
Design inspired by Medium.com and mellow.dev — minimal, readable, captivating.
All fonts are free/open-source (Google Fonts: Playfair Display, Inter, Merriweather).
"""

import os
import re
import glob
from datetime import datetime


# ── Configuration ──────────────────────────────────────────────────────────

WORDS_PER_MINUTE = 200
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DISCOVERIES_DIR = os.path.join(PROJECT_ROOT, "discoveries")

# ── Markdown to HTML Converter ─────────────────────────────────────────────

class MarkdownConverter:
    """Convert markdown to HTML with discovery-specific styling hooks."""

    def __init__(self):
        self.in_code_block = False
        self.code_buffer = []
        self.code_lang = ""
        self.in_table = False
        self.table_buffer = []
        self.in_list = False
        self.list_buffer = []
        self.list_type = "ul"

    def convert(self, text: str) -> str:
        lines = text.split('\n')
        html_blocks = []
        i = 0

        while i < len(lines):
            line = lines[i]
            stripped = line.strip()

            # Code blocks
            if stripped.startswith('```'):
                if not self.in_code_block:
                    self._flush_lists(html_blocks)
                    self.in_code_block = True
                    self.code_buffer = []
                    self.code_lang = stripped[3:].strip()
                else:
                    self.in_code_block = False
                    code = '\n'.join(self.code_buffer)
                    html_blocks.append(
                        f'<pre><code class="language-{self.code_lang}">{self._escape_html(code)}</code></pre>'
                    )
                    self.code_buffer = []
                i += 1
                continue

            if self.in_code_block:
                self.code_buffer.append(line)
                i += 1
                continue

            # Tables
            if '|' in stripped and not stripped.startswith('#') and not stripped.startswith('>'):
                self._flush_lists(html_blocks)
                if not self.in_table:
                    self.in_table = True
                    self.table_buffer = []
                self.table_buffer.append(stripped)
                i += 1
                continue
            elif self.in_table:
                self.in_table = False
                html_blocks.append(self._render_table(self.table_buffer))
                self.table_buffer = []
                continue

            # Empty line
            if stripped == '':
                self._flush_lists(html_blocks)
                i += 1
                continue

            # Headers
            if stripped.startswith('# '):
                self._flush_lists(html_blocks)
                html_blocks.append(f'<h1>{self._inline_format(stripped[2:])}</h1>')
            elif stripped.startswith('## '):
                self._flush_lists(html_blocks)
                html_blocks.append(f'<h2>{self._inline_format(stripped[3:])}</h2>')
            elif stripped.startswith('### '):
                self._flush_lists(html_blocks)
                html_blocks.append(f'<h3>{self._inline_format(stripped[4:])}</h3>')
            elif stripped.startswith('#### '):
                self._flush_lists(html_blocks)
                html_blocks.append(f'<h4>{self._inline_format(stripped[5:])}</h4>')
            # Horizontal rule
            elif stripped == '---' or stripped == '***':
                self._flush_lists(html_blocks)
                html_blocks.append('<hr>')
            # Blockquote
            elif stripped.startswith('> '):
                self._flush_lists(html_blocks)
                html_blocks.append(f'<blockquote><p>{self._inline_format(stripped[2:])}</p></blockquote>')
            # Unordered list
            elif stripped.startswith('- ') or stripped.startswith('* '):
                if not self.in_list or self.list_type != "ul":
                    self._flush_lists(html_blocks)
                    self.in_list = True
                    self.list_type = "ul"
                    self.list_buffer = []
                self.list_buffer.append(stripped[2:])
            # Ordered list
            elif re.match(r'^\d+\.\s', stripped):
                if not self.in_list or self.list_type != "ol":
                    self._flush_lists(html_blocks)
                    self.in_list = True
                    self.list_type = "ol"
                    self.list_buffer = []
                content = re.sub(r'^\d+\.\s', '', stripped)
                self.list_buffer.append(content)
            # Paragraph
            else:
                self._flush_lists(html_blocks)
                html_blocks.append(f'<p>{self._inline_format(stripped)}</p>')

            i += 1

        # Flush any remaining lists
        self._flush_lists(html_blocks)

        # Flush any open table
        if self.in_table and self.table_buffer:
            html_blocks.append(self._render_table(self.table_buffer))

        return '\n'.join(html_blocks)

    def _flush_lists(self, html_blocks):
        if self.in_list and self.list_buffer:
            tag = self.list_type
            items = '\n'.join(f'<li>{self._inline_format(item)}</li>' for item in self.list_buffer)
            html_blocks.append(f'<{tag}>\n{items}\n</{tag}>')
            self.in_list = False
            self.list_buffer = []

    def _render_table(self, rows: list) -> str:
        if len(rows) < 2:
            return ''

        html = ['<div class="table-wrapper"><table>']

        for i, row in enumerate(rows):
            # Skip separator rows
            if re.match(r'^[\s\-|:]+$', row.replace('|', '').strip()):
                continue

            cells = [c.strip() for c in row.split('|')]
            cells = [c for c in cells if c]

            if not cells:
                continue

            tag = 'th' if i == 0 else 'td'
            html.append('<tr>' + ''.join(f'<{tag}>{self._inline_format(c)}</{tag}>' for c in cells) + '</tr>')

        html.append('</table></div>')
        return '\n'.join(html)

    def _inline_format(self, text: str) -> str:
        text = self._escape_html(text)
        # Bold
        text = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', text)
        text = re.sub(r'__(.*?)__', r'<strong>\1</strong>', text)
        # Italic
        text = re.sub(r'\*(.*?)\*', r'<em>\1</em>', text)
        text = re.sub(r'_(.*?)_', r'<em>\1</em>', text)
        # Inline code
        text = re.sub(r'`([^`]+)`', r'<code>\1</code>', text)
        # Links
        text = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', r'<a href="\2" target="_blank">\1</a>', text)
        return text

    def _escape_html(self, text: str) -> str:
        return text.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')


# ── Reading Time ───────────────────────────────────────────────────────────

def calculate_reading_time(text: str) -> dict:
    words = len(text.split())
    minutes = max(1, round(words / WORDS_PER_MINUTE))
    return {
        'words': words,
        'minutes': minutes,
        'label': f'{minutes} min read' if minutes > 1 else '1 min read'
    }


# ── Folder Utilities ───────────────────────────────────────────────────────

def sanitize_name(name: str) -> str:
    name = re.sub(r'[^\w\s-]', '', name.lower())
    name = re.sub(r'[-\s]+', '-', name).strip('-')
    return name[:50]


def create_discovery_folder(problem_name: str) -> str:
    date_prefix = datetime.now().strftime('%Y%m%d')
    sanitized = sanitize_name(problem_name)
    folder_name = f"{date_prefix}-{sanitized}"
    folder_path = os.path.join(DISCOVERIES_DIR, folder_name)
    os.makedirs(folder_path, exist_ok=True)
    return folder_path


def list_discovery_folders() -> list:
    if not os.path.exists(DISCOVERIES_DIR):
        return []

    folders = []
    for name in sorted(os.listdir(DISCOVERIES_DIR), reverse=True):
        path = os.path.join(DISCOVERIES_DIR, name)
        if os.path.isdir(path):
            md_files = glob.glob(os.path.join(path, '*.md'))
            has_report = os.path.exists(os.path.join(path, 'index.html'))
            match = re.match(r'^(\d{8})-(.+)$', name)
            date_str = match.group(1) if match else ''
            problem_name = match.group(2).replace('-', ' ').title() if match else name

            folders.append({
                'name': name,
                'path': path,
                'problem_name': problem_name,
                'date': date_str,
                'formatted_date': datetime.strptime(date_str, '%Y%m%d').strftime('%b %d, %Y') if date_str else '',
                'md_files': len(md_files),
                'has_report': has_report
            })

    return folders


# ── Discovery Saver ────────────────────────────────────────────────────────

def save_discovery_phase(folder_path: str, phase_number: int, phase_name: str, content: str) -> str:
    filename = f"{phase_number:02d}-{phase_name.lower().replace(' ', '-').replace('/', '-')}.md"
    filepath = os.path.join(folder_path, filename)
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    return filepath


def save_discovery_summary(folder_path: str, content: str) -> str:
    filepath = os.path.join(folder_path, 'summary.md')
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    return filepath


# ── HTML Report Generator ──────────────────────────────────────────────────

def generate_report(folder_path: str) -> str:
    md_files = sorted(glob.glob(os.path.join(folder_path, '*.md')))
    if not md_files:
        raise ValueError(f"No markdown files found in {folder_path}")

    sections = []
    total_words = 0
    converter = MarkdownConverter()

    for md_file in md_files:
        basename = os.path.basename(md_file)
        match = re.match(r'^\d{2}-(.+)\.md$', basename)
        if match:
            section_id = match.group(1)
            section_title = section_id.replace('-', ' ').title()
        else:
            section_id = basename.replace('.md', '')
            section_title = section_id.replace('-', ' ').title()

        with open(md_file, 'r', encoding='utf-8') as f:
            content = f.read()

        total_words += len(content.split())
        html_content = converter.convert(content)

        sections.append({
            'id': section_id,
            'title': section_title,
            'html': html_content,
            'filename': basename
        })

    minutes = max(1, round(total_words / WORDS_PER_MINUTE))
    reading_label = f'{minutes} min read' if minutes > 1 else '1 min read'

    folder_name = os.path.basename(folder_path)
    match = re.match(r'^\d{8}-(.+)$', folder_name)
    problem_name = match.group(1).replace('-', ' ').title() if match else folder_name
    date_str = match.group(0)[:8] if match else datetime.now().strftime('%Y%m%d')
    formatted_date = datetime.strptime(date_str, '%Y%m%d').strftime('%B %d, %Y')

    html = _build_html(problem_name, formatted_date, reading_label, total_words, sections)

    output_path = os.path.join(folder_path, 'index.html')
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html)

    return output_path


def _build_html(title: str, date: str, reading_time: str, word_count: int, sections: list) -> str:
    nav_items = '\n'.join(
        f'<li><a href="#{s["id"]}" class="nav-link">{s["title"]}</a></li>'
        for s in sections
    )

    sections_html = '\n'.join(
        f'''<section id="{s["id"]}" class="discovery-section">
            <h2 class="section-title">{s["title"]}</h2>
            <div class="section-content">
                {s["html"]}
            </div>
        </section>'''
        for s in sections
    )

    return f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title} — Product Discovery Report</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,400;0,600;0,700;1,400&family=Inter:wght@300;400;500;600&family=Merriweather:ital,wght@0,300;0,400;0,700;1,300;1,400&display=swap" rel="stylesheet">
    <style>
        *, *::before, *::after {{ box-sizing: border-box; margin: 0; padding: 0; }}
        :root {{
            --bg-warm: #faf9f7; --bg-white: #ffffff; --bg-accent: #f5f3ef;
            --text-primary: #1a1a1a; --text-secondary: #4a4a4a; --text-muted: #737373; --text-light: #999999;
            --accent-orange: #e65100; --accent-blue: #2563eb; --accent-soft: #fef3e2;
            --border-light: #e8e6e1; --border-medium: #d4d0c8;
            --shadow-soft: 0 1px 3px rgba(0,0,0,0.04); --shadow-medium: 0 4px 20px rgba(0,0,0,0.06);
            --radius-sm: 6px; --radius-md: 12px;
        }}
        html {{ scroll-behavior: smooth; scroll-padding-top: 80px; }}
        body {{
            font-family: 'Merriweather', Georgia, serif;
            font-size: 18px;
            line-height: 1.8;
            color: var(--text-primary);
            background: var(--bg-warm);
            -webkit-font-smoothing: antialiased;
            -moz-osx-font-smoothing: grayscale;
        }}
        .page-wrapper {{
            max-width: 1200px;
            margin: 0 auto;
            display: grid;
            grid-template-columns: 260px 1fr;
            gap: 60px;
            padding: 0 40px;
        }}
        @media (max-width: 900px) {{
            .page-wrapper {{ grid-template-columns: 1fr; padding: 0 24px; }}
        }}
        .sidebar {{
            position: sticky;
            top: 40px;
            height: fit-content;
            padding: 32px 0;
        }}
        @media (max-width: 900px) {{ .sidebar {{ display: none; }} }}
        .sidebar-title {{
            font-family: 'Inter', sans-serif;
            font-size: 11px;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 1.5px;
            color: var(--text-light);
            margin-bottom: 20px;
            padding-bottom: 12px;
            border-bottom: 1px solid var(--border-light);
        }}
        .nav-list {{ list-style: none; }}
        .nav-list li {{ margin-bottom: 4px; }}
        .nav-link {{
            display: block;
            font-family: 'Inter', sans-serif;
            font-size: 13px;
            font-weight: 400;
            color: var(--text-muted);
            text-decoration: none;
            padding: 8px 12px;
            border-radius: var(--radius-sm);
            transition: all 0.2s ease;
            line-height: 1.4;
        }}
        .nav-link:hover {{ color: var(--text-primary); background: var(--bg-accent); }}
        .nav-link.active {{ color: var(--accent-orange); background: var(--accent-soft); font-weight: 500; }}
        .main-content {{ max-width: 700px; padding: 60px 0 100px; }}
        .hero {{
            margin-bottom: 60px;
            padding-bottom: 40px;
            border-bottom: 1px solid var(--border-light);
        }}
        .hero-label {{
            font-family: 'Inter', sans-serif;
            font-size: 11px;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 2px;
            color: var(--accent-orange);
            margin-bottom: 20px;
        }}
        .hero-title {{
            font-family: 'Playfair Display', Georgia, serif;
            font-size: 42px;
            font-weight: 700;
            line-height: 1.2;
            color: var(--text-primary);
            margin-bottom: 24px;
            letter-spacing: -0.5px;
        }}
        @media (max-width: 600px) {{ .hero-title {{ font-size: 32px; }} }}
        .hero-meta {{
            display: flex;
            align-items: center;
            gap: 20px;
            flex-wrap: wrap;
        }}
        .meta-item {{
            display: flex;
            align-items: center;
            gap: 8px;
            font-family: 'Inter', sans-serif;
            font-size: 14px;
            color: var(--text-muted);
        }}
        .meta-icon {{ font-size: 16px; }}
        .reading-time {{
            display: inline-flex;
            align-items: center;
            gap: 6px;
            font-family: 'Inter', sans-serif;
            font-size: 13px;
            font-weight: 500;
            color: var(--accent-orange);
            background: var(--accent-soft);
            padding: 6px 14px;
            border-radius: 20px;
        }}
        .progress-bar {{
            width: 100%;
            height: 3px;
            background: var(--border-light);
            border-radius: 2px;
            margin: 30px 0;
            overflow: hidden;
        }}
        .progress-fill {{
            height: 100%;
            width: 100%;
            background: linear-gradient(90deg, var(--accent-orange), #f57c00);
            border-radius: 2px;
        }}
        .discovery-section {{ margin-bottom: 80px; }}
        .section-title {{
            font-family: 'Playfair Display', Georgia, serif;
            font-size: 28px;
            font-weight: 600;
            color: var(--text-primary);
            margin-bottom: 32px;
            padding-bottom: 16px;
            border-bottom: 2px solid var(--border-light);
        }}
        h1 {{
            font-family: 'Playfair Display', Georgia, serif;
            font-size: 36px;
            font-weight: 700;
            line-height: 1.3;
            margin: 48px 0 24px;
            color: var(--text-primary);
        }}
        h2 {{
            font-family: 'Playfair Display', Georgia, serif;
            font-size: 28px;
            font-weight: 600;
            line-height: 1.3;
            margin: 40px 0 20px;
            color: var(--text-primary);
        }}
        h3 {{
            font-family: 'Inter', sans-serif;
            font-size: 20px;
            font-weight: 600;
            line-height: 1.4;
            margin: 32px 0 16px;
            color: var(--text-primary);
        }}
        h4 {{
            font-family: 'Inter', sans-serif;
            font-size: 16px;
            font-weight: 600;
            line-height: 1.4;
            margin: 24px 0 12px;
            color: var(--text-secondary);
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }}
        p {{
            margin-bottom: 1.5em;
            color: var(--text-secondary);
        }}
        p strong {{ color: var(--text-primary); font-weight: 700; }}
        ul, ol {{
            margin: 0 0 1.5em 1.5em;
            color: var(--text-secondary);
        }}
        li {{ margin-bottom: 0.6em; line-height: 1.7; }}
        li::marker {{ color: var(--accent-orange); }}
        blockquote {{
            margin: 32px 0;
            padding: 24px 32px;
            background: var(--bg-accent);
            border-left: 4px solid var(--accent-orange);
            border-radius: 0 var(--radius-md) var(--radius-md) 0;
            font-style: italic;
        }}
        blockquote p {{
            margin-bottom: 0;
            color: var(--text-secondary);
            font-size: 17px;
            line-height: 1.7;
        }}
        blockquote p:last-child {{ margin-bottom: 0; }}
        .table-wrapper {{
            overflow-x: auto;
            margin: 32px 0;
            border-radius: var(--radius-md);
            box-shadow: var(--shadow-soft);
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            font-family: 'Inter', sans-serif;
            font-size: 14px;
            background: var(--bg-white);
        }}
        th {{
            background: var(--bg-accent);
            color: var(--text-primary);
            font-weight: 600;
            text-align: left;
            padding: 14px 18px;
            border-bottom: 2px solid var(--border-medium);
            text-transform: uppercase;
            font-size: 11px;
            letter-spacing: 0.8px;
        }}
        td {{
            padding: 14px 18px;
            border-bottom: 1px solid var(--border-light);
            color: var(--text-secondary);
            line-height: 1.5;
        }}
        tr:hover td {{ background: var(--bg-warm); }}
        tr:last-child td {{ border-bottom: none; }}
        code {{
            font-family: 'SF Mono', Monaco, 'Cascadia Code', monospace;
            font-size: 0.85em;
            background: var(--bg-accent);
            padding: 2px 8px;
            border-radius: 4px;
            color: var(--accent-blue);
        }}
        pre {{
            background: var(--bg-white);
            border: 1px solid var(--border-light);
            border-radius: var(--radius-md);
            padding: 24px;
            overflow-x: auto;
            margin: 24px 0;
            box-shadow: var(--shadow-soft);
        }}
        pre code {{
            background: none;
            padding: 0;
            color: var(--text-primary);
            font-size: 14px;
            line-height: 1.6;
        }}
        hr {{
            border: none;
            height: 1px;
            background: var(--border-light);
            margin: 48px 0;
        }}
        a {{
            color: var(--accent-blue);
            text-decoration: none;
            border-bottom: 1px solid transparent;
            transition: border-color 0.2s ease;
        }}
        a:hover {{ border-bottom-color: var(--accent-blue); }}
        @media print {{
            .sidebar {{ display: none; }}
            .page-wrapper {{ grid-template-columns: 1fr; max-width: 100%; }}
            .main-content {{ max-width: 100%; padding: 0; }}
            body {{ font-size: 12pt; line-height: 1.5; background: white; }}
            .discovery-section {{ break-inside: avoid; margin-bottom: 40px; }}
        }}
        ::-webkit-scrollbar {{ width: 8px; }}
        ::-webkit-scrollbar-track {{ background: transparent; }}
        ::-webkit-scrollbar-thumb {{ background: var(--border-medium); border-radius: 4px; }}
        ::-webkit-scrollbar-thumb:hover {{ background: var(--text-light); }}
    </style>
</head>
<body>
    <div class="page-wrapper">
        <aside class="sidebar">
            <div class="sidebar-title">Discovery Phases</div>
            <ul class="nav-list">
                {nav_items}
            </ul>
        </aside>
        <main class="main-content">
            <header class="hero">
                <div class="hero-label">Product Discovery Report</div>
                <h1 class="hero-title">{title}</h1>
                <div class="hero-meta">
                    <span class="meta-item"><span class="meta-icon">📅</span>{date}</span>
                    <span class="meta-item"><span class="meta-icon">📝</span>{word_count:,} words</span>
                    <span class="reading-time"><span>⏱</span>{reading_time}</span>
                </div>
                <div class="progress-bar"><div class="progress-fill"></div></div>
            </header>
            {sections_html}
            <footer style="margin-top: 80px; padding-top: 40px; border-top: 1px solid var(--border-light); text-align: center; font-family: 'Inter', sans-serif; font-size: 13px; color: var(--text-light);">
                Generated by Product Discovery Manager
            </footer>
        </main>
    </div>
    <script>
        const sections = document.querySelectorAll('.discovery-section');
        const navLinks = document.querySelectorAll('.nav-link');
        function updateActiveLink() {{
            let current = '';
            sections.forEach(section => {{
                if (scrollY >= section.offsetTop - 100) {{
                    current = section.getAttribute('id');
                }}
            }});
            navLinks.forEach(link => {{
                link.classList.remove('active');
                if (link.getAttribute('href') === '#' + current) {{
                    link.classList.add('active');
                }}
            }});
        }}
        window.addEventListener('scroll', updateActiveLink);
        updateActiveLink();
    </script>
</body>
</html>'''


if __name__ == '__main__':
    import sys
    if len(sys.argv) > 1:
        folder = sys.argv[1]
    else:
        folders = list_discovery_folders()
        if not folders:
            print("No discovery folders found.")
            sys.exit(1)
        folder = folders[0]['path']

    output = generate_report(folder)
    print(f"Report generated: {output}")
