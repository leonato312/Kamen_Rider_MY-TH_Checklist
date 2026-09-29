# -*- coding: utf-8 -*-
"""Auditoria del catalogo. SOLO LECTURA: no modifica nada.

Union de las cuatro variantes que existian en las series, adaptada al modelo
nuevo (categoria / procedencia / subtipo / acabado, sin `variants`).

Que comprueba, por orden de importancia:

  1. Que index.html y el disco digan lo mismo. Es lo unico que puede romper el
     sitio publicado, asi que va primero.
  2. Integridad del catalogo de piezas: referencias huerfanas, piezas que
     ningun producto trae, ids duplicados, subtipos y acabados sin etiqueta.
  3. Portada y numeracion de cada producto.
  4. El arbol de `reemplaza`, resuelto en cadena, con ciclos e ids inexistentes.
  4b. Cobertura DEDUCIDA comparando contenidos, para no fiarse de lo declarado.
  5. Nomenclatura.

Que NO comprueba: el contenido de FICHA/. Es material de consulta, de formato
libre; una hoja puede cubrir una coleccion entera. Exigirle un nombre por
producto solo generaba ruido.
Tampoco comprueba la arquitectura -las 7 categorias, el registro de
procedencias, los rastros del sistema viejo-: de eso se encarga audit_maestro.py.

UNA AUDITORIA CON FALSOS POSITIVOS ES PEOR QUE NINGUNA. Tres que daba una
version antigua y aqui no se dan:
  · La carpeta espejo de un producto cruzado (`alsoIn`) no se marca como
    "carpeta que el HTML no referencia": es espejo a proposito.
  · Los productos de una sola imagen, sueltos en su procedencia, se reconocen
    como productos y no como archivos perdidos.
  · Los .webp derivados no se cuentan como fotos: contarlos inventaba huecos de
    numeracion en todos los productos.
"""
import io
import os
import re
import sys

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HTML      = os.path.join(BASE, 'index.html')
FICHA_DIR = 'FICHA'
IMG_EXT   = ('.jpg', '.jpeg', '.png')     # solo originales; los .webp derivan
OMITIR    = ('tools', 'docs', '__pycache__')

if not os.path.exists(HTML):
    print('No hay index.html en %s' % BASE)
    sys.exit(2)

s_html = io.open(HTML, encoding='utf-8').read()

problemas = []


def flag(sev, ruta, motivo):
    problemas.append((sev, ruta, motivo))


def orden(nombre):
    """00 (la caja), 01, 02... Orden puramente numerico."""
    stem = os.path.splitext(nombre)[0]
    return (0, int(stem)) if stem.isdigit() else (1, 0)


def archivos_de_producto(carpeta):
    """Los archivos de galeria de un producto, sea cual sea el punto del ciclo
    de vida en el que este.

    Dos estados legitimos, y hay que reconocer los dos:
      · A medio migrar: originales (.jpg/.png) Y sus .webp derivados conviven.
        Se cuenta por los ORIGINALES -son la fuente real- para no duplicar
        cada numero.
      · Publicado (Maestro 3 §21): el repo de trabajo solo tiene .webp, los
        originales viven en el espejo *_ORIGINALES aparte. Sin este caso,
        toda carpeta de un repositorio ya migrado sale "vacia" -asi se
        encontro, en la primera auditoria de un repo terminado.
    Nunca cuenta los `-thumb.webp`: son la portada reducida, no un numero de
    la galeria.
    """
    todos = os.listdir(carpeta)
    originales = [f for f in todos if f.lower().endswith(IMG_EXT)]
    if originales:
        return sorted(originales, key=orden)
    webp = [f for f in todos
            if f.lower().endswith('.webp') and '-thumb' not in f.lower()]
    return sorted(webp, key=orden)


# ---------------------------------------------------------------- inventario
# Estructura: <CATEGORIA>/<PROCEDENCIA>/<PRODUCTO>/ — igual que la pagina
# (Maestro 1 §4): la carpeta la decide categoriasDe(), no la procedencia sola.
# La MISMA procedencia (p.ej. "DX") aparece legitimamente bajo varias
# categorias -Armas/DX, Dispositivos/DX, Gimmicks/DX-, y eso NO es colision:
# son ramas distintas del arbol, no la misma carpeta repetida.
inv = {}
raiz = sorted(d for d in os.listdir(BASE)
              if os.path.isdir(os.path.join(BASE, d))
              and not d.startswith('.') and d not in OMITIR)

for cat in raiz:
    cdir = os.path.join(BASE, cat)
    for proc in sorted(os.listdir(cdir)):
        pdir = os.path.join(cdir, proc)
        if not os.path.isdir(pdir):
            continue
        clave = '%s/%s' % (cat, proc)
        fp = os.path.join(pdir, FICHA_DIR)
        ficha = len([f for f in os.listdir(fp) if f.lower().endswith(IMG_EXT)]) \
            if os.path.isdir(fp) else 0
        prods, sueltos = {}, []
        for x in sorted(os.listdir(pdir)):
            xp = os.path.join(pdir, x)
            if os.path.isdir(xp) and x != FICHA_DIR:
                prods[x] = archivos_de_producto(xp)
            elif os.path.isfile(xp) and (x.lower().endswith(IMG_EXT) or
                                         (x.lower().endswith('.webp') and
                                          '-thumb' not in x.lower())):
                sueltos.append(x)          # producto de una sola imagen
        inv[clave] = {'ficha': ficha, 'prods': prods, 'sueltos': sueltos}

# ----------------------------------------------------- datos del index.html
titulos, procde, entrega = {}, {}, {}
reemplaza, alsoIn, contiene, componentes, imgde = {}, {}, {}, {}, {}

for m in re.finditer(
        r'\{\s*id:\s*"([a-z0-9-]+)"\s*,\s*title:\s*"([^"]*)"(.*?)contains:\s*\[([^\]]*)\]',
        s_html, re.S):
    pid, tit, cuerpo, cont = m.groups()
    titulos[pid] = tit

    p = re.search(r'procedencia:\s*"([\w-]+)"', cuerpo)
    procde[pid] = p.group(1) if p else ''

    e = re.search(r'entrega:\s*"(\w+)"', cuerpo)
    entrega[pid] = e.group(1) if e else ''

    r = re.search(r'reemplaza:\s*\[([^\]]*)\]', cuerpo)
    reemplaza[pid] = re.findall(r'"([^"]+)"', r.group(1)) if r else []

    a = re.search(r'alsoIn:\s*\[([^\]]*)\]', cuerpo)
    alsoIn[pid] = re.findall(r'"([^"]+)"', a.group(1)) if a else []

    c = re.search(r'componentes:\s*\[([^\]]*)\]', cuerpo)
    if c:
        componentes[pid] = set(re.findall(r'"([^"]+)"', c.group(1)))

    i = re.search(r'img:\s*"([^"]*)"', cuerpo)
    imgde[pid] = i.group(1) if i else ''

    # Sin `variants`, una referencia es el id desnudo. No hay que normalizar.
    contiene[pid] = set(re.findall(r'"([^"]+)"', cont))

# Piezas. El lookahead de `name:` separa una pieza de cualquier objeto anidado.
#
# El array TIENE que llamarse PIEZAS_CATALOG. Si no aparece, todas las
# referencias de `contains` salen huerfanas de golpe -una ALTO por pieza- y el
# informe no dice por que. Un nombre distinto es un fallo de una linea que se
# lee como un catalogo roto entero, asi que se avisa aparte y se para.
piezas = {}
if 'PIEZAS_CATALOG' not in s_html:
    flag('ALTO', 'index.html',
         'no encuentro el array PIEZAS_CATALOG: el catalogo de piezas tiene que '
         'llamarse asi. Sin el, cada `contains` parece una referencia huerfana')
m_pz = re.search(r'const\s+PIEZAS_CATALOG\s*=\s*\[', s_html)
if m_pz:
    ini = m_pz.end()
    # Ancla en la DECLARACION, no en la palabra suelta: un comentario que
    # mencione "PIEZAS_CATALOG y PRODUCTS" en prosa (p.ej. la cabecera del
    # archivo explicando donde editar) engancha el .index() ingenuo mucho
    # antes del array real y deja `bloque` vacio. Fallo real, encontrado
    # auditando el primer repositorio migrado.
    m_prod = re.search(r'const\s+PRODUCTS\s*=\s*\[', s_html[ini:])
    fin = ini + m_prod.start() if m_prod else len(s_html)
    bloque = s_html[ini:fin]
    def campo(cuerpo, n, patron=r'[\w-]+'):
        g = re.search(n + r':\s*"(' + patron + r')"', cuerpo)
        return g.group(1) if g else ''

    for m in re.finditer(r'\{\s*id:\s*"([a-z0-9\'-]+)"\s*,\s*(?=name:)(.*?)\}',
                         bloque, re.S):
        pid, cuerpo = m.groups()
        if pid in piezas:
            flag('ALTO', pid, 'id de pieza duplicado en el catalogo')
        piezas[pid] = {
            'name':        campo(cuerpo, 'name', r'[^"]*'),
            'categoria':   campo(cuerpo, 'categoria'),
            'procedencia': campo(cuerpo, 'procedencia'),
            'subtipo':     campo(cuerpo, 'subtipo'),
            'acabado':     campo(cuerpo, 'acabado'),
        }

def etiquetas(constante):
    """Claves declaradas en un diccionario de rotulos del index.html.

    Devuelve un set vacio si la constante no existe: una serie puede no tener
    acabados, y eso no es un error. Los avisos que dependen de esto se saltan
    solos cuando el set esta vacio -mejor callar que inventar un aviso-.

    Cierre en `};`, no en `\n}`: un registro escrito en una sola linea no
    tiene salto antes de la llave, y exigirlo hace que el regex siga leyendo
    hasta el `};` del SIGUIENTE bloque, arrastrando claves ajenas.

    Solo cuenta como clave lo que abre un objeto propio (`id: { ... }`). Sin
    exigir esa llave de apertura, `label:"..."` o `menor:true` -campos DENTRO
    de cada entrada- se colaban como si fueran subtipos.
    """
    m = re.search(constante + r'\s*=\s*\{(.*?)\};', s_html, re.S)
    return set(re.findall(r'[\'"]?([a-z][\w-]*)[\'"]?\s*:\s*\{', m.group(1))) if m else set()


etiq_subtipo = etiquetas('SUBTIPOS')
etiq_acabado = etiquetas('ACABADOS')

# Carpetas espejo legitimas: las de un producto cruzado.
espejos = set()
for pid, otras in alsoIn.items():
    if imgde.get(pid):
        nombre = imgde[pid].split('/')[-2] if '/' in imgde[pid] else ''
        for o in otras:
            espejos.add('%s/%s' % (o, nombre))


# ===========================================================================
print('=' * 62)
print(' 1. INDEX.HTML  <->  DISCO   (lo unico que puede romper el sitio)')
print('=' * 62)

portadas = re.findall(r'img:\s*"([^"]*)"', s_html)
galerias = re.findall(r'"([^"]+\.(?:webp|jpg|jpeg|png))"',
                      ' '.join(re.findall(r'gallery:\s*\[(.*?)\]', s_html, re.S)))
referenciadas = set(portadas) | set(galerias)

rotas = [p for p in sorted(referenciadas)
         if p and not os.path.exists(os.path.join(BASE, p))]
for p in rotas:
    flag('ALTO', p, 'referenciada en index.html pero no esta en disco')
print('  rutas referenciadas: %d   rotas: %d' % (len(referenciadas), len(rotas)))

# .webp en disco que nadie usa
en_disco = []
for r, d, fs in os.walk(BASE):
    partes = r.upper().split(os.sep)
    if FICHA_DIR in partes or '.GIT' in partes:
        continue
    for f in fs:
        if f.lower().endswith('.webp'):
            en_disco.append(os.path.relpath(os.path.join(r, f), BASE).replace(os.sep, '/'))
sin_usar = [h for h in sorted(en_disco) if h not in referenciadas]
for h in sin_usar:
    flag('MEDIO', h, '.webp en disco que index.html no usa')
print('  .webp en disco: %d   sin usar: %d' % (len(en_disco), len(sin_usar)))
if sin_usar:
    print('     (suele ser el rastro de haber cambiado la portada de un producto)')

# Carpetas con fotos que el HTML ignora
usadas_dir = set(p.rsplit('/', 1)[0] for p in referenciadas if '/' in p)
for clave, datos in sorted(inv.items()):
    for prod in datos['prods']:
        ruta = '%s/%s' % (clave, prod)
        if ruta not in usadas_dir and ruta not in espejos:
            flag('MEDIO', ruta + '/', 'carpeta con fotos que index.html no referencia')

print('')
print('=' * 62)
print(' 2. CATALOGO DE PIEZAS')
print('=' * 62)

todas_ref = set()
for c in contiene.values():
    todas_ref |= c

huerfanas = sorted(x for x in todas_ref if x not in piezas)
for x in huerfanas:
    flag('ALTO', x, 'un producto la declara en `contains` pero no existe en el catalogo')

sin_via = sorted(x for x in piezas if x not in todas_ref)
for x in sin_via:
    flag('MEDIO', x, 'pieza que ningun producto trae: nunca se podra marcar')

## SUBTIPOS/ACABADOS son el registro de rotulos de la BARRA LATERAL, que es
## exclusiva de Gimmicks (Maestro 1 §5). El subtipo de una pieza de otra
## categoria (rider/driver/arma) no necesita entrada ahi: nunca se rotula en
## ese registro, esa pieza vive solo en el catalogo central por producto.
## Sin este filtro, "rider"/"driver"/"arma" salian como huecos falsos.
for pid, d in sorted(piezas.items()):
    if d['categoria'] != 'gimmick':
        continue
    if etiq_subtipo and d['subtipo'] and d['subtipo'] not in etiq_subtipo:
        flag('MEDIO', d['subtipo'], 'subtipo usado por una pieza de gimmick pero sin etiqueta')
    if etiq_acabado and d['acabado'] and d['acabado'] not in etiq_acabado:
        flag('MEDIO', d['acabado'], 'acabado usado por una pieza pero sin etiqueta')

usados_s = set(d['subtipo'] for d in piezas.values()
               if d['subtipo'] and d['categoria']=='gimmick')
for t in sorted(etiq_subtipo - usados_s):
    flag('BAJO', t, 'subtipo declarado que ninguna pieza de gimmick usa: sobra')

print('  piezas: %d   referencias huerfanas: %d   sin via: %d'
      % (len(piezas), len(huerfanas), len(sin_via)))

print('')
print('=' * 62)
print(' 3. PORTADA Y NUMERACION')
print('=' * 62)

for clave, datos in sorted(inv.items()):
    for nombre, files in sorted(datos['prods'].items()):
        ruta = '%s/%s/' % (clave, nombre)
        if not files:
            flag('ALTO', ruta, 'carpeta de producto vacia')
            continue
        stems = [os.path.splitext(f)[0] for f in files]
        nums = sorted(int(s) for s in stems if s.isdigit())
        if not nums:
            flag('ALTO', ruta, 'ninguna imagen numerada: no hay portada')
            continue
        # Los huecos se cuentan desde 01: el 00 es la caja y puede no existir
        # -no todos los productos tienen foto de paquete publicada-.
        faltan = [n for n in range(1, max(nums) + 1) if n not in nums]
        if faltan:
            flag('MEDIO', ruta, 'numeracion con huecos: %s'
                 % ', '.join('%02d' % n for n in faltan))
        no_numeradas = [s for s in stems if not s.isdigit()]
        if no_numeradas:
            flag('MEDIO', ruta, 'imagen sin numerar: %s' % ', '.join(no_numeradas))
        sinpad = [s for s in stems if s.isdigit() and len(s) == 1]
        if sinpad:
            flag('MEDIO', ruta, 'sin cero delante: %s' % ', '.join(sinpad))
n_carpetas = sum(len(d['prods']) for d in inv.values())
print('  productos con carpeta: %d' % n_carpetas)

# Un cero silencioso aqui es peligroso: significa que el disco no tiene la
# forma <CATEGORIA>/<PROCEDENCIA>/<PRODUCTO>/ y esta seccion no ha mirado
# nada. Sin este aviso, un repositorio a medio migrar pasa la auditoria en
# blanco.
if not n_carpetas:
    flag('ALTO', 'estructura de carpetas',
         'ningun producto encontrado: el disco no tiene forma categoria/procedencia/producto')
    print('')
    print('  !! No se ha encontrado NI UN producto. La auditoria no ha mirado')
    print('     nada en esta seccion. Se espera:')
    print('       <CATEGORIA>/<PROCEDENCIA>/<NOMBRE DEL PRODUCTO>/')
    print('     Igual que la pagina: la categoria la decide categoriasDe(),')
    print('     no la procedencia. Sin capa de canal en ningun nivel.')
    print('     Si el repositorio aun no esta migrado, esto es lo esperado.')

print('')
print('=' * 62)
print(' 4. ARBOL DE `reemplaza`')
print('=' * 62)


def rama(pid, nivel, vistos, out):
    for hijo in reemplaza.get(pid, []):
        if hijo in vistos:
            flag('ALTO', hijo, 'ciclo en `reemplaza`')
            continue
        if hijo not in titulos:
            flag('ALTO', pid, '`reemplaza` apunta a "%s", que no existe' % hijo)
            continue
        out.append('    ' + '  ' * nivel + '- ' + titulos[hijo][:56])
        rama(hijo, nivel + 1, vistos | {hijo}, out)


raices = [p for p in sorted(reemplaza) if reemplaza[p]]
for r in raices:
    print('  %s' % titulos[r][:66])
    out = []
    rama(r, 0, {r}, out)
    for l in out:
        print(l)
    print('      cubre %d producto(s) en total' % len(out))
if not raices:
    print('  ningun producto absorbe a otro')

print('')
print('=' * 62)
print(' 4b. COBERTURA DEDUCIDA DE LOS CONTENIDOS')
print('=' * 62)
print('  Compara el contenido real de cada caja en vez de fiarse de lo que')
print('  declaramos. Deducir a ojo que set absorbe a cual fallo dos veces')
print('  seguidas, asi que se comprueba en los dos sentidos.')
print('')
print('  LOS PRODUCTOS CON `entrega:"incierta"` QUEDAN FUERA, en los dos lados.')
print('  Su `contains` son contenidos POSIBLES, no garantizados: una caja')
print('  sorpresa que declara tres piezas te da una, asi que ni cubre a otro')
print('  producto por compartir una, ni la cubre a ella un set que traiga las')
print('  tres. Sin esta salvedad la auditoria encadena ALTO falsos, y una')
print('  auditoria con falsos positivos es peor que ninguna.')
print('')


def total(pid):
    return componentes.get(pid, set()) | contiene.get(pid, set())


def declarado(pid, vistos=None):
    vistos = vistos or set()
    res = set()
    for h in reemplaza.get(pid, []):
        if h in vistos:
            continue
        res.add(h)
        res |= declarado(h, vistos | {h})
    return res


evaluables = sorted(p for p in titulos
                    if total(p) and entrega.get(p) != 'incierta')
avisos = 0
for a in evaluables:
    deducido = set(b for b in evaluables
                   if b != a and total(b) and total(b) < total(a))
    dec = declarado(a)
    for b in sorted(deducido - dec):
        flag('ALTO', titulos[a][:52],
             'contiene todo lo de "%s" pero no lo declara en `reemplaza`' % titulos[b])
        print('  !! %s deberia cubrir a %s' % (titulos[a][:38], titulos[b][:38]))
        avisos += 1
    for b in sorted(dec - deducido):
        if not total(b):
            continue
        flag('ALTO', titulos[a][:52],
             'declara cubrir "%s" pero su contenido no lo incluye' % titulos[b])
        print('  !! %s NO contiene lo de %s' % (titulos[a][:38], titulos[b][:38]))
        avisos += 1
if not avisos:
    print('  La cadena declarada coincide con la deducida de los contenidos.')

print('')
print('=' * 62)
print(' 5. NOMENCLATURA')
print('=' * 62)

for clave, datos in sorted(inv.items()):
    proc = clave.split('/')[-1]
    if proc != proc.upper():
        flag('MEDIO', clave, 'procedencia con minusculas')
    for prod in datos['prods']:
        if prod != prod.upper():
            flag('BAJO', '%s/%s/' % (clave, prod), 'estilo: minusculas en el nombre')
        if prod.rstrip().endswith('.'):
            flag('ALTO', '%s/%s/' % (clave, prod),
                 'el nombre termina en punto: dara 404 publicada')

vistos = {}
for clave, datos in inv.items():
    for f in list(datos['prods']) + list(datos['sueltos']):
        vistos.setdefault(f, []).append(clave)
dups = {k: v for k, v in vistos.items() if len(v) > 1}
if not dups:
    print('  sin nombres repetidos entre procedencias')
for f, cs in sorted(dups.items()):
    esperado = any('%s/%s' % (c, f) in espejos for c in cs)
    if not esperado:
        flag('MEDIO', f[:52],
             'mismo nombre en %s sin ser producto cruzado' % ' y '.join(cs))
    print('  %s en %s  ->  %s' % (f[:40], ' y '.join(cs),
                                  'espejo, correcto' if esperado else 'REVISAR'))

# ===========================================================================
print('')
print('=' * 62)
print(' RESULTADO')
print('=' * 62)

orden_sev = {'ALTO': 0, 'MEDIO': 1, 'BAJO': 2}
problemas.sort(key=lambda p: (orden_sev[p[0]], p[1]))

if not problemas:
    print('  Sin incidencias.')
else:
    for sev, ruta, motivo in problemas:
        print('  [%-5s] %-44s %s' % (sev, ruta[:44], motivo))
    print('')
    print('  %d incidencias (ALTO=%d MEDIO=%d BAJO=%d)' % (
        len(problemas),
        sum(1 for p in problemas if p[0] == 'ALTO'),
        sum(1 for p in problemas if p[0] == 'MEDIO'),
        sum(1 for p in problemas if p[0] == 'BAJO')))

print('')
print('  Cuando la auditoria avisa, la primera pregunta es si el aviso es')
print('  cierto. Un falso positivo se corrige AQUI, no en el catalogo.')

sys.exit(1 if any(p[0] == 'ALTO' for p in problemas) else 0)
