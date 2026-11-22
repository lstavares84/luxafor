# Pendências da Page — LUXCLONE (22 nov. 2026, America/Sao_Paulo)

Resumo das três caixas ainda abertas em *Próximos passos de validação*. A placa rev C **não foi alterada**.

## 1. Comando dos 2 últimos bytes do serial — concluído

Achado desta conversa, já confirmado no aparelho:

- **`0x51 b1 b2 b3 b4 b5 b6`** grava **os 6 bytes** do `iSerial` em memória não volátil. O valor sobrevive a reconectar o USB.
- **`0x52 b1 b2 b3 b4`** grava **só os 4 primeiros**; os 2 últimos ficam como estavam.
- **`0x62`** e **`0x80`** leem de volta (o `0x80` devolve a cópia carregada no boot, então uma gravação só aparece aí e no descritor depois de replugar).
- O serial de fábrica **`000000002498`** (`00 00 00 00 24 98`) foi **restaurado e conferido**.

No clone, implementar os três comandos da mesma forma. Não repetir escritas cegas no original: o `0x51` de fato altera o serial de modo permanente.

## 2. `0x05`/`0x07` — encerrado: opcodes inexistentes

O relatório Claude (varredura do 1º byte com args `ff 10 00 00 05 00 01`, e varredura com payload zerado) mostrou **silêncio** em `0x05` e `0x07`–`0x0F`. Só respondem `01`, `02`, `03`, `04`, `06`, `51`, `52`, `62`, `80`. O `PROTOCOLO.md` do repo **não lista** `0x05`/`0x07` e trata os demais opcodes como silêncio.

A afirmação nossa de “ACK `42` com payload zerado” **não está no PROTOCOLO.md** e contradiz essa varredura — fica retirada (provável confusão com o `0x00`, que o PROTOCOLO marca como ACK `42`). O script `teste_hid_05_07.py` é desnecessário.

A captura lógica deixa de ser bloqueante. Continua **opcional** só para PWM, duty do strobe e curva do wave. Alternativas sem custo (relatório Claude, §17): câmera lenta do celular e fotodiodo no microfone — ver [`captura_logica.md`](captura_logica.md). Especificação do firmware: [`firmware_comportamento.md`](firmware_comportamento.md).

Sobre o `0x80`: é comando de **versão** (`80 3c`). Não é leitura de serial (isso é o `0x62`); os bytes seguintes do pacote parecem só ecoar a cópia de boot do serial.

## 3. Antes de encomendar a rev C (chamada “rev A” na Page) — riscos fechados no papel

Nenhuma mudança de PCB. USB e BOOT0 já estão certos. Detalhes e fontes abaixo; preços/estoque do dia em [`estoque_stm32c071.json`](estoque_stm32c071.json).

### 3.1 Estoque e preço do `STM32C071G8U6` (UFQFPN-28 4×4, 64 KB) — 22 nov. 2026

| Fonte | Qtd. | Preço unit. (US$) | Status |
|---|---|---|---|
| **JLCPCB** C44521811 (extended) | **109** | 2,81 (1–9); 1,80 (100–489); 1,62 (≥980) | verificado (API de peças, 10:51 America/Sao_Paulo) |
| **LCSC** C44521811 | **36** | 2,83 (1); 1,82 (100); 1,63 (980) | verificado (página do produto, `stockNumber` / `productPriceList`) |
| **Mouser** 511-STM32C071G8U6 | 2.781 (busca) | 1,72 (1 un., busca) | **não verificado na página** (fetch 403) |
| **DigiKey** | 42 imediatos (busca, página de destaque STM32C0x1) | 1,85 (1 un., busca) | **não verificado na página** (Cloudflare) |

Com 109 peças na JLC dá para um lote de protótipo (e para ~100 placas montadas, apertado). Para série, o estoque da JLC/LCSC é o gargalo; Mouser (se o número da busca se confirmar) é o caminho para comprar e consignar.

### 3.2 Reserva pin-compatível

**`STM32C071GBU6`** (UFQFPN-28 4×4, **versão GP**, 128 KB): a pinagem coincide nas 28 posições com o `G8U6` (mesmo cristal, mesmos PA11/PA12 nos pinos 18/19, PA14-BOOT0 no 21). Fontes: DS14693 fig. 5 (versão GP) e tabelas de produto ST (família STM32C071x8/xB). O firmware só precisa caber nos 64 KB ou passar a usar 128 KB.

- JLC C42113261: **0** em estoque (verificado).
- Mouser: 4.693 e a partir de US$ 2,37 — **só resultado de busca**, página não aberta.

**Não usar o sufixo N** (`STM32C071G8U6N` / `GBU6N`): no DS14693 a versão N do UFQFPN-28 troca o pino 17 de `PC6` para `VDDIO2`. Não é drop-in na nossa placa.

### 3.3 Remapeamento PA11/PA12 no UFQFPN-28 — não precisa ligar os bits

No encapsulamento GP que usamos:

- Pino **18** = `PA11 [PA9]` = **USB_DM**
- Pino **19** = `PA12 [PA10]` = **USB_DP**

A nossa rev C já liga `U1` pino 18 a `USB_DM` e pino 19 a `USB_DP` (`tools/netlist.py`).

O datasheet (DS14693, nota 3 da tabela de pinos) diz: *“Pins PA9 and PA10 can be remapped **in place of** pins PA11 and PA12 (**default mapping**), using SYSCFG_CFGR1.”*

O RM0490, SYSCFG_CFGR1 (cap. 9):

- **PA11_RMP** = bit 3; 0 = PA11 (padrão), 1 = o pino passa a ser PA9
- **PA12_RMP** = bit 4; 0 = PA12 (padrão), 1 = o pino passa a ser PA10
- Reset desses bits: 0 (o byte baixo do registrador, fora `MEM_MODE`, começa zerado)

Conclusão: no UFQFPN-28 o USB já está nos pinos 18/19 **sem remapeamento**. O firmware **não deve** setar `PA11_RMP`/`PA12_RMP` — isso tiraria PA11/PA12 do pino e quebraria o USB (e o DFU da ROM, que usa PA11/PA12). A nota antiga sobre remapeamento valia para o raciocínio do TSSOP-20 / “PA11 no pino errado”, não para esta peça.

(Comunidade ST, TDK, jan. 2025: *“PA11/PA12 are used until you remap them… PA11/PA12 are default.”*)

### 3.4 Bootloader USB DFU — suportado; a placa já tem caminho de entrada

Fontes: DS14693 §3.5 e tabela de família (“USB DFU”); AN2606; AN5673 tabela 2; bits em `stm32c071xx.h` (CMSIS ST).

- A ROM tem **USB DFU em PA11/PA12** (além de USART/I2C/SPI).
- **Flash vazia:** o EMPTY check (64 bits em `0x08000000` = `0xFFFF…`) força boot na system memory. Peça virgem enumera em DFU **sem** mexer em option bytes e **sem** fechar o JP1. Depois da primeira gravação, é preciso um **power cycle** (ou `OBL_LAUNCH`) para o hardware limpar a flag EMPTY; um reset de sistema não basta (AN5673).
- **Option bytes de fábrica:** `nBOOT_SEL = nBOOT0 = nBOOT1 = 1` (FLASH_OPTR bits 24/26/25). Com `nBOOT_SEL = 1`, o pino **BOOT0 é ignorado** e o boot vem da flash (ou da ROM, se EMPTY).
- **Para o jumper JP1 passar a valer:** gravar **`nBOOT_SEL = 0`** (e manter `BOOT_LOCK = 0`). Aí BOOT0 alto (PA14) no reset entra na ROM; BOOT0 baixo entra na flash (AN5673 tabela 2).
- PA14/BOOT0 só é amostrado na subida do NRST.

O que a rev C já tem (`netlist.py`):

- USB_DM/DP nos pinos 18/19, com ESD e USB-C — certo para o DFU.
- **JP1** (jumper de solda aberto) + **R4** 1 kΩ para 3,3 V no `PA14`/`SWCLK` (`SWCLK_BOOT0`).
- **J2** Tag-Connect TC2030 (SWD: VCC, SWDIO, NRST, SWCLK, GND).

Não falta trilha nem pino. Não há botão; o jumper basta para retrabalho. Depois da primeira programação, ou se fecha o JP1 **e** se grava `nBOOT_SEL = 0`, ou o firmware salta para a ROM, ou usa-se SWD. Recomendação de firmware: na primeira imagem, gravar `nBOOT_SEL = 0` para o JP1 funcionar daí em diante.

### 3.5 Há algo a mudar na placa?

**Não.** USB nos pinos certos, acesso a BOOT0 e SWD já existem. Um botão táctil em paralelo com o JP1 seria só conforto de bancada, não é necessário para encomendar.
