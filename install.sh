#!/usr/bin/env bash
# Instala a barra de consumo do Claude no painel do GNOME.
set -euo pipefail
HERE=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
UUID=executor@raujonas.github.io
EXT=~/.local/share/gnome-shell/extensions/$UUID

for b in jq curl awk; do
    command -v "$b" >/dev/null || { echo "faltando: $b"; exit 1; }
done
[ -d "$EXT" ] || { echo "Instale a extensao Executor antes:"
                   echo "  https://extensions.gnome.org/extension/2932/executor/"; exit 1; }
[ -f ~/.claude/.credentials.json ] || echo "aviso: ~/.claude/.credentials.json nao existe; faca login no Claude Code"

install -Dm755 "$HERE/claude-usage-bar" ~/.local/bin/claude-usage-bar
install -Dm644 "$HERE/icon.svg"         ~/.config/$UUID/icon.svg
python3 "$HERE/patch-executor.py"

# posicao a esquerda dos icones de bandeja, 300s por tick
python3 - "$EXT" <<'PY'
import json, subprocess, sys, os
schemadir = sys.argv[1] + "/schemas"
def g(*a): return subprocess.run(["gsettings", "--schemadir", schemadir, *a],
                                 capture_output=True, text=True, check=True).stdout.strip()
cmd = {"commands": [{"isActive": True,
                     "command": os.path.expanduser("~/.local/bin/claude-usage-bar"),
                     "interval": 300, "uuid": "claude-usage-bar"}]}
for k, v in [("right-commands-json", json.dumps(cmd)), ("right-active", "true"), ("right-index", "0")]:
    g("set", "org.gnome.shell.extensions.executor", k, v)
print("Executor configurado (direita, 300s)")
PY

gnome-extensions enable $UUID 2>/dev/null || true
echo
echo "Pronto. Faca logout/login para o gnome-shell carregar as mudancas."
echo "Diagnostico:  claude-usage-bar --debug"
