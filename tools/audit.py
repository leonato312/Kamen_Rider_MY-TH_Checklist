# -*- coding: utf-8 -*-
"""Auditoria de nombres y estructura. SOLO LECTURA: no modifica nada."""
import io, os, re, unicodedata

import os as _os
BASE = _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))
FICHA_DIR = u'FICHA'
# Solo los originales. Los .webp los genera build_all.py a partir de estos;
# contarlos duplicaba cada numero y hacia ver huecos donde no los hay.
IMG_EXT = ('.jpg', '.jpeg', '.png', '.gif')

problemas = []      # (severidad, ruta, motivo)
def flag(sev, ruta, motivo):
    problemas.append((sev, ruta, motivo))

def mb(n):
    return n / 1048576.0

OMITIR = ('tools',)   # no es una categoria del catalogo
cats = sorted([d for d in os.listdir(BASE) if d not in OMITIR
               if os.path.isdir(os.path.join(BASE, d)) and not d.startswith('.')])

print(u'==============================================================')
print(u' 1. INVENTARIO POR CATEGORIA')
print(u'==============================================================')
print(u'%-16s %6s %8s %10s %9s' % (u'CATEGORIA', u'FICHAS', u'PRODUCT', u'IMAGENES', u'PESO'))

total_files = total_bytes = 0
inventario = {}   # cat -> {'fichas':[...], 'prods':{nombre: [archivos]}}

for cat in cats:
    d = os.path.join(BASE, cat)
    fichas, prods = [], {}
    fpath = os.path.join(d, FICHA_DIR)
    if os.path.isdir(fpath):
        fichas = sorted([f for f in os.listdir(fpath) if f.lower().endswith(IMG_EXT)])
    for s in sorted(os.listdir(d)):
        sp = os.path.join(d, s)
        if os.path.isdir(sp) and s != FICHA_DIR:
            prods[s] = sorted([f for f in os.listdir(sp) if f.lower().endswith(IMG_EXT)])
    inventario[cat] = {'fichas': fichas, 'prods': prods}

    n_img = sum(len(v) for v in prods.values())
    peso = 0
    for r, _, fs in os.walk(d):
        for f in fs:
            peso += os.path.getsize(os.path.join(r, f))
            total_files += 1
    total_bytes += peso
    print(u'%-16s %6d %8d %10d %8.1fM' % (cat, len(fichas), len(prods), n_img, mb(peso)))

print(u'%-16s %6s %8s %10s %8.1fM' % (u'TOTAL', u'', u'', u'', mb(total_bytes)))

print(u'')
print(u'==============================================================')
print(u' 2. CADA PRODUCTO: PORTADA Y NUMERACION')
print(u'==============================================================')

for cat in cats:
    prods = inventario[cat]['prods']
    if not prods:
        print(u'-- %s: (sin carpetas de producto)' % cat)
        continue
    print(u'-- %s' % cat)
    for nombre, files in sorted(prods.items()):
        if not files:
            flag(u'ALTO', u'%s/%s/' % (cat, nombre), u'carpeta de producto vacia')
            print(u'   %-48s  VACIA' % nombre[:48])
            continue

        stems = [os.path.splitext(f)[0] for f in files]
        has_pkg = any(s.upper() == u'PACKAGE' for s in stems)
        nums = sorted([int(s) for s in stems if s.isdigit()])
        otros = [s for s in stems if not s.isdigit() and s.upper() != u'PACKAGE']

        portada = u'PACKAGE' if has_pkg else (u'01' if 1 in nums else u'??')
        if portada == u'??':
            flag(u'ALTO', u'%s/%s/' % (cat, nombre),
                 u'sin PACKAGE y sin 01: no hay portada definible')

        # Numeracion: debe ser 1..n sin huecos
        hueco = u''
        if nums and nums != list(range(1, len(nums) + 1)):
            faltan = [n for n in range(1, max(nums) + 1) if n not in nums]
            hueco = u'  HUECOS: falta %s' % u', '.join(u'%02d' % n for n in faltan)
            flag(u'MEDIO', u'%s/%s/' % (cat, nombre), u'numeracion con huecos: falta %s'
                 % u', '.join(u'%02d' % n for n in faltan))

        # Padding: 1.jpg en vez de 01.jpg
        sinpad = [s for s in stems if s.isdigit() and len(s) < 2]
        if sinpad:
            flag(u'MEDIO', u'%s/%s/' % (cat, nombre),
                 u'sin cero delante: %s' % u', '.join(sinpad))

        # Extensiones mezcladas
        exts = set(os.path.splitext(f)[1].lower() for f in files)
        mix = u'  ext: %s' % u'/'.join(sorted(e[1:] for e in exts)) if len(exts) > 1 else u''

        extra = u'  otros: %s' % u', '.join(otros) if otros else u''
        print(u'   %-48s  %2d img  portada=%-8s%s%s%s'
              % (nombre[:48], len(files), portada, hueco, mix, extra))

print(u'')
print(u'==============================================================')
print(u' 3. FICHAS  <->  CARPETAS DE PRODUCTO')
print(u'==============================================================')

def norm(s):
    """Normaliza para comparar: mayusculas y separadores/espacios colapsados."""
    s = s.upper().replace(u'&', u' & ')
    s = re.sub(u'[\\s_]+', u' ', s).strip()
    return s

for cat in cats:
    fichas = inventario[cat]['fichas']
    prods  = list(inventario[cat]['prods'].keys())
    if not fichas and not prods:
        continue
    print(u'-- %s' % cat)

    if not fichas:
        flag(u'ALTO', u'%s/FICHA/' % cat, u'categoria sin carpeta FICHA o vacia')
        print(u'   (sin fichas)')

    prods_norm = dict((norm(p), p) for p in prods)
    emparejadas = set()

    for f in fichas:
        stem = os.path.splitext(f)[0]
        # nombre del producto = lo anterior al separador de contenidos
        partes = re.split(u'\\s-\\s|-(?=[A-Z][a-z])', stem, 1)
        base = partes[0].strip()
        cont = partes[1].strip() if len(partes) > 1 else None

        n = norm(base)
        if n in prods_norm:
            real = prods_norm[n]
            emparejadas.add(real)
            if real != base:
                flag(u'ALTO', u'%s/%s' % (cat, f),
                     u'ficha "%s" vs carpeta "%s": difieren' % (base, real))
                print(u'   [!=] %-44s  carpeta: %s' % (base[:44], real))
            else:
                print(u'   [ok] %-44s  %s' % (base[:44],
                      u'contenidos: ' + cont[:28] if cont else u'(sin contenidos)'))
        else:
            flag(u'ALTO', u'%s/FICHA/%s' % (cat, f), u'ficha sin carpeta de producto')
            print(u'   [??] %-44s  SIN CARPETA' % base[:44])

    for p in prods:
        if p not in emparejadas:
            flag(u'ALTO', u'%s/%s/' % (cat, p), u'carpeta de producto sin ficha')
            print(u'   [??] %-44s  SIN FICHA' % p[:44])

print(u'')
print(u'==============================================================')
print(u' 4. NOMENCLATURA')
print(u'==============================================================')

for cat in cats:
    if cat != cat.upper():
        flag(u'MEDIO', cat, u'categoria con minusculas')
    for f in inventario[cat]['fichas']:
        stem = os.path.splitext(f)[0]
        partes = re.split(u'\\s-\\s|-(?=[A-Z][a-z])', stem, 1)
        base = partes[0].strip()
        if base != base.upper():
            flag(u'BAJO', u'%s/FICHA/%s' % (cat, f),
                 u'estilo: minusculas en el nombre: "%s"' % base)
        if u' - ' not in stem and len(partes) > 1:
            flag(u'BAJO', u'%s/FICHA/%s' % (cat, f),
                 u'separador pegado; se recomienda " - " por MY-TH')
    for p in inventario[cat]['prods']:
        if p != p.upper():
            flag(u'BAJO', u'%s/%s/' % (cat, p), u'estilo: minusculas en el nombre')  # informativo

print(u'')
print(u'==============================================================')
print(u' 5. RESULTADO')
print(u'==============================================================')
orden = {u'ALTO': 0, u'MEDIO': 1, u'BAJO': 2}
problemas.sort(key=lambda x: (orden[x[0]], x[1]))
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
