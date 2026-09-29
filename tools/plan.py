# -*- coding: utf-8 -*-
"""Construye el plan de imagenes: portada + galeria de cada producto.

SOLO LECTURA. Correr esto antes de build_all para ver que saldria.

MOTOR. No contiene ni un dato de serie: el mapa de carpetas vive en serie.py,
en la raiz del repositorio. Antes iba incrustado aqui y era la causa de que
este script divergiera en las cinco series -206 lineas de datos contra 40 de
logica-, ademas del paso que mas se olvidaba al anadir un producto.

NUMERACION. La caja se guarda como 00 y las fotos del producto desde 01. Con eso
el orden es puramente numerico y la portada es "el numero mas bajo": no hay
nombre especial que reconocer ni mayusculas que comparar.

  EXCEPCION, declarada en serie.py -> PORTADA_01:
  en cajas sorpresa, shokugan de despiece y model kits de varias piezas la
  portada salta el 00 y usa el 01, porque la caja es identica para todas las
  variantes y lo que identifica al producto es la figura.

Dos clases de producto:
  · CARPETA  -> subcarpeta propia con varias fotos numeradas.
  · SUELTO   -> una sola imagen, sin subcarpeta.

Un producto cruzado (`alsoIn`) tiene carpeta espejo en la otra categoria, pero
se lista SOLO por su categoria primaria: la copia espejo no recibe .webp.
"""
import os
import sys

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HTML = os.path.join(BASE, 'index.html')

sys.path.insert(0, BASE)
try:
    import serie
except ImportError:
    print('No se encuentra serie.py en %s' % BASE)
    print('')
    print('  Es el unico archivo propio del repositorio. Debe declarar:')
    print('    CARPETA     {id de producto: ruta de su carpeta}')
    print('    SUELTO      {id de producto: ruta de su unica imagen}')
    print('    PORTADA_01  [ids cuya portada salta el 00 y usa el 01]')
    sys.exit(2)

CARPETA = getattr(serie, 'CARPETA', {})
SUELTO = getattr(serie, 'SUELTO', {})
PORTADA_01 = set(getattr(serie, 'PORTADA_01', []))

IMG_EXT = ('.jpg', '.jpeg', '.png')


def orden(nombre):
    """00, 01, 02... Orden numerico y nada mas.

    Antes habia que reconocer el nombre PACKAGE y ponerlo delante a mano. Con
    la caja guardada como 00 eso desaparece: el orden del archivo ES el orden
    de la galeria, y la portada es el primero.
    """
    stem = os.path.splitext(nombre)[0]
    return (0, int(stem)) if stem.isdigit() else (1, 0)


def portada_de(pid, files):
    """El numero mas bajo, salvo que el producto pida saltarse la caja.

    Devuelve (portada, aviso). El aviso no es un error: un producto declarado
    en PORTADA_01 que solo tenga la caja se queda con ella y lo dice, en vez de
    quedarse sin portada.
    """
    if pid not in PORTADA_01:
        return files[0], ''
    sin_caja = [f for f in files if os.path.splitext(f)[0] != '00']
    if sin_caja:
        return sin_caja[0], ''
    return files[0], 'pide portada 01 y solo tiene la caja (00)'


def plan():
    """[(pid, ruta, portada, [archivos], es_suelto, error)]

    Para un producto suelto, `ruta` es el archivo y `portada` su nombre.
    """
    filas = []
    for pid, carpeta in sorted(CARPETA.items()):
        full = os.path.join(BASE, carpeta)
        if not os.path.isdir(full):
            filas.append((pid, carpeta, None, [], False, 'CARPETA NO EXISTE'))
            continue
        # Solo originales: los .webp son derivados y contarlos duplicaria cada
        # numero, ademas de arrastrar el -thumb de la portada.
        files = [f for f in os.listdir(full) if f.lower().endswith(IMG_EXT)]
        if not files:
            filas.append((pid, carpeta, None, [], False, 'VACIA'))
            continue
        files.sort(key=orden)
        portada, aviso = portada_de(pid, files)
        filas.append((pid, carpeta, portada, files, False, aviso))

    for pid, ruta in sorted(SUELTO.items()):
        full = os.path.join(BASE, ruta)
        if not os.path.isfile(full):
            filas.append((pid, ruta, None, [], True, 'ARCHIVO NO EXISTE'))
            continue
        nombre = os.path.basename(ruta)
        filas.append((pid, ruta, nombre, [nombre], True, ''))

    return filas


if __name__ == '__main__':
    filas = plan()
    print('%-24s %-50s %-11s %s' % ('PRODUCTO', 'RUTA', 'PORTADA', 'GALERIA'))
    print('-' * 108)
    pkg = uno = total = errores = 0
    peso = 0
    for pid, ruta, portada, files, suelto, err in filas:
        if portada is None:
            print('%-24s %-50s  !! %s' % (pid, ruta[:50], err))
            errores += 1
            continue
        if os.path.splitext(portada)[0] == '00':
            pkg += 1
        else:
            uno += 1
        total += len(files)
        base = os.path.dirname(ruta) if suelto else ruta
        peso += os.path.getsize(os.path.join(BASE, base, portada))
        etiqueta = ' (suelto)' if suelto else ''
        if err:
            etiqueta += '  ~ ' + err
        print('%-24s %-50s %-11s %d img%s'
              % (pid, ruta[:50], portada[:11], len(files), etiqueta))
    print('-' * 108)
    print('%d productos   portada caja (00): %d   portada 01/suelto: %d   imagenes: %d'
          % (len(filas), pkg, uno, total))
    print('Peso de las %d portadas hoy: %.1f MB  ->  se convertiran a WebP'
          % (len(filas) - errores, peso / 1048576.0))
    sys.exit(1 if errores else 0)
