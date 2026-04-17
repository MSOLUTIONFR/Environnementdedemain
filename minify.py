#!/usr/bin/env python3

import os
import re
import shutil

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SRC_DIR = os.path.join(BASE_DIR, 'src')
DIST_DIR = os.path.join(BASE_DIR, 'dist')

os.makedirs(SRC_DIR, exist_ok=True)
os.makedirs(DIST_DIR, exist_ok=True)


def minify_css(content):
    content = re.sub(r'/\*[\s\S]*?\*/', '', content)
    content = re.sub(r'\s+', ' ', content)
    content = re.sub(r'\s*\{\s*', '{', content)
    content = re.sub(r'\s*\}\s*', '}', content)
    content = re.sub(r'\s*;\s*', ';', content)
    content = re.sub(r'\s*,\s*', ',', content)
    content = re.sub(r'(\w)\s*:\s*', r'\1:', content)
    content = re.sub(r';}', '}', content)
    return content.strip()


def _add_draggable(match):
    tag = match.group(0)
    if 'draggable=' not in tag.lower():
        if tag.endswith('/>'):
            tag = tag[:-2].rstrip() + ' draggable="false"/>'
        else:
            tag = tag[:-1].rstrip() + ' draggable="false">'
    return tag


def minify_html(content):
    content = re.sub(r'<!--(?!\[if\b)[\s\S]*?-->', '', content)
    content = re.sub(r'<img[^>]*>', _add_draggable, content, flags=re.IGNORECASE)
    lines = [line.strip() for line in content.splitlines()]
    content = ''.join(line for line in lines if line)
    return content


files = [f for f in os.listdir(BASE_DIR)
         if os.path.isfile(os.path.join(BASE_DIR, f)) and f != 'minify.py']

for filename in sorted(files):
    src_path = os.path.join(BASE_DIR, filename)
    dist_path = os.path.join(DIST_DIR, filename)
    src_copy = os.path.join(SRC_DIR, filename)

    shutil.copy2(src_path, src_copy)

    ext = os.path.splitext(filename)[1].lower()

    if ext == '.css':
        with open(src_path, 'r', encoding='utf-8') as f:
            result = minify_css(f.read())
        with open(dist_path, 'w', encoding='utf-8') as f:
            f.write(result)

    elif ext == '.html':
        with open(src_path, 'r', encoding='utf-8') as f:
            result = minify_html(f.read())
        with open(dist_path, 'w', encoding='utf-8') as f:
            f.write(result)

    else:
        shutil.copy2(src_path, dist_path)


css_files = ['index.css', 'Page2.css', 'Page3.css', 'Page4.css', 'Page5.css']
combined_css = ""

for css_file in css_files:
    css_path = os.path.join(DIST_DIR, css_file)
    if os.path.exists(css_path):
        with open(css_path, 'r', encoding='utf-8') as f:
            combined_css += f.read() + '\n'

if combined_css:
    combined_path = os.path.join(DIST_DIR, 'styles.min.css')
    combined_css_minified = minify_css(combined_css)
    with open(combined_path, 'w', encoding='utf-8') as f:
        f.write(combined_css_minified)
