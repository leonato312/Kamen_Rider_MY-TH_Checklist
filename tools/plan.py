# -*- coding: utf-8 -*-
"""Construye el plan: portada + galeria de cada producto. Modo simulacro."""
import io, os, re, json

import os as _os
BASE = _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))
HTML = os.path.join(BASE, u'index.html')

# El Ridewatter sale de su categoria primaria (DX SETS), aunque tenga
# carpeta espejo en TAF por ser producto puente.
CARPETA = {
 'dx-myth-edge':            u'ARMAS/DX MY-TH EDGE',
 'dx-zodiac-weapons-01':    u'ARMAS/DX TWELVE ZODIAC ALLIANCE RIDER WEAPONS SET 01',
 'dx-bite-bone-buckle':     u'BUCKLES SETS/DX BITE BONE BUCKLE & Ride Ex 6 SET',
 'dx-hammer-bone-buckle':   u'BUCKLES SETS/DX HAMMER BONE BUCKLE',
 'dx-shot-bone-buckle':     u'BUCKLES SETS/DX SHOT BONE BUCKLE & Ride Ex 10 SET',
 'dx-slashbone-buckle':     u'BUCKLES SETS/DX SLASHBONE BUCKLE & Ride Ex 4 SET',
 'dx-myth-driver':          u'DX DRIVERS/DX MY-TH DRIVER',
 'dx-myth-driver-rid-set':  u'DX DRIVERS/DX MY-TH DRIVER KAMEN RIDER MY-TH & RID SET',
 'dx-myth-driver-narikiri': u'DX DRIVERS/DX MY-TH DRIVER SPECIAL NARIKIRI SET',
 'dx-random-box-01':        u'DX RANDOM BOX/DX RIDER EX RANDOM BOX 01',
 'dx-random-box-02':        u'DX RANDOM BOX/DX RIDER EX RANDOM BOX 02',
 'dx-expack':               u'DX SETS/DX EXPACK',
 'dx-hokokuro':             u'DX SETS/DX HOKOKURO',
 'dx-legend-set-00':        u'DX SETS/DX LEGEND RIDER EX SET 00',
 'dx-legend-set-01':        u'DX SETS/DX LEGEND RIDER EX SET 01',
 'dx-legend-set-02':        u'DX SETS/DX LEGEND RIDER EX SET 02',
 'dx-myth-phone':           u'DX SETS/DX MY-TH PHONE',
 'dx-rider-ex-set-01':      u'DX SETS/DX RIDER EX SET 01',
 'dx-rider-ex-set-02':      u'DX SETS/DX RIDER EX SET 02',
 'dx-ridewatter-ex':        u'DX SETS/DX Ridewatter Ex',
 'sg-random-box-01':        u'SG RANDOM BOX/SG RIDER EX RANDOM BOX 01',
 'sv-datt':                 u'SOFT VINYL/RIDER HERO SERIES KAMEN RIDER DATT',
 'sv-jao':                  u'SOFT VINYL/RIDER HERO SERIES KAMEN RIDER JAO',
 'sv-mao':                  u'SOFT VINYL/RIDER HERO SERIES KAMEN RIDER MAO',
 'sv-myth':                 u'SOFT VINYL/RIDER HERO SERIES KAMEN RIDER MYTH',
 'sv-rido':                 u'SOFT VINYL/RIDER HERO SERIES KAMEN RIDER RIDO',
 'sv-tigul':                u'SOFT VINYL/RIDER HERO SERIES KAMEN RIDER TIGUL',
 'taf-datt':                u'TAF/TAF KAMEN RIDER DATT',
 'taf-jao':                 u'TAF/TAF KAMEN RIDER JAO',
 'taf-mao':                 u'TAF/TAF KAMEN RIDER MAO',
 'taf-muton':               u'TAF/TAF KAMEN RIDER MUTON',
 'taf-myth':                u'TAF/TAF KAMEN RIDER MYTH',
 'taf-rido':                u'TAF/TAF KAMEN RIDER RIDO',
 'taf-vanken':              u'TAF/TAF KAMEN RIDER VANKEN',
}

def orden(nombre):
    """PACKAGE primero, luego 01, 02, 03..."""
    stem = os.path.splitext(nombre)[0]
    if stem.upper() == u'PACKAGE':
        return (0, 0)
    return (1, int(stem)) if stem.isdigit() else (2, 0)

def plan():
    filas = []
    for pid, carpeta in sorted(CARPETA.items()):
        full = os.path.join(BASE, carpeta)
        if not os.path.isdir(full):
            filas.append((pid, carpeta, None, [], u'CARPETA NO EXISTE'))
            continue
        files = [f for f in os.listdir(full)
                 if f.lower().endswith(('.jpg', '.jpeg', '.png', '.webp'))]
        files.sort(key=orden)
        if not files:
            filas.append((pid, carpeta, None, [], u'VACIA'))
            continue
        filas.append((pid, carpeta, files[0], files, u''))
    return filas

if __name__ == '__main__':
    filas = plan()
    print(u'%-26s %-46s %-11s %s' % (u'PRODUCTO', u'CARPETA', u'PORTADA', u'GALERIA'))
    print(u'-' * 104)
    pkg = uno = 0
    total_img = 0
    for pid, carpeta, portada, files, err in filas:
        if err:
            print(u'%-26s %-46s  !! %s' % (pid, carpeta[:46], err))
            continue
        if portada.upper().startswith(u'PACKAGE'):
            pkg += 1
        else:
            uno += 1
        total_img += len(files)
        print(u'%-26s %-46s %-11s %d img  (%s)'
              % (pid, carpeta[:46], portada, len(files),
                 u', '.join(os.path.splitext(f)[0] for f in files[:6])
                 + (u'...' if len(files) > 6 else u'')))
    print(u'-' * 104)
    print(u'%d productos   portada PACKAGE: %d   portada 01: %d   imagenes en galerias: %d'
          % (len(filas), pkg, uno, total_img))

    # Peso actual de las portadas (lo que hoy se descargaria al abrir)
    peso = 0
    for pid, carpeta, portada, files, err in filas:
        if portada:
            peso += os.path.getsize(os.path.join(BASE, carpeta, portada))
    print(u'Peso de las 34 portadas hoy (JPG): %.1f MB  ->  se convertiran a WebP'
          % (peso / 1048576.0))
