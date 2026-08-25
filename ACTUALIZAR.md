# Actualización — Kamen Rider Myth

> **Esto es una guía, no un parche.** No lo apliques al pie de la letra: las
> cifras y los nombres son de Gavan Infinity, y algunas cosas aquí **no te
> tocan**. Lee el §3 antes de tocar nada.
>
> **Y no es el destino final.** El encargo de verdad está en el §5: fundir toda
> tu documentación en **un solo md**, que es lo que heredará el próximo
> repositorio.

Sustituye a la versión anterior de este archivo, que ya está aplicada.

---

## 1. Lo que ha cambiado en Gavan Infinity

Cinco cosas de uso general, todas salidas de tropezar con ellas:

| Qué | En una línea |
|---|---|
| **Un solo md por repositorio** | los cinco documentos se fundieron en `Gavan-Infinity.md` |
| **La checklist se pliega por línea** | 129 piezas en un scroll eran 152 elementos |
| **Las reediciones son versiones, no piezas** | y la referencia lleva `@` siempre |
| **Colección contra familia** | la familia solo ordena dentro de una línea |
| **El límite de barras de la cabecera hay que medirlo** | el que teníais escrito estaba mal |

---

## 2. Lo que sí te toca, con tus propios números

### 2.1 El `@` desnudo — esto es concreto y es tuyo

`SISTEMA.md` §3 fija que una reedición va como `variants`. Bien. Pero la
referencia se escribe de dos formas distintas en el mismo catálogo, y **una
pieza las mezcla consigo misma**:

| Pieza | Referencias desnudas | Con `@std` |
|---|---|---|
| `ride-eggs-1` | **3** | 0 |
| `ride-eggs-4` | **1** | 2 |
| `ride-eggs-11` | 0 | 1 |

Las cuatro desnudas funcionan —el motor las normaliza— pero se leen mal: parecen
declarar *la pieza* cuando declaran *una versión*. Y `ride-eggs-4` es el caso
feo: el mismo id escrito de las dos maneras según el producto.

**La regla que conviene fijar:** si la pieza declara `variants`, su referencia
lleva `@` siempre, también `@std`. Son cuatro ediciones, ningún cambio de
motor.

### 2.2 Plegar la checklist de Eggs por línea

Tus 41 Eggs son **35 en DX y 6 en SG**, y la línea DX se reparte en cinco tipos.
Dibujado de una vez, eso es un muro — y es tu propio `SISTEMA.md` §4 el que dice
que apilar así estaba mal.

La solución es la misma máquina que ya tienes en el acordeón de meses,
`max-height` + `data-open`, aplicada a la sección de línea, con lo abierto
guardado en el estado. **Cerrada no puede esconder el resumen:** el encabezado
mantiene nombre, contador y barra. Y en la primera visita, todas cerradas: dos
barras juntas ya son la respuesta.

Con dos líneas gana menos que con cinco, pero la DX con 35 piezas lo justifica
sola.

### 2.3 El límite de la cabecera estaba mal, y era vuestro

`SISTEMA.md` §4 dice: *«A partir de la séptima ocupará dos líneas casi
siempre»*. Gavan Infinity llegó a siete y **sí caben a 1280 px**. Lo que sí
fallaba estaba más abajo: entre 1081 y 1279 quedaba una barra huérfana en una
segunda fila, porque el responsive solo bajaba las barras a fila propia por
debajo de 1080.

Arreglo: subir ese umbral, **en su propia consulta** para no adelantar el resto
del responsive.

**Tú tienes seis barras.** Comprueba la banda entre tu breakpoint y 1280 antes
de dar por bueno el número; puede que ya te esté pasando.

### 2.4 Colección contra familia

**Si dos grupos se compran por separado y no comparten línea, son colecciones
distintas.** La familia solo sirve para ordenar dentro de una misma línea.

En Gavan, cinco piezas repartidas entre tres líneas quedaban invisibles como
familia: agrupando primero por línea, no había forma de verlas juntas. Tu
equivalente son los `EGGS_TYPES`: si alguno se compra por su cuenta y aparece en
DX y en SG, hoy no se puede ver entero.

### 2.5 Una comprobación más para la auditoría

Avisa de un tipo usado sin etiqueta, pero no del caso contrario: **una familia
declarada que ya ninguna pieza usa**. Como no dibuja nada, se queda ahí para
siempre sin que nada la delate. Es un aviso en BAJO —no rompe, solo miente sobre
cómo está organizada la colección—.

---

## 3. Lo que NO te toca

- **La trampa del parser de piezas con `variants`.** Tu `audit.py` no parsea el
  catálogo de piezas; ese parser es un añadido de Gavan. Si algún día se lo
  pones, que exija `name` detrás de `id` **con un lookahead**: consumirlo deja
  el cuerpo sin el campo y revienta igual.
- **`CATEGORY_BADGE`, `exclusiva`, `reservas`, `LINE_LABEL`.** Ya estaban en la
  actualización anterior.
- **El modelo con `collection`.** Sigues teniendo una sola colección repartida.

---

## 4. Verificar

```bash
python tools/audit.py
python tools/check_urls.py
```

Y **ejecuta la lógica, no la leas**: marca una caja en el navegador, recarga, y
mira que la checklist siga diciendo lo mismo. Los fallos de esta clase no se ven
leyendo el código.

Aviso del que se aprendió por las malas: **las transiciones CSS no avanzan en
una pestaña en segundo plano.** Si un acordeón parece no abrirse, comprueba eso
antes de buscar el fallo en tu CSS.

---

## 5. El encargo de verdad: un solo md

Hoy tienes `SISTEMA.md`, `PROJECT-RED.md`, `tools/README.md` y este archivo. Se
solapan, y mantener varios es cómo se desincronizan.

**Fúndelos en un único documento llamado `Myth.md`** (o como quieras referirte a
esa conversación), que sea el punto de entrada para cualquier actualización,
mejora o investigación. Lo que debe llevar dentro:

1. Qué es esto y cómo se mantiene.
2. El motor: estructura, la regla de oro del estado, el modelo de datos.
3. De dónde salen los datos y las imágenes, con sus trampas.
4. Qué se decidió en Myth **y por qué** — MY-TH, MAOU y RID salidos de las
   cajas, el `related` descartado, la etiqueta «Estimado» retirada.
5. Lo aprendido: los errores y lo que se probó y no funcionó.

**Escríbelo para heredarse.** La serie siguiente copia ese archivo, lo renombra
y sustituye la parte que es solo tuya. Todo lo demás debe servirle tal cual.

Y borra al terminar: `PROJECT-RED.md`, `tools/README.md`, `ACTUALIZAR.md` y
`SISTEMA.md` una vez volcados. **Si queda un `.md` suelto en la raíz, no es un
segundo documento: es algo pendiente de bajar y borrar.**
