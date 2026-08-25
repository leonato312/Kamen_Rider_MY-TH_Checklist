# -*- coding: utf-8 -*-
"""Comprueba las rutas de index.html distinguiendo mayusculas.

SOLO LECTURA.

`audit.py` usa os.path.exists, que en Windows resuelve sin distinguir
mayusculas: una ruta mal capitalizada pasa el filtro en local y da 404 en
GitHub Pages. Aqui se compara cada tramo contra el nombre REAL del directorio,
letra a letra, que es lo mismo que hara el servidor.

Con `--servidor <URL base>` ademas pide cada ruta al sitio publicado, que es la
unica prueba definitiva.
"""
import io
import os
import re
import sys

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
s = io.open(os.path.join(BASE, 'index.html'), encoding='utf-8').read()

rutas = re.findall(r'img:"([^"]*)"', s)
rutas += re.findall(r'"([^"]+\.webp)"',
                    ' '.join(re.findall(r'gallery:\[(.*?)\]', s, re.S)))
rutas = sorted(set(rutas))

print('%d rutas referenciadas' % len(rutas))
malas = []
for r in rutas:
    partes = r.split('/')
    actual = BASE
    for p in partes:
        try:
            reales = os.listdir(actual)
        except OSError:
            malas.append((r, 'no se puede listar ' + actual[len(BASE):]))
            break
        if p not in reales:
            coincide = [x for x in reales if x.lower() == p.lower()]
            malas.append((r, 'en disco es "%s"' % coincide[0] if coincide
                          else 'no existe "%s"' % p))
            break
        actual = os.path.join(actual, p)

print('  mayusculas o nombres que no cuadran: %d' % len(malas))
for r, m in malas[:20]:
    print('   !! %-58s %s' % (r[:58], m))

if len(sys.argv) > 2 and sys.argv[1] == '--servidor':
    import time
    import urllib.parse
    import urllib.request
    base = sys.argv[2].rstrip('/')
    print('')
    print('Pidiendo las %d rutas a %s' % (len(rutas), base))
    fallos = []
    for i, r in enumerate(rutas, 1):
        url = base + '/' + urllib.parse.quote(r)
        try:
            req = urllib.request.Request(url, method='HEAD')
            code = urllib.request.urlopen(req, timeout=25).status
        except Exception as e:
            code = getattr(e, 'code', 0) or 0
        if code != 200:
            fallos.append((code, r))
        if i % 50 == 0:
            print('  %d/%d  fallos: %d' % (i, len(rutas), len(fallos)))
        time.sleep(0.05)
    print('  %d de %d con codigo distinto de 200' % (len(fallos), len(rutas)))
    for c, r in fallos[:25]:
        print('   !! %s  %s' % (c, r))
    sys.exit(1 if fallos else 0)

sys.exit(1 if malas else 0)
