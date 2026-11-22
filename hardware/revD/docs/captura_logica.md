# Guia de captura — timing dos LEDs (Luxafor original)

**Status (22 nov. 2026):** a decodificação de `0x05`/`0x07` está **encerrada**. Varredura sistemática do relatório Claude (1º byte com args `ff 10 00 00 05 00 01`, e payload zerado) e o `PROTOCOLO.md` (que nem lista esses opcodes) apontam **silêncio**: são inexistentes. A afirmação nossa de “ACK `42` com zeros” estava errada e foi retirada. O script `teste_hid_05_07.py` é desnecessário.

Esta captura fica **opcional**. Serve só para confirmar o protocolo elétrico (~800 kHz), a ordem dos canais, a frequência do PWM, o duty do strobe e a curva do wave. As fórmulas de tempo do firmware original (`0,252 ms × tempo` no fade, `65,5 ms × tempo` no strobe, `~65 ms × vel` no wave 5) já estão em [`firmware_comportamento.md`](firmware_comportamento.md) e bastam para um clone compatível.

Há duas alternativas **sem custo** (relatório Claude, §17), descritas no fim deste guia, antes de comprar analisador.

## Equipamento recomendado

- Analisador lógico barato de **8 canais, 24 MHz** (clone Saleae com chip FX2 / “24M 8CH”), USB.
- Software: **sigrok / PulseView** (livre). O PulseView traz o decodificador **WS2812** (protocolo timing-compatible com SK6812 / WS281x de 800 kHz).
- No Debian/Ubuntu: `sudo apt install sigrok pulseview`.
- Pontas com GND comum; se possível, um clip em pinos de 0,5–1,27 mm ou um fio soldado temporário.

Um Saleae Logic 8 oficial (12/24 MHz+) também serve; o fluxo no PulseView é o mesmo.

## Onde pontar (Flag original)

Abrir o case com cuidado (o difusor costuma estar colado). A placa tem 3 LEDs endereçáveis só na face de cima, em cadeia, comandados pelo `PIC16F1454`.

| Sinal | Onde | Notas |
|---|---|---|
| **DIN (preferido)** | Pino de dados do **primeiro** LED da cadeia (o de baixo, LED 1), ou a trilha que sai do PIC até esse pino | Nível do MCU (5 V no PIC). É o mesmo fluxo que vai para os 3 LEDs. |
| **GND** | Qualquer GND da placa (pad do USB-C, plano, pino GND do TC2030) | Obrigatório; sem GND comum a captura fica ilegível. |
| Alternativa | Pino de dados de D2 ou D3 | Só mostra o que sobra depois do LED anterior (útil para confirmar a ordem da cadeia). |

Não pontar VBUS direto no analisador. A massa do analisador deve ser a do Flag, não a de outra fonte flutuante.

Na **placa clone rev C** (quando existir): o ponto mais cômodo é o lado 5 V depois do conversor — `U3` pino 4, `R3`, ou `D1` pino 2 (`DI`). O pino 13 do STM32 (`PA7`, `LED_DIN_3V3`) é o mesmo sinal em 3,3 V, antes do 74AHCT1G125.

## Ajustes de captura

- **Taxa:** no mínimo **12 MHz**; **24 MHz é o alvo**. Um bit WS281x dura ~1,25 µs; a 12 MHz há ~15 amostras/bit, o suficiente para o decodificador. A 1–4 MHz a captura costuma falhar.
- **Limiar:** ~1,6–2,0 V se o sinal for 5 V; ~1,0–1,4 V se for 3,3 V.
- **Gatilho:** borda de **subida** no canal de DIN, depois de mandar o comando HID. Capture 20–100 ms (um quadro de 3 LEDs × 24 bits em 800 kHz cabe em < 0,1 ms; deixe folga para o firmware começar a transmitir).
- **Canais:** 1 canal basta (DIN + GND). Um segundo canal no USB D+ é opcional e não ajuda a decodificar o LED.

## Como decodificar no PulseView

1. Capturar, como acima.
2. *Decoders → Add → WS2812* (às vezes listado como “RGB LED (WS281x)”).
3. Atribuir o canal de DIN. Reset típico: pulso baixo ≥ 50 µs no fim do quadro.
4. Conferir:
   - taxa aparente (~800 kHz, não 400 kHz);
   - ordem dos canais (**GRB** é o usual em WS2812/SK6812; RGB em alguns SK6805);
   - 8 vs 16 bits por canal (o original provavelmente é 8 bits; o clone rev C usa WS2816B de 16 bits);
   - 3 “pixels” por comando de cor sólida.

## Comando sigrok-cli (exemplo)

Substitua `fx2lafw` / o canal e o arquivo se o aparelho aparecer com outro driver (`sigrok-cli -D`).

```bash
# listar aparelhos
sigrok-cli --scan

# capturar 50 ms a 24 MHz, gatilho na subida de D0, já com o decodificador WS2812
# (mande o comando HID um instante antes, ou use um atraso no host)
sigrok-cli -d fx2lafw -c samplerate=24M \
  -C D0 --samples 1.2M \
  --triggers D0=r \
  -P ws2812:dat=D0 \
  -A ws2812 \
  -o /tmp/luxafor-led.sr

# só o texto decodificado, sem gravar a sessão
sigrok-cli -d fx2lafw -c samplerate=24M -C D0 --samples 1.2M --triggers D0=r -P ws2812:dat=D0 -A ws2812
```

Protocolo de teste sugerido com analisador (um comando por captura, LEDs visíveis). **Não mandar `0x05`/`0x07`**: já foram tratados como inexistentes; o script `teste_hid_05_07.py` não precisa rodar.

1. `01 FF FF 00 00` — todos vermelhos (baseline; deve aparecer um quadro de 3 pixels).
2. `01 01 00 FF 00` — só o LED 1 verde (confirma posição e ordem dos canais).
3. `01 02 00 00 FF` — só o LED 2 azul.
4. `02 FF 00 FF 00 14` — fade verde, `tempo` 20 (medir intervalo entre quadros no DIN / duração aparente).
5. `03 FF FF 00 00 01 00 04` — strobe vermelho, `tempo` 1, `rep` 4 (duty e período).
6. `04 05 FF 00 00 00 01 01` — wave tipo 5, um ciclo (curva e ~65 ms × vel).

A ordem GRB/RGB, a largura de bit e o PWM só saem desta captura (ou das alternativas abaixo). O original é 8 bit linear; o clone rev C usa WS2816B de 16 bit.

## Alternativas sem custo (sem analisador)

### Câmera lenta do celular

A maioria dos celulares grava em **120 ou 240 fps**. Fixar o aparelho, apagar a luz ambiente, mandar o comando HID e filmar o Flag de perto (preencher o quadro com os LEDs).

- **Strobe / atenção / erro:** contar os frames entre dois acendimentos (ou entre aceso e apagado) e converter: período = frames / fps. Em 240 fps, um ciclo de 65,5 ms são ~16 frames; 2,5 Hz são 96 frames.
- **Fade:** filmar um fade 0→255 com `tempo` conhecido (10, 20, 100) e marcar o frame em que a luz “começa” e o em que estabiliza. Confere a fórmula 0,252 ms × `tempo` × |Δ|.
- **Wave:** um ciclo do tipo 5 deve caber em ~65 ms × `vel`.

Vantagem: não abre o case. Limite: não vê o PWM de kHz nem a ordem GRB no fio.

### Fotodiodo no microfone

Um fotodiodo (ou fototransistor, ou até a célula de um calculadora solar) aponta para o LED, polarizado se preciso, e o sinal entra na entrada de microfone do PC ou do celular (capacitor de acoplamento, nível de linha — não mandar 5 V direto no jack).

Gravar no Audacity (ou no gravador do celular) com taxa de 44,1 ou 48 kHz e medir o período no envelope:

- strobe e padrões “flash” saem com precisão de ~1 ms;
- a respiração (2,4 s) e o fade longo também;
- PWM de alguns kHz às vezes aparece como tom no espectro (útil para comparar com os 10 kHz do WS2816B no clone; no original, 8 bit linear, a frequência exata é o que se quer medir).

Não substitui o analisador para decodificar a cadeia 800 kHz, mas fecha duty, período e curva sem comprar nada.
