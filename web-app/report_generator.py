#!/usr/bin/env python3
"""
Discovery Report Generator
Generates a beautiful, typography-focused HTML report from discovery markdown files.
Design inspired by Medium.com and mellow.dev — minimal, readable, captivating.
Sans-serif font (Inter), gentle dark mode, related jobs table with importance badges.
"""

import os
import re
import glob
import getpass
from datetime import datetime


# ── Configuration ──────────────────────────────────────────────────────────

WORDS_PER_MINUTE = 200
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DISCOVERIES_DIR = os.path.join(PROJECT_ROOT, "Discovery", "discoveries")
SOLUTIONS_DIR = os.path.join(PROJECT_ROOT, "Solutions", "solutions")

GITHUB_LINK = "https://github.com/stnkcl/ai-pm-tools"  # Update to actual repo URL


# ── Importance / Satisfaction Badge Helpers ────────────────────────────────

def _importance_badge(value: str) -> str:
    """Wrap an importance value in a colored badge span."""
    val_lower = value.lower()
    if "critical" in val_lower:
        cls = "importance-critical"
    elif "important" in val_lower or "high" in val_lower:
        cls = "importance-important"
    elif "moderate" in val_lower or "medium" in val_lower:
        cls = "importance-moderate"
    elif "low" in val_lower or "nice" in val_lower or "optional" in val_lower:
        cls = "importance-low"
    else:
        cls = "importance-default"
    return f'<span class="importance-badge {cls}">{value}</span>'


def _satisfaction_badge(value: str) -> str:
    """Wrap a satisfaction value in a subtle badge span."""
    val_lower = value.lower()
    # Try to extract numeric rating
    match = re.search(r'(\d+(?:\.\d+)?)\s*/\s*\d+', value)
    if match:
        num = float(match.group(1))
        if num <= 2:
            cls = "sat-poor"
        elif num <= 3:
            cls = "sat-okay"
        elif num <= 4:
            cls = "sat-good"
        else:
            cls = "sat-excellent"
    elif any(w in val_lower for w in ["low", "poor", "bad", "terrible", "frustrated"]):
        cls = "sat-poor"
    elif any(w in val_lower for w in ["okay", "fine", "neutral", "mixed"]):
        cls = "sat-okay"
    elif any(w in val_lower for w in ["good", "happy", "satisfied", "great"]):
        cls = "sat-good"
    elif any(w in val_lower for w in ["excellent", "love", "amazing", "delighted"]):
        cls = "sat-excellent"
    else:
        cls = "sat-default"
    return f'<span class="satisfaction-badge {cls}">{value}</span>'


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

        result = '\n'.join(html_blocks)
        # Post-process: wrap importance and satisfaction values in badges
        result = self._post_process_badges(result)
        return result

    def _post_process_badges(self, html: str) -> str:
        """Wrap importance and satisfaction values in styled badges."""
        def replace_importance(match):
            prefix = match.group(1)
            value = match.group(2).strip()
            return f'{prefix}{_importance_badge(value)}'

        def replace_satisfaction(match):
            prefix = match.group(1)
            value = match.group(2).strip()
            return f'{prefix}{_satisfaction_badge(value)}'

        # Importance: various formats
        html = re.sub(
            r'(<strong>Importance\s*:?\s*</strong>\s*:?\s*)([^<\n]+)',
            replace_importance, html, flags=re.IGNORECASE
        )
        # Satisfaction: various formats
        html = re.sub(
            r'(<strong>Satisfaction\s*:?\s*</strong>\s*:?\s*)([^<\n]+)',
            replace_satisfaction, html, flags=re.IGNORECASE
        )
        return html

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


def create_solution_folder(problem_name: str) -> str:
    date_prefix = datetime.now().strftime('%Y%m%d')
    sanitized = sanitize_name(problem_name)
    folder_name = f"{date_prefix}-{sanitized}"
    folder_path = os.path.join(SOLUTIONS_DIR, folder_name)
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


def list_solution_folders() -> list:
    if not os.path.exists(SOLUTIONS_DIR):
        return []

    folders = []
    for name in sorted(os.listdir(SOLUTIONS_DIR), reverse=True):
        path = os.path.join(SOLUTIONS_DIR, name)
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


def save_solution_phase(folder_path: str, phase_number: int, phase_name: str, content: str) -> str:
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


def save_solution_summary(folder_path: str, content: str) -> str:
    filepath = os.path.join(folder_path, 'summary.md')
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    return filepath


# ── Duplicate Heading Detection ────────────────────────────────────────────

def _headings_match(section_title: str, html_content: str) -> bool:
    """Check if the first heading in html_content matches the section_title."""
    title_norm = re.sub(r'[^\w]', '', section_title.lower())

    # Find first h1 or h2
    match = re.search(r'<h[12][^>]*>(.*?)</h[12]>', html_content, re.IGNORECASE | re.DOTALL)
    if not match:
        return False

    heading_text = re.sub(r'<[^>]+>', '', match.group(1))
    heading_norm = re.sub(r'[^\w]', '', heading_text.lower())

    return title_norm == heading_norm or title_norm in heading_norm or heading_norm in title_norm


# ── Related Jobs Table Builder ─────────────────────────────────────────────

# Regex patterns for parsing related jobs markdown
_RE_JOB = re.compile(r'^-\s*\*\*Job\*\*\s*[:\-]?\s*(.+)$', re.IGNORECASE)
_RE_VALUE = re.compile(r'^-\s*\*\*Value\*\*\s*[:\-]?\s*(.+)$', re.IGNORECASE)
_RE_SATISFACTION = re.compile(r'^-\s*\*\*Satisfaction\*\*\s*[:\-]?\s*(.+)$', re.IGNORECASE)
_RE_IMPORTANCE = re.compile(r'^-\s*\*\*Importance\*\*\s*[:\-]?\s*(.+)$', re.IGNORECASE)
_RE_CATEGORY_HEADER = re.compile(r'^#{3,4}\s*(Functional|Emotional|Social)\s*$', re.IGNORECASE)
_RE_RELATED_JOBS_HEADER = re.compile(r'^#{2,3}\s*Related\s*Jobs\s*$', re.IGNORECASE)


def _extract_related_jobs(markdown: str) -> tuple:
    """
    Extract related jobs data from markdown.
    Returns (table_html_fragment, modified_markdown_without_related_jobs).
    If no related jobs found, returns (None, markdown).
    """
    lines = markdown.split('\n')
    in_related_section = False
    current_category = None
    current_entry = {}
    entries = []
    related_start = -1
    related_end = -1

    i = 0
    while i < len(lines):
        line = lines[i]
        stripped = line.strip()

        if not in_related_section:
            if _RE_RELATED_JOBS_HEADER.match(stripped):
                in_related_section = True
                related_start = i
                i += 1
                continue
            i += 1
            continue

        # We're inside the Related Jobs section
        if stripped.startswith('#') and not _RE_CATEGORY_HEADER.match(stripped):
            # Another heading ended the section
            related_end = i
            break

        cat_match = _RE_CATEGORY_HEADER.match(stripped)
        if cat_match:
            # Flush previous entry
            if current_entry:
                entries.append(current_entry)
                current_entry = {}
            current_category = cat_match.group(1).capitalize()
            i += 1
            continue

        job_match = _RE_JOB.match(stripped)
        if job_match:
            if current_entry:
                entries.append(current_entry)
            current_entry = {
                'category': current_category or 'Other',
                'job': job_match.group(1).strip(),
                'value': '-',
                'satisfaction': '-',
                'importance': '-'
            }
            i += 1
            continue

        value_match = _RE_VALUE.match(stripped)
        if value_match and current_entry:
            current_entry['value'] = value_match.group(1).strip()
            i += 1
            continue

        sat_match = _RE_SATISFACTION.match(stripped)
        if sat_match and current_entry:
            current_entry['satisfaction'] = sat_match.group(1).strip()
            i += 1
            continue

        imp_match = _RE_IMPORTANCE.match(stripped)
        if imp_match and current_entry:
            current_entry['importance'] = imp_match.group(1).strip()
            i += 1
            continue

        # Empty lines within related section are okay
        if stripped == '':
            i += 1
            continue

        i += 1

    if in_related_section:
        if related_end == -1:
            related_end = len(lines)
        if current_entry:
            entries.append(current_entry)

    if not entries:
        return None, markdown

    # Build table HTML
    table_html = '<div class="related-jobs-table-wrapper">\n'
    table_html += '<table class="related-jobs-table">\n'
    table_html += '<thead><tr>'
    table_html += '<th>Category</th><th>Job</th><th>Value</th><th>Satisfaction</th><th>Importance</th>'
    table_html += '</tr></thead>\n<tbody>\n'

    cat_colors = {
        'Functional': 'cat-functional',
        'Emotional': 'cat-emotional',
        'Social': 'cat-social'
    }

    for entry in entries:
        cat_cls = cat_colors.get(entry['category'], '')
        sat_badge = _satisfaction_badge(entry['satisfaction']) if entry['satisfaction'] != '-' else '<span class="satisfaction-badge sat-default">-</span>'
        imp_badge = _importance_badge(entry['importance']) if entry['importance'] != '-' else '<span class="importance-badge importance-default">-</span>'

        table_html += '<tr>\n'
        table_html += f'  <td><span class="category-pill {cat_cls}">{entry["category"]}</span></td>\n'
        table_html += f'  <td class="job-cell">{entry["job"]}</td>\n'
        table_html += f'  <td>{entry["value"]}</td>\n'
        table_html += f'  <td>{sat_badge}</td>\n'
        table_html += f'  <td>{imp_badge}</td>\n'
        table_html += '</tr>\n'

    table_html += '</tbody></table>\n</div>\n'

    # Reconstruct markdown without the related jobs section
    before = lines[:related_start]
    after = lines[related_end:]

    # Use a bracket placeholder that survives markdown conversion
    # (HTML comments get escaped; brackets pass through as plain text)
    placeholder = '\n[[RELATED_JOBS_TABLE]]\n'
    new_markdown = '\n'.join(before) + placeholder + '\n'.join(after)

    return table_html, new_markdown


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

        # Extract related jobs table from raw markdown
        related_table, modified_content = _extract_related_jobs(content)

        if related_table:
            # Split at placeholder and convert parts separately
            # (avoids placeholder being mangled by markdown formatting)
            parts = modified_content.split('[[RELATED_JOBS_TABLE]]')
            before_html = converter.convert(parts[0])
            after_html = converter.convert(parts[1]) if len(parts) > 1 else ''
            html_content = before_html + f'<h3>Related Jobs</h3>\n{related_table}' + after_html
        else:
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
    match = re.match(r'^(\d{8})-(.+)$', folder_name)
    problem_name = match.group(2).replace('-', ' ').title() if match else folder_name
    date_str = match.group(0)[:8] if match else datetime.now().strftime('%Y%m%d')
    formatted_date = datetime.strptime(date_str, '%Y%m%d').strftime('%B %d, %Y')

    html = _build_html(problem_name, formatted_date, reading_label, total_words, sections)

    output_path = os.path.join(folder_path, 'index.html')
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html)

    return output_path


def _build_html(title: str, date: str, reading_time: str, word_count: int, sections: list) -> str:
    username = getpass.getuser()

    nav_items = '\n'.join(
        f'<li><a href="#{s["id"]}" class="nav-link">{s["title"]}</a></li>'
        for s in sections
    )

    section_blocks = []
    for s in sections:
        # Skip section title if it duplicates the first heading in content
        skip_title = _headings_match(s['title'], s['html'])

        title_html = ''
        if not skip_title:
            title_html = f'<h2 class="section-title">{s["title"]}</h2>'

        section_blocks.append(
            f'''<section id="{s["id"]}" class="discovery-section">
                {title_html}
                <div class="section-content">
                    {s["html"]}
                </div>
            </section>'''
        )

    sections_html = '\n'.join(section_blocks)

    return f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title} — Product Discovery Report</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">
    <style>
        *, *::before, *::after {{ box-sizing: border-box; margin: 0; padding: 0; }}
        :root {{
            /* Gentle dark palette — soft grays, never pure black/white */
            --bg-primary: #141416;
            --bg-secondary: #1a1a1d;
            --bg-tertiary: #202023;
            --bg-elevated: #252529;
            --text-primary: #e2e2e6;
            --text-secondary: #a0a0a8;
            --text-muted: #6e6e78;
            --text-faint: #4a4a52;
            --accent-orange: #e88b4a;
            --accent-orange-soft: rgba(232, 139, 74, 0.12);
            --accent-blue: #6ba3e0;
            --accent-green: #7cc09a;
            --accent-yellow: #d4a954;
            --accent-red: #d97a7a;
            --border-light: #2a2a2e;
            --border-medium: #333338;
            --shadow-soft: 0 1px 3px rgba(0,0,0,0.2);
            --shadow-medium: 0 4px 20px rgba(0,0,0,0.3);
            --radius-sm: 6px;
            --radius-md: 10px;
            --radius-lg: 14px;
        }}
        html {{ scroll-behavior: smooth; scroll-padding-top: 80px; }}
        body {{
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            font-size: 16px;
            line-height: 1.7;
            color: var(--text-primary);
            background: var(--bg-primary);
            -webkit-font-smoothing: antialiased;
            -moz-osx-font-smoothing: grayscale;
        }}
        .page-wrapper {{
            max-width: 1200px;
            margin: 0 auto;
            display: grid;
            grid-template-columns: 240px 1fr;
            gap: 56px;
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
            font-size: 11px;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 1.5px;
            color: var(--text-faint);
            margin-bottom: 20px;
            padding-bottom: 12px;
            border-bottom: 1px solid var(--border-light);
        }}
        .nav-list {{ list-style: none; }}
        .nav-list li {{ margin-bottom: 4px; }}
        .nav-link {{
            display: block;
            font-size: 13px;
            font-weight: 400;
            color: var(--text-muted);
            text-decoration: none;
            padding: 8px 12px;
            border-radius: var(--radius-sm);
            transition: all 0.2s ease;
            line-height: 1.4;
        }}
        .nav-link:hover {{ color: var(--text-primary); background: var(--bg-tertiary); }}
        .nav-link.active {{ color: var(--accent-orange); background: var(--accent-orange-soft); font-weight: 500; }}
        .main-content {{ max-width: 720px; padding: 60px 0 100px; }}
        .hero {{
            margin-bottom: 56px;
            padding-bottom: 36px;
            border-bottom: 1px solid var(--border-light);
        }}
        .hero-label {{
            font-size: 11px;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 2px;
            color: var(--accent-orange);
            margin-bottom: 20px;
        }}
        .hero-title {{
            font-size: 40px;
            font-weight: 700;
            line-height: 1.2;
            color: var(--text-primary);
            margin-bottom: 24px;
            letter-spacing: -0.8px;
        }}
        @media (max-width: 600px) {{ .hero-title {{ font-size: 30px; }} }}
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
            font-size: 13px;
            color: var(--text-muted);
        }}
        .meta-icon {{ font-size: 15px; }}
        .reading-time {{
            display: inline-flex;
            align-items: center;
            gap: 6px;
            font-size: 12px;
            font-weight: 500;
            color: var(--accent-orange);
            background: var(--accent-orange-soft);
            padding: 5px 12px;
            border-radius: 20px;
        }}
        .progress-bar {{
            width: 100%;
            height: 3px;
            background: var(--border-light);
            border-radius: 2px;
            margin: 28px 0;
            overflow: hidden;
        }}
        .progress-fill {{
            height: 100%;
            width: 100%;
            background: linear-gradient(90deg, var(--accent-orange), #c77a3e);
            border-radius: 2px;
        }}
        .discovery-section {{ margin-bottom: 72px; }}
        .section-title {{
            font-size: 26px;
            font-weight: 600;
            color: var(--text-primary);
            margin-bottom: 28px;
            padding-bottom: 14px;
            border-bottom: 1px solid var(--border-medium);
        }}
        h1 {{
            font-size: 32px;
            font-weight: 700;
            line-height: 1.3;
            margin: 44px 0 22px;
            color: var(--text-primary);
            letter-spacing: -0.4px;
        }}
        h2 {{
            font-size: 26px;
            font-weight: 600;
            line-height: 1.3;
            margin: 36px 0 18px;
            color: var(--text-primary);
            letter-spacing: -0.3px;
        }}
        h3 {{
            font-size: 18px;
            font-weight: 600;
            line-height: 1.4;
            margin: 28px 0 14px;
            color: var(--text-primary);
        }}
        h4 {{
            font-size: 13px;
            font-weight: 600;
            line-height: 1.4;
            margin: 22px 0 10px;
            color: var(--text-secondary);
            text-transform: uppercase;
            letter-spacing: 0.6px;
        }}
        p {{
            margin-bottom: 1.4em;
            color: var(--text-secondary);
        }}
        p strong {{ color: var(--text-primary); font-weight: 600; }}
        ul, ol {{
            margin: 0 0 1.4em 1.3em;
            color: var(--text-secondary);
        }}
        li {{ margin-bottom: 0.5em; line-height: 1.65; }}
        li::marker {{ color: var(--accent-orange); }}
        blockquote {{
            margin: 28px 0;
            padding: 22px 28px;
            background: var(--bg-secondary);
            border-left: 3px solid var(--accent-orange);
            border-radius: 0 var(--radius-md) var(--radius-md) 0;
        }}
        blockquote p {{
            margin-bottom: 0;
            color: var(--text-secondary);
            font-size: 15px;
            line-height: 1.65;
            font-style: italic;
        }}
        blockquote p:last-child {{ margin-bottom: 0; }}
        .table-wrapper {{
            overflow-x: auto;
            margin: 28px 0;
            border-radius: var(--radius-md);
            border: 1px solid var(--border-light);
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            font-size: 13px;
            background: var(--bg-secondary);
        }}
        th {{
            background: var(--bg-tertiary);
            color: var(--text-primary);
            font-weight: 600;
            text-align: left;
            padding: 12px 16px;
            border-bottom: 1px solid var(--border-medium);
            text-transform: uppercase;
            font-size: 10px;
            letter-spacing: 0.7px;
        }}
        td {{
            padding: 12px 16px;
            border-bottom: 1px solid var(--border-light);
            color: var(--text-secondary);
            line-height: 1.5;
        }}
        tr:hover td {{ background: var(--bg-tertiary); }}
        tr:last-child td {{ border-bottom: none; }}

        /* ── Importance Badges ──────────────────────────────────────────────── */
        .importance-badge, .satisfaction-badge {{
            display: inline-flex;
            align-items: center;
            gap: 4px;
            font-size: 11px;
            font-weight: 600;
            padding: 3px 10px;
            border-radius: 20px;
            white-space: nowrap;
            letter-spacing: 0.2px;
        }}
        .importance-critical {{
            background: rgba(217, 122, 122, 0.15);
            color: #e09090;
        }}
        .importance-critical::before {{ content: "🔴"; font-size: 8px; }}
        .importance-important {{
            background: rgba(212, 169, 84, 0.15);
            color: #dfc07a;
        }}
        .importance-important::before {{ content: "🟠"; font-size: 8px; }}
        .importance-moderate {{
            background: rgba(107, 163, 224, 0.12);
            color: #8ab8e8;
        }}
        .importance-moderate::before {{ content: "🔵"; font-size: 8px; }}
        .importance-low {{
            background: rgba(124, 192, 154, 0.12);
            color: #9dd4b2;
        }}
        .importance-low::before {{ content: "🟢"; font-size: 8px; }}
        .importance-default {{
            background: var(--bg-elevated);
            color: var(--text-muted);
        }}

        .satisfaction-badge {{ padding: 2px 8px; font-size: 11px; font-weight: 500; }}
        .sat-poor {{ background: rgba(217, 122, 122, 0.12); color: #e09090; }}
        .sat-okay {{ background: rgba(212, 169, 84, 0.12); color: #dfc07a; }}
        .sat-good {{ background: rgba(124, 192, 154, 0.12); color: #9dd4b2; }}
        .sat-excellent {{ background: rgba(107, 163, 224, 0.12); color: #8ab8e8; }}
        .sat-default {{ background: var(--bg-elevated); color: var(--text-muted); }}

        /* ── Related Jobs Table ─────────────────────────────────────────────── */
        .related-jobs-table-wrapper {{
            overflow-x: auto;
            margin: 24px 0;
            border-radius: var(--radius-md);
            border: 1px solid var(--border-light);
        }}
        .related-jobs-table {{
            width: 100%;
            border-collapse: collapse;
            font-size: 13px;
            background: var(--bg-secondary);
        }}
        .related-jobs-table th {{
            background: var(--bg-tertiary);
            padding: 12px 14px;
            font-size: 10px;
            text-transform: uppercase;
            letter-spacing: 0.7px;
            font-weight: 600;
            color: var(--text-primary);
            border-bottom: 1px solid var(--border-medium);
            text-align: left;
        }}
        .related-jobs-table td {{
            padding: 12px 14px;
            border-bottom: 1px solid var(--border-light);
            color: var(--text-secondary);
            line-height: 1.5;
            vertical-align: top;
        }}
        .related-jobs-table tr:last-child td {{ border-bottom: none; }}
        .related-jobs-table tr:hover td {{ background: var(--bg-tertiary); }}
        .related-jobs-table .job-cell {{
            color: var(--text-primary);
            font-weight: 500;
            max-width: 320px;
        }}
        .category-pill {{
            display: inline-block;
            font-size: 10px;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            padding: 3px 10px;
            border-radius: 20px;
        }}
        .cat-functional {{ background: rgba(107, 163, 224, 0.15); color: #8ab8e8; }}
        .cat-emotional {{ background: rgba(217, 122, 122, 0.15); color: #e09090; }}
        .cat-social {{ background: rgba(124, 192, 154, 0.15); color: #9dd4b2; }}

        code {{
            font-family: 'SF Mono', Monaco, 'Cascadia Code', 'Fira Code', monospace;
            font-size: 0.82em;
            background: var(--bg-tertiary);
            padding: 2px 7px;
            border-radius: 4px;
            color: var(--accent-blue);
        }}
        pre {{
            background: var(--bg-secondary);
            border: 1px solid var(--border-light);
            border-radius: var(--radius-md);
            padding: 22px;
            overflow-x: auto;
            margin: 22px 0;
        }}
        pre code {{
            background: none;
            padding: 0;
            color: var(--text-primary);
            font-size: 13px;
            line-height: 1.55;
        }}
        hr {{
            border: none;
            height: 1px;
            background: var(--border-light);
            margin: 40px 0;
        }}
        a {{
            color: var(--accent-blue);
            text-decoration: none;
            border-bottom: 1px solid transparent;
            transition: border-color 0.2s ease;
        }}
        a:hover {{ border-bottom-color: var(--accent-blue); }}

        /* ── Footer ─────────────────────────────────────────────────────────── */
        .report-footer {{
            margin-top: 72px;
            padding: 32px 0;
            border-top: 1px solid var(--border-light);
            display: flex;
            justify-content: space-between;
            align-items: center;
            flex-wrap: wrap;
            gap: 12px;
            font-size: 12px;
            color: var(--text-muted);
        }}
        .report-footer a {{
            color: var(--text-secondary);
            border-bottom-color: var(--border-medium);
        }}
        .report-footer a:hover {{ color: var(--accent-blue); border-bottom-color: var(--accent-blue); }}

        @media print {{
            .sidebar {{ display: none; }}
            .page-wrapper {{ grid-template-columns: 1fr; max-width: 100%; }}
            .main-content {{ max-width: 100%; padding: 0; }}
            body {{ font-size: 11pt; line-height: 1.5; background: white; color: #222; }}
            .discovery-section {{ break-inside: avoid; margin-bottom: 32px; }}
            .report-footer {{ border-color: #ddd; color: #666; }}
        }}
        ::-webkit-scrollbar {{ width: 8px; }}
        ::-webkit-scrollbar-track {{ background: transparent; }}
        ::-webkit-scrollbar-thumb {{ background: var(--border-medium); border-radius: 4px; }}
        ::-webkit-scrollbar-thumb:hover {{ background: var(--text-faint); }}
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
            <footer class="report-footer">
                <span>Generated by: {username} based on product discovery tools by <strong>stnkcl</strong></span>
                <span>Get the tool from <a href="{GITHUB_LINK}" target="_blank">GitHub</a></span>
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
