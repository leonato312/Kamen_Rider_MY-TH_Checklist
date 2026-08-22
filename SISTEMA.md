# Cómo funciona este sistema

Guía para reconstruirlo de cero cuando salga la próxima temporada de Kamen Rider.
No es documentación de código: es **por qué está hecho así**, que es lo que no se
deduce mirando los archivos.

Escrito el 2026-08-22, con el catálogo de Myth ya publicado y funcionando.

---

## 1. Qué problema resuelve

Dos preguntas, en este orden de importancia:

1. **¿Cuándo llega la próxima wave?** Por eso el mes es la categoría raíz y todo
   cuelga de la fecha.
2. **¿Qué gimmicks me faltan?** Los coleccionables de la temporada son decenas y
   vienen repartidos entre sets, cajas sorpresa y exclusivas. Rastrearlos a mano
   es inviable; rastrear los drivers o las figuras, no, porque son pocos.

Todo lo demás del diseño sale de servir a esas dos preguntas. Si la próxima
temporada tiene otro gimmick coleccionable masivo, el sistema sirve tal cual
cambiando los nombres. Si no lo tiene, la checklist sobra y el sistema se reduce
a un calendario.

---

## 2. La decisión que lo sostiene todo

**La página es un archivo HTML que se genera desde dos arrays de datos.**

No hay tarjetas escritas a mano. `index.html` contiene:

- `PRODUCTS` — un objeto por producto
- `EGGS_CATALOG` — un objeto por pieza coleccionable

y de ahí se dibuja el catálogo entero, los contadores, las barras de progreso y
la checklist. Mantener el catálogo es editar dos listas.

**Por qué importa:** la checklist tiene que saber qué piezas trae cada producto.
Si las tarjetas fueran HTML escrito a mano, esa relación viviría en la cabeza del
que las escribió y se rompería a la tercera wave. Al declararla como dato
(`contains: [...]`), marcar un producto como obtenido actualiza la checklist sola
y nunca se desincroniza.

**El coste:** un error de sintaxis en los datos deja la página en blanco, porque
todo se genera en tiempo de ejecución. De ahí que el repositorio sea Git: revertir
es inmediato.

Sin frameworks, sin build, sin dependencias. Un archivo que se abre con doble clic
y funciona igual en local que publicado.

---

## 3. El modelo de datos

### Producto

```js
{ id:"dx-rider-eggs-set-01",              // <línea>-<producto>, minúsculas
  title:"DX RIDER EGGS SET 01",           // el nombre de la caja
  category:"DX SETS",                     // una de CATEGORY_ORDER
  date:"2026-09-05",                      // el mes del acordeón sale de aquí
  dateType:"release",                     // "release" | "preorder" (P-Bandai)
  price:2200,                             // yenes con impuestos, o null
  priceLabel:"Premio de campaña",         // opcional: sustituye o matiza el precio
  alsoIn:["TAF"],                         // opcional: productos que son de dos categorías
  img:"DX SETS/.../PACKAGE-thumb.webp",   // portada de la tarjeta
  gallery:["...PACKAGE.webp", "...01.webp"],
  contains:["ride-eggs-8","kuuga-ride-eggs"] }
```

**`date` es la única fuente de verdad temporal.** El mes se deriva de ella al
cargar (`p.month = p.date.slice(0,7)`). Guardar mes y fecha por separado los deja
desincronizarse tarde o temprano.

**`dateType: "preorder"`** existe porque Premium Bandai no tiene fecha de tienda,
tiene fecha de reserva. Se trata como equivalente al release y se marca con badge
para no confundir.

### Pieza coleccionable

```js
{ id:"ride-eggs-4",
  name:"Ride Eggs 4",
  type:"ride-eggs",       // agrupa dentro del panel
  line:"DX",              // DX y SG se contabilizan por separado
  variants:[ {id:"std", label:"Estándar"},
             {id:"special", label:"Special ver."} ] }
```

`contains` las referencia como `"id"` o `"id@variante"`.

### Las tres decisiones difíciles del modelo

**Líneas separadas.** DX y SG llevan contadores independientes porque cada línea
saca piezas que la otra no. Fundirlas haría que "me faltan 3" no significara nada.

**Variantes contra piezas propias.** Es lo que más se presta a error:

| Situación | Cómo va |
|---|---|
| Misma pieza, otro acabado (`special ver.`, `Gold ver.`) | `variants` — una línea, cualquier versión cuenta |
| Diseños distintos que comparten nombre | `variants` también, con sub-marcas que enlazan a su producto |
| Piezas que aluden a **riders distintos** (`Ride Eggs 1` vs `Ride Eggs 1 Origin`) | entradas separadas |

Se probó un campo `related` con entradas independientes enlazadas entre sí. Se
descartó: ocupaba tres líneas del panel repitiendo enlaces cruzados, peor de leer
que el problema que resolvía.

**Productos que absorben a otros.** Un set deluxe suele traer dentro el producto
base. Se declara con `reemplaza: ["id", ...]` **en el que absorbe**, no en el
absorbido: cuando salga un driver nuevo se toca un sitio, en vez de editar todo
lo que deja obsoleto. **La cobertura es transitiva** — si el Narikiri absorbe al
MY-TH & RID SET, y ese absorbía al Driver suelto y al Hammer Bone Buckle, tener
el Narikiri los cubre los cuatro. Cada set declara solo lo que absorbe
directamente.

**Y se verifica solo.** En los productos donde esto ocurre —Drivers y Buckles—
se lista además el contenido no coleccionable en `componentes`. La auditoría
compara contenidos y **deduce** qué caja absorbe a cuál, avisando tanto de la
cobertura que falta declarar como de la declarada que el contenido no respalda.
La declaración sigue moviendo la interfaz; los contenidos la vigilan. Se llegó
aquí después de equivocarse dos veces deduciendo la cadena a ojo.

Al documentar una caja hay que anotar **todo lo que trae**, no solo los
coleccionables: un set que incluye un buckle deja sin sentido comprar ese buckle
suelto, y eso es fácil pasarlo por alto cuando la atención está en el gimmick
principal. El producto cubierto no se marca como obtenido —no lo
tienes— sino que se atenúa y avisa de en qué caja viene; sí cuenta en el
contador del mes, que responde a "¿me queda algo por comprar?".

**Qué alimenta la checklist y qué no.** Solo los gimmicks de la temporada. Los
model kits y las figuras de montar traen miniaturas que la propia caja advierte
que no funcionan con el driver — contarlas inflaría el progreso con algo que no
puedes usar. Se catalogan, se marcan, pero no suman.

---

## 4. La estructura de carpetas

```
PROYECTO/
├── index.html
├── .gitignore
├── tools/
├── CATEGORÍA EN MAYÚSCULAS/
│   ├── FICHA/                        ← consulta, NO se publica
│   │   └── cualquier cosa
│   ├── NOMBRE DEL PRODUCTO-Contenidos/
│   │   ├── PACKAGE.jpg               ← original, NO se publica
│   │   ├── PACKAGE.webp              ← galería, 1600 px
│   │   ├── PACKAGE-thumb.webp        ← portada, 700 px
│   │   ├── 01.jpg  01.webp
│   │   └── 02.jpg  02.webp
│   └── PRODUCTO DE UNA SOLA IMAGEN-Contenidos.jpg   ← sin carpeta
```

**`FICHA/` es material de consulta de formato libre.** Capturas de las páginas de
Bandai de donde salen fecha, precio y contenidos. Se guardan a resolución original
—sin convertir a WebP— precisamente para poder leer los datos. No se publican, y
sus nombres no tienen que corresponderse con nada: una sola hoja puede cubrir una
colección de diez tipos.

Costó llegar aquí. La primera versión exigía una ficha por producto con el mismo
nombre, y la auditoría se pasó días gritando por una regla inventada.

**Portada = `PACKAGE` si existe, si no `01`.** Regla deliberada.

**Las mayúsculas importan.** Windows es case-insensitive y GitHub Pages no: una
mayúscula mal puesta es una imagen que funciona en tu equipo y da 404 publicada.
Es el fallo más traicionero de todo el sistema.

---

## 5. Las imágenes

Los originales pesan cientos de megas. Publicarlos tal cual es inviable: 34
portadas a 1 MB son 36 MB solo para pintar la primera pantalla.

**Dos derivados por foto:**

| Archivo | Tamaño | Calidad | Para qué |
|---|---|---|---|
| `<nombre>.webp` | 1600 px | 80 | galería, se abre en el visor |
| `<nombre>-thumb.webp` | 700 px | 82 | portada de la tarjeta |

Resultado en Myth: **portadas de 36,2 MB a 2,0 MB** (94% menos) y **galerías de
218 MB a 38 MB** (83%). Los originales no se tocan y no se suben; el respaldo va
por otro lado (Google Drive, en este caso).

**700 px para una tarjeta de 252 px** porque en pantallas retina se ve al doble.

### Tres trampas que costaron encontrar

**No pongas `loading="lazy"` en las portadas.** Las tarjetas viven dentro de un
acordeón que arranca con `max-height: 0`. El navegador las considera fuera de
pantalla y no las pide; al abrir el mes no siempre re-evalúa hasta que hay scroll,
así que las tarjetas aparecen vacías hasta que mueves el ratón. Con 62 KB por
portada, diferirlas no aportaba nada.

**Las fotos de galería sí se difieren, pero de verdad.** No basta con `lazy`: las
`<img>` se crean sin `src` y solo se rellena al abrir el visor. Si dejas el `src`
puesto, el navegador empieza a tirar de las cercanas y el ahorro se evapora.

**Google Drive no sirve como hosting de imágenes.** Los enlaces `uc?export=view`
van con límite de peticiones y suelen funcionar solo para quien tiene sesión
iniciada. Las imágenes van junto al HTML, con rutas relativas.

**Rutas relativas, siempre.** Así el sitio funciona igual bajo `usuario.github.io/repo/`
que en la raíz de un dominio propio. Con rutas absolutas, añadir un dominio
rompería todas las imágenes.

---

## 6. Las herramientas

Tres scripts de Python en `tools/`, con Pillow como única dependencia:

| Script | Qué hace | Escribe |
|---|---|---|
| `audit.py` | Cruza `index.html` con el disco | nada |
| `plan.py` | Muestra qué portada y galería saldrían | nada |
| `build_all.py` | Genera los `.webp` y repunta el HTML | sí |

**Los dos primeros son de solo lectura y se corren siempre antes.** Un simulacro
que imprime lo que haría, se revisa, y solo entonces se ejecuta.

**`audit.py` comprueba lo único que puede romper el sitio:** rutas que la página
referencia y no existen, `.webp` en disco que nadie usa —peso muerto en el
repositorio— y carpetas con fotos que la página ignora. Más portada determinable,
numeración sin huecos y duplicados entre categorías.

Lección aprendida por las malas: **una auditoría que da falsos positivos es peor
que no tenerla.** La primera versión contaba los `.webp` derivados como si fueran
fotos y avisaba de huecos inexistentes en las 34 galerías; con 74 avisos de los
que 70 eran ruido, nadie los lee.

---

## 7. Qué se publica y qué no

```
se sube          index.html + los .webp + tools/          ~43 MB
se queda local   originales JPG/PNG + FICHA/ + xlsx      ~238 MB
```

El `.gitignore` lo resuelve por patrón, así que vale igual para los productos que
añadas dentro de seis meses.

**Git no es tu copia de seguridad.** Los originales están ignorados a propósito;
necesitan respaldo aparte.

Publicado con GitHub Pages desde `main` / root. Tras un push que renombra rutas,
Pages tarda uno o dos minutos en reconstruir: **un 404 justo después de subir no
es un fallo**, es que aún no ha republicado.

---

## 8. Nomenclatura

**La romanización sale de la caja, no de la transcripción.** En Myth, tres nombres
estaban mal durante semanas —MYTH, MAO y RIDO— hasta que las cajas de TAF
mostraron que Bandai escribe **MY-TH**, **MAOU** y **RID**. Si hay foto de la caja,
manda la caja.

**Prima que se entienda sobre la fidelidad literal.** El gimmick es エグズ, que
Bandai romaniza **EGZ**. Se eligió **Eggs** porque son huevos y así se lee solo.
Del mismo modo, "Myceed" pasó a "Myth Seed".

**Los identificadores internos son slugs**, `<línea>-<producto>` en minúsculas. La
puntuación interna se pierde: MY-TH queda como `myth`, porque ahí el guion ya es
separador de palabras.

**Decide la nomenclatura antes de publicar.** Renombrar después es barato en local
y caro una vez hay enlaces fuera.

---

## 9. Levantar el repositorio de una temporada nueva

1. **Copiar `index.html` y `tools/`.** Vaciar `PRODUCTS` y `EGGS_CATALOG`, ajustar
   `CATEGORY_ORDER` a las líneas de juguete de la temporada y `EGGS_TYPES` /
   `EGGS_LINES` al gimmick que toque. El resto del código no cambia.
2. **Renombrar la clave de `localStorage`** (`krmyth-catalog-v1`). Si dos catálogos
   comparten dominio y clave, se pisan el estado.
3. **Fijar la nomenclatura** mirando cajas reales, y anotarla.
4. **Crear las categorías en mayúsculas**, cada una con su `FICHA/`.
5. **Copiar el `.gitignore`.**
6. Ir cargando waves: ficha, carpetas con fotos, `audit.py`, entradas en los
   arrays, registrar la carpeta en el diccionario `CARPETA` de `plan.py`,
   `build_all.py`.
7. **Repositorio público y GitHub Pages** desde `main` / root.

Ver `tools/README.md` para el procedimiento detallado de cada wave.

---

## 10. Lo que se probó y no funcionó

Vale más que la lista de aciertos, porque evita repetirlos.

- **Desplegable de galería en la tarjeta.** Tira de miniaturas dentro de cada
  tarjeta: metía una fila de ruido en las 46. Se sustituyó por pulsar la portada,
  que abre un visor en superposición.
- **Una página por producto.** Nunca se hizo, y se descartó de entrada: es una
  checklist, no una tienda. Todo ocurre en la misma página.
- **Entradas separadas enlazadas con `related`.** Ver sección 3.
- **Etiqueta "Estimado"** para datos sin confirmar. Se retiró: si un dato no está
  confirmado, o se omite o se pone sin anunciarlo.
- **Enlaces de Google Drive** como origen de las imágenes.
- **Confiar en el `.xlsx` de apoyo para los nombres.** Servía para fechas y precios;
  para nomenclatura transcribía mal la mitad.
