# Luxafor Flag: protocolo USB (engenharia reversa)

Levantado em 2026-11-08 com a unidade de firmware `0x3c`. Cada item está marcado:
**[V]** = validado visualmente pelo usuário, **[M]** = medido pelo host, **[?]** = não confirmado.

## Hardware / USB

| Campo | Valor |
|---|---|
| VID:PID | `04d8:f372` (VID da Microchip, logo é um PIC com USB) |
| Fabricante / produto | GREYNUT LTD / LUXAFOR FLAG |
| `bcdDevice` | `3c.00` = versão do firmware (igual à resposta do comando `0x80`) |
| Serial (`iSerial`) | era `000000002498`; virou `000000000000` durante os testes (ver "Incidentes") |
| Interface | 1 interface HID; EP1 IN e EP1 OUT, interrupt, 8 bytes, intervalo de 1 ms |
| LEDs físicos **[V]** | **3** RGB empilhados: 1 = baixo, 2 = meio, 3 = topo; visíveis dos dois lados por difusão |

Descritor HID (33 bytes): página vendor `0xFF00`, um Input de 8 × uint8 e um Output de 8 × uint8, sem Report ID.

> **Linux:** o `/dev/hidraw` descarta um primeiro byte `0x00` (Report ID 0).
> Por isso, escreva `00` + os 8 bytes do comando.
> O driver do kernel `hid-led` expõe `/sys/class/leds/luxaforN:*` em paralelo.

## Comandos (host → dispositivo)

| Op | Nome | Bytes | Resposta |
|---|---|---|---|
| `01` | Cor fixa | `01 LED R G B` | `42` |
| `02` | Fade | `02 LED R G B tempo` | `42` e depois `00 01` |
| `03` | Strobe | `03 LED R G B tempo 00 rep` | `42` e depois `00 01` |
| `04` | Wave | `04 tipo R G B 00 rep vel` | `42` (e `00 01` só no tipo 5) |
| `06` | Padrão | `06 id rep` | `42` e depois `00 01` (exceto o padrão 2) |
| `80` | Versão do firmware | `80` | `80 3c` (os bytes seguintes parecem a cópia do serial no boot) |
| `51` | Gravar serial (6 bytes) na NVM **[M]** | `51 b1 b2 b3 b4 b5 b6` | ecoa os argumentos |
| `52` | Gravar os 4 primeiros bytes do serial na NVM **[M]** | `52 b1 b2 b3 b4` | ecoa os argumentos |
| `62` | Ler o serial atual (não grava) **[M]** | `62` | `62 b1 b2 b3 b4` (os 4 primeiros, como medido) |

Os opcodes `05` e `07`–`0F` **não existem**: o aparelho não responde. O `00` aparente nas primeiras varreduras era o Report ID engolido pelo `hidraw` (o aparelho recebia o segundo byte).

### Endereço de LED (byte 1)
- `01`, `02`, `03` **[V]**: LED individual (baixo, meio, topo).
- `ff` **[V]**: todos.
- `04`–`06`, `41`, `42` **[V]**: aceitos (ACK), mas não acendem nada; seriam LEDs de outro modelo.
- **`13` trava o firmware [M]**: o endpoint OUT para de aceitar dados, e só uma reconexão física resolve. É provável que o endereço seja usado como índice de array sem checagem de limite.
- Os valores de `14` a `fe` não foram testados.

### Cor e brilho **[V]**
- PWM linear de 8 bits por canal. Até o valor 1 acende, fraco.
- A diferença entre 64 e 255 parece pequena por causa da percepção logarítmica do olho. Para escurecer de forma perceptível, use uma curva gamma.
- As 8 cores testadas aparecem fiéis nos 3 LEDs.

### Fade **[M]**
- Duração ≈ |Δbrilho| × `tempo` × 0,25 ms.
- Exemplos de 0 a 255: `tempo` 1 → 0,12 s, 10 → 0,64 s, 20 → 1,29 s, 100 → 6,4 s, 200 → 12,8 s.
- Se a cor-alvo for igual à atual, termina na hora.

### Strobe **[M][V]**
- Duração ≈ `rep` × `tempo` × 65 ms.
- `rep` = número de piscadas **[V]**.
- No fim, **restaura a cor anterior** **[V]**.

### Wave **[V]** (`vel` maior = mais lento)
| Tipo | Com 3 LEDs |
|---|---|
| 1 | sobe de baixo para cima |
| 2 | vários LEDs acesos juntos, mudando |
| 3 | sobe de baixo para cima (variação) |
| 4 | os 3 fixos na cor, depois apagam |
| 5 | os 3 pulsam juntos, uma vez por `rep`; único tipo que manda `00 01` |

### Padrões embutidos **[V][M]** (duração por repetição)
| Id | Descrição | Duração |
|---|---|---|
| 1 | semáforo: vermelho → vermelho+amarelo → verde | 2,1 s |
| 2 | sobe um a um, fica branco, troca de cor e repete | sem evento de fim |
| 3 | arco-íris | 11,5 s |
| 4 | 3 cores, cada uma forte e depois clareando | 15,8 s |
| 5 | polícia: flash vermelho e depois azul | 0,9 s |
| 6 | arco-íris terminando em azul | 2,6 s |
| 7 | verde → rosa → azul | 1,35 s |
| 8 | arco-íris | 3,5 s |

Os ids 0 e 9+ não foram testados, pelo mesmo risco de índice fora da tabela.

### Repetições = 0 **[M]**
Em strobe, wave e padrão, `rep = 0` repete até chegar outro comando. Nenhum evento de fim foi recebido em 8 s. Qualquer comando de cor interrompe a animação.

## Respostas (dispositivo → host)
- `42 00 …`: ACK de comando de LED.
- `00 01 …`: evento assíncrono de fim de animação.
- `80 VV …`: versão do firmware.

## Incidentes durante a engenharia reversa
1. **Travamento com `01 13 …`.** Um reset USB por software (`USBDEVFS_RESET`) recuperou o aparelho uma vez. Na segunda tentativa, o processo ficou preso no kernel e travou o USB do barramento, e foi preciso reiniciar o PC. Não use reset por software; reconecte o aparelho fisicamente.
2. **O serial mudou de forma permanente** de `000000002498` para `000000000000`. Os testes posteriores mostraram que `51` grava 6 bytes do serial na NVM e `52` grava os 4 primeiros; `62` só lê. A troca é consistente com uma escrita de zeros via `51` ou `52`. Na época não foi possível separar isso do travamento com `0x13`. O valor fica guardado em memória não volátil.

## Em aberto
- Endereços de `14` a `fe` e padrões 0/9+ (risco de travar).
- Firmware: identificar o MCU (abrir o case) e verificar ICSP ou bootloader.

`51`, `52` e `62` foram identificados: ver a tabela de comandos. `51` e `52` **gravam** o serial; não os use em um aparelho cujo serial você queira preservar.
