# Kamen Rider Myth — checklist de merchandising

Punto de entrada de este repositorio. La arquitectura —qué se cataloga, cómo
se ordena, cómo funcionan el catálogo central y la barra lateral— vive en los
documentos maestros de `D:\DG\` (`MAESTRO-1-CHECKLIST.md`,
`MAESTRO-2-INVESTIGACION.md`, `MAESTRO-3-CODIFICACION.md`) y **son la
autoridad**. Este archivo recoge únicamente lo que queda fuera de su alcance:
el cuestionario del maestro respondido para Myth, las excepciones reales que
Myth se ganó por haberse publicado antes de que los maestros existieran, y las
lecciones de esta serie en concreto.

Myth fue el primer repositorio migrado a la arquitectura de los maestros, y
también el primero en probar el pivote de enciclopedia (§10.2). Lo que se
aprendió en el camino ya está incorporado a los maestros; aquí solo queda el
resto de la historia.

---

## 1. Identidad y excepciones declaradas

- **Franquicia · Serie:** Kamen Rider · Myth
- **Repositorio:** `leonato312/Kamen_Rider_MY-TH_Checklist`
- **Sitio:** https://leonato312.github.io/Kamen_Rider_MY-TH_Checklist/
- **Clave de estado:** `krmyth-catalog-v1`
- **Estado:** `abierto` — sigue recibiendo waves

**Ninguno de los dos primeros sigue la convención** (`Kamen-Rider_Myth_Checklist`
/ `myth-catalog-v1`), y es a propósito (Maestro 3 §10): este repositorio se
publicó antes de que la convención existiera, la web está en línea y
compartida, y ya tiene visitantes con checklist guardada. Renombrar el repo
deja la dirección vieja en 404; cambiar la clave no da error, deja la página
en blanco al visitante con lo que llevaba marcado inaccesible bajo la clave
vieja. **Ninguna de las dos se toca nunca.**

---

## 2. Cuestionario del maestro, respondido

**Coleccionable principal:** los **Eggs**, en dos familias — **Ride Eggs**
(numerados, más las versiones Legend Rider) y **Seed Eggs** (temática animal,
más las Legend). Es el gimmick masivo. El menor son los **Bone Buckles**.
47 filas en total (41 DX, 6 SG).

**Por qué "Eggs" y no otra transcripción:** Bandai escribe エグズ, en alfabeto
latino EGZ (el título de SO-DO es `装動 仮面ライダーマイス EGZ1`). Se descartó
EGZ por opaco y "Ex" por ser una transcripción inicial; se eligió **Eggs**
porque son huevos y así se lee solo. Del mismo modo "Myceed" se occidentalizó
a **"Myth Seed Eggs"**.

**Categorías declaradas** (`ROTULOS` en `serie.py`): Protagonista → Riders,
Dispositivo → Drivers, Arma → Armas, Gimmick → Eggs & Buckles, Apariciones y
Extras sin producto todavía. `mecha` se omite: Myth no tiene mechas.

**Las 4 declaradas son interactivas** (Maestro 1 §3): las 47 tarjetas se
marcan en el catálogo central y alimentan la barra lateral por igual, sin
reglas especiales por categoría.

**Riders (8):** MY-TH (マイス), MAOU (マオウ), DATT, RID (リド), JAO, TIGUL,
MUTON, VANKEN — romanización de la caja. Cada uno existe en una o varias
líneas (TAF, Soft Vinyl, SO-DO, SG Model Kits); cada línea es su propia fila.

**Dispositivo (1 objeto, 3 filas):** MY-TH Driver, en DX, SG Model Kits y SG
Model Kits (Hammer On) — mismo objeto, tres acabados/procedencias. Más 3
accesorios de dispositivo que no son arma ni gimmick: MY-TH Phone, Expack,
Hokokuro (dispositivo de brazo con gimmick de sellos — decisión del usuario,
manda sobre lo que sugiera la foto).

**Armas (4):** MY-TH Edge suelta, más Rabbit Sword, Snake Size y Dog Gun, que
vienen las tres en el Twelve Zodiac Alliance Rider Weapons Set 01.

**Procedencias usadas:** `taf`, `sofv` (1·Protagonistas) · `sodo`, `sg-kit`,
`sg-random` (2·Protagonistas/Dispositivos vía SG) · `dx`, `dx-random`,
`buckles` (3·Gimmick/Armas/Dispositivos vía DX) · `promo` (Gimmick). `sg-kit`
y `sg-random` van separadas aunque compartan el sello SG: una se elige, la
otra es azar (Maestro 1 §5.1, aportado desde aquí).

**Paleta:** dos tonos fuertes reservados al coleccionable principal — ámbar
para la línea DX, cian para la línea SG — y tonos suaves para el resto de
categorías (uno por categoría, no por procedencia).

**Sets que absorben otros productos:** el DX Narikiri Set absorbe al DX RID
SET, que a su vez absorbe al DX Driver suelto y al Hammer Bone Buckle; el
Slashbone Buckle set es independiente. La cobertura es transitiva —cada uno
declara solo lo que absorbe directamente— y cada absorbente declara en
`contains` **todo** lo que entrega, incluida la pieza del dispositivo que
absorbe (ver §10.2, fue un error real).

---

## 3. Decisiones propias de Myth, con su porqué

**Entrega de las random box.** Las tres cajas sorpresa (`dx-random-box-01/02`,
`sg-random-box-01`) van `entrega:"incierta"`: marcar la caja cuenta una de sus
piezas posibles, sin decir cuál, y quedan fuera de la deducción de cobertura
en los dos sentidos (Maestro 1 §2.1/§2.3).

**SCRATCH CARDDASS se queda, retitulado como campaña.** El maestro saca el TCG
del catálogo, pero esta ficha no cataloga cartas: cataloga el **premio** de la
campaña, un Ride Eggs 1 (Gold ver.) físico, y es su única vía de obtención. Va
como `promo`, igual que TELEVI-KUN (premio de revista).

**`HOKOKURO` no es arma.** Es un dispositivo de brazo con gimmick de sellos.
La categoría que le puso el usuario manda sobre lo que sugiera la foto.

**Sin galería desplegable en la tarjeta.** Se probó una tira de miniaturas y
se quitó: metía una fila de ruido en las 47. Las fotos se abren pulsando la
portada, que lanza un visor en superposición. Nunca una segunda página por
producto: es una checklist, no una tienda.

**El `.xlsx` de apoyo** sirve para fechas y precios. Para nombres transcribe
mal la mitad (Dad/Maoh/Lido/Tigre por Datt/Maou/Rid/Tigul, "Ride Exe" por Ride
Eggs) — mandan los nombres de las cajas, extraídos a mano.

---

## 4. Puntos abiertos

- **SO-DO está incompleto.** Los tipos 9 y 10 siguen sin revelar y la fecha
  del 15 de septiembre es una estimación: la ficha solo dice "septiembre 2026".
- **`SHF` no está dada de alta.** La línea existe pero no tiene ningún
  producto todavía; una procedencia sin ficha no se declara (Maestro 1 §4.2).
  El día que entre su primer producto, cada figura suya añade una fila `shf`
  a su rider correspondiente.
- **Los originales en alta resolución y los `FICHA/` no están respaldados en
  ningún repositorio Git** (correcto: `.gitignore` los excluye a propósito,
  Maestro 3 §10). Verificar que el respaldo de Google Drive del usuario los
  tiene antes de necesitarlos para una wave nueva.

---

## 5. Errores que costaron tiempo

**Un ternario compacto disparó un falso ALTO en `audit_maestro.py`.** El check
que cuenta productos busca el patrón textual `title:`; un `fuente?fuente.title:""`
en el propio motor coincide con ese patrón sin ser un producto. Se corrigió el
check con una exclusión `(?<!\.)` en vez de retorcer el código para
esquivarlo — el síntoma se corrige en la herramienta, no en el dato.

**Un nombre de función cambiado rompió un check del maestro.** `audit_maestro.py`
comprobaba la ausencia de una restricción buscando literalmente el string
`entregaGimmick` en el código; al generalizar esa función bajo otro nombre, el
check se disparó igual sin que hubiera ningún problema real. Se corrigió para
que inspeccione el cuerpo real de la función, no su nombre.

**Un producto sin subcarpeta numerada rompió su portada silenciosamente.**
`MY-TH FIRST KIT 02` vivía en una subcarpeta pero sus imágenes conservaban el
nombre largo del producto en vez de `00`/`00-thumb`; `index.html` lo
referenciaba como archivo suelto. `check_urls.py` no lo vio (las mayúsculas
cuadraban), `audit.py` sí, con dos avisos distintos que apuntaban al mismo
origen.

**Deducir a ojo qué set absorbe a cuál falló dos veces seguidas**, antes del
pivote a `PIEZAS_CATALOG`. Por eso `componentes` existe y la auditoría
**deduce** la cobertura comparando contenidos en vez de fiarse de lo declarado
a mano.

---

## 6. Lo que se probó y no funcionó

- **Restringir el marcado a una sola categoría (solo Gimmicks).** Diagnóstico
  correcto —el proyecto se había diluido dando checklist a todo sin un motor
  común—, cura mal dirigida —reducir alcance en vez de unificar el mecanismo.
  Revertido: las 7 categorías comparten un solo motor (Maestro 1 §1, §3).
- **Calendario de waves como vista principal.** Fue la pregunta fundacional
  del proyecto y funcionó bien con 46 productos en cinco meses, pero no
  escala a una franquicia con décadas de trasfondo (otros riders, sentai):
  demasiados acordeones de mes. Sustituido por catálogo central navegado por
  categoría → procedencia, con una caja de "nuevos lanzamientos" que solo se
  dibuja cuando el repositorio se declara `cerrado` (§7 del maestro).
- **Checklists apiladas en un solo panel sin pestañas.** Quien colecciona una
  línea no debería recorrer las demás para llegar a la suya — de ahí las
  pestañas por categoría en la barra lateral.
- **Desplegable de galería en la tarjeta del catálogo.** Una fila de ruido en
  todas las tarjetas.
- **Una página por producto.** Descartada de entrada: es una checklist.
- **Exigir que cada ficha de referencia se llamara igual que un producto.**
  `FICHA/` es de formato libre; la regla inventada disparó avisos falsos
  durante días antes de corregirla.
- **Fiarse del `.xlsx` para los nombres de producto.** Transcribe mal la
  mitad; mandan los nombres extraídos a mano de las cajas.
