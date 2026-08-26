# Instrucciones del proyecto

## Proyecto

- Nombre: `<NOMBRE>`
- Propósito: `<PROPÓSITO_EN_UNA_FRASE>`
- Estado: `<desarrollo|staging|producción>`

## Stack

- Backend: `<BACKEND>`
- Frontend: `<FRONTEND>`
- Mobile: `<MOBILE_O_NINGUNO>`
- Base de datos: `<BASE_DE_DATOS>`
- Infraestructura: `<INFRAESTRUCTURA>`
- Integraciones: `<INTEGRACIONES>`

## Arquitectura

`<DESCRIPCIÓN_CORTA_DE_LA_ARQUITECTURA_ACTUAL>`

Límites importantes:

- `<LÍMITE_1>`
- `<LÍMITE_2>`

## Mapa del repositorio

- `<ruta>` — `<responsabilidad>`
- `<ruta>` — `<responsabilidad>`

## Comandos

Instalar:

```bash
<COMANDO_INSTALL>
```

Correr:

```bash
<COMANDO_RUN>
```

Tests enfocados:

```bash
<COMANDO_TEST_ENFOCADO>
```

Tests completos:

```bash
<COMANDO_TEST_COMPLETO>
```

Lint / typecheck:

```bash
<COMANDO_LINT_O_TYPECHECK>
```

Build:

```bash
<COMANDO_BUILD>
```

## Reglas propias del proyecto

- Preservá los contratos de API pública salvo que la tarea pida cambiarlos.
- No cambies el esquema de base de datos sin una migración.
- No modifiques datos de producción directamente.
- No agregues dependencias sin verificar antes si el proyecto ya tiene esa capacidad.
- Nunca inventes campos de integración ni objetos de base de datos: verificalos.

## Restricciones de negocio

- `<REGLA_DE_NEGOCIO_1>`
- `<REGLA_DE_NEGOCIO_2>`
