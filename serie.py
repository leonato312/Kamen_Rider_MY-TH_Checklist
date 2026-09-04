# -*- coding: utf-8 -*-
"""Kamen Rider Myth — datos propios de la serie.

ES EL UNICO ARCHIVO PROPIO DEL REPOSITORIO. Todo lo de `tools/` es motor clonado
de DG y no se edita en su sitio; audit_maestro.py lo comprueba por hash.

Este es el repositorio PUBLICADO. La arquitectura -catalogo central + barra
lateral, dos superficies- se probo primero en un build de validacion aparte
(Kamen-Rider_Myth_Checklist, local, no publicado) leyendo unicamente
MAESTRO-1/2/3 y las tools canonicas de DG; una vez verificada con las tres
auditorias limpias, se trajo aqui.

Pivote de enciclopedia (2026-09-02): el catalogo central abandona el
calendario de waves -no escala a franquicias con decadas de trasfondo, como
otros riders o sentai- por navegacion categoria > procedencia > divisor. La
caja de nuevos lanzamientos (Maestro 1 §7) sustituye al calendario para lo que
llegue tras el cierre.

Con el pivote se probo tambien ampliar el marcado a las 7 categorias (un
unico motor, PIEZAS_CATALOG + piezaEstado, sin reglas especiales por
categoria) y se revirtio el mismo dia: en produccion, con visitantes reales,
anadia una pestaña y un contador por cada Rider/Driver/Arma sin que nadie
fuera a "completarlos" como coleccion -solo volvia mas engorrosos el panel y
el catalogo. Solo Gimmicks vuelve a ser interactivo (Maestro 1 §1, §3).
"""

# ---------------------------------------------------------------- IDENTIDAD
FRANQUICIA = 'Kamen Rider'
SERIE = 'Myth'

# EXCEPCION DECLARADA (Maestro 3 §10). La convencion pide
# 'Kamen-Rider_Myth_Checklist' / 'myth-catalog-v1' -y asi se llamo el build de
# validacion-, pero este repositorio se publico antes de los maestros, la web
# esta en linea y compartida, y ya tiene visitantes con checklist guardada.
# Renombrar el repo deja la direccion vieja en 404; cambiar la clave no da
# error, deja la pagina en blanco con lo marcado inaccesible. Ninguna de las
# dos se toca.
REPO = 'Kamen_Rider_MY-TH_Checklist'
CLAVE_ESTADO = 'krmyth-catalog-v1'

# Serie en emision; sigue recibiendo waves.
ESTADO = 'abierto'


# --------------------------------------------------------------- CATEGORIAS
# 'mecha' se omite: Myth no tiene mechas. Solo Gimmicks es interactiva
# (Maestro 1 §3) — el resto es catalogo de consulta.
ROTULOS = {
    'protagonista': 'Riders',
    'dispositivo':  'Drivers',
    'arma':         'Armas',
    'gimmick':      'Eggs',
    'aparicion':    'Apariciones',
    'extra':        'Extras',
}

# Los dos huecos de la jerarquia masivo/menor (Maestro 1 §5.2). El maestro y
# esta plantilla nunca los nombran con el sustantivo de una serie: 'gimmick1'
# y 'gimmick2' son los huecos genericos, y aqui se traducen a los nombres
# reales de Myth. Una serie sin gimmick menor solo declara 'gimmick1'.
GIMMICKS = {
    'gimmick1': 'Eggs',      # masivo — Ride/Seed Eggs, lineas DX y SG
    'gimmick2': 'Buckles',   # menor  — Bone Buckles
}


# ------------------------------------------------------------------ IMAGENES
# id de producto -> carpeta relativa, desde la raiz del repositorio.
# Estructura: <CATEGORIA>/<PROCEDENCIA>/<NOMBRE DEL PRODUCTO>/ — igual que la
# pagina (Maestro 1 §4). La categoria es la que calcula categoriasDe(): la del
# producto tras retirar 'gimmick' si hay mezcla (Maestro 1 §3.2). Un producto
# con alsoIn (Ridewatter) vive en UNA sola carpeta -la de su categoria real-;
# la seccion extra donde tambien aparece solo apunta a esa misma ruta.
CARPETA = {
    # ---- TAF
    'taf-myth':   'PROTAGONISTA/TAF/TAF KAMEN RIDER MY-TH',
    'taf-maou':   'PROTAGONISTA/TAF/TAF KAMEN RIDER MAOU',
    'taf-datt':   'PROTAGONISTA/TAF/TAF KAMEN RIDER DATT',
    'taf-rid':    'PROTAGONISTA/TAF/TAF KAMEN RIDER RID',
    'taf-jao':    'PROTAGONISTA/TAF/TAF KAMEN RIDER JAO',
    'taf-vanken': 'PROTAGONISTA/TAF/TAF KAMEN RIDER VANKEN',
    'taf-muton':  'PROTAGONISTA/TAF/TAF KAMEN RIDER MUTON',

    # ---- SOFT VINYL
    'sv-myth':  'PROTAGONISTA/SOFT VINYL/RIDER HERO SERIES KAMEN RIDER MY-TH',
    'sv-maou':  'PROTAGONISTA/SOFT VINYL/RIDER HERO SERIES KAMEN RIDER MAOU',
    'sv-datt':  'PROTAGONISTA/SOFT VINYL/RIDER HERO SERIES KAMEN RIDER DATT',
    'sv-rid':   'PROTAGONISTA/SOFT VINYL/RIDER HERO SERIES KAMEN RIDER RID',
    'sv-jao':   'PROTAGONISTA/SOFT VINYL/RIDER HERO SERIES KAMEN RIDER JAO',
    'sv-tigul': 'PROTAGONISTA/SOFT VINYL/RIDER HERO SERIES KAMEN RIDER TIGUL',

    # ---- SO-DO
    'sg-sodo-myth': 'PROTAGONISTA/SO-DO/SO-DO MY-TH',
    'sg-sodo-maou': 'PROTAGONISTA/SO-DO/SO-DO MAOU',
    'sg-sodo-datt': 'PROTAGONISTA/SO-DO/SO-DO DATT',
    'sg-sodo-rid':  'PROTAGONISTA/SO-DO/SO-DO RID',

    # ---- SG MODEL KITS
    'sg-kit-01':
        'DISPOSITIVO/SG MODEL KITS/MY-TH FIRST KIT 01-MYTH DRIVER, RIDE EGGS 1 (NEZUMI)',

    # ---- SG RANDOM BOX
    'sg-random-box-01': 'GIMMICK/SG RANDOM BOX/SG RIDER EGGS RANDOM BOX 01',

    # ---- DX
    'dx-myth-driver':          'DISPOSITIVO/DX/DX MY-TH DRIVER',
    'dx-myth-driver-rid-set':  'DISPOSITIVO/DX/DX MY-TH DRIVER KAMEN RIDER MY-TH & RID SET',
    'dx-myth-driver-narikiri': 'DISPOSITIVO/DX/DX MY-TH DRIVER SPECIAL NARIKIRI SET',
    'dx-myth-edge':            'ARMA/DX/DX MY-TH EDGE',
    'dx-zodiac-weapons-01':    'ARMA/DX/DX TWELVE ZODIAC ALLIANCE RIDER WEAPONS SET 01',
    'dx-rider-eggs-set-01':    'GIMMICK/DX/DX RIDER EGGS SET 01',
    'dx-rider-eggs-set-02':    'GIMMICK/DX/DX RIDER EGGS SET 02',
    'dx-legend-set-00':        'GIMMICK/DX/DX LEGEND RIDER EGGS SET 00',
    'dx-legend-set-01':        'GIMMICK/DX/DX LEGEND RIDER EGGS SET 01',
    'dx-legend-set-02':        'GIMMICK/DX/DX LEGEND RIDER EGGS SET 02',
    'dx-expack':               'DISPOSITIVO/DX/DX EXPACK',
    'dx-ridewatter-eggs':      'GIMMICK/DX/DX RIDEWATTER EGGS',
    'dx-hokokuro':             'DISPOSITIVO/DX/DX HOKOKURO',
    'dx-myth-phone':           'DISPOSITIVO/DX/DX MY-TH PHONE',

    # ---- DX RANDOM BOX
    'dx-random-box-01': 'GIMMICK/DX RANDOM BOX/DX RIDER EGGS RANDOM BOX 01',
    'dx-random-box-02': 'GIMMICK/DX RANDOM BOX/DX RIDER EGGS RANDOM BOX 02',

    # ---- BONE BUCKLES
    'dx-hammer-bone-buckle':
        'GIMMICK/BONE BUCKLES/DX HAMMER BONE BUCKLE',
    'dx-slashbone-buckle':
        'GIMMICK/BONE BUCKLES/DX SLASHBONE BUCKLE & RIDE EGGS 4 SET',
    'dx-bite-bone-buckle':
        'GIMMICK/BONE BUCKLES/DX BITE BONE BUCKLE & RIDE EGGS 6 SET',
    'dx-shot-bone-buckle':
        'GIMMICK/BONE BUCKLES/DX SHOT BONE BUCKLE & RIDE EGGS 10 SET',
}

# id -> archivo suelto, para productos de UNA sola imagen sin subcarpeta.
SUELTO = {
    'sg-kit-02':
        'DISPOSITIVO/SG MODEL KITS/MY-TH FIRST KIT 02-MYTH DRIVER HAMMER ON, RIDE EGGS 1 (NEKO).jpg',
    'sg-kit-03':
        'PROTAGONISTA/SG MODEL KITS/MY-TH FIRST KIT 03-KAMEN RIDER MYTH, RIDEWATTER.jpg',
    'sg-kit-04':
        'PROTAGONISTA/SG MODEL KITS/MY-TH FIRST KIT 04-KAMEN RIDER RID, RIDE EGGS 1 (NEZUMI Y NEKO).jpg',

    'promo-store-tokyo':
        'GIMMICK/PROMOCIONALES/DX RIDER EGGS KAMEN RIDER STORE TOKYO SET-Myth Seed Eggs (Kamen Rider Store Tokyo ver.), Hato Seed Eggs.jpeg',
    'promo-store-nagoya':
        'GIMMICK/PROMOCIONALES/DX RIDER EGGS KAMEN RIDER STORE NAGOYA SET-Myth Seed Eggs (Kamen Rider Store Nagoya ver.), Koala Seed Eggs.jpeg',
    'promo-scratch':
        'GIMMICK/PROMOCIONALES/SCRATCH CARDDASS-Ride Eggs 1 (Gold ver.).jpeg',
    'promo-televi-kun':
        'GIMMICK/PROMOCIONALES/TELEVI-KUN-Ride Eggs 1 (Special ver.).jpeg',
}

# Productos cuya portada salta el 00 (la caja) y usa el 01.
PORTADA_01 = [
    'sg-sodo-myth', 'sg-sodo-maou', 'sg-sodo-datt', 'sg-sodo-rid',
    'dx-random-box-01', 'dx-random-box-02', 'sg-random-box-01',
]


# ------------------------------------------------------------------- PALETA
# Myth tiene DOS gimmicks: el masivo -Ride Eggs- llega por DX y SG, cada una
# con su contador (los dos tonos fuertes); el menor -Bone Buckles- va en rosa.
PALETA = {
    'gimmick':      '#f0b429',   # DX  — fuerte
    'gimmick_alt':  '#35d0d8',   # SG  — fuerte
    'gimmick_menor':'#ff8fab',   # Bone Buckles
    'protagonista': '#7ee0c2',
    'dispositivo':  '#e8c26a',
    'arma':         '#d98cf0',
    'aparicion':    '#9b8fb0',
    'extra':        '#8a8a8a',
}


# ------------------------------------------------------------- PROCEDENCIAS
# Catalogo central. El registro de Gimmicks (barra lateral) es OTRO, mas
# grueso -DX/SG-, definido dentro del propio index.html (Maestro 1 §5.1).
PROCEDENCIAS_USADAS = [
    'taf', 'sofv',
    'sodo', 'sg-kit', 'sg-random',
    'dx', 'dx-random', 'buckles',
    'promo',
]
