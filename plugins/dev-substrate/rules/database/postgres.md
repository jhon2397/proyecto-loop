---
paths:
  - "**/*.sql"
  - "**/migrations/**/*"
  - "**/alembic*/**/*"
  - "**/repositories/**/*"
---

# PostgreSQL

## RLS: habilitar no alcanza, hay que forzar
`ENABLE ROW LEVEL SECURITY` **no aplica al dueño de la tabla**, y el dueño es quien
corre las migraciones, quien conecta las tareas de mantenimiento y —si nadie lo
cambió— quien conecta la aplicación. Una política sin `FORCE` puede existir y no
filtrar absolutamente nada.

```sql
ALTER TABLE <tabla> ENABLE ROW LEVEL SECURITY;
ALTER TABLE <tabla> FORCE  ROW LEVEL SECURITY;
```

Que la política exista no es evidencia de que aísle: verificá con el rol real de la
aplicación, no con el dueño.

## Contexto de sesión: `set_config()`, no `SET`
`SET x = :valor` funciona solo de prestado, porque psycopg2 interpola del lado del
cliente y a Postgres le llega un literal. `SET` **no admite un parámetro a nivel
protocolo**, así que un driver que ligue del lado del servidor rompe el único lugar
donde se fija el alcance del usuario. `set_config()` es una función: el valor viaja
como parámetro de verdad.

```sql
SELECT set_config('app.<clave>', :valor, false);
```

## Limpiar el contexto al terminar
`set_config(..., false)` es de **sesión**, no de transacción, y las conexiones
vuelven a un pool. Sin limpieza explícita, la próxima consulta que use esa conexión
—otro servicio, un worker, el propio login— hereda el contexto del último usuario y
ve de más.

## Roles
La aplicación no conecta como dueño de la tabla. Un rol de aplicación por base, con
lo mínimo necesario.

## Migraciones
- No reescribas una migración ya aplicada en algún entorno: agregá una nueva.
- Si la forma del esquema importa más que la comodidad, escribí el DDL en SQL crudo
  en vez de depender del autogenerate.
- Toda migración tiene que poder desplegarse con la versión anterior de la aplicación
  todavía corriendo.

## Dinero
Nunca `float` ni `double`. `NUMERIC` con escala explícita, o entero en la unidad
mínima. La decisión se toma una vez para todo el proyecto y se documenta.
