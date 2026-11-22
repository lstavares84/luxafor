# Especificação de comportamento — firmware LUXCLONE rev C

Objetivo: o firmware da placa rev C (STM32C071 + 3× **WS2816B-2020**, 16 bit, PWM 10 kHz) deve ser **compatível com o protocolo HID do Luxafor Flag** (firmware original `0x3c`) e, por cima disso, renderizar nativamente os cinco estados de presença. Documento de 22 nov. 2026. Fontes no final.

O relatório detalhado do Claude (anexo do Lucas) não pôde ser aberto por este agente (arquivo privado). Os fatos da varredura de opcodes, as fórmulas de tempo, a nota WCAG e os métodos da §17 entram pelo resumo que o agente pai extraiu desse relatório. Cores, curvas e a escada de prioridade dos cinco estados vêm da cópia no workspace (`luxrepo/docs/conceito/gerar_conceito.py`), que usa os mesmos nomes (livre / processando / atenção / erro / em reunião).

## 1. O que foi reconciliado (ler antes de implementar)

### 1.1 `0x05` e `0x07` são opcodes inexistentes

Há uma contradição nas nossas notas, e a evidência sistemática vence.

| Fonte | O que afirma |
|---|---|
| Relatório Claude (varredura do 1º byte com args `ff 10 00 00 05 00 01`) | `0x05` e `0x07`–`0x0F` **não respondem** (inexistentes) |
| Relatório Claude (varredura “00xx”, payload zerado) | Só respondem `01`, `02`, `03`, `04`, `06`, `51`, `52`, `62`, `80` |
| `luxrepo/PROTOCOLO.md` (21 nov. 2026) | **Não lista** `0x05` nem `0x07`. Outros opcodes: silêncio. `00` responde `42` (único ponto em que a lista “00xx” do relatório e o PROTOCOLO divergem) |
| Page / `pendencias.md` / `captura_logica.md` (rascunho anterior) | Diziam ACK `42` com payload zerado para `0x05`/`0x07` — **isso não está no PROTOCOLO.md** e **contradiz** a varredura |

**Decisão:** tratar `0x05` e `0x07` como **inexistentes** (silêncio, como qualquer opcode não mapeado). O ACK `42` com zeros foi um erro nosso, provavelmente confusão com o `0x00`. O script `teste_hid_05_07.py` ficou desnecessário. A captura lógica **não é mais necessária para decodificar esses opcodes**; permanece **opcional** só para medir PWM, duty do strobe e a curva do wave.

### 1.2 `0x80` é comando de versão, não de leitura de serial

- Relatório Claude e `PROTOCOLO.md`: `0x80` devolve **`80 3c`** — versão do firmware `0x3c` (igual ao `bcdDevice 3c.00`).
- Nossa afirmação posterior de que “`0x80` lê o serial” é **imprecisa**. O `0x62` é a leitura do serial atual. O que observamos nos testes de NVM é que os **bytes seguintes** do relatório de 8 bytes do `0x80` parecem carregar a **cópia do serial do boot** (uma gravação só aparece aí e no descritor USB depois de reconectar). Isso é compatível com “`0x80` devolve a versão `0x3c`”, não substitui o `0x62`.

**Implementar:** resposta `80 <versão> [cópia de boot do serial, 4 bytes, como no original] …`. Versão do clone: `0x3c` se quiser imitar o Flag; ou um valor próprio, documentado. Não chamar o `0x80` de “comando de leitura de serial”.

O restante do relatório (hipóteses sobre `51`/`52`/`62`) **fica superado** pelos testes desta conversa: `0x51` grava 6 bytes em NVM, `0x52` grava 4, `0x62` lê o valor atual.

## 2. Envelope USB HID (compatível)

- VID:PID: no clone, **não usar** `04d8:f372` em produto vendido (ver Page, questão de VID/PID). Protótipo pessoal pode temporariamente.
- 1 interface HID, página vendor `0xFF00`, 8 bytes IN + 8 bytes OUT, sem Report ID.
- EP `0x81` / `0x01` interrupt, intervalo 1 ms, Full Speed, MaxPower 100 mA.
- Linux hidraw: o host prefixa `00` (Report ID 0). O firmware vê os 8 bytes crus, opcode no byte 0.

## 3. Opcodes

| Op | Função | Payload (8 bytes) | Resposta | Fim (`00 01`) |
|---|---|---|---|---|
| `00` | ACK solto | `00 …` | `42` (conforme PROTOCOLO; o relatório Claude não o listou na varredura 00xx) | — |
| `01` | Cor fixa | `01 alvo R G B …` | `42` | — |
| `02` | Fade / smooth | `02 alvo R G B tempo …` | `42` | sim, no fim (imediato se a cor-alvo = atual) |
| `03` | Strobe | `03 alvo R G B tempo 00 rep` | `42` | sim, no fim (não enviar se `rep = 0` e a animação segue) |
| `04` | Wave | `04 tipo R G B 00 rep vel` | `42` | **só tipo 5** |
| `06` | Padrão 1–8 | `06 id rep …` | `42` | sim, exceto o padrão 2 |
| `51` | Gravar serial (6 bytes) | `51 b1 b2 b3 b4 b5 b6` | eco dos args (como o original) | — |
| `52` | Gravar serial (4 primeiros) | `52 b1 b2 b3 b4 …` | eco | — |
| `62` | Ler serial atual | `62 …` | `62 b1 b2 b3 b4 …` (os 4 primeiros, como medido) | — |
| `80` | Versão (+ cópia de boot do serial) | `80 …` | `80 3c` (ou versão do clone) + 4 bytes do serial carregados no boot | — |
| `05`, `07`–`0F`, demais | Inexistentes | qualquer | **silêncio** | — |

Qualquer comando novo de LED (e, na prática, qualquer opcode válido) **interrompe** a animação em curso. `rep = 0` em strobe, wave e padrão = repetir até outro comando; sem evento de fim.

## 4. Endereços de LED (`alvo`)

Conjunto seguro, e **somente** este: `{0x01, 0x02, 0x03, 0xFF}`.

| Valor | Significado |
|---|---|
| `01` | LED 1, baixo |
| `02` | LED 2, meio |
| `03` | LED 3, topo |
| `FF` | todos |

- `04`–`06`, `0x41`, `0x42` no original dão ACK e não acendem (herança do Flag de 6 LEDs). No clone: **ACK `42` e não acender**, ou rejeitar com silêncio — preferir ACK vazio para não quebrar software antigo, mas **nunca** indexar um buffer com o valor cru.
- **`0x13` (e vizinhos como `0x15`) travam o Flag original.** O clone **deve rejeitar com segurança** todo `alvo` fora de `{1,2,3,0xFF}` e dos ACK-vazios acima: não indexar array, não escrever fora da cadeia. Resposta sugerida: silêncio, ou ACK `42` sem efeito. Jamais crashar.

## 5. Temporização (firmware original `0x3c`) — o clone deve reproduzir

PWM do original: **8 bit linear** por canal (até o valor 1 acende, fraco). Fórmulas abaixo são as do relatório Claude, cruzadas com as medições do `PROTOCOLO.md`.

| Fenômeno | Fórmula / valor | Notas |
|---|---|---|
| Passo de fade | **0,252 ms × `tempo` por degrau de brilho** | Duração total ≈ \|\Δbrilho\| × `tempo` × 0,252 ms, com \|\Δbrilho\| = max(\|\ΔR\|, \|\ΔG\|, \|\ΔB\|). Medições 0→255: `tempo` 10 → 0,64 s; 20 → 1,29 s; 100 → 6,4 s; 200 → 12,8 s (casam com 0,252 ms). A medida antiga `tempo` 1 → 0,12 s é o dobro da fórmula (~0,064 s) e fica como outlier. |
| Strobe (uma piscada) | **65,5 ms × `tempo`** | Duração total ≈ `rep` × `tempo` × 65,5 ms. No fim, **restaurar a cor anterior**. (`PROTOCOLO.md` arredondava 65 ms.) |
| Wave tipo 5 (um ciclo) | **~65 ms × `vel`** | `vel` maior = mais lento. Só o tipo 5 envia `00 01`. |
| `rep = 0` | infinito | strobe, wave e padrão; interrompido por qualquer comando novo. |
| Padrão 1 | 2,1 s / rep | semáforo: vermelho → vermelho+amarelo → verde |
| Padrão 2 | (sem evento de fim) | sobe um a um, fica branco, troca de cor e repete |
| Padrão 3 | 11,5 s / rep | arco-íris |
| Padrão 4 | 15,8 s / rep | 3 cores, forte e depois clareando |
| Padrão 5 | 0,9 s / rep | polícia: flash vermelho e azul |
| Padrão 6 | 2,6 s / rep | arco-íris terminando em azul |
| Padrão 7 | 1,35 s / rep | verde → rosa → azul |
| Padrão 8 | 3,5 s / rep | arco-íris |
| Padrões 0 e 9+ | não implementar / rejeitar | no original não foram testados (risco de índice) |

No motor do clone: tick de 1 ms; interpolar os três canais juntos para chegarem ao mesmo tempo. Os bytes R,G,B do protocolo continuam 8 bit (0–255), para o software existente.

## 6. Do protocolo 8 bit para o WS2816B de 16 bit

O relatório Claude fala em SK6805 (8 bit). A **rev C usa WS2816B-2020** (16 bit/canal, PWM 10 kHz, gama interna). Não voltar atrás.

1. Aceitar R,G,B de 8 bit no HID (compatibilidade).
2. Expandir para 16 bit com **curva gamma** (γ ≈ 2,2, LUT) antes de enviar à cadeia. Assim o fade de 8 bit no fio fica perceptualmente suave, e o PWM de 10 kHz elimina cintilação no verde/âmbar — que era o limite do SK6805 a ~1 kHz.
3. Ordem dos canais no fio: seguir o datasheet do WS2816B (conferir G/R/B vs o original no primeiro protótipo; captura opcional, §8).
4. Corrente: ~20 mA/LED no branco máximo (datasheet); orçamento < 100 mA no descritor.

## 7. Sistema de estados (Modo SALA + Modo IA · SIGNA rev C)

O dispositivo opera em dois modos combináveis (**cor diz o quê; ritmo diz urgência**), endereçando os 3 LEDs em conjunto (`0xFF`) ou separados por zona (`0x03+0x02` = sala; `0x01` = IA). Fonte única de dados do conceito: `docs/caderno-signa/dados/produto.json` (e a cópia em `software/data/produto.json`).

### 7.1 Escada de prioridade global

**SALA: OCUPADO > SALA: PRESTES A ENTRAR > IA: ERRO > IA: PRECISA DE ATENÇÃO > IA: PROCESSANDO > IA: LIMITE ATINGIDO > SALA: LIVRE > IA: DESOCUPADA**

Quando `SALA = OCUPADO`, a sala **sempre vence** e trava os 3 LEDs (`0xFF`) em vermelho `#FF3B2F`. No v1 o `LED 1` da IA **some** (não é configurável).

### 7.2 Tabela de estados

| Modo | Estado | Cor | Curva no tempo | LEDs | Notas / fonte |
|---|---|---|---|---|---|
| SALA | LIVRE | `#2FD28A` | contínuo baixo (`0,28`) | `0xFF` (ou `0x02+0x03` misto) | pode interromper |
| SALA | PRESTES A ENTRAR | `#FF8A1A` | pulso lento `3,0 s` (`0,20 + 0,80·((1−cos)/2)^1,4`) | `0xFF` (ou `0x02+0x03` misto) | Google/Outlook Agenda (padrão 5 min antes do evento, configurável no app) |
| SALA | OCUPADO | `#FF3B2F` | contínuo forte (`1,0`) | `0xFF` (trava os 3 LEDs; LED 1 da IA some no v1) | reunião (agenda/mic/câm.) ou foco manual; não configurável no v1 |
| IA | IA DESOCUPADA | `#7C8EA6` | contínuo mínimo (`0,08`) | `0xFF` (só IA) ou `0x01` (misto) | Claude, ChatGPT e Grok ociosos (ou LED 1 apagado no misto) |
| IA | PROCESSANDO | `#3D8BFF` | respiração `2,4 s` (`0,15 + 0,85·((1−cos(2πt/2,4))/2)^1,6`) | `0xFF` (só IA) ou `0x01` (misto) | geração / ferramenta em curso |
| IA | PRECISA DE ATENÇÃO | `#FFE02E` | onda quadrada `1 Hz`, duty `50 %`, piso `0,06` | `0xFF` (só IA) ou `0x01` (misto) | aguarda resposta ou aprovação humana |
| IA | ERRO | `#FF3FC8` | strobe `2,5 Hz` (período `0,4 s`, pulso `130 ms`, piso `0,04`) | `0xFF` (só IA) ou `0x01` (misto) | **WCAG 2.3.1:** `2,5 Hz < 3 Hz` (não usar `4 Hz`) |
| IA | LIMITE ATINGIDO | `#9B5CFF` | **5 h:** pulso duplo a cada `3,0 s` (`0,25 s` on, `0,25 s` gap, `0,25 s` on a `0,55`, piso `0,06`) · **semanal:** contínuo baixo (`0,28`) | `0xFF` (só IA) ou `0x01` (misto) | diferencia janela de 5 h vs teto semanal pelo ritmo mesmo num único LED |

### 7.3 Fontes no daemon do PC (a validar na engenharia)

- **Agenda:** Google Calendar API (OAuth) e Microsoft Graph / Outlook (OAuth), mais atalho manual e sensor de chamada.
- **CLI de IA (oficiais):** hooks do Claude Code e `notify` do Codex CLI.
- **Web/desktop sem API oficial:** extensão de navegador para ChatGPT, Claude e Grok (*proposta*); leitura de limites 5 h/semanal (*a validar*).
- O daemon resolve a escada e envia **um** comando HID por transição (`0x01` contínuo, `0x03` estrobo/quadrada, ou tabela interna no firmware para curvas suaves/duplo-pulso sem depender de streaming do host).

## 8. Captura opcional (não bloqueia o firmware)

Para PWM, duty do strobe e curva do wave, se ainda quiser medir o Flag original: ver `captura_logica.md` (analisador, **câmera lenta do celular**, **fotodiodo no microfone**). Não é pré-requisito para implementar as fórmulas da §5.

## Fontes

- Resumo do relatório de engenharia reversa do Claude (varreduras de opcode, 0,252 ms / 65,5 ms / ~65 ms, `rep = 0`, PWM 8 bit, crash `0x13`, estados §15, métodos §17, WCAG 2,5 Hz) — o arquivo anexado é privado e não foi relido aqui.
- `PROTOCOLO.md` e `luxafor.py` na raiz (a versão de 21 nov. 2026; os fatos de `51`/`52`/`62` e dos opcodes inexistentes foram atualizados neste PR).
- Testes desta conversa: `0x51` / `0x52` / `0x62` / serial `000000002498`.
- `.old/docs/conceito/gerar_conceito.py`: cores, curvas e escada dos estados do caderno antigo.
- Datasheet WS2816B-2020 (rev C); DS14693 / AN2606 (MCU, não repetido aqui).
