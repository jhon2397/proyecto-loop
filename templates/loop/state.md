# Loop State

> Archivo de control del loop. Lo leen y actualizan TODAS las skills del arsenal.
> No borrar. Es la fuente de verdad para reanudar el ciclo sin perder contexto.

## Meta
- **proyecto:** <nombre>
- **platform:** mobile | web | full-stack | data        # 95% mobile por defecto
- **stack:** <p.ej. Expo/React Native + Supabase>
- **aesthetic:** <dirección estética fijada (Frontend Design); ver §10 del blueprint>
- **autonomía:** full-auto | checkpoint-tras-review

## Estado actual
- **etapa:** inicio | analisis | plan | ejecucion | revision | test | correccion | entrega
- **tarea_activa:** <id y título de la tarea de plan.md, o "—">
- **iteracion:** <n>            # nº de vuelta del loop para la tarea activa
- **ultima_skill:** <nombre>    # qué skill escribió por última vez
- **timestamp:** <YYYY-MM-DD>

## Artefactos
- analysis.md: pendiente | listo
- plan.md: pendiente | listo
- stack.md: pendiente | listo
- adr/: <conteo de ADRs>
- review-log.md: <conteo de hallazgos abiertos>

## Bitácora (append-only, lo más nuevo arriba)
- <YYYY-MM-DD> · <skill> · <qué hizo / a qué etapa pasó>
