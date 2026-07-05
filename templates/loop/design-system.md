# Design System

> Fuente de verdad visual del proyecto. Lo crea la **primera tarea de UI** (apoyada en
> `design:design-system` + `frontend-design`). `code-exec` lo reusa en cada pantalla:
> **nunca estilos ad-hoc**. Solo aplica si el proyecto tiene UI.

## Dirección estética
<tono, personalidad, audiencia, principios — heredado de `aesthetic` en state.md>

## Tokens
- **Color:** primario / superficies / texto / estados (éxito, error, warning, info) / bordes.
- **Tipografía:** familia(s), escala (display/h1/h2/body/caption), pesos, line-height.
- **Espaciado:** escala (4/8/12/16/24/32…), radios, sombras/elevación.
- **Breakpoints** (web) / densidades (mobile).

## Componentes base
<Button (variantes/estados), Input/Field (label, required, error), Card, Modal/Drawer
(focus trap, retorno de foco, Esc), Badge de estado, Table, Toast, EmptyState…>
Para cada uno: variantes, **estados** (default/hover/focus/disabled/loading/error) y a11y.

## Reglas de uso
- Siempre tokens/componentes; nada de valores mágicos por pantalla.
- Estados de carga, vacío y error son **obligatorios**, no opcionales.
- Verificado con `design:design-critique` + `accesslint` / `web-design-guidelines`.

## Dónde vive en el código
<p. ej. `packages/ui/` (tokens + componentes) · `apps/web/src/app/globals.css`>
