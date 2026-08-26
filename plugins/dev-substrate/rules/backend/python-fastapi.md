---
paths:
  - "**/*.py"
---

# Python / FastAPI

> Alternativa a `backend/python-flask.md`. **Nunca instales las dos**: matchean los
> mismos archivos y se contradicen.

## Capas
- `app/api/v1/` — routers. Solo traducen HTTP: validan entrada, llaman al servicio,
  devuelven el schema. Nada de lógica de negocio ni de acceso a datos acá.
- `app/services/` — lógica de negocio.
- `app/models/` y `app/db/` — persistencia.
- `app/integrations/<vendor>/` — todo lo que habla con un sistema externo, detrás de
  su propia frontera. No disperses llamadas a un vendor por los servicios.
- `app/workers/` — procesos que no atienden requests.

## HTTPException solo en la capa API
Una capa que también usa un worker **no puede** levantar `HTTPException`: el worker
no atiende requests y quedaría con un error que no sabe manejar. Definí una excepción
de dominio propia y que el middleware o el router la traduzcan a código HTTP.

Es la diferencia entre un 500 y decirle al frontend que tiene que volver al ingreso.

## SQLAlchemy 2, sesiones y engines
- Seguí el estilo de SQLAlchemy 2 que ya use el repo (sync o async): no mezcles.
- La sesión llega por **dependency**, no se crea dentro del servicio.
- Si cacheás engines, la clave es un **identificador público** (un UUID), nunca la
  connection string: esa lleva la contraseña adentro y quedaría de clave en un dict
  global, viva todo el proceso y visible en cualquier volcado de memoria o `repr`.
- El cache de engines se toca desde varios hilos: protegelo con un candado.

## Configuración
Nada de credenciales ni URLs en el código. Van por configuración, y la de cada
tenant se descifra en el momento de usarla.

## Tests
`pytest`. Para HTTP saliente, mockeá en el borde con `respx` en vez de parchear el
cliente: así el test ejercita el request real que sale.
