# Actualización pendiente — Kamen Rider Myth

**Este documento es una tarea, no documentación.** Se aplica, se verifica y
**se borra**, junto con los archivos que deja obsoletos.

Viene de lo aprendido montando **Gavan Infinity**, la tercera serie de la
franquicia. Nada de lo que hay aquí es de Gavan: son cosas de uso general que se
descubrieron allí y que este repositorio necesita.

> **Adáptalo a Myth.** Las tablas de abajo llevan los valores de esta serie ya
> calculados, pero **revísalos** antes de pegarlos: son mi lectura de tu
> `CATEGORY_ORDER`, no una verdad comprobada contra las cajas.

---

## 1. Lo que ya está copiado en el repositorio

| Archivo | Estado | Qué hacer |
|---|---|---|
| `tools/check_urls.py` | **copiado y probado aquí** | nada, ya funciona |
| `PROJECT-RED.md` | **copiado** | leerlo: resuelve la referencia rota de `SISTEMA.md` |

`check_urls.py` se corrió en seco en este repositorio: **274 rutas, 0
discrepancias de mayúsculas.** No hace falta adaptarlo.

### Por qué hacía falta esa herramienta

`audit.py` comprueba las rutas con `os.path.exists`, que **en Windows no
distingue mayúsculas**. Una ruta mal capitalizada pasa la auditoría en tu equipo
y da 404 publicada. Es el fallo que tu propio `SISTEMA.md` §5 llama «el más
traicionero de todo el sistema», y dice literalmente que la auditoría no puede
detectarlo. Ahora sí.

```bash
python tools/check_urls.py
python tools/check_urls.py --servidor https://leonato312.github.io/Kamen_Rider_MY-TH_Checklist
```

**No lo canalices.** `check_urls.py | tail -4` devuelve el código de salida de
`tail`, no el suyo, y un fallo pasa por bueno. Usa `${PIPESTATUS[0]}`.

---

## 2. Lo que hay que aplicar a mano en `index.html`

### 2.1 El distintivo de línea está mal en seis categorías

**Este es el arreglo que de verdad importa aquí.** En la línea 1656:

```js
const isSG = p.category.startsWith("SG");
```

y en la 1667:

```js
isSG ? '<span class="badge badge--sg">SG</span>' : '<span class="badge badge--dx">DX</span>',
```

Todo lo que no empiece por `SG` recibe el distintivo **DX**. De tus doce
categorías, **seis no son DX**: una figura TAF no es DX, ni un Soft Vinyl, ni un
S.H.Figuarts, ni un premio de campaña.

**Sustituye** las dos líneas por esto, y añade el mapa al Bloque 1:

```js
/* Distintivo de linea que lleva la tarjeta, por prefijo de categoria.
   Sin entrada, sin distintivo: es mejor no poner nada que poner una linea
   equivocada. */
const CATEGORY_BADGE = {
  "DX SETS":"DX", "DX RANDOM BOX":"DX", "DX DRIVERS":"DX",
  "BUCKLES SETS":"DX", "ARMAS":"DX",
  "SG MODEL KITS":"SG", "SG SO-DO":"SG", "SG RANDOM BOX":"SG"
};
```

```js
const linea   = CATEGORY_BADGE[p.category] || "";
const isPromo = p.category === "RIDE-SEED EGGS PROMOCIONALES";
```

```js
linea ? `<span class="badge badge--${esc(linea.toLowerCase())}">${esc(linea)}</span>` : "",
```

**Quedan sin distintivo a propósito:** `TAF`, `SOFT VINYL`, `SHF` y
`RIDE-SEED EGGS PROMOCIONALES`. **Comprueba si `BUCKLES SETS` y `ARMAS` son de
verdad línea DX** antes de dejarlos así; es lo único de la tabla que he supuesto.

### 2.2 Campos para Premium Bandai, si alguna vez hace falta

Dos campos opcionales del producto. **Solo si Myth llega a tener exclusivas de
P-Bandai**; si no, sáltate esto entero.

```js
exclusiva:"Premium Bandai",       // distintivo propio, aparte de dateType
reservas:"6 jul - 4 oct 2026",    // linea bajo el precio
```

El detalle está en `PROJECT-RED.md` §2, con el CSS y dónde se pintan. Y la
decisión de fondo: **`date` es la fecha de entrega, no la de reserva.**

### 2.3 `LINE_LABEL`: no lo necesitas

Solo hace falta cuando una clave de línea es compuesta. `EGGS_LINES` aquí es
`{DX, SG}`, las dos de una palabra. **Ignóralo.**

---

## 3. Ojo: tu motor es anterior al de Omegahorn

`PROJECT-RED.md` habla de `PIEZAS_CATALOG` y `LINES`. En Myth se llaman
**`EGGS_CATALOG`** y **`EGGS_LINES`**, y las piezas no llevan campo
`collection` porque aquí solo hay una colección repartida.

**No renombres nada.** Funciona, está publicado y el cambio no aporta. Solo
tenlo presente al leer la plantilla: los nombres no coinciden, la arquitectura
sí.

---

## 4. Verificar antes de dar por bueno

```bash
python tools/audit.py          # debe seguir sin incidencias ALTO
python tools/check_urls.py     # 274 rutas, 0 discrepancias
```

Y abre `index.html` en el navegador: **comprueba que una tarjeta de TAF ya no
dice «DX»** y que las de `DX SETS` y `SG SO-DO` siguen bien.

---

## 5. Qué borrar al terminar

### `tools/README.md`

Queda obsoleto en cuanto `PROJECT-RED.md` esté en el repositorio: su tabla de
scripts se queda corta —ahora son cuatro— y el procedimiento por wave está en el
§10 de la plantilla, más completo.

**Antes de borrarlo, rescata lo que es solo de Myth** y llévalo a `SISTEMA.md`
si no está ya:

- MY-TH, MAOU y RID, las tres romanizaciones que salieron de las cajas de TAF
- que `TAF/DX Ridewatter Eggs/` es la copia espejo del producto cruzado y que la
  auditoría avise de ella es correcto
- que los model kits y las figuras de montar no alimentan la checklist

Lo demás ya está en la plantilla.

### Este archivo

`ACTUALIZAR.md` se borra cuando los puntos 1 a 4 estén hechos y verificados. Si
lo dejas, la próxima vez que lo abras no sabrás si se aplicó.

---

## 6. Lo que NO se trae de Gavan Infinity, y por qué

Para que no lo busques:

- **El motor con `collection`.** Myth tiene una sola colección repartida; el
  campo no aportaría nada.
- **Las seis líneas y `LINE_LABEL`.** Aquí hay dos, DX y SG.
- **El `REGISTRO.md` de Gavan.** Son sus datos. El tuyo es `SISTEMA.md`, que
  cumple ese papel y además es la memoria de por qué el sistema es así.

Lo que sí conviene leer de allí, aunque no se copie, es el §5 de
`PROJECT-RED.md` —**de dónde salen las imágenes**, nueve fuentes con sus
trampas— porque la próxima wave de Myth se recopila igual.
