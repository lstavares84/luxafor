# SIGNA — software (firmware + app de desktop)

Arquitetura, protocolo e decisões: [`arquitetura.md`](arquitetura.md).

```
software/
  data/produto.json        fonte única dos estados (cópia do caderno)
  firmware/                C, STM32C071G8U6 + TinyUSB, testes de host em tests/
  app/                     Python 3.10+: daemon, CLI, bandeja, extensão, exemplos de hooks
  docs/                    este README e arquitetura.md
```

## 1. Firmware

### Compilar

Precisa de `arm-none-eabi-gcc` (testado com 14.2.1, pacote `gcc-arm-none-eabi` do Debian 13), `make`, `python3` e `git`.

```sh
cd firmware
tools/fetch_deps.sh        # TinyUSB, cmsis-device-c0 e CMSIS 5 nas versões testadas
make                       # build/signa.elf, .bin, .hex  (≈ 17,5 KB de flash, 2,9 KB de RAM)
make test                  # testes de host (gcc, ASan + UBSan)
make tables                # regenera as tabelas depois de mudar data/produto.json
```

Variantes: `make USB_IDS=luxafor` usa `04d8:f372`, o par do Luxafor Flag. Serve só no protótipo pessoal, para testar software que procura esse par, e nunca em unidade vendida. `make AUTO_NBOOT_SEL=1` faz o firmware zerar `nBOOT_SEL` sozinho no 1º boot.

**VID:PID:** o padrão é `1209:0001`, o "Test PID" do pid.codes, que só serve para desenvolvimento. O par definitivo é uma decisão sua (`firmware/src/usb_ids.h` e `app/signa/device.py`).

### Gravar por USB (DFU da ROM)

1. Chip novo (flash vazia): ligue o USB e ele já aparece como `0483:df11` ("STM32 BOOTLOADER").
2. Depois, para voltar ao DFU: feche o **JP1** (ponte de solda BOOT0), replugue e grave. Abra o JP1 de novo para rodar o firmware. Isso só funciona com `nBOOT_SEL = 0` (passo 3).

```sh
dfu-util -l                                   # deve listar 0483:df11
make flash-dfu                                # = dfu-util -a 0 -d 0483:df11 -s 0x08000000:leave -D build/signa.bin
```

No Linux, para gravar sem root, use a regra udev em `app/examples/99-signa.rules`. No Windows, o dfu-util precisa do driver WinUSB no `0483:df11` (Zadig), ou então use o STM32CubeProgrammer, que traz o próprio driver.

### Option bytes (uma vez por placa)

Com a flash já gravada, o JP1 só vale se `nBOOT_SEL = 0`, porque aí o pino BOOT0 (PA14) passa a decidir. Deixe `nBOOT1 = 1` (padrão), para que BOOT0 = 1 escolha o bootloader da ROM.

```sh
STM32_Programmer_CLI -c port=SWD  -ob nBOOT_SEL=0     # pelo Tag-Connect (ST-LINK)
STM32_Programmer_CLI -c port=usb1 -ob nBOOT_SEL=0     # ou pelo próprio DFU, na 1ª gravação
STM32_Programmer_CLI -c port=SWD  -ob displ           # conferir
```

Alternativa: compilar com `make AUTO_NBOOT_SEL=1`.

### Gravar e depurar por SWD (TC2030)

Tag-Connect TC2030-IDC-NL na face de baixo, com a pinagem 1 VCC, 2 SWDIO, 3 nRESET, 4 SWCLK, 5 GND. Mantenha o JP1 aberto ao depurar: o PA14 é SWCLK e BOOT0 ao mesmo tempo.

```sh
make flash-swd     # = openocd -f interface/stlink.cfg -f target/stm32c0x.cfg -c "program build/signa.elf verify reset exit"
# ou
STM32_Programmer_CLI -c port=SWD -w build/signa.hex -v -rst
```

O OpenOCD 0.12.0 (a release de 2023) **não reconhece** o STM32C071. Use um build do OpenOCD com o commit 250ab10 ("flash/stm32l4x: add STM32C071xx support", jan. 2025) ou mais novo, ou então o STM32CubeProgrammer.

### Primeiro teste na placa (checklist)

1. `lsusb` mostra `1209:0001 SIGNA rev C`, com serial de 12 dígitos hex (derivado do UID).
2. `signa-cli devices` responde "SIGNA nativo".
3. `python3 ../../luxafor.py`, ajustado para o VID:PID, ou `signa-cli demo` com a placa: `01 FF FF 00 00` tem que dar **vermelho**. Se der verde, a ordem G/R/B está trocada (`ws2816_encode.c`).
4. Analisador lógico ou osciloscópio no R3: bit 0 ≈ 250 ns alto, bit 1 ≈ 667 ns, sem intervalo entre palavras.
5. ERRO pisca a 2,5 Hz (câmera lenta do celular: 12 piscadas em 4,8 s).

## 2. App de desktop

### Instalar

```sh
cd app
python3 -m venv .venv && . .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -e ".[google,outlook]"                   # + [tray] para a bandeja, [hotkey] para o atalho
signa-cli init                                        # cria config.toml e token.txt na pasta de config
signa-cli demo                                        # simulador: todos os estados no terminal
signa-cli daemon --sim                                # o serviço inteiro, sem hardware
signa-cli daemon                                      # com SIGNA ou Luxafor plugado
```

Pasta de config: `%APPDATA%\signa` (Windows), `~/Library/Application Support/signa` (macOS) ou `~/.config/signa` (Linux). Também dá para apontar outra com `SIGNA_HOME`. No Linux, instale a regra udev (`app/examples/99-signa.rules`).

Para iniciar com o sistema, crie uma tarefa agendada no login rodando `signa-cli daemon --tray` (Windows), um LaunchAgent (macOS) ou um serviço `systemd --user` (Linux). Ainda não há instalador.

### Agenda

**Google:** no Google Cloud Console, crie um projeto, ative a Google Calendar API e crie um cliente OAuth do tipo "App para computador". Baixe o JSON para fora do repositório e aponte `[google].client_secrets_file` para ele.

```sh
signa-cli login google      # abre o navegador; o token vai para o chaveiro do sistema
```

Depois, em `config.toml`: `[google] enabled = true`, `calendars = ["primary"]`. Enquanto o app estiver em modo de teste no Google, só as contas adicionadas como "usuário de teste" conseguem entrar.

**Outlook / Microsoft 365:** no portal do Microsoft Entra ID, registre um app, ative "Permitir fluxos de cliente público" e adicione a permissão delegada `Calendars.Read`. Copie o "ID do aplicativo (cliente)" para `[outlook].client_id`.

```sh
signa-cli login outlook     # mostra um código para digitar em microsoft.com/devicelogin
```

Opções da sala: `lead_minutes` (padrão 5, o aviso de "prestes a entrar"), `tentative_is_busy` e `ignore_all_day`.

### Comandos manuais

```sh
signa-cli sala ocupado --por 45m     # vence a agenda por 45 min
signa-cli sala livre                 # até `signa-cli sala auto`
signa-cli toggle                     # para ligar num atalho do sistema
signa-cli modo --display misto --ia on     # sala | misto | escada; IA é opt-in
signa-cli status
```

### IAs (opt-in)

- **Claude Code:** mescle `app/examples/claude-code-settings.json` em `~/.claude/settings.json`. Todos os eventos chamam `signa-cli hook claude-code`, que lê o JSON do hook e decide o estado. Para chamar um estado fixo em cada evento, use a versão sem tradutor, `claude-code-settings-explicit.json` (`signa-cli ai --source claude-code --state …`). Cada hook custa ~50–100 ms de Python por chamada de ferramenta.
- **Codex CLI:** copie `app/examples/codex-hooks.json` para `~/.codex/hooks.json` e aprove em `/hooks`, porque o Codex só roda hooks revisados. Alternativa mínima: `codex-config-notify.toml` (só "terminou o turno").
- **ChatGPT, Claude e Grok na web:** abra `chrome://extensions`, ligue o modo desenvolvedor, use "Carregar sem compactação" e escolha `app/extension`. Nas opções da extensão, cole o conteúdo de `token.txt`. **É experimental:** lê o HTML das páginas e vai quebrar quando os sites mudarem. Os seletores ficam em `extension/sites.js`.

### Luxafor Flag original

O app detecta pelo `0x1F`: sem resposta, usa o protocolo do Flag. Em `[device] luxafor_render`, o modo `stream` (padrão) reproduz as curvas mandando `01` a 25 Hz, e o modo `opcodes` usa um comando por estado (`04` wave 5 para respiração, `03` strobe para piscar; pulso duplo vira cor fixa). O app nunca manda endereço fora de 1, 2, 3 e FF.

### Testes

```sh
cd app && pip install -e ".[test]" && python -m pytest -q
```
