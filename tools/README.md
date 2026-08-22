# tools/ — mantenimiento del catálogo

Scripts para regenerar las imágenes de la web cuando se anuncia una wave nueva.
Son la **receta**: mientras se usen estos parámetros, las imágenes nuevas
saldrán idénticas a las que ya están publicadas.

Requiere Python 3 con Pillow (`python -m pip install Pillow`).
Se ejecutan desde la raíz del proyecto; deducen las rutas de su propia
ubicación, así que no hay nada que configurar.

---

## Los tres scripts

| Script | Qué hace | Escribe |
|---|---|---|
| `audit.py` | Cruza `index.html` con el disco: rutas rotas, WebP huérfanos, portadas y numeración | nada |
| `plan.py` | Muestra qué portada y qué galería saldría de cada producto | nada |
| `build_all.py` | Genera los `.webp` y repunta `index.html` | sí |

```bash
python tools/audit.py        # 1. comprobar que los nombres cuadran
python tools/plan.py         # 2. ver el plan sin tocar nada
python tools/build_all.py    # 3. ejecutar
```

Los dos primeros son de solo lectura: correrlos siempre antes.

---

## Parámetros (no cambiar sin motivo)

| Derivado | Lado máximo | Calidad | Para qué |
|---|---|---|---|
| `<nombre>.webp` | 1600 px | 80 | galería, se abre en el visor |
| `<nombre>-thumb.webp` | 700 px | 82 | portada de la tarjeta |

Compresión con `method=5`. Si se cambian estos valores, las imágenes nuevas
dejarán de casar visualmente con las ya publicadas.

`FICHA/` se salta **a propósito**: son las capturas de Bandai a resolución
original, de donde se leen contenidos, mes y precio. No se les genera WebP
para no perder detalle, y no se publican.

---

## Añadir un producto

1. Guardar la captura de Bandai en `CATEGORIA/FICHA/` con el nombre del
   producto y, tras un guion, sus contenidos.
2. Crear `CATEGORIA/NOMBRE DEL PRODUCTO/` — **idéntico** al nombre de la ficha
   sin la parte de contenidos — y meter las fotos: `PACKAGE.jpg` si la hay,
   luego `01.jpg`, `02.jpg`… correlativas y con cero delante.
3. `python tools/audit.py` y comprobar que sale sin incidencias ALTO.
4. Añadir el producto a `PRODUCTS` en `index.html` (id, título, categoría,
   `date`, `price`, `contains`) y las piezas nuevas a `EGGS_CATALOG` si la wave
   trae Ride Eggs o Seed Eggs inéditos.
5. Añadir su carpeta al diccionario `CARPETA` de `plan.py`.
6. `python tools/build_all.py`.

El paso 5 es el que se olvida: si el producto no está en `CARPETA`, el script
no le genera nada y la tarjeta se queda sin imagen.

---

## Convenciones que sostienen todo esto

- **La romanización sale de la caja, no de la transcripción.** Verificado en
  las cajas de TAF: マイス es **MY-TH**, マオウ es **MAOU**, リド es **RID**.
- Los gimmicks son **Eggs** (エグズ). Bandai los escribe **EGZ** en alfabeto
  latino, pero se descartó por opaco.
- **Portada = `PACKAGE` si existe, si no `01`.** Decisión deliberada.
- Las carpetas van en MAYÚSCULAS. En Windows da igual, en el servidor no:
  una mayúscula mal puesta es una imagen rota solo en producción.
- **`FICHA/` es de formato libre.** Es material de consulta, no publicable:
  una sola hoja puede cubrir toda una colección y sus nombres no tienen que
  corresponderse con los de los productos. `audit.py` no la revisa.
- El Ridewatter Eggs tiene carpeta en `DX SETS` y en `TAF` por ser figura y
  gimmick a la vez. La web usa la de `DX SETS`, su categoría primaria.
- Los productos de una sola imagen no llevan carpeta propia: el archivo va
  suelto en la categoría, con su nombre completo. Es el caso de
  `RIDE-SEED EGGS PROMOCIONALES` y de tres de los cuatro `SG MODEL KITS`.
- `TAF/DX Ridewatter Eggs/` es la copia espejo del producto puente y la
  auditoría avisa de que nadie la referencia. Es correcto: la web usa la de
  `DX SETS` y esas fotos no se convierten ni se suben.
