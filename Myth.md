# Kamen Rider Myth — checklist de merchandising

Punto de entrada único del repositorio. Cualquier actualización, mejora o
investigación empieza aquí.

Reemplaza a `SISTEMA.md`, `PROJECT-RED.md`, `tools/README.md` y `ACTUALIZAR.md`,
que se borraron al volcarlos. **Si aparece otro `.md` suelto en la raíz, no es
un segundo documento: es algo pendiente de bajar aquí y borrar.**

---

## Cómo se hereda este archivo

La serie siguiente copia este archivo, lo renombra y **solo sustituye la
Parte II**. Todo lo demás le sirve tal cual.

| Parte | Qué es | Al heredar |
|---|---|---|
| **I. El motor** | arquitectura, modelo, imágenes, herramientas, despliegue | se queda igual |
| **II. Esta serie** | Myth: su vocabulario, sus categorías, sus decisiones | **se reemplaza entero** |
| **III. Lo aprendido** | errores que costaron tiempo y lo que se descartó | se queda igual |

Antes de arrancar una serie nueva, responder el cuestionario del §13. Sin eso,
cualquier estructura que se monte es a ciegas.

---
---

# PARTE I — EL MOTOR

## 0. Un repositorio por serie

**No meter dos series en el mismo catálogo.** Cada una tiene su coleccionable,
sus líneas y su calendario, y sobre todo: **una serie sigue sacando producto
después de que acabe su emisión**. Si compartieran repositorio, el catálogo de la
vieja seguiría creciendo dentro del de la nueva y el calendario dejaría de
responder a la pregunta que lo justifica.

Consecuencia práctica: cada serie con su repositorio, su `index.html`, su URL y
**su propia clave de `localStorage`**.

---

## 1. Para qué existe

Dos preguntas, en este orden:

1. **¿Cuándo llega la próxima wave?** Por eso el mes es la categoría raíz y todo
   cuelga de la fecha de salida.
2. **¿Qué me falta del coleccionable?** Las piezas se reparten entre sets, cajas
   sorpresa y exclusivas — decenas, imposibles de rastrear a ojo. Las figuras y
   los cinturones no: son pocos.

Vocabulario, porque se confunden: una **wave** es el ciclo de lanzamientos de un
mes; las **tandas** son los días concretos dentro de ese mes. Septiembre de Myth
es una wave con seis tandas.

Si una serie no tiene un coleccionable masivo repartido, media máquina sobra y
queda un calendario con checklists por categoría. Compruébalo antes de montar.

---

## 2. La arquitectura

### Un archivo, dos listas

`index.html` es HTML5 + CSS3 + Vanilla JS. Sin frameworks, sin build, sin
dependencias. Se abre con doble clic y funciona igual en local que publicado.
Todo el catálogo se genera desde dos arrays:

- `EGGS_CATALOG` — un objeto por pieza coleccionable
- `PRODUCTS` — un objeto por producto

De ahí salen tarjetas, contadores, barras y checklists. Mantener el catálogo es
editar dos listas.

**Por qué así:** la checklist necesita saber qué piezas trae cada producto. Si
las tarjetas fueran HTML a mano, esa relación viviría en la cabeza de quien las
escribió y se rompería a la tercera wave. Declarada como dato, marcar un producto
actualiza la checklist sola y no puede desincronizarse.

**El coste:** un error de sintaxis deja la página en blanco, porque todo se
genera en tiempo de ejecución. De ahí que el repositorio sea Git **desde antes de
escribir la primera entrada**.

### La regla de oro del estado

Solo se persiste `{products:{id:estado}, ui:{...}}` bajo `krmyth-catalog-v1`.
**Las checklists nunca se guardan: se derivan de los productos en cada render.**
Progreso, cobertura, qué pieza falta — todo es cálculo. Esa es la razón de que no
puedan mentir.

`loadState()` descarta ids que ya no existen, para que renombrar un producto no
deje basura invisible engordando el guardado.

**Cada serie necesita su propia clave.** Si dos catálogos comparten dominio y
clave, se pisan lo que el usuario tenga marcado. El patrón es `<serie>-catalog-v1`.

---

## 3. El modelo de datos

### Producto

```js
{ id:"dx-rider-eggs-set-01",     // <línea>-<producto>, minúsculas
  title:"DX RIDER EGGS SET 01",  // el nombre de la caja
  category:"DX SETS",            // una de CATEGORY_ORDER
  date:"2026-09-05",             // el mes del acordeón sale de aquí
  dateType:"release",            // "release" | "preorder" (Premium Bandai)
  price:2200,                    // con impuestos, o null
  priceLabel:"Premio de campaña",// opcional: matiza o sustituye el precio
  alsoIn:["TAF"],                // opcional: producto que pertenece a dos categorías
  reemplaza:["dx-myth-driver"],  // opcional: productos que trae dentro
  componentes:["driver-myth"],   // opcional: piezas no coleccionables, solo auditoría
  img:"...-thumb.webp",
  gallery:["....webp"],
  contains:["ride-eggs-8","ride-eggs-4@std"] }
```

**`date` es la única fuente de verdad temporal.** El mes se deriva al cargar
(`p.month = p.date.slice(0,7)`). Guardar mes y fecha por separado los deja
desincronizarse tarde o temprano.

**`dateType:"preorder"`** existe porque Premium Bandai no tiene fecha de tienda,
tiene fecha de reserva. Se trata como equivalente al release y se marca con badge
para no confundir.

**`priceLabel`** cubre lo que no es un precio normal. Si `price` es `null`,
sustituye al texto "Precio por confirmar" — porque un premio de campaña no es un
precio pendiente, es que no lo tendrá nunca. Si hay precio, sale como tooltip.

### Pieza coleccionable

```js
{ id:"ride-eggs-4",
  name:"Ride Eggs 4",
  type:"ride-eggs",   // clave de EGGS_TYPES, agrupa dentro del panel
  line:"DX",          // contadores separados por línea
  variants:[ {id:"std", label:"Estandar"},
             {id:"special", label:"Special ver."} ] }
```

**Regla de referencia:** si la pieza declara `variants`, en `contains` va con `@`
**siempre**, también `@std`. El motor normaliza la desnuda, pero se lee mal:
parece declarar *la pieza* cuando declara *una versión*, y el mismo id acaba
escrito de dos formas en el mismo catálogo.

### Las cuatro reglas que más se prestan a error

**Líneas separadas.** DX y SG llevan contadores independientes porque cada línea
saca piezas que la otra no. Fundirlas haría que "me faltan 3" no significara nada.

**Variantes contra piezas propias:**

| Situación | Cómo va |
|---|---|
| Misma pieza reeditada (`special ver.`, `Gold ver.`) | `variants` — una línea, cualquier versión cuenta |
| Diseños distintos que comparten nombre o procedencia | `variants` también, con sub-marcas que enlazan a su producto |
| Piezas que aluden a **personajes distintos** | entradas separadas |

La tercera fila es la trampa: `Ride Eggs 1` y `Ride Eggs 1 Origin` parecen
variante y no lo son, porque aluden a dos riders.

**Productos que absorben a otros.** Un set deluxe suele traer dentro el producto
base. Se declara con `reemplaza` **en el que absorbe**, y la cobertura es
**transitiva**: basta declarar lo que se absorbe directamente y las cadenas se
recorren solas. Cuando salga un set nuevo se toca un sitio en vez de editar todo
lo que deja obsoleto.

El cubierto **no** pasa a Obtenido —no lo tienes, lo tienes *dentro de otra
caja*—: se atenúa y avisa de en qué caja viene. Sí cuenta en el contador del mes,
que responde a "¿me queda algo por comprar?". **Ojo con el doble sentido:** en la
tarjeta cubierto significa *no lo necesitas*; en la checklist significa *lo
tienes* y se marca en verde. Misma información, dos preguntas distintas.

**Productos puente.** Un producto puede pertenecer de verdad a dos categorías —el
Ridewatter Eggs es figura y gimmick a la vez—. Se resuelve con `alsoIn`: se dibuja
una tarjeta en cada subcategoría pero sigue siendo **un único producto**, con
estado compartido vía `data-pid`, contando una vez en el mes y una en la
checklist. Sin eso habría que duplicar la entrada y las copias se
desincronizarían.

### El desplegable de contenidos

Todo producto que traiga piezas las lista en un desplegable cerrado por defecto,
que no altera la altura de la tarjeta.

**El texto distingue lo que de verdad es distinto.** En una caja sorpresa las
piezas son **posibles** —te toca una— y pone "Ver posibles contenidos", borde
punteado. En un set vienen **garantizadas**: "Eggs incluidos", singular si es una,
borde continuo. Llamarlos igual daría a entender que comprar un set es una
lotería.

---

## 4. Las checklists

Hay **dos clases y no funcionan igual**, aunque se vean parecidas.

**Del coleccionable.** La pieza está repartida entre productos, así que ninguno la
representa. Se declara con `contains` y el progreso se **deriva**. Es la razón de
ser del sistema.

**De producto** (`PRODUCT_CHECKLISTS`). Cada producto **es** la pieza; la
checklist solo los agrupa. Aporta ver todos juntos, porque el catálogo está
ordenado por mes y si no habría que recorrer cinco meses.

### Cada una en su pestaña, nunca apiladas

Se probaron primero como bloques en un mismo panel y estaba mal: **hay
coleccionistas que siguen una sola línea** y a esos, pasar por 41 piezas del
gimmick para llegar a sus cuatro kits no les sirve. Y hay quien lleva dos cuentas
a la vez y quiere compararlas.

Cada checklist es una pestaña (`CHECKLIST_TABS`) con su contador en la solapa, su
texto de ayuda y su color. El panel recuerda en cuál estabas y el filtro de
ocultar se mantiene al cambiar.

### La línea se pliega

Una línea con decenas de piezas repartidas en varios tipos, dibujada de una vez,
es un muro. Se pliega con la misma maquinaria que el acordeón de meses
—`max-height` + `data-open`, con lo abierto guardado—.

**Cerrada no puede esconder el resumen:** nombre, contador y barra quedan fuera
del bloque plegable a propósito, porque son justo lo que se viene a mirar. En la
primera visita, todas cerradas: dos barras juntas ya son la respuesta.

### El color orienta

Cada checklist tiene un tono que se repite en los tres sitios donde aparece: la
mini-barra de la cabecera, la solapa de su pestaña y el encabezado de su sección.

**Los dos tonos fuertes se reservan al coleccionable principal**; el resto usa
tonos suaves. Con seis barras, si todas gritan igual se pierde cuál importa.

### Cuánto cabe en la cabecera

**Hay que medirlo, no estimarlo.** Con seis barras esta cabecera aguanta en una
línea hasta 1280 px; a 1240 el botón de las checklists se caía solo a una segunda
fila. El responsive baja las barras a fila propia en `max-width: 1279px`, en su
propia consulta para no adelantar el resto.

Si se añaden barras, volver a medir: forzar el viewport a varios anchos y contar
posiciones verticales distintas. El número escrito en un documento envejece.

### Añadir una checklist nueva

Tres pasos en `index.html`: entrada en `PRODUCT_CHECKLISTS` (`cat`, `label`,
`slug`), entrada en `CHECKLIST_TABS` (`id`, `label`, `hint`), y un color en
`:root` con las cuatro reglas que lo aplican. Una categoría sin productos no
dibuja pestaña, así que se puede declarar antes de tener nada.

---

## 5. De dónde salen los datos

### `FICHA/`, la base de datos

Cada categoría contiene una carpeta `FICHA/` con las capturas de las páginas
oficiales de donde salen fecha, precio y contenidos. **Es lo primero que hay que
mirar antes de actualizar nada.**

**Es de formato libre.** No se publica, no se le generan derivados —se guarda a
resolución original precisamente para poder leer los datos— y **sus nombres no
tienen que corresponderse con ningún producto**: una sola hoja puede cubrir una
colección de diez tipos.

### Jerarquía de fuentes

1. **Los nombres, de la caja del producto.** Si hay foto de la caja, manda la
   caja. En Myth tres nombres estuvieron mal semanas hasta que las cajas de TAF
   los zanjaron.
2. **Fechas y precios, de la ficha oficial.**
3. **Las hojas de cálculo de apoyo, solo para fechas y precios.** Para
   nomenclatura transcriben mal la mitad.

### Las páginas de donde se saca todo

**Ninguna serie tiene todas sus fotos ni todos sus datos en un sitio.** Este es
el orden de búsqueda, y cada fuente tiene su trampa.

| Fuente | Para qué |
|---|---|
| `toy.bandai.co.jp` | ficha: fotos, fecha, precio, contenidos |
| **CDN de Akamai** | fotos de cualquier producto, aunque su página no abra |
| `bandai.co.jp/candy` | la raíz de la línea SG |
| `tamashiiweb.com` | S.H.Figuarts: datos buenos, fotos pequeñas |
| `p-bandai.jp` | **geobloqueado** |
| `1999.co.jp` | **las fotos de caja** |
| `tokullectibles.com` | números de modelo, contenidos y banners |
| la wiki de la serie | premios, que ninguna tienda vende |
| el repositorio hermano | piezas de crossover |

**1 · La ficha de Bandai.** Conviven dos hosts y hay que mirar **los dos**:

```
bandai-a.akamaihd.net/bc/img/model/xl/<nº modelo>_<n>.jpg      fichas antiguas
assets-toy.bandai.co.jp/toy/ja/product/AAAA/MM/<hash>/<n>.jpg  nuevas
```

Mirando solo el primero se queda fuera **la mitad** de los productos. Se enumera
`_1`, `_2`… hasta el primer 404, conservando el **orden del documento**: es el de
la galería oficial.

**2 · El CDN por número de modelo es la llave maestra.** No está geobloqueado y
responde aunque la página del producto no se pueda abrir.

> **La trampa más cara: devuelve 200 a cualquier número válido, sea de la serie
> que sea.** En Gavan Infinity entraron diez fotos de otra serie porque una
> tienda daba un número equivocado y la descarga «funcionó». **Abre una imagen y
> míralas** antes de dar por buena una carpeta.

**3 · Bandai Candy**, la raíz de SG:
`bandai.co.jp/candy/search/result.html?q=<término en japonés>`. En la ficha, la
galería propia son las imágenes con pareja `-product-mobile`; las que solo
aparecen como `-product-main` son de otros productos. Sirve los mismos archivos
que el CDN, así que aporta datos más que resolución — pero hay que ir: destapó un
producto que ninguna otra fuente listaba.

**4 · Tamashii Web** para S.H.Figuarts. Datos completos —precio, reservas,
`セット内容`— pero **las fotos más pequeñas**, y las fichas nuevas solo en
`.webp`.

**5 · Premium Bandai está geobloqueado.** `p-bandai.jp` devuelve 302 desde fuera
de Japón, y `p-bandai.com/us` no distribuye las exclusivas japonesas. **La salida
es el CDN:** el número de item de la URL *es* el número de modelo.

**6 · HobbySearch (`1999.co.jp`) es de donde salen las cajas.** Bandai no publica
la foto del paquete por separado:

```
www.1999.co.jp/itbig<NN>/<id>.jpg     miniatura 224 px
www.1999.co.jp/itbig<NN>/<id>b*.jpg   galería 1200 px
www.1999.co.jp/itbig<NN>/<id>p*.jpg   PAQUETE 1200 px   <- esto
```

Son JPEG de verdad aunque el navegador reciba `.webp`. **Su buscador tiene
truco:** el parámetro que funciona es `searchkey=`, no `sw=`; con `sw=` devuelve
el catálogo entero sin filtrar. No stockea exclusivas de P-Bandai ni premios.

**7 · Tokullectibles**, que es Shopify y sirve para tres cosas:

```
tokullectibles.com/products/<handle>.json
tokullectibles.com/collections/<slug>/products.json?limit=250
```

- **Números de modelo de todo**, incluidos SG y gashapon. Con eso, el CDN da las
  fotos: es la vía más rápida para levantar una línea entera.
- **Contenidos** que a veces Bandai no lista.
- **Banners** que Bandai no publica: se reconocen porque su nombre **no** sigue
  el patrón `<nº modelo>_<n>.jpg`.

Dos avisos: **sus copias de Bandai están recomprimidas** —ni un byte coincide con
las del CDN— y **reutiliza una imagen genérica** en los productos sin foto, que
se detecta porque el mismo nombre aparece en varios. Sus precios son de
importación en dólares.

**8 · La wiki es la única fuente de los premios**: campañas, máquina de garra,
bonos de ropa y regalos de revista. En Fandom los nombres de archivo están en los
atributos `data-image-name`. Ojo: a veces el original subido es pequeño.

**9 · El repositorio hermano.** Si una pieza es un crossover, puede estar mejor
al otro lado. Aquí pasa con el Ridewatter Eggs.

### Después de descargar, comprueba

**Abre y decodifica todas las imágenes.** Un `PACKAGE.jpg` llegó truncado —107.826
bytes en vez de 164.106— **con código 200**, y abría como imagen válida hasta que
la conversión intentó leer el último bloque. Ni el código ni el tamaño bastan.

### Qué anotar de cada caja

**Todo lo que trae, no solo los coleccionables.** Un set que incluye un cinturón
deja sin sentido comprar ese cinturón suelto, y eso se pasa por alto con
facilidad cuando la atención está en el gimmick principal. Si es un set especial,
anotar además **de qué sets es upgrade**: con la cobertura transitiva, basta con
eso.

---

## 6. Las imágenes

### Estructura

```
CATEGORÍA EN MAYÚSCULAS/
├── FICHA/                        ← consulta, NO se publica
├── NOMBRE DEL PRODUCTO-Contenidos/
│   ├── PACKAGE.jpg               ← original, NO se publica
│   ├── PACKAGE.webp              ← galería, 1600 px
│   ├── PACKAGE-thumb.webp        ← portada, 700 px
│   └── 01.jpg  01.webp
└── PRODUCTO DE UNA IMAGEN-Contenidos.jpg   ← sin carpeta
```

**Portada = `PACKAGE` si existe, si no `01`.** Los productos de una sola imagen no
llevan carpeta: el archivo va suelto con su nombre completo.

### Los derivados

| Archivo | Lado máx. | Calidad | Para qué |
|---|---|---|---|
| `<nombre>.webp` | 1600 px | 80 | galería, se abre en el visor |
| `<nombre>-thumb.webp` | 700 px | 82 | portada de la tarjeta |

En Myth: portadas de 36,2 → 2,0 MB (94% menos) y galerías de 218 → 38 MB (83%).
700 px para una tarjeta de 252 px porque en pantallas retina se ve al doble.

Los originales no se tocan ni se suben; su respaldo va aparte.

### Cinco trampas que costaron horas

**1. No pongas `loading="lazy"` en las portadas.** Las tarjetas viven dentro de un
acordeón que arranca con `max-height: 0`; el navegador las da por fuera de
pantalla y no las pide hasta que hay scroll, así que aparecen vacías hasta que
mueves el ratón. Con 62 KB por portada, diferirlas no aporta nada.

**2. Las fotos de galería sí se difieren, pero de verdad.** Las `<img>` se crean
sin `src` y solo se rellena al abrirlas. Con `lazy` a secas el navegador tira de
las cercanas y el ahorro se evapora.

**3. Cuidado con las miniaturas que cargan la imagen grande.** Una tira de
miniaturas de 62 px apuntando al archivo de 1600 px son 2 MB para pintar diez
cuadraditos. Se detecta midiendo, no mirando.

**4. Las mayúsculas de las rutas.** Windows resuelve sin distinguirlas y el
servidor no: una mayúscula mal puesta funciona en tu equipo y da 404 publicada.
Es el fallo más traicionero del sistema, y por eso existe `check_urls.py`.

**5. Nada de servir imágenes desde Drive.** Límites de peticiones, y funcionan
solo para quien tiene sesión iniciada. Van junto al HTML, con **rutas relativas**
— así el sitio funciona igual bajo `/repo/` que en un dominio propio.

---

## 7. Las herramientas

Cuatro scripts en `tools/`, con Pillow como única dependencia
(`python -m pip install Pillow`). Deducen las rutas de su propia ubicación.

| Script | Qué hace | Escribe |
|---|---|---|
| `audit.py` | Cruza `index.html` con el disco | nada |
| `check_urls.py` | Igual, pero distinguiendo mayúsculas | nada |
| `plan.py` | Muestra qué portada y galería saldrían | nada |
| `build_all.py` | Genera los `.webp` y repunta el HTML | sí |

**Los tres primeros son de solo lectura: correrlos siempre antes.**

`audit.py` comprueba lo único que puede romper el sitio: rutas referenciadas que
no existen, `.webp` en disco que nadie usa, carpetas con fotos que la página
ignora, portada determinable, numeración y duplicados. Y dibuja el árbol de
`reemplaza`, deduciéndolo además de los `componentes` para avisar si la
declaración no cuadra con el contenido real.

**Una auditoría con falsos positivos es peor que ninguna.** Una versión contaba
los `.webp` derivados como fotos y avisaba de huecos inexistentes: con 74 avisos
de los que 70 eran ruido, nadie los lee.

### Añadir un producto

1. Guardar la captura en `CATEGORIA/FICHA/`, anotando **todo** lo que trae.
2. Crear `CATEGORIA/NOMBRE DEL PRODUCTO-Contenidos/` con `PACKAGE.jpg` si la hay
   y luego `01.jpg`, `02.jpg`… correlativas y con cero delante.
3. `python tools/audit.py`, sin incidencias ALTO.
4. Entrada en `PRODUCTS`, y piezas nuevas en `EGGS_CATALOG`. Si absorbe a otros,
   `reemplaza`; si es de las categorías donde eso pasa, también `componentes`.
5. **Registrar la carpeta en el diccionario `CARPETA` de `plan.py`.** Es el paso
   que se olvida: sin él el script no le genera nada y la tarjeta se queda sin
   imagen.
6. `python tools/build_all.py`.

---

## 8. Qué se publica y despliegue

```
se sube          index.html + los .webp + tools/     ~43 MB
se queda local   originales + FICHA/ + xlsx          ~238 MB
```

El `.gitignore` filtra por patrón, así vale para lo que se añada dentro de meses.
**Git no es la copia de seguridad** de los originales: están ignorados a propósito
y necesitan respaldo aparte.

GitHub Pages desde `main` / root. **Tras un push que renombra rutas, tarda uno o
dos minutos en reconstruir: un 404 justo después de subir no es un fallo.**

### Cómo verificar de verdad

`python tools/audit.py` y `python tools/check_urls.py`, y después **ejecuta la
lógica, no la leas**: marca una caja en el navegador, recarga y comprueba que la
checklist siga diciendo lo mismo. Los fallos de esta clase no se ven leyendo.

Dos avisos del entorno de pruebas:

- **Las transiciones CSS no avanzan en una pestaña en segundo plano.** Si un
  acordeón parece no abrirse, comprueba eso antes de buscar el fallo en tu CSS.
- **`localStorage` está deshabilitado en URLs `data:`.** Si la vista previa carga
  así, la persistencia no se puede probar ahí: hay que abrir el archivo o el sitio
  publicado.

---
---

# PARTE II — ESTA SERIE

> Esto es lo único que la serie siguiente sustituye.

## 9. Kamen Rider Myth

### Estado

46 productos de julio a noviembre de 2026 · 41 piezas Eggs (35 DX, 6 SG) ·
12 categorías · 6 checklists · ~280 archivos y 43,5 MB publicados.

- **Repositorio:** `leonato312/Kamen_Rider_MY-TH_Checklist`
- **Sitio:** https://leonato312.github.io/Kamen_Rider_MY-TH_Checklist/
- **Clave de estado:** `krmyth-catalog-v1`

### Vocabulario

El gimmick son los **Eggs**, en dos familias: **Ride Eggs** (numerados, más las
versiones Legend Rider) y **Seed Eggs** (temática animal, más las Legend). Aparte,
los **Bone Buckles** y el **Ridewatter Eggs**.

Riders, con la romanización de las cajas: **MY-TH** (マイス), **MAOU** (マオウ),
**DATT**, **RID** (リド), JAO, TIGUL, MUTON, VANKEN.

**Bandai escribe エグズ, y en alfabeto latino EGZ** —el título de SO-DO es
`装動 仮面ライダーマイス EGZ1`—. Se eligió **Eggs** porque son huevos y así se
lee solo; se descartó EGZ por opaco y "Ex" por ser una transcripción inicial. Del
mismo modo "Myceed" se occidentalizó a **"Myth Seed Eggs"**.

### Categorías

En este orden dentro de cada mes: `TAF`, `SOFT VINYL`, `SHF` (declarada y vacía,
esperando su primer producto), `SG MODEL KITS`, `SG SO-DO`, `SG RANDOM BOX`,
`DX SETS`, `DX RANDOM BOX`, `DX DRIVERS`, `BUCKLES SETS`, `ARMAS`,
`RIDE-SEED EGGS PROMOCIONALES`.

Checklists: Eggs (DX y SG), TAF, SO-DO, Buckles y Vinyl.

### Decisiones propias de Myth, con su porqué

**Una Random Box marcada cuenta sus 6 contenidos.** El usuario asume caja
completa. No implementar checks individuales por pieza sorpresa.

**Tres estados por producto:** Pendiente / Reservado / Obtenido. Solo `owned`
cuenta. "Reservado" existe porque el eje de la página son las fechas y hace falta
ver qué ya se pidió de una wave futura.

**Los model kits y SO-DO no alimentan la checklist de Eggs.** La propia caja avisa
de que sus piezas son exclusivas de esa serie y no funcionan con el Driver:
contarlas inflaría el progreso con algo que no puedes usar.

**`RIDE-SEED EGGS PROMOCIONALES`** agrupa gimmicks de revista, campaña y
exclusivas de tienda. Procedencia irregular: alguno no tiene precio porque es
premio.

**Sin galería desplegable.** Se implementó una tira de miniaturas en la tarjeta y
se quitó: metía una fila de ruido en las 46. Las fotos se abren pulsando la
portada, que lanza un visor en superposición. **Nunca una segunda página por
producto**: es una checklist, no una tienda.

**El `.xlsx` de apoyo** sirve para fechas y precios. Para nombres transcribe mal
la mitad (Dad/Maoh/Lido/Tigre por DATT/MAOU/RID/TIGUL, "Ride Exe" por Ride Eggs).

**Alcance acordado:** la página está terminada y en producción. Se admiten waves
nuevas y correcciones; **no rediseños** sin pedirlo.

---
---

# PARTE III — LO APRENDIDO

## 10. Errores que costaron tiempo

**Deducir a ojo qué set absorbe a cuál falló dos veces seguidas.** Primero se
escapó un cinturón incluido en un set, luego otro. Por eso ahora se declara
`componentes` en las categorías donde pasa y la auditoría **deduce** la cobertura
comparando contenidos, avisando en los dos sentidos: la que falta declarar y la
declarada que el contenido no respalda.

**Inventarse reglas y hacérselas cumplir a la auditoría.** Se exigió que cada
ficha se llamara igual que un producto. No era una regla real —`FICHA/` es de
formato libre— y la auditoría pasó días gritando con nueve avisos falsos.

**Fiarse de un número escrito en un documento.** El límite de barras de la
cabecera estaba mal y nadie lo notó hasta medirlo.

**Reemplazos masivos sin comprobar los bordes.** Al pasar "Ex" a "Eggs", el
límite de palabra protegió `EXPACK` pero un guion bloqueó una sustitución en una
ficha, que se quedó atrás. Verificar siempre el resultado, no la intención.

## 11. Lo que se probó y no funcionó

- **Checklists apiladas en un panel.** Quien colecciona una línea no debería
  recorrer las demás para llegar a la suya.
- **Desplegable de galería en la tarjeta.** Una fila de ruido en todas.
- **Una página por producto.** Descartada de entrada: es una checklist.
- **Entradas separadas enlazadas con un campo `related`.** Tres líneas del panel
  repitiendo enlaces cruzados, peor de leer que el problema que resolvía.
- **Etiqueta "Estimado"** para datos sin confirmar. Si un dato no está
  confirmado, o se omite o se pone sin anunciarlo.
- **Enlaces de Drive** como origen de las imágenes.
- **Exigir que cada ficha se llamara igual que un producto.**
- **Fiarse del `.xlsx` para los nombres.**

## 12. Puntos abiertos

- **SO-DO está incompleto.** Los tipos 9 y 10 siguen sin revelar y la fecha del
  15 de septiembre es una estimación: la ficha solo dice "septiembre 2026".
- **`SHF` está declarada y vacía**, esperando su primer producto.
- **`TAF/DX Ridewatter Eggs/`** es la copia espejo del producto puente. La
  auditoría avisa de que nadie la referencia, y es correcto: la web usa la de
  `DX SETS`. Es el único aviso MEDIO que queda.
- **Los seis avisos BAJO** son minúsculas dentro de nombres, ya decididas.
- **Las miniaturas de la galería** cargan el WebP de 1600 px. Se decidió dejarlo:
  precarga lo que el visor va a mostrar. Si molesta, generar `-thumb` para las 204
  fotos sube el despliegue ~6 MB y divide por seis lo que baja quien navegue.
- **Drivers y Armas no tienen checklist propia.** Son 3 y 2 productos.

---

---

## 13. Cuestionario para la serie siguiente

Responder antes de escribir una línea. Es lo que **no** se hereda:

1. ¿Cuál es el coleccionable principal, cómo se llama y cómo se escribe en el
   catálogo? ¿Cuántos hay aproximadamente?
2. ¿Tiene familias? Son los grupos dentro del panel.
3. ¿Hay líneas de producto que saquen piezas exclusivas? Si sí, contadores
   separados.
4. ¿Qué categorías de producto, y en qué orden?
5. ¿Cuáles llevan checklist propia?
6. ¿Hay sets que traigan dentro otros productos?
7. ¿Qué colores? Los dos fuertes para el coleccionable.
8. Clave de `localStorage` propia.
