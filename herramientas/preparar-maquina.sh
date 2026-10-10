#!/usr/bin/env bash
# Verifica que esta máquina tenga lo que el loop necesita y, si se le pide, instala lo
# que falta.
#
#   preparar-maquina.sh                 # solo verifica: no cambia nada
#   preparar-maquina.sh --instalar      # instala lo que se puede instalar solo
#   preparar-maquina.sh --actualizar    # trae la última versión de los plugins del loop
#
# Cada línea dice una de cuatro cosas:
#   OK              verificado y está
#   FALTA           verificado y no está
#   AVISO           está, pero no como conviene
#   NO VERIFICADO   no se pudo comprobar (falta la herramienta con la que se comprueba)
#
# "No pude verificar" nunca cuenta como "está": el script sale con 1 si queda algún FALTA
# o algún NO VERIFICADO.
#
# Lo que no instala, porque no se puede o porque no le corresponde: Xcode, Docker
# Desktop, la conexión de Figma y las skills que provee la cuenta (engineering, design,
# figma, anthropic-skills). Esas las informa y dice dónde se resuelven.
set -u

MODO="verificar"
case "${1:-}" in
  --instalar) MODO="instalar" ;;
  --actualizar) MODO="actualizar" ;;
  "" ) ;;
  *) echo "uso: $0 [--instalar | --actualizar]"; exit 2 ;;
esac

FALTAN=0; SIN_VERIFICAR=0; AVISOS=0; INSTALADOS=0
ok()    { printf '  OK             %s\n' "$1"; }
falta() { printf '  FALTA          %s\n' "$1"; FALTAN=$((FALTAN + 1)); }
aviso() { printf '  AVISO          %s\n' "$1"; AVISOS=$((AVISOS + 1)); }
nover() { printf '  NO VERIFICADO  %s\n' "$1"; SIN_VERIFICAR=$((SIN_VERIFICAR + 1)); }
hay()   { command -v "$1" >/dev/null 2>&1; }
# Corre un comando de instalación mostrando qué hace; no corta el script si falla.
instalar() {
  printf '  → %s\n' "$*"
  if "$@" >/tmp/preparar-maquina.$$.log 2>&1; then
    INSTALADOS=$((INSTALADOS + 1)); return 0
  fi
  printf '    falló: %s\n' "$(tail -1 /tmp/preparar-maquina.$$.log)"; return 1
}

MAC=0; [ "$(uname -s)" = "Darwin" ] && MAC=1

# ---------------------------------------------------------------- plugins
# marketplace|url
MARKETPLACES="
proyecto-loop-local|https://github.com/jhon2397/proyecto-loop.git
superpowers-marketplace|https://github.com/obra/superpowers-marketplace.git
callstack-agent-skills|https://github.com/callstackincubator/agent-skills.git
accesslint|https://github.com/accesslint/skills.git
"
PLUGINS="
proyecto-loop@proyecto-loop-local
dev-substrate@proyecto-loop-local
superpowers@superpowers-marketplace
react-native-best-practices@callstack-agent-skills
accesslint@accesslint
"

if [ "$MODO" = "actualizar" ]; then
  echo "Actualizar los plugins del loop"
  if ! hay claude; then
    nover "no está la CLI 'claude': actualizá el marketplace desde la app"
  else
    instalar claude plugin marketplace update proyecto-loop-local
    for p in proyecto-loop@proyecto-loop-local dev-substrate@proyecto-loop-local; do
      instalar claude plugin update "$p"
    done
    claude plugin list 2>/dev/null | grep -A1 -E 'proyecto-loop@|dev-substrate@' | grep -E '@|Version' | sed 's/^ */  /'
    echo "  Abrí una sesión nueva: las skills cargan al iniciar."
  fi
  rm -f /tmp/preparar-maquina.$$.log
  [ "$SIN_VERIFICAR" -eq 0 ] && exit 0 || exit 1
fi

echo "Plugins"
if ! hay claude; then
  nover "no está la CLI 'claude' en el PATH: no puedo listar ni instalar plugins. Hacelo desde la app (+ → Add marketplace from GitHub)"
else
  MK_LISTA="$(claude plugin marketplace list 2>/dev/null)"
  PL_LISTA="$(claude plugin list 2>/dev/null)"
  if [ -z "$MK_LISTA$PL_LISTA" ]; then
    nover "'claude plugin list' no devolvió nada"
  else
    for linea in $MARKETPLACES; do
      nombre="${linea%%|*}"; url="${linea##*|}"
      if printf '%s' "$MK_LISTA" | grep -qF "$url" || printf '%s' "$MK_LISTA" | grep -qF "❯ $nombre"; then
        :
      elif [ "$MODO" = "instalar" ]; then
        instalar claude plugin marketplace add "$url"
      fi
    done
    [ "$MODO" = "instalar" ] && PL_LISTA="$(claude plugin list 2>/dev/null)"
    for p in $PLUGINS; do
      if printf '%s' "$PL_LISTA" | grep -qF "❯ $p"; then
        ok "$p"
      elif [ "$MODO" = "instalar" ] && instalar claude plugin install "$p" --yes; then
        ok "$p (recién instalado)"
      else
        falta "$p"
      fi
    done
  fi
fi

# ---------------------------------------------------------------- skills sueltas
# skill|repo   (viven en ~/.claude/skills; se instalan con `npx skills`)
SKILLS="
animate|delphi-ai/animate-skill
design-taste-frontend|Leonxlnx/taste-skill
web-design-guidelines|vercel-labs/agent-skills
hyperframes|heygen-com/hyperframes
hyperframes-core|heygen-com/hyperframes
hyperframes-cli|heygen-com/hyperframes
hyperframes-creative|heygen-com/hyperframes
hyperframes-animation|heygen-com/hyperframes
hyperframes-registry|heygen-com/hyperframes
"
echo "Skills sueltas (~/.claude/skills)"
for linea in $SKILLS; do
  s="${linea%%|*}"; repo="${linea##*|}"
  if [ -f "$HOME/.claude/skills/$s/SKILL.md" ]; then
    ok "$s"
  elif [ "$MODO" = "instalar" ]; then
    # Sin -a: que detecte el agente solo. Con -a '*' instala a decenas de agentes.
    if hay npx && instalar npx --yes skills add "$repo" -g --copy -y -s "$s" \
       && [ -f "$HOME/.claude/skills/$s/SKILL.md" ]; then
      ok "$s (recién instalada)"
    else
      falta "$s  (npx skills add $repo -g --copy -y -s $s)"
    fi
  else
    falta "$s"
  fi
done

# ---------------------------------------------------------------- herramientas
echo "Herramientas"
brew_instalar() {  # nombre visible, fórmula
  if [ "$MODO" = "instalar" ] && [ "$MAC" -eq 1 ] && hay brew; then
    instalar brew install "$2" && return 0
  fi
  return 1
}

if [ "$MAC" -eq 1 ]; then
  if hay brew; then ok "Homebrew"; else falta "Homebrew (https://brew.sh): sin él no puedo instalar el resto"; fi
fi

# Node 22 o más: alcanza con que haya uno disponible, aunque no sea el de por defecto.
NODE_OK=""
if hay node && [ "$(node -p 'process.versions.node.split(".")[0]' 2>/dev/null || echo 0)" -ge 22 ]; then
  NODE_OK="por defecto ($(node -v))"
else
  for d in "$HOME"/.nvm/versions/node/v2[2-9]* "$HOME"/.nvm/versions/node/v[3-9][0-9]* /opt/homebrew/opt/node@22 /usr/local/opt/node@22; do
    [ -x "$d/bin/node" ] && NODE_OK="en $d/bin, no es el de por defecto"
  done
fi
if [ -n "$NODE_OK" ]; then
  case "$NODE_OK" in
    por\ defecto*) ok "Node 22+ — $NODE_OK" ;;
    *) aviso "Node 22+ — $NODE_OK$(hay node && printf ' (por defecto: %s)' "$(node -v)")" ;;
  esac
elif brew_instalar "Node 22" node@22; then
  ok "Node 22 (recién instalado; no queda como el de por defecto)"
else
  falta "Node 22 o más (lo piden supabase-js e HyperFrames)"
fi

for par in "uv|uv" "ffmpeg|ffmpeg" "gh|gh"; do
  cmd="${par%%|*}"; formula="${par##*|}"
  if hay "$cmd"; then ok "$cmd"
  elif brew_instalar "$cmd" "$formula" && hay "$cmd"; then ok "$cmd (recién instalado)"
  else falta "$cmd"; fi
done

if hay docker && docker info >/dev/null 2>&1; then ok "Docker (corriendo)"
elif hay docker; then aviso "Docker está instalado pero no responde: abrilo antes de correr el loop"
else falta "Docker (Docker Desktop: se instala a mano)"; fi

# ---------------------------------------------------------------- matriz de dispositivos
echo "Matriz de dispositivos (solo si el proyecto tiene mobile)"
if java -version >/dev/null 2>&1; then ok "Java"
elif brew_instalar "Java 17" openjdk@17; then ok "Java 17 (recién instalado; falta JAVA_HOME, ver Entorno)"
else falta "Java 17 (sin él Maestro no arranca; en macOS /usr/bin/java es un señuelo)"; fi

if hay maestro; then ok "Maestro"
elif [ "$MODO" = "instalar" ] && [ "$MAC" -eq 1 ] && hay brew \
     && instalar brew tap mobile-dev-inc/tap && instalar brew install mobile-dev-inc/tap/maestro && hay maestro; then
  ok "Maestro (recién instalado)"
else
  # `brew install maestro` a secas instala otro programa con el mismo nombre.
  falta "Maestro (brew tap mobile-dev-inc/tap && brew install mobile-dev-inc/tap/maestro)"
fi

if [ -n "${ANDROID_HOME:-}" ] && [ -x "$ANDROID_HOME/platform-tools/adb" ] && [ -x "$ANDROID_HOME/emulator/emulator" ]; then
  N="$("$ANDROID_HOME/emulator/emulator" -list-avds 2>/dev/null | grep -c .)"
  if [ "$N" -ge 2 ]; then ok "Android SDK con $N emuladores"; else aviso "Android SDK sin los dos emuladores de la matriz (hay $N)"; fi
elif brew_instalar "Android" android-commandlinetools; then
  aviso "herramientas de Android recién instaladas: faltan ANDROID_HOME (ver Entorno), las imágenes del sistema y los emuladores"
else
  falta "Android SDK (ANDROID_HOME con platform-tools y emulator)"
fi

if [ "$MAC" -eq 1 ]; then
  if xcrun simctl list devices >/dev/null 2>&1; then ok "Xcode con simuladores de iOS"
  else falta "Xcode (App Store): no se instala solo"; fi
else
  aviso "esta máquina no es macOS: los dos dispositivos de iOS no se pueden correr acá; las tareas de UI van a quedar con deuda [d]"
fi

# ---------------------------------------------------------------- entorno
# Los agentes y los scripts corren en shells NO interactivas: lo que esté solo en
# ~/.zshrc no existe para ellos. Por eso se mira ~/.zshenv, con una shell limpia.
echo "Entorno para shells no interactivas (~/.zshenv)"
if hay zsh; then
  for v in ANDROID_HOME JAVA_HOME; do
    val="$(zsh -c "printf %s \"\${$v:-}\"" 2>/dev/null)"
    if [ -n "$val" ] && [ -d "$val" ]; then ok "$v=$val"
    elif [ "$MODO" = "instalar" ] && [ "$MAC" -eq 1 ] && hay brew; then
      case "$v" in
        ANDROID_HOME) ruta="$(brew --prefix)/share/android-commandlinetools" ;;
        JAVA_HOME)    ruta="$(brew --prefix)/opt/openjdk@17" ;;
      esac
      if [ -d "$ruta" ] && ! grep -q "^export $v=" "$HOME/.zshenv" 2>/dev/null; then
        [ -f "$HOME/.zshenv" ] && cp "$HOME/.zshenv" "$HOME/.zshenv.bak-$(date +%Y%m%d-%H%M%S)"
        {
          printf '\n# proyecto-loop: los agentes corren en shells no interactivas y no leen ~/.zshrc\n'
          printf 'export %s="%s"\n' "$v" "$ruta"
          [ "$v" = "ANDROID_HOME" ] && printf 'export ANDROID_SDK_ROOT="$ANDROID_HOME"\nexport PATH="$ANDROID_HOME/platform-tools:$ANDROID_HOME/emulator:$PATH"\n'
          [ "$v" = "JAVA_HOME" ] && printf 'export PATH="$JAVA_HOME/bin:$PATH"\n'
        } >> "$HOME/.zshenv"
        INSTALADOS=$((INSTALADOS + 1)); ok "$v=$ruta (agregado a ~/.zshenv, con respaldo)"
      else
        falta "$v en ~/.zshenv"
      fi
    else
      falta "$v en ~/.zshenv (si solo está en ~/.zshrc, los agentes no lo ven)"
    fi
  done
else
  nover "no hay zsh: no puedo comprobar el entorno de las shells no interactivas"
fi

# ---------------------------------------------------------------- cierre
rm -f /tmp/preparar-maquina.$$.log
echo
echo "Desde la terminal no se puede comprobar, y hay que mirarlo en una sesión:"
echo "  · que Figma esté conectado (propuesta estética, pantallas y storyboard)"
echo "  · las skills que provee la cuenta: engineering, design, figma y anthropic-skills"
echo
printf 'Resumen: %s faltan · %s sin verificar · %s avisos' "$FALTAN" "$SIN_VERIFICAR" "$AVISOS"
[ "$MODO" = "instalar" ] && printf ' · %s instalaciones hechas' "$INSTALADOS"
echo
[ "$MODO" = "instalar" ] && [ "$INSTALADOS" -gt 0 ] && echo "Abrí una sesión nueva: las skills y los plugins cargan al iniciar."
if [ "$FALTAN" -eq 0 ] && [ "$SIN_VERIFICAR" -eq 0 ]; then exit 0; fi
[ "$MODO" = "verificar" ] && echo "Para instalar lo que se puede: $0 --instalar"
exit 1
