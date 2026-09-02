# -*- coding: utf-8 -*-
"""Auditoria maestra: comprueba que un repositorio respeta la arquitectura de DG.

NO audita el contenido de la serie -de eso se encarga tools/audit.py-. Comprueba
dos cosas y ninguna mas:

  a) ORDEN ESTABLECIDO   las 7 categorias, el registro de procedencias, la
                         nomenclatura y los campos que la arquitectura exige.
  b) INTEGRIDAD          estructura de carpetas, rastros del sistema viejo,
                         nombres invalidos y herramientas sin modificar.

Solo lectura: no escribe nada. Sale con codigo 1 si hay alguna incidencia ALTO,
para poder encadenarlo -en particular, para NO borrar originales si falla.

    python tools/audit_maestro.py

Regla que gobierna este archivo, aprendida por las malas:
    UNA AUDITORIA CON FALSOS POSITIVOS ES PEOR QUE NINGUNA.
Una version antigua daba 74 avisos de los que 70 eran ruido, y nadie los leia.
Antes de anadir una comprobacion, preguntate si puede gritar cuando no toca.
"""
import io
import os
import re
import sys
import hashlib

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HTML = os.path.join(BASE, 'index.html')
SERIE = os.path.join(BASE, 'serie.py')

problemas = []


def flag(sev, donde, motivo):
    problemas.append((sev, donde, motivo))


# ---------------------------------------------------------------------------
# CONSTANTES DE LA ARQUITECTURA
# ---------------------------------------------------------------------------

# Las 7 categorias, en orden. El rotulo cambia por serie; la clave no.
CATEGORIAS = ['protagonista', 'dispositivo', 'mecha', 'arma',
              'gimmick', 'aparicion', 'extra']

# Categorias que NO se pueden omitir.
OBLIGATORIAS = ['protagonista']

# FICHA/ solo sobrevive donde hay hojas de despiece que recortar.
FICHA_PERMITIDA_EN = ['SO-DO', 'YU-DO']

# Archivos que NUNCA se auditan ni se senalan como huerfanos.
IGNORAR_SIEMPRE = ['book1.xlsx']

# Carpetas que no son catalogo y por tanto no se les exige nada de un producto.
# Sin esto, docs/diagramas -que guarda el modelo entidad-relacion- salia como
# "carpeta sin portada", que es un falso positivo de manual.
NO_CATALOGO = ('.git', 'tools', 'docs', '__pycache__', '.scrape', 'node_modules')


def es_catalogo(ruta_abs):
    partes = os.path.relpath(ruta_abs, BASE).split(os.sep)
    return not any(p in NO_CATALOGO for p in partes)


def leer(ruta):
    if not os.path.exists(ruta):
        return None
    return io.open(ruta, encoding='utf-8', errors='replace').read()


src = leer(HTML)
if src is None:
    # Se ejecuta DENTRO de un repositorio de serie, no en DG. Sin index.html
    # no hay repositorio, y seguir adelante recorreria los repos vecinos
    # soltando decenas de avisos que no son de nadie: exactamente el ruido
    # que este archivo existe para evitar.
    print('audit_maestro.py se ejecuta dentro de un repositorio de serie.')
    print('No hay index.html en: %s' % BASE)
    print('')
    print('  cd <repositorio de la serie> && python tools/audit_maestro.py')
    sys.exit(2)


# ---------------------------------------------------------------------------
# 1. ORDEN ESTABLECIDO
# ---------------------------------------------------------------------------
print('=' * 62)
print(' 1. ORDEN ESTABLECIDO')
print('=' * 62)

# --- 1.1 Las 7 categorias, en orden, y solo omisiones permitidas -----------
declaradas = re.findall(r'categoria\s*:\s*[\'"]([a-z]+)[\'"]', src)
orden_html = []
for c in declaradas:
    if c not in orden_html:
        orden_html.append(c)

desconocidas = [c for c in orden_html if c not in CATEGORIAS]
for c in desconocidas:
    flag('ALTO', c, 'categoria que no existe en la arquitectura')

conocidas = [c for c in orden_html if c in CATEGORIAS]
esperado = [c for c in CATEGORIAS if c in conocidas]
if conocidas != esperado:
    flag('ALTO', 'index.html',
         'las categorias no van en el orden de la arquitectura: %s'
         % ' > '.join(conocidas))

for c in OBLIGATORIAS:
    if conocidas and c not in conocidas:
        flag('ALTO', c, 'categoria obligatoria ausente')

print('  categorias declaradas: %s' % (' > '.join(conocidas) or 'ninguna'))

# --- 1.2 subtipo y acabado son campos SEPARADOS ----------------------------
# La arquitectura los separo a proposito: una pieza puede ser Legend Y KiraClear.
if src and 'subtipo' in src and 'acabado' not in src:
    flag('ALTO', 'index.html',
         'hay `subtipo` pero no `acabado`: son dos ejes, no uno')

# `variants` murio con la reestructuracion: cada acabado es su propia fila.
if re.search(r'\bvariants\s*:', src):
    flag('ALTO', 'index.html',
         '`variants` ya no existe: cada acabado es una fila propia')

# --- 1.2b `entrega` declarada y valida en cada producto --------------------
# Sin este campo no se sabe si una caja garantiza lo que lista o es una
# loteria, y de eso dependen el texto de la tarjeta Y la deduccion de
# cobertura. Antes se deducia de la categoria; ahora lo declara el producto.
ENTREGAS = ('garantizada', 'incierta', 'identificada')

# (?<!\.) descarta "objeto.title:" -un acceso de propiedad dentro de un
# ternario compacto (fuente?fuente.title:"") se lee igual que la clave de un
# producto si no se excluye. Sin esto un ternario de estilo apretado en
# cualquier parte del archivo infla el conteo en uno y dispara un ALTO falso.
n_prod = len(re.findall(r'(?<!\.)\btitle\s*:', src))
entregas = re.findall(r'(?<!\.)\bentrega\s*:\s*[\'"](\w+)[\'"]', src)

for e in set(entregas):
    if e not in ENTREGAS:
        flag('ALTO', 'entrega:"%s"' % e,
             'valor invalido; usa garantizada|incierta|identificada')

if n_prod and len(entregas) < n_prod:
    flag('ALTO', 'PRODUCTS',
         '%d producto(s) sin declarar `entrega`' % (n_prod - len(entregas)))

if 'identificada' in entregas:
    flag('MEDIO', 'entrega:"identificada"',
         'la caja dice que pieza trae: deberia partirse en N productos')

print('  productos: %d, con `entrega` declarada: %d' % (n_prod, len(entregas)))

# --- 1.3 El registro de procedencias manda ---------------------------------
# `canal` NO es un campo del registro ni una capa de disco: la procedencia
# cuelga directa de la categoria (Maestro 1 §4) y directa de la raiz del
# repositorio (Maestro 2 §10). No hay envoltorio "1-FIGURA/..." en ningun
# lado; que no aparezca uno en disco se comprueba aparte en 2.1.
#
# Acotado al bloque PROCEDENCIAS = { ... }: un regex sin acotar sobre "algo: {
# label: ..." engancharia cualquier objeto del HTML que tenga esa forma.
def _leer_registro(constante):
    # `};` cierra tanto el formato multilinea como el de una sola linea -no se
    # puede exigir salto de linea antes de la llave-. Fallo real: con \n\}
    # como cierre, un registro compacto de una linea no encontraba su propio
    # final y el regex seguia leyendo hasta el `};` del SIGUIENTE bloque,
    # arrastrando entradas ajenas (paso de gimmick=2 reales a gimmick=8).
    m = re.search(constante + r'\s*=\s*\{(.*?)\};', src, re.S)
    if not m:
        return {}
    # La clave puede ir con o sin comillas -"taf": o taf:- ambas son JS valido.
    return dict(re.findall(
        r'[\'"]?([\w-]+)[\'"]?\s*:\s*\{\s*label\s*:\s*[\'"]([^\'"]*)[\'"]',
        m.group(1)))


# Dos registros de procedencia, deliberadamente separados (Maestro 1 §5.1):
# PROCEDENCIAS es del catalogo central (linea comercial fina); PROCEDENCIAS_
# GIMMICK es de la barra lateral (canal grueso: DX/SG/GP). Una procedencia
# usada solo tiene que existir en UNO de los dos, segun donde se use.
registro = _leer_registro('PROCEDENCIAS')
registro_gimmick = _leer_registro('PROCEDENCIAS_GIMMICK')
registro_unificado = {**registro, **registro_gimmick}

# Si hay procedencias EN USO pero los dos registros salieron vacios, es mas
# probable un fallo de parseo que un repositorio sin registro: avisar en vez
# de callar.
if not registro_unificado and re.search(r'procedencia\s*:\s*[\'"][\w-]+[\'"]', src):
    flag('MEDIO', 'PROCEDENCIAS',
         'no se pudo leer ningun registro pero hay procedencias en uso: revisar formato')

if ' ' in ''.join(registro.keys()):
    flag('ALTO', 'PROCEDENCIAS', 'una clave lleva espacios: hace de clase CSS')

usadas = set(re.findall(r'procedencia\s*:\s*[\'"]([\w-]+)[\'"]', src))
for u in sorted(usadas):
    if registro_unificado and u not in registro_unificado:
        flag('ALTO', u, 'procedencia usada que no esta en ningun registro')

print('  procedencias: catalogo=%d, gimmick=%d, usadas=%d'
      % (len(registro), len(registro_gimmick), len(usadas)))

# --- 1.4 Nomenclatura: la categoria no lleva el nombre del gimmick ---------
# El gimmick cambia cada ano; el tipo de caja no. Se compara contra el nombre
# del gimmick declarado, no contra una lista cerrada.
gim = re.search(r'gimmick\s*:\s*\{[^}]*label\s*:\s*[\'"]([^\'"]+)[\'"]', src)
if gim:
    nombre_gim = gim.group(1).strip().upper()
    for carpeta in os.listdir(BASE) if os.path.isdir(BASE) else []:
        if nombre_gim and nombre_gim in carpeta.upper() \
                and 'PROMOCIONAL' not in carpeta.upper():
            flag('MEDIO', carpeta,
                 'la categoria lleva el nombre del gimmick: usa <LINEA> RANDOM BOX')

# --- 1.5 TCG fuera del catalogo -------------------------------------------
# OJO: el discriminador es QUE ENTREGA, no como se llama.
#
# Una promocion puede USAR cromos para repartir una pieza del gimmick -un
# "Scratch Carddass" que entrega un Ride Eggs dorado- y eso es catalogo de pleno
# derecho, no TCG. Lo que sale del catalogo es el producto cuyo contenido SON
# las cartas de una linea de cromos.
#
# Una primera version buscaba CARDDASS|GANBARI|TCG en el titulo y marcaba esa
# promocion como TCG. Falso positivo, y de los caros: habria borrado una pieza
# real del catalogo. Por eso ahora solo se mira el producto que ademas NO
# entrega nada.
for m in re.finditer(
        r'\{[^{}]*?title\s*:\s*[\'"]([^\'"]*(?:CARDDASS|GANBARI|TCG)[^\'"]*)[\'"](.*?)\}',
        src, re.S | re.I):
    titulo, cuerpo = m.group(1), m.group(2)
    cont = re.search(r'contains\s*:\s*\[([^\]]*)\]', cuerpo)
    entrega_algo = bool(cont and cont.group(1).strip())
    if not entrega_algo:
        flag('ALTO', titulo[:52],
             'parece una linea de cromos y no entrega ninguna pieza: revisa si es TCG')

# --- 1.5b Gimmicks es estricta (Maestro 1 §3.2) ----------------------------
# No se puede verificar por DATO -eso exigiria re-implementar categoriasDe()
# aqui y arriesgar otro falso positivo del dia de hoy-. Se comprueba que el
# CODIGO trae el salvavidas: la funcion que decide donde se pinta una tarjeta
# debe retirar "gimmick" cuando hay mezcla, y la que decide si se puede marcar
# NO debe pasar por ese filtro. Sin esto, un driver con gimmick de regalo se
# duplicaria en Eggs, o peor, perderia su selector de estado.
if 'categoriasDe' in src:
    m_fn = re.search(r'function\s+categoriasDe\s*\([^)]*\)\s*\{(.*?)\n\}', src, re.S)
    if m_fn and 'delete("gimmick")' not in m_fn.group(1) and "delete('gimmick')" not in m_fn.group(1):
        flag('ALTO', 'categoriasDe',
             'no retira gimmick cuando hay mezcla: se duplicaria en Eggs (Maestro 1 §3.2)')
    m_int = re.search(r'(?:const|function)\s+esInteractivo\b.*?\n\n', src, re.S)
    if m_int and 'categoriasDe(' in m_int.group(0):
        flag('MEDIO', 'esInteractivo',
             'depende de categoriasDe(): un producto mixto perderia su selector de estado')

# --- 1.6 Extras no lleva barra de progreso --------------------------------
if re.search(r'extra[^\n]{0,80}(barra|progress|pct)', src, re.I):
    flag('MEDIO', 'Extras', 'no debe llevar barra: el total es desconocido')

# --- 1.7 Clave de estado propia -------------------------------------------
clave = re.search(r'[\'"]([\w-]+)-catalog-v\d+[\'"]', src)
if not clave:
    flag('ALTO', 'localStorage',
         'sin clave `<serie>-catalog-v1`: dos catalogos se pisarian')
else:
    print('  clave de estado: %s-catalog-v1' % clave.group(1))


# ---------------------------------------------------------------------------
# 2. INTEGRIDAD
# ---------------------------------------------------------------------------
print('')
print('=' * 62)
print(' 2. INTEGRIDAD')
print('=' * 62)

raiz = sorted(d for d in os.listdir(BASE)
              if os.path.isdir(os.path.join(BASE, d)) and not d.startswith('.')
              and d not in ('tools', 'docs', '__pycache__'))

# --- 2.1 Las carpetas de la raiz son CATEGORIAS, igual que la pagina -------
# Estructura: <CATEGORIA>/<PROCEDENCIA>/<PRODUCTO>/ (Maestro 1 §4). La
# categoria de cada producto es la que calcula categoriasDe() -la de sus
# piezas, con gimmick retirado si hay mezcla (Maestro 1 §3.2)-, nunca la
# procedencia. Ni la categoria ni la procedencia llevan prefijo numerico: eso
# fue el canal, y ya no existe en ningun nivel (ni render, ni disco).
CATEGORIA_FOLDER = {'PROTAGONISTA', 'DISPOSITIVO', 'MECHA', 'ARMA', 'GIMMICK',
                     'APARICION', 'EXTRA'}
for d in raiz:
    if re.match(r'^\d+-', d):
        flag('ALTO', d + '/',
             'prefijo numerico en la raiz: eso era el canal, ya no existe en ningun nivel')
    elif d.upper() not in CATEGORIA_FOLDER:
        flag('MEDIO', d + '/',
             'no es una de las 7 categorias: revisa si deberia colgar de una')

# --- 2.3 Ningun nombre termina en punto ------------------------------------
# El sistema local se lo come en silencio; la ruta da 404 publicada.
for dirpath, dirnames, filenames in os.walk(BASE):
    if not es_catalogo(dirpath):
        continue
    for nombre in dirnames:
        if nombre.rstrip().endswith('.'):
            rel = os.path.relpath(os.path.join(dirpath, nombre), BASE)
            flag('ALTO', rel, 'el nombre termina en punto: dara 404 publicada')

# --- 2.4 FICHA solo donde hace falta ---------------------------------------
for dirpath, dirnames, filenames in os.walk(BASE):
    if not es_catalogo(dirpath):
        continue
    if os.path.basename(dirpath).upper() == 'FICHA':
        padre = os.path.basename(os.path.dirname(dirpath)).upper()
        if not any(p in padre for p in FICHA_PERMITIDA_EN):
            rel = os.path.relpath(dirpath, BASE)
            flag('MEDIO', rel, 'FICHA/ solo se conserva en SO-DO y YU-DO')

# --- 2.5 Numeracion: la caja es 00, las fotos desde 01 ---------------------
# No se exige que exista el 00: no todos los productos tienen foto de paquete
# publicada. Lo que se exige es que haya alguna imagen numerada, porque la
# portada es "el numero mas bajo" y sin numeros no hay portada.
for dirpath, dirnames, filenames in os.walk(BASE):
    if not es_catalogo(dirpath) or os.path.basename(dirpath).upper() == 'FICHA':
        continue
    imgs = [f for f in filenames if f.lower().endswith(('.jpg', '.jpeg', '.png'))]
    if not imgs or dirnames:
        continue
    rel = os.path.relpath(dirpath, BASE)
    stems = [f.rsplit('.', 1)[0] for f in imgs]
    # NO se exige que haya imagenes numeradas. Una carpeta cuyas imagenes son
    # todas nombres descriptivos es una carpeta de PRODUCTOS SUELTOS -los de una
    # sola imagen, sin subcarpeta-, que es estructura legitima. Distinguirla de
    # un producto mal numerado no se puede hacer solo mirando el disco: de eso
    # se encarga audit.py, que si conoce el inventario. Aqui gritaria sobre las
    # categorias de promocionales en todas las series.
    viejos = [s for s in stems if s.upper() == 'PACKAGE']
    if viejos:
        flag('ALTO', rel, 'queda un PACKAGE: la caja se guarda como 00')

# --- 2.6 Herramientas sin modificar ----------------------------------------
# La copia canonica vive en DG. Editar un clonado reabre la deriva.
CANON = os.path.join(os.path.dirname(BASE), 'tools')
mios = os.path.join(BASE, 'tools')
if os.path.isdir(CANON) and os.path.isdir(mios) \
        and os.path.abspath(CANON) != os.path.abspath(mios):
    for f in sorted(os.listdir(CANON)):
        if not f.endswith('.py'):
            continue
        a, b = os.path.join(CANON, f), os.path.join(mios, f)
        if not os.path.exists(b):
            flag('MEDIO', 'tools/' + f, 'herramienta canonica que falta')
            continue
        ha = hashlib.md5(open(a, 'rb').read()).hexdigest()
        hb = hashlib.md5(open(b, 'rb').read()).hexdigest()
        if ha != hb:
            flag('MEDIO', 'tools/' + f,
                 'editada en su sitio: clona la canonica y usa serie.py')

# --- 2.7 serie.py existe ---------------------------------------------------
if not os.path.exists(SERIE):
    flag('MEDIO', 'serie.py',
         'no existe: los datos de serie no deben vivir dentro de tools/')


# ---------------------------------------------------------------------------
# INFORME
# ---------------------------------------------------------------------------
print('')
print('=' * 62)
print(' INFORME')
print('=' * 62)

orden_sev = {'ALTO': 0, 'MEDIO': 1, 'BAJO': 2}
problemas.sort(key=lambda p: (orden_sev[p[0]], p[1]))

if not problemas:
    print('  Sin incidencias. El repositorio respeta la arquitectura.')
else:
    for sev, donde, motivo in problemas:
        print('  [%-5s] %-44s %s' % (sev, donde[:44], motivo))
    print('')
    print('  %d incidencias (ALTO=%d MEDIO=%d BAJO=%d)' % (
        len(problemas),
        sum(1 for p in problemas if p[0] == 'ALTO'),
        sum(1 for p in problemas if p[0] == 'MEDIO'),
        sum(1 for p in problemas if p[0] == 'BAJO')))

print('')
print('  Recordatorio: cuando la auditoria avisa, la primera pregunta es si el')
print('  aviso es cierto. Un falso positivo se corrige AQUI, no en el catalogo.')

sys.exit(1 if any(p[0] == 'ALTO' for p in problemas) else 0)
