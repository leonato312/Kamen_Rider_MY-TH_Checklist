# -*- coding: utf-8 -*-
"""Auditoria del catalogo. SOLO LECTURA: no modifica nada.

Que comprueba, por orden de importancia:

  1. Que index.html y el disco digan lo mismo. Es lo unico que puede romper
     el sitio publicado, asi que va primero.
  2. Que cada producto tenga portada y una numeracion sana.
  3. Nomenclatura y duplicados.

Que NO comprueba: el contenido de FICHA/. Esas carpetas son material de
consulta, de formato libre y no publicable — una hoja puede cubrir una
coleccion entera. Exigirles un nombre por producto solo generaba ruido.
"""
import io, os, re, sys

import os as _os
BASE = _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))

HTML      = os.path.join(BASE, u'index.html')
FICHA_DIR = u'FICHA'
IMG_EXT   = ('.jpg', '.jpeg', '.png')      # solo originales; los .webp son derivados
OMITIR    = ('tools',)

problemas = []
def flag(sev, ruta, motivo):
    problemas.append((sev, ruta, motivo))

def orden(nombre):
    """PACKAGE primero, luego 01, 02, 03..."""
    stem = os.path.splitext(nombre)[0]
    if stem.upper() == u'PACKAGE': return (0, 0)
    return (1, int(stem)) if stem.isdigit() else (2, 0)

cats = sorted([d for d in os.listdir(BASE)
               if os.path.isdir(os.path.join(BASE, d))
               and not d.startswith('.') and d not in OMITIR])

# ---------------------------------------------------------------- inventario
inv = {}          # cat -> {'ficha': n, 'prods': {nombre: [archivos]}, 'sueltos': [archivos]}
for cat in cats:
    d = os.path.join(BASE, cat)
    fpath = os.path.join(d, FICHA_DIR)
    ficha = len([f for f in os.listdir(fpath) if f.lower().endswith(IMG_EXT)]) \
            if os.path.isdir(fpath) else 0
    prods, sueltos = {}, []
    for x in sorted(os.listdir(d)):
        xp = os.path.join(d, x)
        if os.path.isdir(xp) and x != FICHA_DIR:
            prods[x] = sorted([f for f in os.listdir(xp) if f.lower().endswith(IMG_EXT)],
                              key=orden)
        elif os.path.isfile(xp) and x.lower().endswith(IMG_EXT):
            sueltos.append(x)              # producto de una sola imagen
    inv[cat] = {'ficha': ficha, 'prods': prods, 'sueltos': sueltos}

print(u'==============================================================')
print(u' 1. INDEX.HTML  <->  DISCO   (lo unico que puede romper el sitio)')
print(u'==============================================================')

s = io.open(HTML, encoding='utf-8').read()
portadas = re.findall(r'img:"([^"]*)"', s)
galerias = re.findall(r'"([^"]*\.webp)"',
                      u' '.join(re.findall(r'gallery:\[(.*?)\]', s, re.S)))

rotas = [p for p in portadas + galerias if not os.path.exists(os.path.join(BASE, p))]
for p in rotas:
    flag(u'ALTO', p, u'referenciada en index.html pero no esta en disco')
print(u'  portadas %d · fotos de galeria %d · rutas rotas %d'
      % (len(portadas), len(galerias), len(rotas)))

# WebP en disco que nadie usa: peso muerto que se subiria al repositorio
refs = set(portadas) | set(galerias)
huerfanos = []
for r, d, fs in os.walk(BASE):
    if '.git' in r.split(os.sep) or FICHA_DIR in [x.upper() for x in r.split(os.sep)]:
        continue
    for f in fs:
        if f.endswith('.webp'):
            rel = os.path.relpath(os.path.join(r, f), BASE).replace(os.sep, u'/')
            if rel not in refs:
                huerfanos.append(rel)
for h in huerfanos:
    flag(u'MEDIO', h, u'.webp en disco que index.html no usa')
print(u'  .webp huerfanos: %d' % len(huerfanos))

# Carpetas de producto que la pagina no conoce
conocidas = set()
for p in portadas + galerias:
    conocidas.add(p.rsplit(u'/', 1)[0])
for cat in cats:
    for prod in inv[cat]['prods']:
        ruta = u'%s/%s' % (cat, prod)
        if ruta not in conocidas and inv[cat]['prods'][prod]:
            flag(u'MEDIO', ruta + u'/', u'carpeta con fotos que index.html no referencia')

print(u'')
print(u'==============================================================')
print(u' 2. PORTADA Y NUMERACION DE CADA PRODUCTO')
print(u'==============================================================')
for cat in cats:
    prods, sueltos = inv[cat]['prods'], inv[cat]['sueltos']
    if not prods and not sueltos:
        print(u'-- %-28s (vacia)' % cat)
        continue
    print(u'-- %-28s ficha: %d archivo(s)' % (cat, inv[cat]['ficha']))
    for x in sueltos:
        print(u'   %-52s 1 img  (suelto)' % os.path.splitext(x)[0][:52])
    for nombre, files in sorted(prods.items()):
        if not files:
            flag(u'ALTO', u'%s/%s/' % (cat, nombre), u'carpeta de producto vacia')
            print(u'   %-52s VACIA' % nombre[:52]); continue
        stems = [os.path.splitext(f)[0] for f in files]
        pkg   = any(v.upper() == u'PACKAGE' for v in stems)
        nums  = sorted(int(v) for v in stems if v.isdigit())
        portada = u'PACKAGE' if pkg else (u'01' if 1 in nums else u'??')
        if portada == u'??':
            flag(u'ALTO', u'%s/%s/' % (cat, nombre), u'sin PACKAGE y sin 01: no hay portada')
        aviso = u''
        if nums and nums != list(range(1, len(nums) + 1)):
            faltan = [n for n in range(1, max(nums) + 1) if n not in nums]
            aviso = u'  HUECOS: %s' % u', '.join(u'%02d' % n for n in faltan)
            flag(u'MEDIO', u'%s/%s/' % (cat, nombre), u'numeracion con huecos: %s' % aviso.strip())
        sinpad = [v for v in stems if v.isdigit() and len(v) < 2]
        if sinpad:
            flag(u'MEDIO', u'%s/%s/' % (cat, nombre), u'sin cero delante: %s' % u', '.join(sinpad))
        print(u'   %-52s %2d img  portada=%-8s%s' % (nombre[:52], len(files), portada, aviso))

print(u'')
print(u'==============================================================')
print(u' 3. NOMENCLATURA Y DUPLICADOS')
print(u'==============================================================')
for cat in cats:
    if cat != cat.upper():
        flag(u'MEDIO', cat, u'categoria con minusculas')
    for prod in inv[cat]['prods']:
        if prod != prod.upper():
            flag(u'BAJO', u'%s/%s/' % (cat, prod), u'estilo: minusculas en el nombre')

vistos = {}
for cat in cats:
    for f in list(inv[cat]['prods'].keys()) + list(inv[cat]['sueltos']):
        vistos.setdefault(f, []).append(cat)
dups = {k: v for k, v in vistos.items() if len(v) > 1}
if dups:
    for f, cs in dups.items():
        print(u'  mismo nombre en %s: %s' % (u' y '.join(cs), f[:60]))
else:
    print(u'  sin nombres repetidos entre categorias')

print(u'')
print(u'==============================================================')
print(u' RESULTADO')
print(u'==============================================================')
orden_sev = {u'ALTO': 0, u'MEDIO': 1, u'BAJO': 2}
problemas.sort(key=lambda x: (orden_sev[x[0]], x[1]))
if not problemas:
    print(u'  Sin incidencias.')
else:
    print(u'  %d incidencias (ALTO=%d MEDIO=%d BAJO=%d)' % (
        len(problemas),
        sum(1 for p in problemas if p[0] == u'ALTO'),
        sum(1 for p in problemas if p[0] == u'MEDIO'),
        sum(1 for p in problemas if p[0] == u'BAJO')))
    print(u'')
    for sev, ruta, motivo in problemas:
        print(u'  [%-5s] %-52s %s' % (sev, ruta[:52], motivo))
