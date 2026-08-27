# Stack de Servicios (capability slots)

> Registro capacidad → vendor por proyecto. No se fijan vendors en project-init;
> se eligen en plan-architect (con ADR) según "qué tan caro es meterlo después".

## Tier 1 — desde el día 1 (cableado por project-init)

Tres estados, y la diferencia importa:

- **cableado** — el código está y las variables declaradas, pero sin credenciales el
  servicio es inerte. Es donde lo deja `project-init`.
- **activo** — hay credenciales **y alguien verificó que un evento real llegó**.
- **pendiente** — ni siquiera está cableado.

Marcar `activo` sin la verificación es lo mismo que no tenerlo, pero peor: el equipo
cree que está cubierto.

| Slot | Vendor | Estado | Notas |
|------|--------|--------|-------|
| Observabilidad | Sentry | <cableado/activo> | source maps / symbolication Hermes en Expo |
| Backend/Auth/DB | Supabase | <cableado/activo> | diseñar RLS desde el inicio |

### Qué falta para pasar de cableado a activo

**Sentry** — un proyecto por **aplicación**, no por producto: las plataformas procesan
los stack traces distinto.

| Variable | Dónde va | ¿Es secreto? |
|----------|----------|--------------|
| `NEXT_PUBLIC_SENTRY_DSN` / `EXPO_PUBLIC_SENTRY_DSN` | `.env` de cada app | No: viaja en el bundle del cliente |
| `SENTRY_DSN` (backend) | `.env` del servicio | No, pero no hace falta exponerlo |
| `SENTRY_ORG`, `SENTRY_PROJECT` | entorno de build | No |
| `SENTRY_AUTH_TOKEN` | **solo CI / entorno de build** | **Sí. Nunca se commitea** |

Sin `SENTRY_AUTH_TOKEN` no se suben source maps, y sin source maps un error de
producción llega como un stack trace minificado ilegible. Ese es el caso que engaña:
parece que anda porque el evento llega.

**Verificación para marcar `activo`:** lanzá un error de prueba desde cada app y
confirmá que llega al dashboard **con el stack trace legible**. Anotá la fecha acá.

**Supabase** — proyecto creado, `SUPABASE_URL` y las claves en `.env`, migraciones
aplicadas y **al menos una política RLS probada con el rol de la aplicación**, no con
el service_role. Una tabla con RLS habilitado y sin política probada no aísla nada.

## Tier 2 — feature-gated (tras una interfaz, solo si el requerimiento lo pide)
| Slot | Vendor | Estado | Notas |
|------|--------|--------|-------|
| Pagos (mobile digital) | RevenueCat + IAP | diferido | NO Stripe por default en mobile |
| Pagos (físico/web) | Stripe | diferido | solo bienes físicos/servicios reales/web |
| Email transaccional | SendGrid | diferido | auth los cubre Supabase |

## Decisiones (enlazar a adr/)
- <slot> → <vendor> · ADR-00X · motivo

## Comandos del proyecto (contrato para loop-verify)
| Acción | Comando |
|--------|---------|
| test (suite completa) | `<comando>` |
| test (archivo/patrón) | `<comando> <patrón>` |
| typecheck | `<comando>` |
| lint | `<comando>` |
| build | `<comando>` |
