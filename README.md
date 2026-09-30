# claude-usage-bar

Barra de consumo do plano claude.ai no painel superior do GNOME.

```
[icone] ███████░░░ 75%
```

Hover mostra `$150.00 de $200.00 usados  -  restam $50.00`.
A cor segue o campo `severity` que a propria API devolve: laranja em `normal`,
amarelo em `warning`, vermelho em qualquer nivel acima.

## Como funciona

Um script de shell consulta `https://api.anthropic.com/api/oauth/usage` — o mesmo
endpoint que o `/usage` do Claude Code usa — e le `spend.used` / `spend.limit`.
A saida vai para a extensao [Executor](https://extensions.gnome.org/extension/2932/executor/),
que a renderiza no painel.

O token OAuth e lido de `~/.claude/.credentials.json` **em tempo de execucao** e
usado apenas no header `Authorization`. Nao e copiado, gravado nem impresso em
nenhum momento — nem no modo `--debug`, que sanitiza a resposta.

## Instalacao

Requisitos: GNOME Shell 45+, `jq`, `curl`, Claude Code logado, e a extensao
Executor instalada.

```bash
./install.sh
```

Depois faca **logout/login** — no Wayland o gnome-shell nao recarrega extensoes
em runtime.

Para remover: `./uninstall.sh`

## Diagnostico

```bash
claude-usage-bar --debug
```

Imprime o codigo HTTP, o campo `spend`, o estado do cache e o corpo sanitizado
da resposta.

Falhas ficam registradas em `~/.cache/claude-usage-bar.log` (so timestamp e
codigo HTTP — sem token, sem corpo).

## Cache e rate limit

O endpoint aplica rate limit e nao e documentado; o orcamento real e desconhecido,
e o proprio Claude Code consome do mesmo balde. Por isso:

| | |
|---|---|
| TTL do cache | 900s (~96 chamadas/dia no teto) |
| Recuo apos falha | 1800s, apagado no primeiro sucesso |
| Tick do Executor | 300s (le cache, nao a rede) |
| Cache aceito ate | 48h, com a idade no tooltip e a cor apagada |

Sem resposta da API, a barra segura o ultimo valor conhecido em tom apagado em
vez de zerar. A matiz da severidade e preservada, para um alarme nao sumir so
porque o dado envelheceu.

## Limitacoes conhecidas

- **O endpoint nao e documentado.** Foi extraido do binario do Claude Code
  (`strings`), e pode mudar ou sumir em qualquer atualizacao. A resposta traz
  varios campos com nomes de codinome, todos nulos; so `spend` e usado.
- **O script nao renova o token.** Quem renova e o Claude Code. Se voce passar
  a madrugada sem abrir o Claude Code, o token vence e a chamada devolve 401 —
  a barra segue mostrando o ultimo valor ate 48h. Renovar pelo `refreshToken`
  aqui significaria escrever no mesmo arquivo que o Claude Code escreve, e uma
  escrita concorrente malfeita pode invalidar o refresh token.
- **Com 10 celulas, 97% e 100% pintam as dez.** O numero ao lado desambigua.
- O texto do tooltip nao pode conter `>`: a diretiva
  `<executor.tooltip.TEXTO>` e delimitada por esse caractere.

## Patches na extensao

O Executor nao acompanha arquivo de licenca no pacote da loja, entao este repo
nao redistribui o codigo dele — `patch-executor.py` aplica as mudancas sobre a
sua instalacao, de forma idempotente e com backup em `extension.js.orig`:

1. **Icone** — o Executor renderiza um `St.Label`, que e texto puro. O patch
   insere um `St.Icon` no inicio do box, lendo `~/.config/<uuid>/icon.svg`.
2. **Tooltip** — o GNOME Shell nao tem API de tooltip. O patch conecta
   `enter-event`/`leave-event` e monta um `St.Label` com a classe `dash-label`,
   o mesmo balao que a dash do sistema usa. O texto chega numa diretiva nova,
   `<executor.tooltip.…>`, encaixada no parser que ja existia para `css` e `markup`.

Se uma atualizacao do Executor sobrescrever `extension.js`, rode
`patch-executor.py` de novo.
