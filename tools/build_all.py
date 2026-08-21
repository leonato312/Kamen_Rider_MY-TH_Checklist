# -*- coding: utf-8 -*-
"""Genera los WebP de despliegue.

  <nombre>.webp        1600 px  -> galeria (se abre en el visor)
  <nombre>-thumb.webp   700 px  -> portada de la tarjeta

FICHA/ se salta por completo: es base de datos y se queda a resolucion
original para poder extraer informacion. Tampoco se sube al despliegue.
Nada se renombra, se mueve ni se borra: solo se anaden .webp.
"""
import io, os, re, sys, time
from PIL import Image

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from plan import BASE, HTML, CARPETA, plan

GAL_LADO,   GAL_Q   = 1600, 80
THUMB_LADO, THUMB_Q = 700,  82
SALTAR = u'FICHA'

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

print(u'== GALERIAS -> WebP %d px ==' % GAL_LADO)
orig_total = gal_total = thumb_total = 0
n_gal = 0
img_field   = {}
gallery_map = {}

for pid, carpeta, portada, files, err in filas:
    if err:
        print(u'  !! %s: %s' % (pid, err))
        continue
    assert SALTAR not in carpeta.upper().split(u'/'), carpeta

    dir_abs = os.path.join(BASE, carpeta)
    rutas_webp = []
    peso_o = peso_w = 0

    for f in files:
        stem = os.path.splitext(f)[0]
        if stem.endswith(u'-thumb'):
            continue                       # derivado nuestro, no fuente
        src_abs = os.path.join(dir_abs, f)
        out_abs = os.path.join(dir_abs, stem + u'.webp')
        if f.lower().endswith('.webp'):
            continue                       # ya es el destino
        peso_o += os.path.getsize(src_abs)
        peso_w += convertir(src_abs, out_abs, GAL_LADO, GAL_Q)
        rutas_webp.append(u'%s/%s.webp' % (carpeta, stem))
        n_gal += 1

    # Portada reducida, a partir del original de mayor calidad
    stem_p = os.path.splitext(portada)[0]
    thumb_abs = os.path.join(dir_abs, stem_p + u'-thumb.webp')
    thumb_total += convertir(os.path.join(dir_abs, portada),
                             thumb_abs, THUMB_LADO, THUMB_Q)

    orig_total += peso_o
    gal_total  += peso_w
    img_field[pid]   = u'%s/%s-thumb.webp' % (carpeta, stem_p)
    gallery_map[pid] = rutas_webp

    print(u'  %-26s %2d fotos  %6.1f MB -> %6.1f MB'
          % (pid, len(rutas_webp), peso_o / 1048576.0, peso_w / 1048576.0))

print(u'  ' + u'-' * 62)
print(u'  %d fotos   originales %.1f MB -> galeria WebP %.1f MB  (%.0f%% menos)'
      % (n_gal, orig_total / 1048576.0, gal_total / 1048576.0,
         100.0 * (1 - float(gal_total) / orig_total)))
print(u'  %d portadas -thumb: %.2f MB' % (len(filas), thumb_total / 1048576.0))
print(u'  tiempo: %.0f s' % (time.time() - t0))

# ---------------------------------------------------------------- HTML
src = io.open(HTML, encoding='utf-8').read()

def js_array(rutas):
    return u'[' + u',\n              '.join(u'"%s"' % r for r in rutas) + u']'

n_i = n_g = 0
for pid in sorted(CARPETA):
    if pid not in img_field:
        continue
    pat = re.compile(u'(\\{ id:"' + re.escape(pid) + u'",.*?img:)"[^"]*"', re.S)
    src, k = pat.subn(lambda m: m.group(1) + u'"' + img_field[pid] + u'"', src, count=1)
    n_i += k
    pat_g = re.compile(u'(\\{ id:"' + re.escape(pid) + u'",.*?)gallery:\\[.*?\\],', re.S)
    src, k = pat_g.subn(lambda m: m.group(1) + u'gallery:' + js_array(gallery_map[pid]) + u',',
                        src, count=1)
    n_g += k

io.open(HTML, 'w', encoding='utf-8', newline='').write(src)
print(u'')
print(u'== HTML ==  img: %d   gallery: %d' % (n_i, n_g))

# ---------------------------------------------------------------- Verificacion
imgs = re.findall(r'img:"([^"]*)"', src)
gals = re.findall(r'gallery:\[(.*?)\]', src, re.S)
todas = re.findall(r'"([^"]*\.webp)"', u' '.join(gals))
rotos = [p for p in imgs + todas if not os.path.exists(os.path.join(BASE, p))]
print(u'  portadas: %d   fotos de galeria: %d   rutas rotas: %d'
      % (len(imgs), len(todas), len(rotos)))
print(u'  no-webp que hayan quedado referenciados: %d'
      % len([p for p in imgs + todas if not p.endswith('.webp')]))
for p in rotos[:5]:
    print(u'   !! ' + p)

# Peso de despliegue: todo menos FICHA y menos originales
sube = 0
for r, d, fs in os.walk(BASE):
    if SALTAR in r.upper().split(os.sep):
        continue
    for f in fs:
        if f.lower().endswith(('.webp', '.html')):
            sube += os.path.getsize(os.path.join(r, f))
print(u'')
print(u'== DESPLIEGUE ==  WebP + HTML, sin FICHA ni originales: %.1f MB'
      % (sube / 1048576.0))
