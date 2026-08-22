# Plantilla de checklist — Project Red

Cómo levantar la checklist de cualquier serie de la franquicia, empezando por
**Omegahorn**. Recoge todo lo aprendido construyendo la de Kamen Rider Myth,
separando lo que sirve siempre de lo que hay que volver a decidir cada vez.

Este documento se copia al repositorio de cada serie nueva y se adapta.

---

## 0. Antes de nada: un repositorio por serie

**No meter dos series en el mismo catálogo.** Cada una tiene su propio
coleccionable, sus propias líneas de producto y su propio calendario, y sobre
todo: **una serie sigue sacando producto después de que acabe su emisión**. Si
compartieran repositorio, el catálogo de la serie vieja seguiría creciendo
dentro del de la nueva y el calendario dejaría de responder a la pregunta que
justifica su existencia.

Consecuencia práctica: cada serie tiene su repositorio, su `index.html` y su
URL. Y **su propia clave de `localStorage`** — si dos catálogos comparten
dominio y clave, se pisan lo que el usuario tenga marcado.

---

## 1. Para qué existe una checklist así

Dos preguntas, en este orden:

1. **¿Cuándo llega la próxima tanda?** Por eso el mes es la categoría raíz y
   todo cuelga de la fecha de salida.
2. **¿Qué me falta del coleccionable principal?** Toda serie de la franquicia
   suele tener una pieza que se reparte entre sets, cajas sorpresa y exclusivas
   — decenas de ellas, imposibles de rastrear a ojo. Ese es el corazón.

Si una serie **no tiene** un coleccionable masivo repartido, la mitad del
sistema sobra y queda un calendario con checklists por categoría. Es una
posibilidad real: compruébalo antes de construir.

---

## 2. El motor: lo que no cambia entre series

### Un archivo, dos listas

`index.html` es HTML5 + CSS3 + Vanilla JS. Sin frameworks, sin build, sin
dependencias. Todo el catálogo se genera desde dos arrays:

- `PRODUCTS` — un objeto por producto
- `PIEZAS_CATALOG` — un objeto por unidad del coleccionable

De ahí salen las tarjetas, los contadores, las barras y las checklists.
Mantener el catálogo es editar dos listas.

**Por qué así:** la checklist necesita saber qué piezas trae cada producto. Si
las tarjetas fueran HTML a mano, esa relación viviría en la cabeza de quien las
escribió y se rompería a la tercera tanda. Declarada como dato, marcar un
producto actualiza la checklist sola y nunca se desincroniza.

**El coste:** un error de sintaxis deja la página en blanco, porque todo se
genera en tiempo de ejecución. De ahí que el repositorio sea Git.

### Modelo de producto

```js
{ id:"linea-producto",        // <línea>-<producto>, minúsculas
  title:"NOMBRE DE LA CAJA",
  category:"CATEGORÍA",       // una de CATEGORY_ORDER
  date:"2027-04-11",          // el mes del acordeón sale de aquí
  dateType:"release",         // "release" | "preorder" (exclusivas online)
  price:2200,                 // con impuestos, o null
  priceLabel:"Premio",        // opcional: matiza o sustituye el precio
  alsoIn:["OTRA CATEGORÍA"],  // opcional: producto que pertenece a dos
  reemplaza:["id"],           // opcional: productos que trae dentro
  componentes:["pieza-no-coleccionable"],  // opcional, ver §6
  img:"...-thumb.webp",
  gallery:["....webp"],
  contains:["pieza-id","pieza-id@variante"] }
```

`date` es **la única fuente de verdad temporal**; el mes se deriva de ella al
cargar. Guardar mes y fecha por separado los deja desincronizarse.

### Modelo de pieza coleccionable

```js
{ id:"pieza-1",
  name:"Nombre visible",
  type:"familia",     // agrupa dentro del panel
  line:"DX",          // línea de producto; se contabilizan por separado
  variants:[ {id:"std", label:"Estándar"},
             {id:"special", label:"Special ver."} ] }
```

### Las tres reglas del modelo que más se prestan a error

**Líneas separadas.** Si la serie tiene dos líneas de juguete que sacan piezas
exclusivas cada una, van con contadores independientes. Fundirlas hace que "me
faltan 3" no signifique nada.

**Variantes contra piezas propias:**

| Situación | Cómo va |
|---|---|
| Misma pieza reeditada (otro acabado, edición limitada) | `variants` — una línea, cualquier versión cuenta |
| Diseños distintos que comparten nombre o procedencia | `variants` también, con sub-marcas que enlazan a su producto |
| Piezas que aluden a **personajes distintos** | entradas separadas |

**Qué alimenta la checklist principal.** Solo el coleccionable de verdad. Los
model kits y figuras de montar suelen traer miniaturas que la propia caja
advierte que no funcionan con el juguete principal: contarlas infla el progreso
con algo que no puedes usar.

---

## 3. Las checklists

Hay **dos clases y no funcionan igual**:

**Del coleccionable.** La pieza está repartida entre productos, así que ninguno
la representa. Se declara con `contains` y el progreso se **deriva**.

**De producto** (líneas de figuras, buckles, kits…). Cada producto **es** la
pieza; la checklist solo los agrupa. Aporta ver todos juntos, porque el catálogo
está ordenado por mes.

**Cada una en su pestaña, nunca apiladas.** Hay coleccionistas que siguen una
sola línea, y a esos pasar por 41 piezas del gimmick para llegar a sus cuatro
kits no les sirve. Cada checklist lleva su contador en la solapa, su texto de
ayuda y su color; el panel recuerda en cuál estabas.

**El color orienta.** Se reservan los dos tonos más fuertes para el
coleccionable principal y el resto usa tonos suaves. Con seis barras en la
cabecera, si todas gritan igual se pierde cuál importa.

**Cuidado con "cubierto":** en la tarjeta significa *no necesitas comprarlo* y
se atenúa; en la checklist significa *lo tienes* y se marca en verde. Misma
información, dos preguntas distintas.

---

## 4. Estructura de carpetas

```
SERIE/
├── index.html
├── .gitignore
├── tools/
├── CATEGORÍA EN MAYÚSCULAS/
│   ├── FICHA/                    ← consulta, NO se publica
│   ├── NOMBRE DEL PRODUCTO-Contenidos/
│   │   ├── PACKAGE.jpg           ← original, NO se publica
│   │   ├── PACKAGE.webp          ← galería, 1600 px
│   │   ├── PACKAGE-thumb.webp    ← portada, 700 px
│   │   └── 01.jpg  01.webp
│   └── PRODUCTO DE UNA IMAGEN-Contenidos.jpg   ← sin carpeta
```

**`FICHA/` es material de consulta de formato libre.** Capturas de las páginas
oficiales de donde salen fecha, precio y contenidos. A resolución original, sin
convertir, precisamente para poder leerlas. No se publican y sus nombres no
tienen que corresponderse con nada: una hoja puede cubrir una colección entera.

**Portada = `PACKAGE` si existe, si no `01`.**

**Las mayúsculas importan.** Windows es case-insensitive y el servidor no: una
mayúscula mal puesta es una imagen que funciona en tu equipo y da 404 publicada.

---

## 5. Imágenes

| Archivo | Lado máx. | Calidad | Para qué |
|---|---|---|---|
| `<nombre>.webp` | 1600 px | 80 | galería, se abre en el visor |
| `<nombre>-thumb.webp` | 700 px | 82 | portada de la tarjeta |

En Myth: portadas de 36,2 → 2,0 MB y galerías de 218 → 38 MB. Los originales no
se tocan ni se suben; su respaldo va aparte (Drive o similar).

### Cuatro trampas que costaron horas

**No pongas `loading="lazy"` en las portadas.** Las tarjetas viven dentro de un
acordeón que arranca con `max-height: 0`; el navegador las da por fuera de
pantalla y no las pide hasta que hay scroll, así que aparecen vacías. Con 62 KB
por portada, diferirlas no aporta nada.

**Las fotos de galería sí se difieren, pero de verdad:** las `<img>` se crean
sin `src` y solo se rellena al abrirlas. Con `lazy` a secas el navegador tira de
las cercanas y el ahorro se evapora.

**Nada de servir imágenes desde Drive.** Límites de peticiones y funcionan solo
para quien tiene sesión. Van junto al HTML, con **rutas relativas** — así el
sitio funciona igual bajo `/repo/` que en un dominio propio.

**Cuidado con las miniaturas que cargan la imagen grande.** Si una tira de
miniaturas de 62 px apunta al archivo de 1600 px, abrir una galería de diez
fotos son 2 MB para pintar diez cuadraditos.

---

## 6. Herramientas

Tres scripts de Python con Pillow como única dependencia:

| Script | Qué hace | Escribe |
|---|---|---|
| `audit.py` | Cruza `index.html` con el disco | nada |
| `plan.py` | Muestra qué portada y galería saldrían | nada |
| `build_all.py` | Genera los `.webp` y repunta el HTML | sí |

Los dos primeros son de solo lectura: **correrlos siempre antes**.

`audit.py` comprueba lo único que puede romper el sitio: rutas referenciadas que
no existen, `.webp` en disco que nadie usa, y carpetas con fotos que la página
ignora. Más portada determinable, numeración y duplicados.

**Una auditoría con falsos positivos es peor que ninguna.** La primera versión
contaba los `.webp` derivados como fotos y avisaba de huecos inexistentes: con
74 avisos de los que 70 eran ruido, nadie los lee.

### Verificar la cobertura comparando contenidos

Cuando un set trae dentro otro producto, se declara con `reemplaza` **en el que
absorbe**, y la cobertura es **transitiva**: basta declarar lo que se absorbe
directamente. Pero deducir eso a ojo **falló dos veces seguidas** en Myth.

Por eso, en las categorías donde ocurre, se lista además en `componentes` lo que
la caja trae y no es coleccionable. Con eso la auditoría **deduce** qué absorbe a
qué comparando conjuntos, y avisa en los dos sentidos: cobertura que falta
declarar, y cobertura declarada que el contenido no respalda.

Se limita a las categorías donde pasa. Las figuras nunca vienen dentro de otro
set, así que catalogarlas sería trabajo sin retorno.

---

## 7. Qué se publica

```
se sube          index.html + los .webp + tools/
se queda local   originales + FICHA/ + hojas de cálculo de apoyo
```

El `.gitignore` filtra por patrón, así vale para lo que añadas dentro de meses.
**Git no es la copia de seguridad** de los originales: están ignorados a
propósito y necesitan respaldo aparte.

GitHub Pages desde `main` / root. Tras un push que renombra rutas, tarda uno o
dos minutos en reconstruir: **un 404 justo después de subir no es un fallo**.

---

## 8. Nomenclatura

**La romanización sale de la caja, no de la transcripción.** En Myth tres
nombres estuvieron mal semanas hasta que las fotos de las cajas los zanjaron. Si
hay foto de la caja, manda la caja.

**Prima que se entienda sobre la fidelidad literal.** El gimmick de Myth se
romaniza oficialmente "EGZ" y se eligió escribir **Eggs**, porque son huevos y
así se lee solo.

**Decide la nomenclatura antes de publicar.** Renombrar es barato en local y
caro cuando ya hay enlaces fuera.

Nombre de carpeta: `PRODUCTO EN MAYÚSCULAS-Contenidos en Title Case`. Los `id`
internos son slugs `<línea>-<producto>`; la puntuación interna se pierde.

---

## 9. Lo que hay que decidir en cada serie

Esto es lo que **no** se hereda. Responder antes de escribir una línea:

1. **¿Cuál es el coleccionable principal?** ¿Cómo se llama en la serie, cómo se
   escribe en nuestro catálogo, y cuántos hay aproximadamente?
2. **¿Tiene familias?** En Myth eran Ride Eggs y Seed Eggs, más las versiones
   Legend. Son los grupos dentro del panel.
3. **¿Tiene líneas de producto que saquen piezas exclusivas?** En Myth, DX y SG.
   Si las hay, van con contadores separados.
4. **¿Qué categorías de producto tiene?** Las líneas de juguete, en el orden en
   que quieras verlas dentro de cada mes.
5. **¿Cuáles llevan checklist propia?** Además de la del coleccionable.
6. **¿Hay sets que traigan dentro otros productos?** Suele pasar con los
   cinturones y sus accesorios.
7. **¿Qué colores?** Los dos más fuertes para el coleccionable.
8. **Clave de `localStorage`** propia de la serie.

---

## 10. Arrancar Omegahorn

1. Copiar `index.html`, `tools/` y `.gitignore` a un repositorio nuevo.
2. Vaciar `PRODUCTS` y el catálogo de piezas.
3. Responder el cuestionario del §9 y ajustar `CATEGORY_ORDER`, los tipos y
   líneas de piezas, `PRODUCT_CHECKLISTS`, `CHECKLIST_TABS` y los colores.
4. Cambiar la clave de `localStorage` y el `<title>`.
5. Crear las categorías en mayúsculas, cada una con su `FICHA/`.
6. Cargar tandas: ficha → carpetas con fotos → `audit.py` → entradas en los
   arrays → registrar la carpeta en `CARPETA` de `plan.py` → `build_all.py`.
7. Repositorio público y GitHub Pages desde `main` / root.

**Lo que hace falta de ti para empezar:** las respuestas del §9 y la primera
tanda de fichas. Sin saber cómo se llama el coleccionable de Omegahorn y si
tiene líneas separadas, cualquier estructura que monte será a ciegas.

---

## 11. Lo que se probó y no funcionó

Vale más que la lista de aciertos.

- **Checklists apiladas en un panel.** Quien colecciona una línea no debería
  recorrer las demás para llegar a la suya.
- **Desplegable de galería en la tarjeta.** Una tira de miniaturas por tarjeta
  metía una fila de ruido en todas. Se sustituyó por pulsar la portada, que abre
  un visor en superposición.
- **Una página por producto.** Es una checklist, no una tienda.
- **Entradas separadas enlazadas con un campo `related`.** Ocupaban tres líneas
  del panel repitiendo enlaces cruzados.
- **Etiqueta "Estimado"** para datos sin confirmar. Si un dato no está
  confirmado, o se omite o se pone sin anunciarlo.
- **Enlaces de Drive** como origen de las imágenes.
- **Fiarse de una hoja de cálculo de apoyo para los nombres.** Sirve para fechas
  y precios; para nomenclatura transcribe mal la mitad.
- **Exigir que cada ficha se llamara igual que un producto.** Regla inventada
  que hizo gritar a la auditoría durante días.
