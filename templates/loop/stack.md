# Stack de Servicios (capability slots)

> Registro capacidad → vendor por proyecto. No se fijan vendors en project-init;
> se eligen en plan-architect (con ADR) según "qué tan caro es meterlo después".

## Tier 1 — desde el día 1 (cableado por project-init)
| Slot | Vendor | Estado | Notas |
|------|--------|--------|-------|
| Observabilidad | Sentry | <activo/pendiente> | source maps / symbolication Hermes en Expo |
| Backend/Auth/DB | Supabase | <activo/pendiente> | diseñar RLS desde el inicio |

## Tier 2 — feature-gated (tras una interfaz, solo si el requerimiento lo pide)
| Slot | Vendor | Estado | Notas |
|------|--------|--------|-------|
| Pagos (mobile digital) | RevenueCat + IAP | diferido | NO Stripe por default en mobile |
| Pagos (físico/web) | Stripe | diferido | solo bienes físicos/servicios reales/web |
| Email transaccional | SendGrid | diferido | auth los cubre Supabase |

## Decisiones (enlazar a adr/)
- <slot> → <vendor> · ADR-00X · motivo
