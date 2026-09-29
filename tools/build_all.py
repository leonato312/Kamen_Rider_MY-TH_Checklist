# -*- coding: utf-8 -*-
"""Genera los WebP de despliegue y repunta las rutas en index.html.

  <nombre>.webp        1600 px lado maximo  -> galeria, se abre en el visor
  <nombre>-thumb.webp   700 px lado maximo  -> portada de la tarjeta

NUNCA AMPLIA: `escala = min(1, lado/max(w,h))`. Si los originales son de
1500 px, las galerias se quedaran por debajo de los 1600 nominales. No es un
fallo: no hay mas resolucion publicada. Queda escrito para no perseguirlo.

FICHA/ se salta por completo: son las hojas de despiece, se quedan a resolucion
original para poder recortarlas y no se publican.

NADA SE RENOMBRA, SE MUEVE NI SE BORRA: solo se anaden .webp. Es una decision
deliberada, pero tiene consecuencia -> ver el bloque de HUERFANOS al final.
"""
import io
import os
import re
import sys
import time
from PIL import Image

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from plan import BASE, HTML, plan

GAL_LADO,   GAL_Q   = 1600, 80
THUMB_LADO, THUMB_Q = 700,  82
SALTAR = 'FICHA'


def convertir(src_abs, out_abs, lado, calidad):
    im = Image.open(src_abs)
    if im.mode not in ('RGB', 'RGBA'):
        im = im.convert('RGB')
    w, h = im.size
    escala = min(1.0, float(lado) / max(w, h))
    if escala < 1.0:
        im = im.resize((int(w * escala), int(h * escala)), Image.LANCZOS)
    im.save(out_abs, 'WEBP', quality=calidad, method=5)
    return os.path.getsize(out_abs)


filas = plan()
t0 = time.time()

print('== GALERIAS -> WebP %d px ==' % GAL_LADO)
orig_total = gal_total = thumb_total = 0
n_gal = 0
img_field, gallery_map = {}, {}
esperados = set()          # .webp que este build considera vivos

for pid, ruta, portada, files, suelto, err in filas:
    # `err` con portada != None es un aviso, no un fallo: se sigue adelante.
    if portada is None:
        print('  !! %s: %s' % (pid, err))
        continue
    if err:
        print('  ~  %s: %s' % (pid, err))

    dir_rel = os.path.dirname(ruta) if suelto else ruta
    assert SALTAR not in dir_rel.upper().split('/'), dir_rel
    dir_abs = os.path.join(BASE, dir_rel)

    rutas_webp = []
    peso_o = peso_w = 0
    for f in files:
        stem = os.path.splitext(f)[0]
        if stem.endswith('-thumb'):
            continue                              # derivado nuestro, no fuente
        src_abs = os.path.join(dir_abs, f)
        out_abs = os.path.join(dir_abs, stem + '.webp')
        peso_o += os.path.getsize(src_abs)
        peso_w += convertir(src_abs, out_abs, GAL_LADO, GAL_Q)
        rutas_webp.append('%s/%s.webp' % (dir_rel, stem))
        esperados.add(os.path.normcase(out_abs))
        n_gal += 1

    # Portada reducida, generada del original de mayor calidad.
    stem_p    = os.path.splitext(portada)[0]
    thumb_abs = os.path.join(dir_abs, stem_p + '-thumb.webp')
    thumb_total += convertir(os.path.join(dir_abs, portada), thumb_abs,
                             THUMB_LADO, THUMB_Q)
    esperados.add(os.path.normcase(thumb_abs))

    orig_total += peso_o
    gal_total  += peso_w
    img_field[pid]   = '%s/%s-thumb.webp' % (dir_rel, stem_p)
    gallery_map[pid] = rutas_webp

    print('  %-24s %2d fotos  %6.1f MB -> %6.1f MB'
          % (pid, len(rutas_webp), peso_o / 1048576.0, peso_w / 1048576.0))

print('  ' + '-' * 62)
print('  %d fotos   originales %.1f MB -> galeria WebP %.1f MB  (%.0f%% menos)'
      % (n_gal, orig_total / 1048576.0, gal_total / 1048576.0,
         100.0 * (1 - gal_total / orig_total) if orig_total else 0))
print('  %d portadas -thumb: %.2f MB' % (len(img_field), thumb_total / 1048576.0))
print('  tiempo: %.0f s' % (time.time() - t0))

# ------------------------------------------------------------------ HTML
src = io.open(HTML, encoding='utf-8').read()


def js_array(rutas):
    return '[' + ',\n             '.join('"%s"' % r for r in rutas) + ']'


n_i = n_g = 0
for pid in sorted(img_field):
    # Anclado al id del producto y no-greedy: no se sale de su entrada.
    pat = re.compile(r'(\{\s*id:\s*"' + re.escape(pid) + r'",.*?img:\s*)"[^"]*"', re.S)
    src, k = pat.subn(lambda m: m.group(1) + '"' + img_field[pid] + '"', src, count=1)
    n_i += k
    pat_g = re.compile(r'(\{\s*id:\s*"' + re.escape(pid) + r'",.*?)gallery:\s*\[.*?\],', re.S)
    src, k = pat_g.subn(
        lambda m: m.group(1) + 'gallery:' + js_array(gallery_map[pid]) + ',',
        src, count=1)
    n_g += k

io.open(HTML, 'w', encoding='utf-8', newline='').write(src)
print('')
print('== HTML ==  img repuntadas: %d   gallery repuntadas: %d' % (n_i, n_g))
if n_i != len(img_field) or n_g != len(gallery_map):
    print('  !! algun producto no se repunto: revisa que el id exista en PRODUCTS')

# ---------------------------------------------------------- Verificacion
imgs  = re.findall(r'img:\s*"([^"]*)"', src)
gals  = re.findall(r'gallery:\s*\[(.*?)\]', src, re.S)
todas = re.findall(r'"([^"]*\.webp)"', ' '.join(gals))
rotas = [p for p in imgs + todas if not os.path.exists(os.path.join(BASE, p))]
noweb = [p for p in imgs + todas if not p.endswith('.webp')]
print('  portadas: %d   fotos de galeria: %d   rutas rotas: %d'
      % (len(imgs), len(todas), len(rotas)))
print('  no-webp que hayan quedado referenciados: %d' % len(noweb))
for p in (rotas + noweb)[:6]:
    print('   !! ' + p)

# ------------------------------------------------------------- HUERFANOS
# Este script NUNCA borra. Consecuencia real: ascender 10.jpg a PACKAGE.jpg deja
# atras su 10.webp y el -thumb de la portada vieja. En un caso documentado
# fueron 105 archivos que se habrian publicado sin que nada los referenciara.
# No se borran aqui -borrar automaticamente es peor-, pero se listan.
huerfanos = []
for r, d, fs in os.walk(BASE):
    partes = r.upper().split(os.sep)
    if SALTAR in partes or '.GIT' in partes:
        continue
    for f in fs:
        if not f.lower().endswith('.webp'):
            continue
        full = os.path.join(r, f)
        if os.path.normcase(full) not in esperados:
            huerfanos.append(os.path.relpath(full, BASE))

print('')
print('== HUERFANOS ==  %d .webp que este build no ha generado' % len(huerfanos))
if huerfanos:
    for p in huerfanos[:15]:
        print('   ~ ' + p)
    if len(huerfanos) > 15:
        print('   ... y %d mas' % (len(huerfanos) - 15))
    print('')
    print('  Suele pasar tras cambiar que archivo es la portada. Revisalos y')
    print('  borralos a mano; luego vuelve a auditar. Se publicarian sin que')
    print('  nada los referencie.')

# Peso de despliegue: todo menos FICHA y menos originales.
sube = 0
for r, d, fs in os.walk(BASE):
    partes = r.upper().split(os.sep)
    if SALTAR in partes or '.GIT' in partes:
        continue
    for f in fs:
        if f.lower().endswith(('.webp', '.html')):
            sube += os.path.getsize(os.path.join(r, f))
print('')
print('== DESPLIEGUE ==  WebP + HTML, sin FICHA ni originales: %.1f MB'
      % (sube / 1048576.0))

sys.exit(1 if (rotas or noweb) else 0)
