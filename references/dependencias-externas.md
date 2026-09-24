# Dependencias externas del loop

> El loop invoca skills que no son suyas. En la máquina local suelen estar; en una
> sesión cloud, muchas no, porque los plugins y las skills del usuario no viajan. Este
> archivo dice qué verifica cada una, para que una etapa que no la encuentra sepa
> exactamente qué dejó sin revisar.

## La regla

Antes de invocar una skill de esta tabla, comprobá que esté disponible. Si no está:

1. **No la saltees en silencio** ni des por aprobada la revisión que hacía.
2. Registrá en `.loop/review-log.md` una línea con este formato exacto:

   `NO VERIFICADO — <skill> no disponible en este entorno. Quedó sin evaluar: <qué>.`

   donde `<qué>` es lo concreto de esta tarea: la pantalla, la regla o el cambio que esa
   skill habría revisado. "La UI" no alcanza; "la jerarquía visual (UI-007) de
   H-03 · Checkout" sí.
3. Seguí con la etapa. Estas líneas **no bloquean** la entrega, pero `project-loop` las
   lista en el reporte de entrega.

Las marcadas como vendoreadas viajan dentro del proyecto (ver `.claude/loop/TERCEROS.md`):
están disponibles también en la nube.

## Qué verifica cada una

| Skill | La usan | Qué verifica | Vendoreada |
|---|---|---|---|
| `engineering:code-review` | code-exec, project-loop | correctitud, seguridad y rendimiento del diff | no — la provee la app |
| `engineering:debug` | fix-loop | diagnóstico de fallos no obvios | no — la provee la app |
| `engineering:architecture` | plan-architect | decisiones de arquitectura y ADRs | no — la provee la app |
| `engineering:system-design` | plan-architect | diseño del sistema | no — la provee la app |
| `engineering:deploy-checklist` | loop-ship | checklist previo a desplegar | no — la provee la app |
| `deploy-checklist` | code-exec, project-loop | checklist previo a desplegar | no — la provee la app |
| `design:design-critique` | plan-architect, project-loop | usabilidad, jerarquía (UI-007) y consistencia | no — la provee la app |
| `figma:figma-use` | loop-design | escritura correcta en Figma | no — la provee la app |
| `figma:figma-generate-design` | loop-design | traducir una pantalla a Figma | no — la provee la app |
| `figma:figma-design-to-code` | code-exec | valores exactos del diseño al implementar | no — la provee la app |
| `frontend-design` | code-exec, loop-design, project-init, project-loop | dirección estética | no |
| `ui-ux-pro-max` | code-exec, project-init, project-loop | paletas y tipografía | no |
| `animate` | code-exec | motion y transiciones | no — sin licencia |
| `web-design-guidelines` | plan-architect, project-loop | guías de interfaz web | no — sin licencia |
| `accesslint` | plan-architect, project-loop | accesibilidad | no — sin licencia |
| `documentation` | project-loop | documentación al cierre | no |
| `standup` | project-loop | resumen de cierre | no |
| `hyperframes` | loop-pitch | render de la presentación del producto | no — solo local |
| `design-taste-frontend` | code-exec, loop-design, project-init, project-loop | que el diseño no parezca una plantilla | **sí** |
| `react-native-best-practices` | code-exec, project-loop | rendimiento y buenas prácticas de React Native | **sí** |
