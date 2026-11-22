# Luxafor Flag: como ele funciona por dentro

Relatório completo da engenharia reversa do Luxafor Flag (USB `04d8:f372`, firmware `0x3c`), feita em 2026-11-08. O trabalho combinou testes automáticos pelo Python com validação visual do dono do aparelho.

Este documento explica:
- como o aparelho fala com o computador;
- como ele produz cor, brilho e transições;
- como cada animação se comporta no tempo;
- o que a lâmina 05 do caderno conceitual ("Em funcionamento") representa, e como reproduzir cada estado dela no Luxafor de hoje e no indicador próprio;
- todos os testes feitos, em ordem, com o que foi enviado, o que voltou e o que se viu.

A especificação curta do protocolo está em [`PROTOCOLO.md`](../PROTOCOLO.md), e a biblioteca está em [`luxafor.py`](../luxafor.py).

## Como ler as marcações

| Marca | Significado |
|---|---|
| **[V]** | Validado visualmente pelo usuário olhando o aparelho |
| **[M]** | Medido pelo computador (tempo de chegada de eventos USB, respostas do firmware) |
| **[D]** | Derivado das medições por cálculo |
| **[H]** | Hipótese: coerente com os dados, mas não provada |
| **[?]** | Não testado ou desconhecido |

---

## Sumário

1. [Visão geral em uma página](#1-visão-geral-em-uma-página)
2. [O hardware visto pelo USB](#2-o-hardware-visto-pelo-usb)
3. [Como conversar com ele](#3-como-conversar-com-ele)
4. [Onde estão os LEDs](#4-onde-estão-os-leds)
5. [Cor: como o Luxafor produz cada tom](#5-cor-como-o-luxafor-produz-cada-tom)
6. [As "frequências": espectro, PWM e ritmo das animações](#6-as-frequências-espectro-pwm-e-ritmo-das-animações)
7. [Transição suave (fade)](#7-transição-suave-fade)
8. [Piscar (strobe)](#8-piscar-strobe)
9. [Onda (wave)](#9-onda-wave)
10. [Padrões embutidos](#10-padrões-embutidos)
11. [Repetição infinita e interrupção](#11-repetição-infinita-e-interrupção)
12. [O relógio interno do firmware](#12-o-relógio-interno-do-firmware)
13. [Comandos desconhecidos e varreduras](#13-comandos-desconhecidos-e-varreduras)
14. [Incidentes](#14-incidentes)
15. [Lâmina 05 explicada em detalhe](#15-lâmina-05-explicada-em-detalhe)
16. [Cronologia completa dos testes](#16-cronologia-completa-dos-testes)
17. [O que ainda não sabemos e como descobrir](#17-o-que-ainda-não-sabemos-e-como-descobrir)

---

## 1. Visão geral em uma página

O Luxafor Flag é um **dispositivo HID genérico**, o mesmo tipo de um teclado ou mouse, mas com uma página "vendor" própria. Por isso funciona sem driver em qualquer sistema.

**Comunicação:** o computador manda pacotes de **8 bytes**. O primeiro byte é o comando; os outros são parâmetros. O aparelho responde com **`42`** ("recebido") e, nas animações, manda um segundo pacote **`00 01`** quando ela termina.

**Dentro do aparelho:** há **3 LEDs RGB** empilhados (baixo, meio, topo). Cada canal é controlado por **PWM linear de 8 bits**, ou seja, 256 níveis por cor e cerca de 16,7 milhões de combinações. A luz atravessa a bandeira difusora e aparece igual dos dois lados.

**Animações e seus tempos:**

| Animação | Comando | Duração |
|---|---|---|
| Cor fixa | `01` | imediata |
| Transição (fade) | `02` | ≈ **0,25 ms × tempo** por degrau de brilho |
| Piscar (strobe) | `03` | ≈ **65 ms × tempo** por piscada |
| Onda (wave) | `04` | ≈ **65 ms × velocidade** por ciclo |
| Padrão embutido | `06` | de 0,9 s a 15,8 s, conforme o padrão |

Todas as animações aceitam repetição infinita (`rep = 0`), e qualquer comando novo interrompe a que está rodando.

**Os números que importam:**

| Grandeza | Valor | Marca |
|---|---|---|
| LEDs físicos | 3 RGB (baixo = 1, meio = 2, topo = 3) | [V] |
| Resolução | 8 bits por canal, PWM linear | [V] |
| Degrau do fade | 0,252 ms × `tempo` | [M][D] |
| Piscada do strobe | 65,5 ms × `tempo` | [M][D] |
| Ciclo da wave 5 | 64,9 ms × `velocidade` | [M][D] |
| Versão do firmware | `0x3c` (60) | [M] |
| Comando que trava o firmware | `01 13 …` | [M] |

---

## 2. O hardware visto pelo USB

### 2.1 Descritores

Lidos com `lsusb -v -d 04d8:f372` **[M]**:

| Campo | Valor | O que significa |
|---|---|---|
| `idVendor` | `0x04d8` | Microchip: o microcontrolador é um PIC com USB integrado |
| `idProduct` | `0xf372` | Luxafor Flag |
| `bcdDevice` | `3c.00` | Versão do firmware, a mesma que o comando `80` devolve |
| Fabricante / produto | GREYNUT LTD / LUXAFOR FLAG | |
| `iSerial` | era `000000002498`, virou `000000000000` | ver [Incidentes](#14-incidentes) |
| Velocidade | Full Speed, 12 Mbit/s | USB 1.1/2.0 |
| `bMaxPacketSize0` | 8 | pacotes de controle de 8 bytes |
| `bmAttributes` | `0xc0` (se declara autoalimentado) | o valor é comum em firmwares de exemplo |
| `MaxPower` | 100 mA | pedido ao host |
| Interface | 1, classe HID, 2 endpoints | |
| Endpoints | EP1 IN e EP1 OUT, interrupt, 8 bytes, intervalo de 1 ms | |

### 2.2 Descritor de relatório HID

Lido em `/sys/class/hidraw/hidrawN/device/report_descriptor` (33 bytes) **[M]**:

```
06 00 ff   Usage Page (Vendor 0xFF00)
09 01      Usage (1)
a1 01      Collection (Application)
19 01        Usage Minimum (1)
29 08        Usage Maximum (8)
15 00        Logical Minimum (0)
26 ff 00     Logical Maximum (255)
75 08        Report Size (8 bits)
95 08        Report Count (8)
81 00        Input  (Data, Array)   -> 8 bytes do aparelho para o PC
19 01        Usage Minimum (1)
29 08        Usage Maximum (8)
75 08        Report Size (8)
95 08        Report Count (8)
91 00        Output (Data, Array)   -> 8 bytes do PC para o aparelho
c0         End Collection
```

O descritor **não tem Report ID**. É um canal bruto de 8 bytes em cada direção, e todo o significado está no firmware.

### 2.3 O que o Linux já faz sozinho

O kernel carrega o driver **`hid-led`**, que expõe 18 LEDs em `/sys/class/leds/luxaforN:{red,green,blue}:led{0..5}`: 3 cores × 6 LEDs. Cada um aceita `brightness` de 0 a 255 **[M]**.

O driver presume 6 LEDs, mas esta unidade só tem 3 físicos (ver [seção 4](#4-onde-estão-os-leds)). O `luxafor.py` não usa esse driver: fala direto com `/dev/hidrawN`.

---

## 3. Como conversar com ele

### 3.1 O detalhe do byte zero no Linux

No `hidraw`, **o primeiro byte escrito é o número do Report ID**. Se ele é `0x00`, o kernel o descarta e envia o resto. Como o Luxafor não usa Report ID:

- Escrever `00 01 FF FF 00 00 …` faz chegar ao aparelho **`01 FF FF 00 00 …`**, que é o certo.
- Escrever `01 FF FF 00 00` sem o zero na frente também funciona por acaso, porque o primeiro byte não é zero e vai junto.

Por isso o `luxafor.py` sempre prefixa um `0x00` antes dos 8 bytes do comando.

Esse detalhe explica um resultado curioso das primeiras varreduras: "comandos" `00 51`, `00 52`, `00 80` respondiam como `51`, `52` e `80`. O `00` era engolido pelo kernel e o aparelho recebia só o segundo byte. Ver [seção 13](#13-comandos-desconhecidos-e-varreduras).

### 3.2 Formato dos pacotes

**Do computador para o aparelho (8 bytes):**

| Op | Nome | Bytes | Resposta |
|---|---|---|---|
| `01` | Cor fixa | `01 LED R G B 00 00 00` | `42` |
| `02` | Fade | `02 LED R G B tempo 00 00` | `42`, depois `00 01` |
| `03` | Strobe | `03 LED R G B tempo 00 rep` | `42`, depois `00 01` |
| `04` | Wave | `04 tipo R G B 00 rep vel` | `42` (e `00 01` só no tipo 5) |
| `06` | Padrão | `06 id rep 00 00 00 00 00` | `42`, depois `00 01` (exceto o padrão 2) |
| `80` | Versão | `80 00 …` | `80 3c` |

**Do aparelho para o computador (8 bytes):**

| Pacote | Significado |
|---|---|
| `42 00 00 00 00 00 00 00` | ACK: comando de LED aceito |
| `00 01 00 00 00 00 00 00` | Evento assíncrono: a animação terminou |
| `80 3c 00 …` | Resposta de versão |
| `51 xx` / `52 xx` / `62 xx` | Respostas dos comandos desconhecidos (seção 13) |

### 3.3 Endereço do LED (byte 1)

| Valor | Efeito | Marca |
|---|---|---|
| `01` | LED de baixo | [V] |
| `02` | LED do meio | [V] |
| `03` | LED do topo | [V] |
| `ff` | Todos | [V] |
| `04`, `05`, `06` | Aceitos (ACK), mas nada acende | [V] |
| `41` ("front"), `42` ("back") | Aceitos, mas nada acende | [V] |
| `13` | **Trava o firmware** | [M] |
| `14`–`fe` | Não testados | [?] |

---

## 4. Onde estão os LEDs

Este foi o primeiro mapeamento, feito com validação visual a cada passo.

1. **Todos em vermelho** (`01 FF FF 00 00`): o usuário viu "vermelho em tudo" **[V]**.
2. **"front" verde** (`01 41 00 FF 00`): ACK, mas tudo continuou vermelho **[V]**. Assim, o endereço `0x41` da documentação pública não funciona nesta unidade.
3. **Uma cor por endereço de 1 a 6**: vermelho, verde, azul, amarelo, magenta e branco. O usuário viu **só 3 LEDs**: topo azul, meio verde e baixo vermelho **[V]**. Conclusão: 1 = baixo, 2 = meio, 3 = topo, e 4 a 6 não aparecem.
4. **Retestes isolados**, cada um com todo o resto apagado:

| Teste | Comando | Resultado |
|---|---|---|
| 1 | só o LED 4 em amarelo | tudo apagado [V] |
| 2 | só o LED 5 em magenta | tudo apagado [V] |
| 3 | só o LED 6 em branco | tudo apagado [V] |
| 4 | LEDs 4, 5 e 6 em vermelho puro | tudo apagado [V] |
| 5 | endereço `0x42` em verde | tudo apagado [V] |
| 6 | endereço `0x41` em verde | tudo apagado [V] |

O teste 4 descarta a hipótese de defeito num canal de cor: nem vermelho puro acende os LEDs 4 a 6.

**Conclusão [V][H]:** o firmware é genérico e endereça 6 LEDs, herança de um modelo com dois lados. Esta placa só tem 3 montados. Os comandos para 4 a 6, `0x41` e `0x42` são aceitos e escritos em registros que não estão ligados a LED nenhum.

**"Não existe lado"** (observação do usuário **[V]**): a cor vista de um lado da bandeira é a mesma do outro. A bandeira é um difusor único iluminado pela borda.

---

## 5. Cor: como o Luxafor produz cada tom

### 5.1 Mistura aditiva

Cada LED tem três chips (vermelho, verde e azul) muito próximos, e o difusor mistura a luz deles. As cores intermediárias saem da soma:

| Cor | R | G | B | Como se forma |
|---|---|---|---|---|
| vermelho | 255 | 0 | 0 | só o chip R |
| verde | 0 | 255 | 0 | só o G |
| azul | 0 | 0 | 255 | só o B |
| amarelo | 255 | 255 | 0 | R + G |
| ciano | 0 | 255 | 255 | G + B |
| magenta | 255 | 0 | 255 | R + B |
| branco | 255 | 255 | 255 | R + G + B |
| laranja | 255 | 80 | 0 | R forte + um pouco de G |

**Teste das 8 cores [V]:** em 7 rodadas, as 8 cores foram giradas pelos 3 LEDs (rodadas da [seção 16](#16-cronologia-completa-dos-testes)). Cada cor passou por cada posição, e o usuário confirmou "tudo confere" nas 7. Nenhum canal está fraco ou ausente em nenhum LED, e o branco saiu neutro.

### 5.2 Brilho: PWM linear de 8 bits

O firmware não varia a corrente do LED. Ele **liga e desliga o chip muito rápido** (PWM) e controla a fração do tempo em que fica ligado. O valor de 0 a 255 de cada canal é essa fração.

| Teste | Comando | O que se viu |
|---|---|---|
| Brilho A | baixo = 255, meio = 64, topo = 16 (vermelho) | "meio ≈ baixo" [V] |
| Brilho B | baixo = 255, meio = 4, topo = 1 | "dá para ver diferença, depende do ângulo; de lado é bem pouco" [V] |
| Alternância | os 3 LEDs entre 1 e 255 a cada 0,8 s, por 10 s | "pulsou bem visível" [V] |

**O que isso prova:**

1. **Até o valor 1 acende** [V]. Não há zona morta: o nível 1 de 255 (0,4% do tempo ligado) já é visível de frente.
2. **A escala é linear no tempo ligado** [D], e por isso parece "comprimida" no alto. O olho não percebe brilho de forma linear; a percepção segue mais ou menos uma potência de 1/2,2 (lei de Stevens, próxima da curva gamma do sRGB).

| Valor PWM | Fração ligada | Brilho percebido (≈ fração^(1/2,2)) |
|---|---|---|
| 255 | 100% | 100% |
| 128 | 50% | 73% |
| 64 | 25% | 53% |
| 16 | 6,3% | 28% |
| 4 | 1,6% | 15% |
| 1 | 0,4% | 8% |

Por isso "64 parece quase igual a 255": 64 já é metade do brilho percebido. E o pulso 1 ↔ 255 é bem visível: de 8% a 100% percebido.

### 5.3 Correção gamma: como pedir um brilho que pareça certo

Para que um "50% de brilho" pareça metade, o valor enviado deve ser `PWM = 255 × (brilho desejado)^2,2`:

| Brilho que você quer ver | PWM a enviar |
|---|---|
| 100% | 255 |
| 75% | 135 |
| 50% | 55 |
| 25% | 12 |
| 10% | 2 |

Consequência prática: com 8 bits lineares, **a parte baixa da escala tem poucos degraus**. Entre "apagado" e "25% percebido" existem só 12 valores, e é ali que os degraus de um fade aparecem (seção 7.3).

---

## 6. As "frequências": espectro, PWM e ritmo das animações

"Frequência" aparece em três sentidos diferentes, e vale separar:

### 6.1 Frequência da luz (cor espectral)

Cada chip emite numa faixa estreita de comprimento de onda; a cor que vemos é essa faixa.

- **No Luxafor:** o comprimento de onda dos chips **não foi medido** [?]. Medir exige um espectrômetro, e o fabricante não publica esse dado.
- **No indicador próprio:** o LED escolhido, SK6805-EC20, tem curvas típicas no datasheet com pico do azul por volta de 465 nm, do verde por volta de 520 nm e do vermelho por volta de 625 nm. Os valores foram lidos no gráfico do datasheet OPSCO, então são aproximados.
- **Por que importa:** amarelo, ciano e branco não são "frequências próprias". São misturas que o olho interpreta (seção 5.1). Um amarelo de LED RGB não tem luz de 580 nm: tem vermelho e verde juntos. Por isso o tom de uma mistura depende do equilíbrio entre os chips e pode variar um pouco de unidade para unidade.

### 6.2 Frequência do PWM (a cintilação invisível)

O PWM liga e desliga cada chip milhares de vezes por segundo, e o olho integra isso como brilho contínuo.

- **No Luxafor, a frequência de PWM não foi medida** [?]. Em nenhum teste o usuário relatou cintilação a olho nu, o que indica algo acima de umas centenas de Hz [H].
- **Como medir sem osciloscópio** está na [seção 17](#17-o-que-ainda-não-sabemos-e-como-descobrir): câmera de celular em câmera lenta, ou fotodiodo ligado à entrada de microfone.
- **No indicador próprio:** o PWM fica dentro de cada SK6805. O datasheet traz curvas de cor e corrente, mas não deixa clara a frequência, que **precisa ser confirmada** [?]. Esse dado importa se o aparelho for filmado em reuniões de vídeo: PWM baixo cria faixas na imagem.

### 6.3 Frequência das animações (o ritmo que se vê)

Esta é a frequência que o usuário percebe e que a lâmina 05 desenha:

| Animação | Período | Frequência | Como se controla |
|---|---|---|---|
| Strobe `tempo` = 4 | 262 ms | ≈ 3,8 Hz | `03 … 04 00 rep` |
| Strobe `tempo` = 15 | 983 ms | ≈ 1 Hz | `03 … 0f 00 rep` |
| Strobe `tempo` = 20 | 1,31 s | 0,76 Hz | medido [M] |
| Wave 5 `vel` = 37 | 2,4 s | 0,42 Hz | `04 05 R G B 00 rep 25` |
| Wave 5 `vel` = 60 | 3,9 s | 0,26 Hz | medido [M] |

As fórmulas estão nas seções 8 e 9.

---

## 7. Transição suave (fade)

### 7.1 O comando

`02 LED R G B tempo` leva o LED da cor atual até a cor-alvo, canal por canal, e manda `00 01` no fim.

### 7.2 Medições

**Primeira tentativa, inválida [M]:** a sequência alternava vermelho e azul conforme o `tempo` era par ou ímpar. Várias medições deram 0,05 s, porque a cor-alvo era igual à atual e o fade terminava na hora. O erro foi corrigido apagando o LED antes de cada medição.

**Medição válida, do preto ao vermelho máximo (Δ = 255) [M]:**

| `tempo` | Duração medida | Por degrau (÷ 255) |
|---|---|---|
| 1 | 0,121 s | (dominado pela latência USB) |
| 2 | 0,141 s | — |
| 5 | 0,342 s | 0,268 ms ÷ 5 |
| 10 | 0,643 s | 0,252 ms ÷ 10 |
| 20 | 1,285 s | 0,252 ms ÷ 20 |
| 50 | 3,211 s | 0,252 ms ÷ 50 |
| 100 | 6,420 s | 0,252 ms ÷ 100 |
| 200 | 12,821 s | 0,251 ms ÷ 200 |
| 20, até 50% (0 → 128) | 0,703 s | confirma a dependência de Δ |

**Fórmula [D]:**

```
duração ≈ |Δ brilho| × tempo × 0,252 ms   (+ ~50 ms de latência de medição)
```

- `Δ brilho` é a maior variação entre os três canais, de 0 a 255.
- `tempo` vai de 1 a 255. O fade mais longo, 0 → 255 com `tempo` = 255, dura cerca de 16,4 s.
- **Se a cor-alvo é igual à atual**, Δ = 0 e o fade termina imediatamente, mas ainda manda `00 01` [M].

### 7.3 Por que o fade parece "rápido no começo e lento no fim"

O fade do firmware é **linear em PWM**: sobe 1 degrau a cada `tempo × 0,25 ms`. Mas o olho é não linear (seção 5.2). Do preto ao máximo em 1,3 s (`tempo` = 20):

| Tempo decorrido | PWM | Brilho percebido |
|---|---|---|
| 0,13 s (10%) | 26 | 35% |
| 0,32 s (25%) | 64 | 53% |
| 0,64 s (50%) | 128 | 73% |
| 0,96 s (75%) | 191 | 88% |
| 1,28 s (100%) | 255 | 100% |

**Em um quarto do tempo, o LED já parece estar na metade do brilho.** A transição "acende de repente e depois se arrasta". Na descida o efeito se inverte: parece demorar a apagar e depois some de uma vez.

**Degraus visíveis:** na subida, os primeiros valores (1, 2, 3, 4…) são saltos grandes de brilho percebido (8%, 11%, 13%, 15%…). Em fades lentos (`tempo` alto) e com o LED quase apagado, cada degrau dura bastante (com `tempo` = 200, são 50 ms por degrau) e o "escadinha" fica visível de frente [H, coerente com a seção 5.2].

### 7.4 Como fazer um fade que pareça suave (perceptualmente linear)

Há dois caminhos:

1. **Pelo computador, com o Luxafor atual:** quebrar a transição em segmentos curtos, cada um um `02` com alvo calculado pela curva gamma, esperando o `00 01` de cada um. Exemplo com 8 segmentos para subir em 1,6 s:

| Segmento | Brilho percebido alvo | PWM alvo | Δ | `tempo` para 0,2 s |
|---|---|---|---|---|
| 1 | 12,5% | 2 | 2 | 255 (limitado) |
| 2 | 25% | 12 | 10 | 79 |
| 3 | 37,5% | 30 | 18 | 44 |
| 4 | 50% | 55 | 25 | 32 |
| 5 | 62,5% | 91 | 36 | 22 |
| 6 | 75% | 135 | 44 | 18 |
| 7 | 87,5% | 190 | 55 | 14 |
| 8 | 100% | 255 | 65 | 12 |

O resultado é uma curva em segmentos de reta que se aproxima da curva perceptual. O custo é a latência USB entre segmentos (cerca de 50 ms, já medida), que limita a fluidez.

2. **No indicador próprio:** o firmware calcula a curva a cada quadro, por exemplo a 100 Hz, com tabela gamma, e manda cores ao SK6805 já corrigidas. Assim a suavidade não depende do USB.

---

## 8. Piscar (strobe)

### 8.1 O comando

`03 LED R G B tempo 00 rep`: pisca `rep` vezes na cor dada e, no fim, **volta à cor anterior** [V].

### 8.2 Medições [M]

| `tempo` | `rep` | Duração | Por (`tempo` × `rep`) |
|---|---|---|---|
| 10 | 1 | 0,663 s | 66,3 ms |
| 10 | 2 | 1,305 s | 65,2 ms |
| 10 | 4 | 2,610 s | 65,2 ms |
| 20 | 1 | 1,325 s | 66,2 ms |
| 20 | 2 | 2,610 s | 65,2 ms |
| 40 | 1 | 2,628 s | 65,7 ms |
| 5 | 4 | 1,324 s | 66,2 ms |

**Fórmula [D]:**

```
duração ≈ rep × tempo × 65,5 ms
período de cada piscada ≈ tempo × 65,5 ms   →   frequência ≈ 15,3 Hz / tempo
```

### 8.3 Validação visual

| Teste | O que se viu |
|---|---|
| Verde, `tempo` 20, `rep` 3 (primeira vez) | o usuário não sabia que devia contar; terminou apagado [V] |
| Mesmo teste, avisado antes | **3 piscadas** [V]: `rep` é o número de piscadas |
| Base azul, depois strobe vermelho com `rep` 2 | **voltou ao azul** [V]: o strobe restaura a cor anterior |

A partir desse teste, todo ensaio visual passou a ter 5 s de espera e um aviso de "o que esperar".

**Proporção ligado/desligado:** a fração do período em que a cor fica acesa **não foi medida** [?]. A hipótese mais simples é 50% [H].

---

## 9. Onda (wave)

### 9.1 O comando

`04 tipo R G B 00 rep vel`: animação entre LEDs. Um `vel` maior deixa a animação **mais lenta** [V]; o byte funciona como período, não como velocidade.

### 9.2 Os 5 tipos, com 3 LEDs [V]

Todos os testes foram em ciano, com `rep` 5 e `vel` 60, exceto onde indicado.

| Tipo | O que o usuário viu | Evento de fim |
|---|---|---|
| 1 | Sobe de baixo para cima. Com `vel` 30 e `rep` 3, durou menos de 5 s; com `vel` 60 ficou visivelmente mais lento | não [M] |
| 2 | "Não liga em ordem"; vários LEDs acesos juntos, mudando | não [M] |
| 3 | Sobe de baixo para cima (variação do 1) | não [M] |
| 4 | Os 3 LEDs ficam parados em azul-claro e depois apagam | não [M] |
| 5 | **Os 3 pulsam juntos, 5 vezes** (= `rep`) | **sim, aos 19,48 s** [M] |

### 9.3 Fórmula [D]

O tipo 5 é o único que avisa o fim, então é o único com tempo medido:

```
19,48 s ÷ 5 pulsos = 3,90 s por pulso;  3,90 s ÷ vel 60 = 64,9 ms
→ período de cada pulso ≈ vel × 65 ms
```

É a **mesma base de 65 ms do strobe** (seção 12).

**Uso prático:** a wave 5 é o "respirar" nativo do Luxafor. Com `rep = 0` ela pulsa para sempre; com `vel` = 37, o período é 2,4 s, que é o ritmo do estado "processando" da lâmina 05. O formato exato da curva de brilho dentro de cada pulso não foi medido [?].

---

## 10. Padrões embutidos

`06 id rep` toca uma das sequências gravadas no firmware. Durações por repetição, medidas pelo evento `00 01` **[M]**, e descrições do usuário **[V]**:

| Id | Nome no `luxafor.py` | O que se vê | Duração por repetição | Evidência |
|---|---|---|---|---|
| 1 | `traffic` | Semáforo: topo vermelho → topo vermelho + meio amarelo → baixo verde | 2,1 s | 1×: 2,10 s; 3×: 6,21 s |
| 2 | `climb` | Acende baixo, meio, topo; fica branco; muda tudo para outra cor; repete | — | **sem evento de fim** em 20 s |
| 3 | `rainbow` | Arco-íris | 11,5 s | 1×: 11,47 s; 3×: 35,10 s |
| 4 | `tones` | 3 cores, cada uma forte nos 3 LEDs e depois clareando | 15,8 s | 1×: 15,82 s (2 vezes) |
| 5 | `police` | Flash vermelho e depois azul | 0,9 s | 1×: 0,90 s |
| 6 | `rainbow-blue` | Arco-íris terminando em azul | 2,6 s | 1×: 2,95 s; 3×: 7,81 s |
| 7 | `gpb` | Verde → rosa → azul | 1,35 s | 3×: 4,06 s; 6×: 8,06 s |
| 8 | `rainbow2` | Arco-íris | 3,5 s | 3×: 10,36 s |

**Observações:**
- No padrão 6, uma execução isolada (2,95 s) dura mais que um terço de três (2,60 s cada). Há um custo fixo de cerca de 0,35 s por comando, provavelmente a primeira transição a partir do apagado [H].
- Os ids 0 e 9+ **não foram testados** [?]. Pelo risco visto no endereço `0x13` (índice fora de tabela), o `luxafor.py` os bloqueia.

---

## 11. Repetição infinita e interrupção

| Teste [M] | Resultado |
|---|---|
| Padrão 5 com `rep = 0`, observado por 8 s | nenhum evento de fim |
| Strobe com `rep = 0`, 8 s | nenhum evento de fim |
| Wave 5 com `rep = 0`, 8 s | nenhum evento de fim |

**Conclusão [M][H]:** `rep = 0` significa "repetir até chegar outro comando". Qualquer comando de cor (`01`) enviado em seguida substitui a animação. É assim que o `luxafor.py off` apaga um padrão em andamento.

---

## 12. O relógio interno do firmware

As medições caem em **duas bases de tempo** muito estáveis **[D]**:

| Base | Valor | Onde aparece |
|---|---|---|
| Degrau do fade | 0,252 ms (cerca de 3,97 kHz) | `02`: um degrau de brilho a cada `tempo` ticks |
| Passo de animação | 65 ms (cerca de 15,3 Hz) | `03` (piscada) e `04` (ciclo da wave) |

**Hipótese [H]:** 65 ms ≈ 256 × 0,252 ms (= 64,5 ms). O passo de animação seria o tempo de **uma rampa completa de 256 degraus** do mesmo relógio do fade. Uma piscada de strobe com `tempo` = 1 duraria o mesmo que um fade de 0 a 255 com `tempo` = 1.

Isso sugere que o firmware tem um único temporizador de cerca de 4 kHz e que as animações são construídas sobre ele, o que é comum em PICs pequenos. A confirmação viria da leitura do firmware via ICSP.

---

## 13. Comandos desconhecidos e varreduras

### 13.1 Varredura do primeiro byte, `00` a `0F` [M]

Cada código foi enviado com o mesmo argumento (`ff 10 00 00 05 00 01`):

| Código | Resposta | Interpretação |
|---|---|---|
| `00` | nada | (o kernel come o zero; ver 3.1) |
| `01` | `42` | cor fixa |
| `02` | `42` e `00 01` | fade (Δ pequeno: terminou rápido) |
| `03` | `42` e `00 01` | strobe |
| `04` | `42` | wave |
| `05` | nada | inexistente |
| `06` | `42` | padrão |
| `07`–`0F` | nada | inexistentes |

### 13.2 Varredura `00 xx` (xx de 00 a FF) [M]

Responderam só: `01`, `02`, `03`, `04`, `06` (comandos de LED), `51`, `52`, `62` e `80`. Pela seção 3.1, essa varredura equivale a enviar cada `xx` sozinho. **Não existe um conjunto escondido de "subcomandos de 00".**

### 13.3 Os comandos `51`, `52` e `62` [M][?]

| Envio | Resposta |
|---|---|
| `51 00` / `51 01` / `51 02` / `51 ff` | `51 00` / `51 01` / `51 02` / `51 ff`: ecoa o argumento |
| `52 00` / `52 01` / `52 02` / `52 ff` | ecoa o argumento |
| `62 00` | `62 00` |
| `62 01` / `62 02` / `62 ff` | `62 ff`: qualquer valor não zero vira `ff` |
| `80 00` / `80 01` / `80 02` | `80 3c`: o argumento é ignorado |
| `81` | nada |

**Hipóteses [H]:** `51` e `52` podem ser leitura/escrita de um registro de configuração; `62` parece um sinalizador booleano.

Depois do reinício do PC, os três responderam `00` ao valor 0. Não se sabe se eles gravam em memória permanente. Um dos suspeitos da troca do número de série (seção 14.2) são exatamente esses comandos. **Desde então, eles só devem ser testados com cuidado e um de cada vez.**

---

## 14. Incidentes

### 14.1 Travamento com o endereço `0x13`

**O que aconteceu:**
1. Uma varredura enviou azul a todos os endereços de LED de `00` a `FE`, um atrás do outro, com intervalo de 20 ms. A escrita parou com `TimeoutError`: o endpoint OUT do aparelho deixou de aceitar dados.
2. Um reset USB por software (`USBDEVFS_RESET`) trouxe o aparelho de volta (firmware `0x3c`).
3. Uma segunda varredura, com reset automático a cada travamento, identificou o culpado: **`CRASH b1=0x13`** [M].
4. No segundo reset, o firmware não respondeu e o processo ficou preso dentro do kernel (estado `D`), segurando o barramento USB 1. Nada novo era detectado: nem na porta original, nem numa porta nova, e o `lsusb` travava. **Só reiniciar o PC resolveu.**

**Interpretação [H]:** o firmware usa o byte do LED como índice de uma tabela sem checar o limite. O valor `0x13` escreve fora da tabela e corrompe algo vital, como a pilha ou o estado do USB.

**Regra adotada:** nunca usar reset USB por software neste aparelho; testar um valor por vez e pedir para reconectar fisicamente. O `luxafor.py` recusa endereços fora de {1, 2, 3, FF}.

### 14.2 Número de série zerado

Antes, `iSerial` era `000000002498`; depois do reinício, passou a `000000000000` em qualquer porta [M]. O valor fica gravado no aparelho: trocar de porta muda só o número do dispositivo no barramento (027 → 028 → 002), nunca o serial.

Os suspeitos são as escritas em `51`, `52` e `62` ou a corrupção causada pelo `0x13`, e não foi possível separar um do outro. O funcionamento dos LEDs não foi afetado [V].

---

## 15. Lâmina 05 explicada em detalhe

### 15.1 O que a lâmina mostra (e o que não mostra)

A lâmina 05 do caderno conceitual ("Em funcionamento") **é a especificação de comportamento do indicador próprio**, não uma gravação do Luxafor. Ela define:
- cinco estados;
- uma cor para cada um;
- uma **forma de onda de brilho no tempo** para cada um, desenhada em 4 segundos;
- uma ordem de prioridade.

Ela foi desenhada **a partir do que a engenharia reversa mostrou ser possível**: cor fixa, fade, strobe e pulso. Abaixo, cada estado vem com a equação exata usada no desenho ([`gerar_conceito.py`](conceito/gerar_conceito.py), função `wave`), a leitura de projeto e a forma de reproduzi-lo **hoje no Luxafor** e **amanhã no indicador próprio**.

### 15.2 A ideia de fundo: cor diz "o quê", ritmo diz "quão urgente"

| Princípio | Como aparece na lâmina |
|---|---|
| A **cor** identifica o assunto | verde = livre, azul = IA trabalhando, âmbar = IA quer você, magenta = IA falhou, vermelho = não interrompa |
| O **ritmo** codifica a urgência | luz parada = estado estável; respiração lenta = "em andamento, sem pressa"; piscar a 1 Hz = "precisa de você"; piscar rápido = "algo deu errado" |
| A **intensidade** distingue fundo e alerta | "livre" é fraco, para não incomodar; "em reunião" é forte, para ser visto de longe |

O ritmo segue uma regra simples: **quanto mais rápido, mais urgente**. Variação lenta (menos de 0,5 Hz) parece calma; 1 a 3 Hz chama a atenção sem assustar.

### 15.3 Estado a estado

#### LIVRE: verde, fixo e fraco

| Parâmetro | Valor |
|---|---|
| Cor nominal | `#2FD28A` = (47, 210, 138) |
| Curva | `brilho(t) = 0,28` (constante) |
| Frequência | 0 Hz (não varia) |
| Intenção | "pode falar comigo", sem chamar atenção |

- **Leitura:** 28% de nível linear **parece cerca de 56%** de brilho (seção 5.2). A lâmina usa 0,28 linear de propósito: visível, mas discreto.
- **No Luxafor hoje:** `01 FF 0D 3B 27`, que é (13, 59, 39), o verde nominal × 0,28. Para que *pareça* 28%, use o valor com gamma, `01 FF 03 0D 08` = (3, 13, 8).
- **No indicador próprio:** o firmware aplica a tabela gamma e o limite de corrente.

#### PROCESSANDO: azul, respirando a cada 2,4 s

| Parâmetro | Valor |
|---|---|
| Cor nominal | `#3D8BFF` = (61, 139, 255) |
| Curva | `brilho(t) = 0,15 + 0,85 × [ (1 − cos(2πt / 2,4)) / 2 ]^1,6` |
| Período / frequência | 2,4 s / 0,42 Hz |
| Mínimo / máximo | 15% / 100% (linear) |
| Intenção | "estou trabalhando, não precisa olhar" |

**Leitura da equação:**
- `(1 − cos)/2` é uma onda que vai suavemente de 0 a 1 e volta, sem quinas. Essa é a diferença entre "respirar" e "piscar".
- O **expoente 1,6** deixa a curva mais tempo embaixo e faz o pico mais estreito. Parece uma inspiração rápida seguida de uma expiração longa, e compensa parte da não linearidade do olho (seção 7.3).
- O **piso de 15%** (cerca de 42% percebido) impede que o LED apague por completo. Assim, "processando" nunca se confunde com "desligado".
- **0,42 Hz** fica perto do ritmo de uma respiração humana calma (12 a 20 por minuto, ou 0,2 a 0,33 Hz). Lê-se como "vivo, mas tranquilo".

**No Luxafor hoje, há duas opções:**
1. **Nativa:** `04 05 3D 8B FF 00 00 25`, wave 5 com `vel` = 37 (37 × 65 ms ≈ 2,4 s) e `rep` = 0 (infinito). É a solução mais simples, mas a curva interna do pulso é a do firmware [?], e não se sabe se ela tem piso.
2. **Fiel à lâmina:** o computador alterna dois fades. Sobe com `02 FF 3D 8B FF 13` (tempo 19 → 255 × 19 × 0,252 ms ≈ 1,22 s) e desce até 15% com `02 FF 09 15 26 13` (Δ = 217 → cerca de 1,04 s), esperando o `00 01` entre um e outro. O formato fica triangular, não cossenoidal. Para chegar à curva exata, use segmentos (seção 7.4).

**No indicador próprio:** a curva é calculada no firmware a 100 Hz, já com gamma, sem tráfego USB.

#### ATENÇÃO: âmbar, piscando a 1 Hz

| Parâmetro | Valor |
|---|---|
| Cor nominal | `#FFB21E` = (255, 178, 30) |
| Curva | `brilho(t) = 1,0 se (t mod 1,0) < 0,5; senão 0,06` |
| Período / frequência / fração acesa | 1,0 s / 1 Hz / 50% |
| Intenção | "a IA parou esperando você" (permissão, pergunta) |

- **Leitura:** uma onda quadrada. Liga e desliga sem rampa, porque o objetivo é *ser notada*.
- O "apagado" fica em 6%, não em zero, para que o aparelho continue visível como aceso entre as piscadas.
- 1 Hz é rápido o bastante para chamar a atenção na visão periférica e lento o bastante para não irritar.
- **No Luxafor hoje:** `03 FF FF B2 1E 0F 00 00`, strobe com `tempo` = 15 (15 × 65,5 ms ≈ 0,98 s por piscada) e `rep` = 0. O strobe do Luxafor volta à cor anterior entre as piscadas, então o "fundo" é a cor que estava antes. Para ter o fundo de 6% âmbar, mande antes `01 FF 0F 0B 02`.
- **No indicador próprio:** onda quadrada exata no firmware.

#### ERRO: magenta, strobe rápido

| Parâmetro | Valor |
|---|---|
| Cor nominal | `#FF3FC8` = (255, 63, 200) |
| Curva | `brilho(t) = 1,0 se (t mod 0,25) < 0,08; senão 0,04` |
| Período / frequência / fração acesa | 0,25 s / 4 Hz / 32% |
| Intenção | "algo falhou e precisa de ação" |

- **Leitura:** flashes curtos (80 ms) e frequentes. É o sinal mais agressivo do conjunto e o único com fração acesa menor que 50%. Lê-se como "alarme".
- **Magenta** foi escolhido porque não se confunde com o vermelho de "em reunião". Erro de IA é assunto do usuário; reunião é aviso para os outros.
- **Ponto de atenção:** 4 flashes por segundo **ultrapassa o limite de 3 flashes por segundo** que as diretrizes de acessibilidade (WCAG 2.3.1) recomendam para evitar risco a pessoas com fotossensibilidade. A área luminosa é pequena, o que reduz o risco, mas o estado vai ficar num ambiente de trabalho com outras pessoas. **Recomendação: baixar para 2,5 Hz** (período 0,4 s, flash de 130 ms) na especificação de firmware.
- **No Luxafor hoje:** `03 FF FF 3F C8 04 00 00`, `tempo` = 4 → 262 ms por piscada, cerca de 3,8 Hz. Na versão recomendada de 2,5 Hz, `tempo` = 6 dá cerca de 2,5 Hz. A fração acesa do strobe do Luxafor não é ajustável; presume-se 50% [H].
- **No indicador próprio:** flashes de 130 ms a 2,5 Hz, com fração acesa configurável.

#### EM REUNIÃO: vermelho, fixo e forte

| Parâmetro | Valor |
|---|---|
| Cor nominal | `#FF3B2F` = (255, 59, 47) |
| Curva | `brilho(t) = 1,0` (constante) |
| Frequência | 0 Hz |
| Intenção | sinal **para os outros**: "não interrompa" |

- **Leitura:** é o único estado pensado para quem está em volta. Fica fixo, porque um aviso para terceiros não deve piscar e chamar o olhar de todos na sala, e no máximo, para ser visto de longe.
- O vermelho levemente alaranjado (um pouco de G e B) fica mais "quente" e legível no difusor que o vermelho puro.
- **No Luxafor hoje:** `01 FF FF 3B 2F`.

### 15.4 A escada de prioridade

```
EM REUNIÃO  >  ERRO  >  ATENÇÃO  >  PROCESSANDO  >  LIVRE
```

Quando vários estados são verdadeiros ao mesmo tempo, aparece o mais alto. Exemplo: a IA deu erro durante uma chamada, e o aparelho fica vermelho. A decisão do usuário foi que **reunião manda em tudo**.

Na especificação, a "atenção" da IA durante uma reunião pode aparecer como uma piscada curta no LED de baixo, sem tirar o vermelho dos outros dois. Isso é opcional e configurável.

A prioridade é aplicada **no computador**: o daemon junta os sinais e envia um único comando por mudança de estado. Como qualquer comando novo interrompe a animação anterior (seção 11), a troca é instantânea.

### 15.5 Resumo dos estados

| Estado | Cor | Forma | Frequência | Fração acesa | Mín–máx (linear) | Luxafor hoje |
|---|---|---|---|---|---|---|
| Livre | `#2FD28A` | constante | 0 | — | 28% | `01 FF 0D 3B 27` |
| Processando | `#3D8BFF` | cosseno^1,6 | 0,42 Hz | — | 15–100% | `04 05 3D 8B FF 00 00 25` |
| Atenção | `#FFB21E` | quadrada | 1 Hz | 50% | 6–100% | `03 FF FF B2 1E 0F 00 00` |
| Erro | `#FF3FC8` | flash curto | 4 Hz (recom. 2,5 Hz) | 32% | 4–100% | `03 FF FF 3F C8 04 00 00` |
| Em reunião | `#FF3B2F` | constante | 0 | — | 100% | `01 FF FF 3B 2F` |

Todos os bytes acima vêm no formato do protocolo. No Linux, prefixe um `00` ao escrever no `hidraw`, ou use o `luxafor.py raw`.

---

## 16. Cronologia completa dos testes

Na ordem em que foram feitos em 2026-11-08. "RX" é a resposta do aparelho.

### Fase 1: reconhecimento (sem risco)

| # | O que foi feito | Resultado |
|---|---|---|
| 1 | `lsusb -v` no aparelho | descritores da seção 2.1 [M] |
| 2 | Listagem de `hidraw` e `/sys/class/leds` | driver `hid-led` com 18 LEDs virtuais; permissão de leitura e escrita para o usuário [M] |
| 3 | Leitura do descritor HID (33 bytes) | vendor `FF00`, 8 + 8 bytes, sem Report ID [M] |
| 4 | Primeiros comandos: `01 FF FF 00 00`, `01 41 …`, `01 42 …`, `01 01 FF FF FF`, `00 52`, `00 47` | ACK `42` nos de LED; `52` ecoou; `47` em silêncio [M] |

### Fase 2: varreduras de comandos

| # | O que foi feito | Resultado |
|---|---|---|
| 5 | Primeiro byte de `00` a `0F` com o mesmo argumento | responderam `01`–`04` e `06`; `02`/`03` com evento de fim [M] |
| 6 | `00 xx` para xx de 00 a FF | responderam `01`–`04`, `06`, `51`, `52`, `62`, `80` [M] |
| 7 | `80`, `80 01`, `80 02`, `81`, `51 …`, `52 …`, `62 …` | tabela da seção 13.3 [M] |

### Fase 3: ferramenta e primeiro mapa

| # | O que foi feito | Resultado |
|---|---|---|
| 8 | `luxafor.py version`, `color all red`, `fade front`, `off` | firmware `0x3c`; ACKs; evento de fim no fade [M] |
| 9 | Usuário rodou `color all red` | "vermelho em tudo" [V] |
| 10 | Usuário rodou `raw 80` | `80 3c` [M] |
| 11 | Usuário rodou `color front green` (2×) | continuou tudo vermelho [V] |
| 12 | LEDs 1–6 com 6 cores diferentes | só 3 LEDs: topo azul, meio verde, baixo vermelho [V] |

### Fase 4: mapa completo com validação visual

| # | O que foi feito | Resultado |
|---|---|---|
| 13 | Só o LED 4, amarelo | tudo apagado [V] |
| 14 | Só o LED 5, magenta | tudo apagado [V] |
| 15 | Só o LED 6, branco | tudo apagado [V] |
| 16 | LEDs 4, 5 e 6 em vermelho puro | tudo apagado [V] |
| 17–23 | 7 rodadas girando 8 cores pelos LEDs 1–3 (baixo/meio/topo): verde/azul/amarelo → azul/amarelo/ciano → amarelo/ciano/magenta → ciano/magenta/branco → magenta/branco/laranja → branco/laranja/vermelho → laranja/vermelho/verde | "tudo confere" nas 7 [V] |
| 24 | Endereço `0x42` em verde | tudo apagado [V] |
| 25 | Endereço `0x41` em verde | tudo apagado [V] |

### Fase 5: varredura de endereços e incidente

| # | O que foi feito | Resultado |
|---|---|---|
| 26 | Azul em todos os endereços `00`–`FE`, exceto 1–3 | firmware travou (`TimeoutError`) [M] |
| 27 | Reset USB por software | voltou com firmware `0x3c` [M] |
| 28 | Varredura com detecção de travamento | `CRASH b1=0x13` [M] |
| 29 | Segundo reset automático | processo preso no kernel; USB do barramento 1 travado [M] |
| 30 | Reconexão na mesma porta e em outra | não reapareceu [M] |
| 31 | Reinício do PC | voltou; serial agora `000000000000`; `51`/`52`/`62` respondem `00` [M] |

### Fase 6: brilho

| # | O que foi feito | Resultado |
|---|---|---|
| 32 | Vermelho 255 / 64 / 16 (baixo/meio/topo) | "meio ≈ baixo" [V] |
| 33 | Vermelho 255 / 4 / 1 | diferença visível dependendo do ângulo; de lado, pouca [V] |
| 34 | Os 3 LEDs alternando entre 1 e 255 a cada 0,8 s, por 10 s | "pulsou bem visível" [V] |

### Fase 7: tempos de animação

| # | O que foi feito | Resultado |
|---|---|---|
| 35 | Fade com `tempo` 1–100, alternando cores | inválido: cor-alvo igual à atual [M] |
| 36 | Fade do preto ao vermelho, `tempo` 1–200, mais 0 → 128 | tabela da seção 7.2 [M] |
| 37 | Strobe com 7 combinações de `tempo`/`rep` | tabela da seção 8.2 [M] |
| 38 | Strobe verde, `tempo` 20, `rep` 3 | usuário não estava preparado; terminou apagado [V] |
| 39 | Repetição com aviso | 3 piscadas [V] |
| 40 | Base azul + strobe vermelho com `rep` 2 | voltou ao azul [V] |

### Fase 8: waves

| # | O que foi feito | Resultado |
|---|---|---|
| 41 | Wave 1, ciano, `rep` 3, `vel` 30 | menos de 5 s, terminou apagado; pediu para repetir [V] |
| 42 | Wave 1, `rep` 5, `vel` 60 | baixo → cima; mais lenta [V] |
| 43 | Wave 2 | sem ordem; vários LEDs juntos [V] |
| 44 | Wave 3 | baixo → cima [V] |
| 45 | Wave 4 | os 3 parados em azul-claro, depois apagaram [V] |
| 46 | Wave 5 | os 3 pulsaram 5 vezes; evento aos 19,48 s [V][M] |

### Fase 9: padrões

| # | O que foi feito | Resultado |
|---|---|---|
| 47–48 | Padrão 1 (1× e 3×) | semáforo; 2,10 s e 6,21 s [V][M] |
| 49 | Padrão 2 (3×) | sobe, fica branco, troca de cor; sem evento [V][M] |
| 50–51 | Padrão 3 (3× e 1×) | arco-íris; 35,10 s e 11,47 s [V][M] |
| 52–53 | Padrão 4 (1×, duas vezes) | 3 tons fortes que clareiam; 15,82 s [V][M] |
| 54 | Padrão 5 | flash de polícia vermelho/azul; 0,90 s [V][M] |
| 55–56 | Padrão 6 (1× e 3×) | arco-íris terminando em azul; 2,95 s e 7,81 s [V][M] |
| 57–58 | Padrão 7 (3× e 6×) | verde → rosa → azul; 4,06 s e 8,06 s [V][M] |
| 59 | Padrão 8 (3×) | arco-íris; 10,36 s [V][M] |

### Fase 10: fechamento

| # | O que foi feito | Resultado |
|---|---|---|
| 60 | `rep = 0` em padrão 5, strobe e wave 5, observados por 8 s | nenhum evento de fim: repete até novo comando [M] |
| 61 | Teste de fumaça da CLI final, com travas de segurança | LED 4 e padrão 9 recusados; `--wait` corrigido; firmware segue `0x3c` [M] |

---

## 17. O que ainda não sabemos e como descobrir

| Pergunta | Como descobrir | Risco |
|---|---|---|
| Frequência do PWM | Câmera de celular em câmera lenta (240 fps) filmando o LED em brilho 32: o número de faixas por quadro dá a frequência. Melhor ainda: fotodiodo ou LED usado como sensor na entrada de microfone e um analisador de espectro (Audacity) | nenhum |
| Fração acesa do strobe | Mesmo fotodiodo, medindo o tempo ligado e desligado | nenhum |
| Curva do pulso da wave 5 | Mesmo fotodiodo, gravando um ciclo com `vel` alto | nenhum |
| Comprimento de onda dos chips | Espectrômetro (há modelos de celular com rede de difração) | nenhum |
| O que fazem `51`, `52` e `62` | Um valor por vez, lendo o serial e a versão antes e depois e reconectando fisicamente entre os testes | **médio**: podem gravar em memória permanente |
| Endereços `14`–`FE` e padrões 0/9+ | Um por vez, com reconexão física se travar, **nunca** reset por software | **médio**: podem travar o firmware |
| Qual PIC e se há proteção de leitura | Abrir o case, ler a marcação do chip, procurar os pads de ICSP | baixo (mecânico) |
| A hipótese do relógio único (seção 12) | Ler o firmware via ICSP, se não estiver protegido | baixo |
