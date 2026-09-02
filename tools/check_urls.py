# -*- coding: utf-8 -*-
"""Comprueba las rutas de index.html distinguiendo mayusculas.

SOLO LECTURA.

`audit.py` usa os.path.exists, que en Windows resuelve SIN distinguir
mayusculas: una ruta mal capitalizada pasa el filtro en local y da 404
publicada. Aqui se compara cada tramo contra el nombre REAL del directorio,
letra a letra, que es lo mismo que hara el servidor.

Es el fallo mas traicionero del sistema y la razon de que este archivo exista.
Con TODAS las rutas cambiando en una migracion, correrlo deja de ser opcional.

    python tools/check_urls.py
    python tools/check_urls.py --servidor https://usuario.github.io/repo

Con `--servidor` ademas pide cada ruta al sitio publicado, que es la unica
prueba definitiva: el disco puede estar bien y la ruta escrita mal.
"""
import io
import os
import re
import sys

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HTML = os.path.join(BASE, 'index.html')

if not os.path.exists(HTML):
    print('No hay index.html en %s' % BASE)
    sys.exit(2)

s = io.open(HTML, encoding='utf-8').read()

rutas = re.findall(r'img:\s*"([^"]*)"', s)
rutas += re.findall(r'"([^"]+\.webp)"',
                    ' '.join(re.findall(r'gallery:\s*\[(.*?)\]', s, re.S)))
rutas = sorted(set(r for r in rutas if r))

print('%d rutas referenciadas' % len(rutas))

# --- 1. Mayusculas y nombres, contra el disco real -------------------------
malas = []
for r in rutas:
    actual = BASE
    for p in r.split('/'):
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
if len(malas) > 20:
    print('   ... y %d mas' % (len(malas) - 20))

# --- 2. Nombres que terminan en punto --------------------------------------
# Windows se come el punto final de un nombre de carpeta en silencio: la ruta
# resuelve en local y da 404 publicada. Se comprueba sobre la ruta escrita, no
# sobre el disco, porque en disco el punto ya no esta.
puntos = [r for r in rutas if any(t.rstrip().endswith('.') for t in r.split('/')[:-1])]
if puntos:
    print('')
    print('  !! %d ruta(s) con un tramo que termina en punto: daran 404' % len(puntos))
    for r in puntos[:10]:
        print('     %s' % r)

# --- 3. Contra el servidor publicado ---------------------------------------
if len(sys.argv) > 2 and sys.argv[1] == '--servidor':
    import time
    import urllib.parse
    import urllib.request
    base = sys.argv[2].rstrip('/')
    print('')
    print('Pidiendo las %d rutas a %s' % (len(rutas), base))
    fallos = []
    reintentos = 0
    for i, r in enumerate(rutas, 1):
        url = base + '/' + urllib.parse.quote(r)
        # Un 5xx NO es una ruta rota: con mil y pico peticiones seguidas el
        # hosting responde 503 de vez en cuando y vuelve en si al segundo
        # intento. Darlo por fallo llena el informe de falsos positivos, que es
        # lo que hace que nadie lo lea. Un 404 NO se reintenta: ese es real.
        for intento in (1, 2, 3):
            try:
                req = urllib.request.Request(url, method='HEAD')
                code = urllib.request.urlopen(req, timeout=25).status
            except Exception as e:
                code = getattr(e, 'code', 0) or 0
            if code == 200 or code == 404 or intento == 3:
                break
            reintentos += 1
            time.sleep(1.5 * intento)
        if code != 200:
            fallos.append((code, r))
        if i % 50 == 0:
            print('  %d/%d  fallos: %d' % (i, len(rutas), len(fallos)))
        time.sleep(0.05)
    print('  %d de %d con codigo distinto de 200   (%d reintentos por 5xx)'
          % (len(fallos), len(rutas), reintentos))
    for c, r in fallos[:25]:
        print('   !! %s  %s' % (c, r))
    print('')
    print('  Recordatorio: tras un push que renombra rutas, el hosting tarda')
    print('  uno o dos minutos. Un 404 justo despues de subir no es un fallo.')
    sys.exit(1 if fallos else 0)

sys.exit(1 if (malas or puntos) else 0)
