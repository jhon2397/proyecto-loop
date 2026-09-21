# Estructura estándar, corrida entregable y pitch — Diseño

**Fecha:** 2026-09-19 · **Versión objetivo:** `proyecto-loop` v0.7.0 (desde v0.6.1)

**Goal:** que todo proyecto nacido del loop tenga la misma estructura, que la decisión
de dónde vive Supabase en producción se tome siempre y quede trazable, que una corrida
del loop entregue código usable y probado en los cuatro dispositivos reales que tenemos,
y que el producto terminado se pueda presentar con una pieza animada que use su propio
design system.

## Decisiones de arquitectura

**A. Extender, no agregar etapas.** Los puntos 1, 2 y 3 son reglas de las etapas que ya
existen, no etapas nuevas: se escriben dentro de `project-init`, `plan-architect`,
`code-exec`, `loop-verify` y `project-loop`. Se suma **una sola skill nueva**,
`loop-pitch`, porque genera un artefacto para humanos que hoy no tiene dueño. Alternativa
descartada: `loop-structure` + `loop-devices` como etapas propias — agregarían dos pasos
al ciclo para algo que son condiciones de etapas existentes, sobre un arsenal que ya
tiene 13 skills.

**B. Cadencia de la matriz de dispositivos: los cuatro en cada tarea.** Se evaluó la
alternativa más barata (un dispositivo primario por tarea, matriz solo al cerrar) y se
descartó: deja que un bug de forma —layout roto en tablet, safe area de iPad— aparezca
recién al final, cuando ya hay pantallas construidas sobre el patrón defectuoso. El
criterio es minimizar errores, no minimizar minutos.

El costo es real y se administra con dos optimizaciones que forman parte del diseño, no
son un detalle de implementación:

- **Pares secuenciales, no los cuatro vivos.** Medido el 2026-09-21: cuatro emuladores
  simultáneos dejan 267 MB libres de 24 GB, con el swap al 95%, antes de compilar nada.
  Se corre el par Android, se apaga, se corre el par iOS. Dentro de cada par se bootea una
  vez. La cobertura por tarea no cambia; la simultaneidad sí.
- **Rebuild nativo solo cuando cambia lo nativo.** Si la tarea toca únicamente JS/TS, se
  reusa el binario ya instalado y se recarga el bundle. El build nativo completo se paga
  solo cuando cambian dependencias nativas o configuración de Expo.

Sin estas dos, la matriz por tarea es inviable; con ellas, el costo por tarea baja a
instalar bundle y correr los flows.

**C. El flujo de diseño ya existe; lo que le falta es estructura.** El punto 2 del pedido
original (UX con skills de diseño plasmado en Figma) lo cubre `loop-design` desde v0.6.1
y no se rediseña. Lo que se le agrega es la **estructura del archivo de Figma** (sección
4): páginas fijas y convención de nombre de frame. Sin eso, el mapa pantalla ↔ nodo que
consume la implementación depende de nombres improvisados y se rompe en silencio.

## Constraints

Heredados del arsenal (siguen vigentes):

- Idioma de todos los prompts de skills: **español**.
- Toda skill es **idempotente y reanudable**: lee `.loop/state.md` y completa el delta.
- El fix va **al repo con bump de versión**; editar `~/.claude/plugins/cache/<version>/`
  se pierde en la próxima actualización.
- Una etapa que otra skill **encadena** nunca lleva `disable-model-invocation: true`;
  el flag es para puntos de entrada.
- El repo es **público**: no commitear nombres internos de repos ni del servidor de deploy.
- Las skills cargan al inicio de sesión: todo cambio exige resync del marketplace + sesión nueva.
- Cada tarea termina en un commit atómico.

Nuevos:

- La estructura estándar es **una sola fuente de verdad** (`templates/estructura/monorepo.md`).
  Ninguna skill la describe por su cuenta; la leen de ahí.
- Ninguna carpeta se crea vacía "por las dudas". Estructura fija significa *mismo lugar
  cuando existe*, no *todas siempre*.

---

## 1. Estructura estándar del proyecto

Monorepo con npm workspaces. Árbol canónico:

```
<proyecto>/
├── .loop/                   estado del loop (state, analysis, design, plan, adr/, stack…)
├── .claude/                 reglas, permisos, hooks (los instala loop-rules)
├── apps/
│   ├── mobile/              Expo + React Native + TS   ← siempre Expo, sin excepción
│   └── web/                 Next.js + TS
├── packages/
│   ├── core/                dominio, tipos, validadores + ADAPTADOR de datos (Tier 1)
│   └── ui/                  design system en código ← materializa .loop/design-system.md
├── supabase/                migrations/ · functions/ · seed.sql · config.toml
├── infra/                   docker-compose de self-host (solo si el hosting es self-hosted)
├── e2e/                     flows de la matriz de dispositivos
├── docs/
│   └── pitch/               presentación HyperFrames
└── .github/workflows/
```

**`packages/core` es donde vive el adaptador de Supabase** que Tier 1 ya cablea. Deja de
ser "una capa" conceptual y pasa a tener dirección fija: el dominio importa de `core`,
nunca llama a Supabase directo. `packages/ui` es la contraparte: el design system de
`.loop/design-system.md` llevado a código, que toda pantalla reusa.

**Pregunta obligatoria de mobile.** `project-init` pregunta siempre si el proyecto tendrá
mobile — no lo infiere del nombre ni de la descripción. La respuesta decide si nace
`apps/mobile` y queda en `state.md` como `mobile: si|no`. Si es `si`, el stack es
**Expo**, no se discute ni se ofrecen alternativas.

Carpetas que el proyecto no usa no se crean. Un proyecto solo-mobile no tiene `apps/web`;
uno con Supabase cloud no tiene `infra/`.

## 2. Supabase: self-hosted vs cloud

Es una decisión de **dónde corre Supabase en producción**, no de entorno de desarrollo.
En desarrollo se usa el CLI local con Docker en los dos casos.

`project-init` la plantea siempre, con las dos consecuencias reales:

- **Self-hosted en el servidor interno** — Supabase en Docker detrás de Caddy, siguiendo
  el patrón `/opt/<PROYECTO>` de los demás deploys. Se scaffoldea `infra/` con su compose.
  Cuesta operarlo (backups, updates, disco); no cuesta licencias ni saca datos de la red interna.
- **Supabase Cloud** — proyecto gestionado, sin `infra/`. Menos operación; los datos salen
  a un tercero y el día 1 depende de credenciales externas.

La respuesta se graba en tres lugares: `state.md` como `supabase_hosting`, `stack.md` en
la fila del slot Backend/Auth/DB, y un **ADR** en `.loop/adr/`. `loop-ship` la lee para
saber si el despliegue incluye levantar Supabase o solo apuntar a un proyecto cloud.

Si al llegar a `plan` la decisión no está tomada, `plan-architect` la fuerza antes de
planificar infraestructura: es cara de revertir una vez que hay datos.

## 3. Corrida completa y entregable

### 3.1 Forma de las tareas (`plan-architect`)

- Cada tarea es una **rebanada vertical**: pantalla + adaptador + datos + test. Nunca un
  fragmento que deje la app sin arrancar. Si algo no entra en una rebanada, se parte en
  rebanadas más chicas, no en capas horizontales.
- El plan completo está obligado a llegar **de scaffold a producto usable**. Lo que se
  difiere va al backlog explícito de `plan.md`, con una línea de por qué. No se admiten
  huecos implícitos para "después".

### 3.2 Criterio de terminado (`code-exec`)

El `done` de una tarea suma **la app levanta**, no solo compila. Typecheck verde con la
app rota no es una tarea terminada, igual que hoy una pantalla fea con tests verdes
tampoco lo es.

### 3.3 Matriz de dispositivos (`loop-verify`)

Dispositivos reales disponibles en la máquina, verificados el 2026-09-19:

| Rol | Dispositivo | Detalle |
|---|---|---|
| Celular Android | AVD `<avd-celular-android>` | Pixel 7, API 34, arm64-v8a google_apis |
| Tablet Android | AVD `<avd-tablet-android>` | Pixel Tablet, API 34, arm64-v8a google_apis |
| iPhone | `iPhone 17 Pro` | + 17 Pro Max / Air / 17e disponibles |
| iPad | `iPad Pro 11-inch (M5)` | + iPad Air (M4), iPad mini (A17 Pro) |

Los ids reales de los AVDs son locales a la máquina: se leen con `emulator -list-avds` y
se anotan en el `.loop/stack.md` de cada proyecto, que no vive en este repo.

SDK de Android en `/opt/homebrew/share/android-commandlinetools`; Xcode en
`/Applications/Xcode.app`.

**Toda tarea se verifica en los cuatro.** No hay dispositivo primario ni verificación
diferida: la tarea no cierra hasta que su flow pasa en teléfono y tablet de ambas
plataformas. Cada dispositivo deja su log en `.loop/device-<dispositivo>-<TAREA>.log`.
Un rojo en cualquiera entra a `fix-loop` y se reverifica en los cuatro; el sub-bucle de
corrección ya existe, solo se le suma esta entrada.

El arranque de la corrida incluye una **fase de preparación de dispositivos**: bootear
los cuatro y dejarlos vivos. `project-loop` la ejecuta una vez y registra en `state.md`
qué dispositivos quedaron listos; si alguno no arranca, la corrida no empieza — es
preferible fallar ahí que descubrirlo en la tarea 12.

**Si `mobile: no`, la matriz no aplica.** El gate equivalente es que la web levante y
responda en el navegador; `loop-verify` lo registra igual, con un solo log. Un proyecto
`data`, sin UI, no tiene gate de arranque: le basta el contrato de test/typecheck/lint
que ya existe.

Vale la regla que ya rige `loop-verify`: **nada se declara verde sin haber ejecutado el
comando**. Si un emulador no arranca, el estado es *bloqueado*, no verde.

### 3.4 Runner de e2e: Maestro (decidido)

Verificado contra documentación el 2026-09-19:

- **Expo lo documenta de primera mano** para E2E sobre EAS Workflows: flows en un
  directorio `.maestro/` en la raíz del proyecto.
- **Selecciona dispositivo** con `--device` / `--udid` (el id va *antes* del subcomando
  `test`) y plataforma con `--platform android|ios`. Un tablet o un iPad no necesitan
  tratamiento especial: son un id más. La matriz se corre como cuatro invocaciones, una
  por dispositivo, que es además lo que da un log por dispositivo.
- Los flows son **YAML declarativo** y el mismo archivo corre en las dos plataformas.
- **Reintenta aserciones inestables** por su cuenta.

Se descartó **Detox** a pesar de tener integración más profunda con React Native
(sincronización gray-box con el hilo de JS, tests en TS con lógica arbitraria). Esa
profundidad es también su fragilidad: exige configuración de build nativo y se acopla a
versiones concretas de React Native y Xcode. En un loop pensado para correr desatendido y
sobre Expo siempre, un runner que se rompe al subir de SDK es exactamente el error que
queremos evitar. Maestro se mantiene fuera del proyecto y no toca el build.

**Restricción heredada:** Maestro corre contra una app compilada (`.apk` para Android,
`.app` de simulador para iOS), no contra el cliente de Expo Go. Por eso el diseño de la
corrida separa build nativo de recarga de bundle: es lo que hace pagable la matriz por
tarea.

### 3.5 Encadenado (`project-loop`)

Corre el plan entero de punta a punta sin devolver control, salvo falla irrecuperable o
el checkpoint de diseño que ya existe. **No declara `entrega` hasta que el gate de
arranque esté verde**: la matriz de cuatro si hay mobile, la web levantada si no. Al
llegar a `entrega`, además de `deploy-checklist` y `loop-ship`, sugiere `loop-pitch`.

## 4. Estructura del archivo de Figma

`loop-design` hoy pide "nombrá las capas de forma reconocible", que es una recomendación,
no una estructura. Como `.loop/design.md` mapea pantalla ↔ nodo y `code-exec` busca cada
pantalla por ese nodo, un nombre improvisado rompe el mapa en silencio y la
implementación vuelve a diseñar de memoria — justo lo que la etapa de diseño existe para
evitar.

### 4.1 Un archivo por proyecto, páginas fijas

```
<Proyecto> — Design
├── 00 · Foundations     variables reales de color, tipografía, espaciado, radios, motion
├── 01 · Components      componentes base con sus variantes y estados
├── 02 · Mobile          pantallas mobile (secciones Teléfono y Tablet)
├── 03 · Web             pantallas web
├── 04 · Flows           cómo se encadenan las pantallas
├── 05 · Opciones        variantes a elegir (sección 4.4)
└── 99 · Archive         descartes: no se borran, pero no se implementan
```

El número fija el orden y hace el nombre estable para búsqueda. Las páginas que el
proyecto no usa no se crean, igual que las carpetas del monorepo.

Foundations y Components viven **dentro del archivo del producto**, no en una librería
publicada aparte: cada producto tiene su propia dirección estética, y una librería
compartida agregaría fricción de publicar/suscribir sin beneficio. `packages/ui` del
monorepo es la contraparte en código de estas dos páginas.

### 4.2 Nombre de frame = clave del mapa

Un frame por pantalla **y por estado**:

```
H-03 · Checkout · default
H-03 · Checkout · vacio
H-03 · Checkout · carga
H-03 · Checkout · error
```

`H-03` es el id de historia de `.loop/analysis.md`. Con eso la cadena queda cerrada:
historia → frame → fila en `design.md` → tarea en `plan.md` → componente en
`packages/ui`. `plan-architect` **deriva** el nombre del frame en vez de adivinarlo.

### 4.3 Tablet no es opcional

Si el gate corre en tablet Android e iPad en cada tarea pero en Figma solo hay pantallas
de teléfono, el layout de tablet lo improvisa `code-exec` y la matriz lo reporta como
rojo sin una referencia contra la cual arreglarlo: se paga el costo de testear en tablet
sin el beneficio de haber diseñado para tablet.

Por eso **cada pantalla existe en las dos secciones** de `02 · Mobile`, `Teléfono` y
`Tablet`. Duplica el trabajo de diseño y es una decisión tomada a conciencia.

**Los tamaños de frame se derivan de los dispositivos de la matriz**, no se hardcodean:
`loop-design` los calcula una vez y los escribe en `.loop/design-system.md`. De los AVDs
salen `Pixel 7 ≈ 412×914 dp` (1080×2400 @420dpi) y `Pixel Tablet = 1280×800 dp`
(2560×1600 @320dpi); los de iOS se miden contra el simulador al implementar. Si mañana
cambia un dispositivo de la matriz, cambian los frames: es una sola fuente.


### 4.4 Opciones gráficas para elegir

`loop-design` no entrega un diseño único a aprobar: en los puntos de decisión visual
ofrece **3 variantes** y la persona elige. Tres, porque es donde todavía se comparan de
un vistazo; con dos, si ninguna convence no hay a dónde ir, y con cinco las opciones
empiezan a parecerse y la elección se vuelve más lenta, no más rica.

Se ofrecen opciones en **dos momentos, y solo en esos dos**:

- **La dirección estética, una sola vez.** Al arrancar el diseño, 3 propuestas de look
  completo —tipografía, paleta, densidad, radios, motion— aplicadas sobre las **mismas 2
  pantallas representativas**, para que la comparación sea de dirección y no de contenido.
  La elegida gobierna todo el resto del proyecto y no se vuelve a preguntar.
- **Donde hay duda real.** El loop propone una sola opción por defecto y abre variantes
  únicamente cuando la decisión no es obvia: un patrón de navegación, una pantalla con
  estados que compiten. Cuando lo hace, **dice por qué dudó**; si no puede justificarlo,
  no abre variantes.

**Lo que no se hace: variantes por pantalla de rutina.** Un producto de 12 pantallas con
3 variantes cada una son 12 decisiones humanas antes de escribir código, y eso destruye
el `full-auto` que el loop tiene por default. La restricción es deliberada.

Las variantes viven en la página `05 · Opciones`, lado a lado. La elegida se promueve a
su página definitiva; las descartadas van a `99 · Archive` — no se borran, queda registro
de qué se evaluó. **La elección se registra** en `state.md` (la dirección estética) o como
ADR (una decisión puntual de patrón), para que no se reabra en la tarea siguiente.

## 5. `loop-pitch` — presentación del producto (HyperFrames)

Skill nueva, **manual a propósito** (`disable-model-invocation: true`), como `loop-ship`:
el loop la sugiere al llegar a `entrega`, nunca la dispara. Renderizar video es caro en
tiempo y es un entregable para humanos, no un paso del ciclo.

Motor: **HyperFrames**, el framework open-source de HeyGen que renderiza HTML/CSS y
animaciones a MP4 determinista, con skills para agentes (`/hyperframes` como router,
`/product-launch-video`, `/motion-graphics`, `slideshow`) e integración con Figma.

Entradas y salida:

- `.loop/analysis.md` → qué problema resuelve el producto y para quién.
- `state.md` (`aesthetic`) + `.loop/design-system.md` → **los tokens reales del producto**,
  no una plantilla genérica. Este es el punto: la presentación se ve como la app.
- `.loop/design.md` → las pantallas y sus nodos de Figma.
- Salida en `docs/pitch/` del proyecto.

## Cambios por archivo

| Archivo | Cambio |
|---|---|
| `templates/estructura/monorepo.md` | **nuevo** — árbol canónico, fuente única |
| `skills/project-init/SKILL.md` | pregunta mobile obligatoria · scaffold del monorepo · pregunta de hosting de Supabase · `infra/` si self-hosted |
| `templates/loop/state.md` | campos `mobile`, `supabase_hosting`, `matriz_dispositivos` (estado de los 4) |
| `templates/loop/stack.md` | hosting en el slot Backend/Auth/DB · comandos de e2e y dispositivos |
| `skills/loop-design/SKILL.md` | estructura fija de páginas · convención de nombre de frame · secciones Teléfono/Tablet · tamaños derivados de la matriz · 3 variantes en los dos momentos de decisión |
| `references/ui-patterns.md` | **nuevo** — catálogo de reglas de UI; lo consultan `loop-design` y `code-exec`, y la revisión de UI chequea las marcadas `[chequeable]` |
| `skills/plan-architect/SKILL.md` | rebanada vertical · plan hasta producto usable · backlog explícito · ADR de hosting · deriva el nombre del frame |
| `skills/code-exec/SKILL.md` | `done` incluye "la app levanta" |
| `skills/loop-verify/SKILL.md` | gate de dispositivo: matriz de 4 por tarea vía Maestro, un log por dispositivo, rebuild nativo solo si cambió lo nativo |
| `skills/project-loop/SKILL.md` | fase de preparación de dispositivos al arrancar · corrida punta a punta · sugiere `loop-pitch` |
| `skills/loop-ship/SKILL.md` | lee `supabase_hosting` para decidir el despliegue |
| `skills/loop-pitch/SKILL.md` | **nueva** |
| `scripts/verificar-arsenal.py` | valida el flag de `loop-pitch` y que las etapas encadenadas sigan sin él |
| `.claude-plugin/plugin.json` | 0.6.1 → 0.7.0 |
| `README.md` | 13 → 14 skills, estructura estándar, matriz de dispositivos |

## Prerrequisitos (fuera del repo, en la máquina)

Estado al 2026-09-19:

1. ✅ **FFmpeg** — `ffmpeg`/`ffprobe` 9.0.2 instalados vía Homebrew. Los necesita HyperFrames.
2. ✅ **HyperFrames** — grupo Core (10 skills) instalado en `~/.claude/skills/`:
   `hyperframes` (router), `-core`, `-cli`, `-animation`, `-keyframes`, `-creative`,
   `-registry`, `-studio`, `-audio`, `media-use`. Las 11 restantes (`slideshow`,
   `product-launch-video`, `motion-graphics`…) las instala el router bajo demanda.
3. ✅ **Android en el PATH** — `ANDROID_HOME=/opt/homebrew/share/android-commandlinetools`
   más `emulator/` y `platform-tools/` agregados en `~/.zshrc`. `emulator -list-avds`
   devuelve `<avd-tablet-android>` y `<avd-celular-android>`.
4. ⬜ **Maestro** — falta instalarlo y verificar que arranca contra un AVD y un simulador.
   Primera tarea del plan.
5. ✅ **MCP de Figma** — conectado y verificado el 2026-09-19: cuenta `Juan Alegre`,
   team propio, tier pro, asiento Full con rol admin. Hay permiso de escritura, que es lo
   que `loop-design` necesita.

## Riesgos

- **La matriz en cada tarea es cara.** Es una decisión tomada a conciencia: se prefiere
  el costo de minutos al costo de un bug de forma descubierto tarde. Depende de que las
  dos optimizaciones (dispositivos calientes, rebuild nativo solo cuando cambia lo
  nativo) funcionen de verdad; si no, una corrida larga se vuelve impracticable. **Es el
  riesgo principal de este spec** y la primera tarea del plan debería medirlo con un
  proyecto real antes de dar el diseño por bueno. La palanca de escape, si duele, es
  bajar la matriz a las tareas que tocan UI.
- **Cuatro emuladores vivos consumen RAM.** Dos emuladores Android más dos simuladores
  iOS simultáneos es carga real en la máquina. Hay que medirlo en la misma primera tarea.
- **La estructura fija puede no calzar** en un proyecto atípico (solo data, sin UI). La
  regla de "no se crea lo que no se usa" lo absorbe: ese proyecto tendría `packages/core`,
  `supabase/` y nada más.
- **HyperFrames es dependencia externa nueva** y se lleva un `npx skills add` global. Si
  resulta pesado o inestable, `loop-pitch` es la única skill que lo toca y se puede
  retirar sin afectar el ciclo.
- **Diseñar cada pantalla dos veces (teléfono y tablet) puede frenar el checkpoint de
  diseño.** Es el costo aceptado de testear en tablet contra algo diseñado. Si el archivo
  se vuelve inmanejable, la palanca es diseñar tablet solo donde el layout cambia de
  verdad y dejar el resto a reglas del design system.
- **El catálogo de UI puede envejecer o contradecirse.** Son referencias recogidas de
  varias fuentes; al crecer, dos reglas pueden chocar (UI-004 recorta texto, UI-008 pide
  mostrar datos de decisión). La marca `[chequeable]` / `[principio]` acota el daño, pero
  el catálogo necesita una pasada de consistencia cada vez que se le suma una tanda.
- **La convención de nombres depende de que los ids de historia sean estables.** Si
  `requirements-analysis` renumera historias al replanificar, los frames quedan
  desalineados con `design.md`. `plan-architect` debe tratar los ids como inmutables una
  vez emitidos.

## Fuera de alcance

- Rediseñar el flujo de `loop-design` — dirección estética, checkpoint humano, mapa en
  `design.md` — que ya existe y funciona. Lo que se le agrega es la estructura del
  archivo (sección 4).
- Tocar `dev-substrate`.
- Cablear Sentry/Supabase con credenciales reales.
- Cambiar la ubicación de los ADRs (siguen en `.loop/adr/`).
