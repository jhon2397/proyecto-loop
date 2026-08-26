---
name: sap-service-layer
description: >-
  Procedimiento de trabajo con SAP Business One Service Layer. Sesiones y login,
  paginación, batch, manejo de errores, campos de usuario, y el límite entre qué se
  hace por Service Layer y qué por SQL.
paths:
  - "**/sap/**"
  - "**/service_layer/**"
  - "**/service-layer/**"
  - "**/integrations/**/*sap*"
---

# SAP Business One — Service Layer

> **ESQUELETO SIN COMPLETAR.** El cuerpo de esta skill se escribe leyendo el código
> de integración real del repo donde se use esta skill. No inventar el
> procedimiento: lo que no se pueda verificar contra el código o la documentación de
> SAP, no entra. Hasta entonces, tratá esta skill como una lista de preguntas a
> responder, no como una fuente.

## Límite fundamental
- Service Layer es la interfaz soportada para operaciones de negocio: crear y
  modificar documentos.
- SQL directo sobre HANA es para consulta y reportes, dentro de los límites
  funcionales de SAP y de las políticas del proyecto. **Nunca para escribir documentos.**

## Sesión
- `<login, vigencia de la cookie de sesión, renovación, un solo login por proceso>`

## Paginación y volumen
- `<$top / $skip, Prefer: odata.maxpagesize, qué hacer con sets grandes>`

## Batch
- `<cuándo conviene $batch y cómo se manejan los errores parciales>`

## Errores
- `<qué códigos se reintentan y cuáles no; idempotencia al reintentar la creación
  de un documento>`

## Campos de usuario
- `<convención de UDF/UDT del proyecto>`
