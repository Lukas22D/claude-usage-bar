#!/usr/bin/env python3
"""Aplica dois patches na extensao Executor: icone no inicio do box e tooltip no hover.

Idempotente: rodar duas vezes nao duplica nada. Guarda extension.js.orig na
primeira execucao. O Executor nao acompanha licenca no pacote da loja, entao
distribuimos o patch em vez de uma copia modificada do codigo dele.
"""
import shutil
import sys
from pathlib import Path

EXT = Path.home() / ".local/share/gnome-shell/extensions/executor@raujonas.github.io"

ICON_ANCHOR = """    initOutputLabels(location) {
        location.box.remove_all_children();
"""
ICON_PATCH = """    initOutputLabels(location) {
        location.box.remove_all_children();

        // icone fixo no inicio do box. Some sozinho se o arquivo nao existir.
        let iconFile = Gio.File.new_for_path(
            GLib.get_user_config_dir() + '/executor@raujonas.github.io/icon.svg');
        if (iconFile.query_exists(null)) {
            location.box.add_child(new St.Icon({
                gicon: new Gio.FileIcon({file: iconFile}),
                style_class: 'system-status-icon',
                style: 'margin-right: 5px;',
                y_align: 2,
            }));
        }
"""

HOVER_ANCHOR = "            this.locations[position].box = new St.BoxLayout({style_class: 'panel-button', reactive: true});\n"
HOVER_PATCH = HOVER_ANCHOR + """
            // tooltip no hover, reusando o estilo 'dash-label' do proprio shell.
            this.locations[position].box.connect('enter-event', () => {
                let box = this.locations[position].box;
                if (!box.__tooltipText || this.tooltip) {
                    return;
                }
                this.tooltip = new St.Label({style_class: 'dash-label', text: box.__tooltipText});
                Main.uiGroup.add_child(this.tooltip);
                let [x, y] = box.get_transformed_position();
                this.tooltip.set_position(
                    Math.round(x + box.width / 2 - this.tooltip.width / 2),
                    Math.round(y + box.height + 4)
                );
            });
            this.locations[position].box.connect('leave-event', () => {
                this.tooltip?.destroy();
                this.tooltip = null;
            });
"""

DIRECTIVE_ANCHOR = """                } else if (settingDivided[1] == 'markup') {
                    markupSet = true;
                }"""
DIRECTIVE_PATCH = """                } else if (settingDivided[1] == 'markup') {
                    markupSet = true;
                } else if (settingDivided[1] == 'tooltip') {
                    location.box.__tooltipText = settingDivided.slice(2).join('.');
                }"""

CLEANUP_ANCHOR = "        console.log('Executor stopped');"
CLEANUP_PATCH = """        this.tooltip?.destroy();
        this.tooltip = null;

        console.log('Executor stopped');"""


def main():
    js = EXT / "extension.js"
    if not js.exists():
        sys.exit(f"Executor nao encontrado em {EXT}\n"
                 "Instale em https://extensions.gnome.org/extension/2932/executor/")

    src = js.read_text()
    if "__tooltipText" in src and "iconFile" in src:
        print("patches ja aplicados, nada a fazer")
        return

    backup = EXT / "extension.js.orig"
    if not backup.exists():
        shutil.copy(js, backup)
        print(f"backup: {backup}")

    for name, old, new in [
        ("icone", ICON_ANCHOR, ICON_PATCH),
        ("hover", HOVER_ANCHOR, HOVER_PATCH),
        ("diretiva tooltip", DIRECTIVE_ANCHOR, DIRECTIVE_PATCH),
        ("limpeza no disable", CLEANUP_ANCHOR, CLEANUP_PATCH),
    ]:
        if new.strip() in src:
            print(f"  {name}: ja presente")
            continue
        if src.count(old) != 1:
            sys.exit(f"  {name}: ancora encontrada {src.count(old)}x, esperava 1. "
                     "Versao do Executor incompativel; restaure extension.js.orig.")
        src = src.replace(old, new)
        print(f"  {name}: ok")

    js.write_text(src)
    print("\npatches aplicados. Faca logout/login para o gnome-shell recarregar.")


if __name__ == "__main__":
    main()
