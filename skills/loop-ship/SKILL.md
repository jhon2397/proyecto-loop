---
name: loop-ship
description: >-
  Prepara y ejecuta el despliegue de un proyecto al servidor interno siguiendo el
  patrón establecido: un directorio por proyecto, compose propio, detrás del reverse
  proxy compartido, publicando solo en loopback. Trigger con "desplegá esto",
  "preparalo para el servidor", "armá el despliegue".
argument-hint: [nombre-del-proyecto]
disable-model-invocation: true
model: opus
effort: high
---

# loop-ship — Entrega al servidor

> **Esta skill toca producción.** No la dispara `project-loop` ni ninguna otra skill:
> la invoca una persona. Y aun invocada, **no ejecutás nada contra el servidor sin que
> el usuario apruebe explícitamente ese paso concreto**. Preparar los archivos es
> seguro; conectarse y levantar contenedores no.

## 0. Antes de empezar
- Lee `.loop/state.md` y `.loop/stack.md`. El plan tiene que estar agotado y los
  tests en verde: desplegar con tareas abiertas no es entregar, es adelantar deuda.
- Corré `engineering:deploy-checklist` si está disponible.

## 1. Reconocer el servidor (no asumir nada)
Antes de elegir un puerto o escribir un bloque de proxy, **mirá el servidor real**:

- qué proyectos ya viven ahí y bajo qué directorio;
- qué puertos están ocupados (`ss -ltnp` o equivalente), incluidos los de los otros
  proyectos;
- cómo está organizado el reverse proxy y **con quién se comparte**.

Un puerto que "parecía libre" y un `Caddyfile` que "parecía del proyecto" son las dos
formas más rápidas de romperle el día a otro sistema.

## 2. El patrón
- **Un directorio por proyecto**, con su clon y su `docker-compose` propio.
- **La aplicación publica solo en `127.0.0.1`.** La única puerta es el reverse proxy.
- **Base de datos y caché no se publican a la red**, aunque la aplicación sí. Lo que
  la red necesita alcanzar es la pantalla, no el motor.
- **Base de datos propia por proyecto** si la aplicación necesita permisos de clúster
  (crear bases o roles): esos permisos alcanzarían también a las bases de los otros
  proyectos que compartan el clúster.

## 3. Red entre contenedores: por nombre de servicio
Los contenedores se hablan por una **red de Docker compartida y nombre de servicio**
(`http://<servicio>:<puerto>`).

**Nunca `host.docker.internal`.** En Docker Desktop (Mac) resuelve al loopback del
host y funciona; en Linux resuelve al gateway del bridge y **no** llega a un bind de
loopback. El síntoma es un `Connection timed out` de dos minutos que no se parece en
nada a la causa. Tampoco publiques en el gateway del bridge: dejarías el puerto al
alcance de todos los contenedores del servidor.

Si hay varias redes, **el orden de arranque importa** y hay que documentarlo: quien
crea la red va primero. Un `up` fuera de orden falla con «network not found».

## 4. Reverse proxy: el archivo es compartido
Un error de sintaxis ahí no rompe tu proyecto, rompe **todos** los sitios del servidor.
Sin excepciones:

1. respaldo con fecha del archivo actual;
2. `validate` sobre el archivo nuevo **antes** de copiarlo;
3. `reload` en caliente, nunca `restart`.

Si el proyecto tiene un frontend que hace de intermediario, **todo entra por ahí**;
no publiques rutas directas al backend salvo que exista una decisión registrada que
lo pida. Un `handle` que secuestra las rutas del frontend rompe la sesión de formas
que no se ven hasta que alguien no puede entrar.

## 5. Encabezados de proxy y límites por IP
Si la aplicación limita por IP, verificá **contra el despliegue real** qué IP ve:
la de la cadena de proxy o la del cliente. Con el valor equivocado el límite no da
error — simplemente empieza a contar a todos los usuarios como uno y bloquea a gente
que no hizo nada. Se comprueba provocando un evento y leyendo qué IP quedó registrada.
De memoria no se puede.

## 6. Secretos
- No se versiona ninguno. Se generan en el servidor.
- **El dueño del archivo tiene que ser el usuario del contenedor**, no el tuyo: si la
  imagen corre con un uid propio y la clave se monta desde el host con permisos
  cerrados y otro dueño, el contenedor no la lee.
- Documentá qué variables **no** se copian del ejemplo y de dónde sale cada una.

## 7. Entregables en el repo
Todo esto vive en el repo, no en la cabeza de nadie: el compose, un `despliegue/`
con el procedimiento, los puertos elegidos y **por qué** cada decisión es así.
Escribí los porqués: lo que no funcionó y su síntoma vale más que la instrucción,
porque evita que alguien lo reintente.

## 8. Verificación después de desplegar
Con evidencia, no con "debería andar": responde la aplicación por su dominio, la
base migrada, el proxy recargado sin tocar a los demás sitios, y el chequeo de la IP
del punto 5. Si algo no lo pudiste comprobar, decilo.

## 9. Cierre
Actualizá `.loop/state.md` (etapa = entrega, bitácora con la fecha y la versión
desplegada) y dejá anotado el procedimiento de rollback.
