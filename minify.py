#!/usr/bin/env python3
"""
Script de production pour le site EDD.
- Copie les originaux dans src/
- Produit les versions minifiees dans dist/
- Supprime tous les commentaires HTML et CSS
- Reduit les espaces et sauts de ligne
- Ajoute draggable="false" sur toutes les balises <img>
"""
import os
import re
import shutil

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SRC_DIR  = os.path.join(BASE_DIR, 'src')
DIST_DIR = os.path.join(BASE_DIR, 'dist')

os.makedirs(SRC_DIR,  exist_ok=True)
os.makedirs(DIST_DIR, exist_ok=True)


# ── CSS ──────────────────────────────────────────────────────────────────────

def minify_css(content):
    # Supprime les commentaires /* ... */
    content = re.sub(r'/\*[\s\S]*?\*/', '', content)
    # Reduit tous les espaces/tabulations/sauts de ligne a un seul espace
    content = re.sub(r'\s+', ' ', content)
    # Supprime les espaces autour des accolades
    content = re.sub(r'\s*\{\s*', '{', content)
    content = re.sub(r'\s*\}\s*', '}', content)
    # Supprime les espaces autour des points-virgules et virgules
    content = re.sub(r'\s*;\s*', ';', content)
    content = re.sub(r'\s*,\s*', ',', content)
    # Supprime l'espace apres les deux-points dans les declarations de proprietes
    # (\w) assure qu'on ne touche pas les pseudo-selecteurs du type "a :focus"
    content = re.sub(r'(\w)\s*:\s*', r'\1:', content)
    # Supprime le point-virgule superflu juste avant une accolade fermante
    content = re.sub(r';}', '}', content)
    return content.strip()


# ── HTML ─────────────────────────────────────────────────────────────────────

def _add_draggable(match):
    """Ajoute draggable="false" sur une balise <img> si absent."""
    tag = match.group(0)
    if 'draggable=' not in tag.lower():
        if tag.endswith('/>'):
            tag = tag[:-2].rstrip() + ' draggable="false"/>'
        else:
            tag = tag[:-1].rstrip() + ' draggable="false">'
    return tag


def minify_html(content):
    # Supprime les commentaires HTML (sauf les conditionnels IE <!--[if...]>)
    content = re.sub(r'<!--(?!\[if\b)[\s\S]*?-->', '', content)
    # Ajoute draggable="false" sur chaque <img>
    content = re.sub(r'<img[^>]*>', _add_draggable, content, flags=re.IGNORECASE)
    # Supprime l'indentation et les espaces en debut/fin de chaque ligne
    lines = [line.strip() for line in content.splitlines()]
    # Supprime les lignes vides et recolle tout en une seule ligne
    content = ''.join(line for line in lines if line)
    return content


# ── Traitement des fichiers ───────────────────────────────────────────────────

files = [f for f in os.listdir(BASE_DIR)
         if os.path.isfile(os.path.join(BASE_DIR, f)) and f != 'minify.py']

print(f"Traitement de {len(files)} fichier(s)...\n")

for filename in sorted(files):
    src_path  = os.path.join(BASE_DIR, filename)
    dist_path = os.path.join(DIST_DIR, filename)
    src_copy  = os.path.join(SRC_DIR,  filename)

    # Copie de l'original dans src/
    shutil.copy2(src_path, src_copy)

    ext = os.path.splitext(filename)[1].lower()

    if ext == '.css':
        with open(src_path, 'r', encoding='utf-8') as f:
            result = minify_css(f.read())
        with open(dist_path, 'w', encoding='utf-8') as f:
            f.write(result)
        ratio = round((1 - len(result) / os.path.getsize(src_path)) * 100)
        print(f"  [CSS ] {filename:<20}  -{ratio}%")

    elif ext == '.html':
        with open(src_path, 'r', encoding='utf-8') as f:
            result = minify_html(f.read())
        with open(dist_path, 'w', encoding='utf-8') as f:
            f.write(result)
        ratio = round((1 - len(result) / os.path.getsize(src_path)) * 100)
        print(f"  [HTML] {filename:<20}  -{ratio}%")

    else:
        shutil.copy2(src_path, dist_path)
        print(f"  [COPY] {filename}")

print("\nTermine !")
print(f"  Originaux   ->  src/")
print(f"  Production  ->  dist/")
