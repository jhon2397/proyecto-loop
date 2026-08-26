---
paths:
  - "**/*.{ts,tsx,js,jsx,mjs,cjs}"
  - "**/*.{py,sql,sh,rb,php}"
  - "**/*.{java,kt,swift,go,rs}"
---

# Ingeniería

## Prioridades
Correctitud > simplicidad > mantenibilidad > seguridad > rendimiento.
La solución más chica que sea correcta gana.

## Antes de editar
- Leé la implementación existente y buscá un patrón similar ya presente en el repo.
- Identificá dependencias e impacto antes de escribir código.

## Alcance
Cambios quirúrgicos. No refactorices código no relacionado, no renombres símbolos ajenos
a la tarea, no reformatees archivos que no tocás, no agregues ni subas dependencias sin
un motivo concreto. Los problemas que encuentres de paso se reportan aparte, no se
arreglan de prepo.

## Grounding
Nunca inventes APIs, métodos de librería, opciones de configuración, tablas, columnas,
campos de servicios externos ni esquemas de respuesta. Verificá contra el repo o la
documentación. Si no lo podés verificar, decilo en vez de adivinar.

## Contexto
No leas el repo entero. Búsqueda dirigida, lookup de símbolos, trazado de imports.

## Verificación
Corré primero el chequeo más chico que sea relevante: test enfocado → lint → typecheck → build.
Nunca declares verificado algo que no ejecutaste.

## Cierre
Terminá con: qué cambió · archivos importantes · verificaciones ejecutadas y su resultado ·
riesgos o pendientes. Sin relleno.
