#!/usr/bin/env bash
# Remove a barra e desfaz os patches na extensao.
set -uo pipefail
UUID=executor@raujonas.github.io
EXT=~/.local/share/gnome-shell/extensions/$UUID
[ -f "$EXT/extension.js.orig" ] && mv "$EXT/extension.js.orig" "$EXT/extension.js" && echo "extension.js restaurado"
rm -fv ~/.local/bin/claude-usage-bar ~/.config/$UUID/icon.svg \
       ~/.cache/claude-usage-bar.cache ~/.cache/claude-usage-bar.retry ~/.cache/claude-usage-bar.log
echo "A extensao Executor em si nao foi removida. Logout/login para aplicar."
