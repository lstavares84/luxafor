# Prompt para outra IA: caderno conceitual "Indicador rev A"

Copie tudo o que está entre as linhas `=====` e cole na outra IA. Antes, preencha as três variáveis do bloco **0. Parâmetros**. Todo o resto pode ficar como está.

=====

## 0. Parâmetros (preencha antes de enviar)

- **PÚBLICO-ALVO:** `[ex.: engenheiros de hardware e firmware | líderes técnicos e gestores de engenharia | investidores-anjo e aceleradoras | compradores B2B de TI | comunidade maker]`
- **IDIOMA:** `[português do Brasil]`
- **SAÍDA:** `[PDF A3 paisagem, 14 lâminas | código que gera esse PDF | as duas coisas]`

## 1. Papel e objetivo

Você é diretor de arte e engenheiro de produto ao mesmo tempo. Sua tarefa é produzir um **caderno conceitual de 14 lâminas** para um produto de hardware chamado provisoriamente **INDICADOR**, na revisão **rev A**.

O caderno é material de apresentação técnica: parece uma prancha de engenharia com acabamento de livro de arte. Cada número que aparece nele foi levantado de verdade (placa desenhada no KiCad, preços consultados na JLCPCB em 08/11/2026, modelo financeiro calculado). Você deve **manter todos os dados exatamente como estão neste prompt**. O que muda conforme o PÚBLICO-ALVO é a ênfase, o tom das poucas frases e a ordem de leitura, nunca os números (ver seção 6).

## 2. O produto

**O que é.** Um indicador de status com três pontos de luz RGB, que fica preso ao lado do monitor e mostra, sem que a pessoa precise olhar para a tela:
- o estado dos agentes de IA no Linux: **processando**, **precisa de atenção** e **erro**;
- a presença do usuário para quem está por perto: **em reunião** (não interrompa) ou **livre**.

**Por que existe.** Quem trabalha com agentes de IA (Claude Code, Codex etc.) passa tempo esperando ou deixa de ver quando o agente parou pedindo permissão. E colegas interrompem em reuniões no Teams ou no Google Meet porque não há sinal físico de "ocupado". O produto resolve as duas coisas com uma luz.

**Como funciona.**
1. **Fontes de evento (Linux):** hooks do Claude Code (início, permissão, fim, erro); `notify` do Codex; microfone em uso (PipeWire); câmera em uso (`/dev/video*` aberto); agenda Google ou Outlook (OAuth, fase posterior).
2. **Daemon Linux em Python:** junta as fontes, aplica a prioridade, escolhe o estado e manda **um comando por mudança** pelo USB.
3. **Aparelho:** USB HID com relatórios de 8 bytes → STM32C071 (USB full-speed sem cristal, animações gravadas na flash, SPI a 800 kHz) → buffer 74AHCT1G125 (3,3 V → 5 V) → cadeia D1 (baixo) → D2 (meio) → D3 (topo).
4. **Prioridade dos estados:** EM REUNIÃO > ERRO > ATENÇÃO > PROCESSANDO > LIVRE.

**Origem.** O protocolo é compatível com o que foi mapeado por engenharia reversa de um indicador comercial (Luxafor Flag). Cite isso uma única vez, na lâmina do sistema, como "compatível com o protocolo mapeado do Luxafor". O produto **não** usa a marca, o visual nem o nome desse fabricante.

## 3. Conceito de design: "Metrologia Luminosa"

**Princípio:** a luz é uma grandeza; ela é medida antes de ser admirada. Cada lâmina parece saída de uma bancada de calibração, ou de um tratado de uma disciplina que ainda não existe. **90% do conteúdo é visual e 10% é texto.** O acabamento precisa parecer o resultado de muitas horas de trabalho de alguém no topo do ofício.

### 3.1 Duas famílias de lâmina
- **Papel (lâminas técnicas):** fundo marfim quente `#EEEAE2`, traço em grafite em três pesos e grade de pontos finíssima (passo de 5 mm, ponto de 0,14 mm, cor `#E2DED5`).
- **Noite (lâminas de emissão de luz, 01 e 05):** fundo `#090C11`, grade de pontos `#151A21`. Ali a cor se comporta como luz de verdade: halo radial suave, sem contorno, que perde força com a distância.

### 3.2 Paleta
| Uso | Cor |
|---|---|
| Papel | `#EEEAE2` |
| Tinta principal / secundária / clara / régua | `#1B1E21` · `#5A5F64` · `#A9A79F` · `#D6D2C8` |
| Noite / painel / borda | `#090C11` · `#161B22` · `#2A313B` · texto `#C9CDD3` |
| Estado LIVRE | `#2FD28A` (verde, brilho baixo) |
| Estado PROCESSANDO | `#3D8BFF` (azul) |
| Estado ATENÇÃO | `#FFB21E` (âmbar) |
| Estado ERRO | `#FF3FC8` (magenta) |
| Estado EM REUNIÃO | `#FF3B2F` (vermelho) |
| Placa: máscara preta fosca / trilhas sob a máscara | `#121417` · `#22262B` |
| Placa: ENIG (ouro) / via | `#C8A35A` · `#8E7135` |
| Epóxi / cerâmica / carcaça USB / LED | `#26282B` · `#BFA57E` · `#B9BCC0` · `#F3F0E8` |

A cor de estado só aparece quando é **emitida**, nunca como decoração. Use no máximo um sinal cromático por lâmina; a exceção é a lâmina 05, que mostra os cinco estados.

### 3.3 Tipografia (fontes OFL)
- **Títulos:** Jura Light, em caixa alta, com espaçamento largo entre letras (~1,6 mm em corpo de 7 mm) e um fio de 26 mm logo abaixo.
- **Rótulos pequenos:** Jura Medium, em caixa alta, com espaçamento médio.
- **Dados, cotas e códigos:** Geist Mono (ou JetBrains Mono), com corpo entre 1,9 e 2,5 mm.
- **Notas à margem:** Instrument Serif Italic, no máximo uma ou duas por lâmina.
- **Texto de tabela:** Work Sans.
- Nunca use parágrafos: só rótulos, legendas e frases curtas.

### 3.4 Esqueleto comum a todas as lâminas
- **Formato:** A3 paisagem, 420 × 297 mm, com margem de 16 mm.
- **Marcas de registro:** em L nos quatro cantos, com braços de 5 mm.
- **Régua no topo:** subdivisão de 1 mm, marcas médias a cada 5 mm e maiores a cada 10 mm.
- **Rodapé:** à esquerda, o fólio `NN / 14`; no centro, `INDICADOR · REV A · CADERNO CONCEITUAL` com espaçamento largo; à direita, o nome da lâmina.
- **Desenho técnico:** projeção ortogonal no 1.º diedro (NBR 10067). As linhas de chamada pontilhadas amarram as vistas umas às outras. Cotas com setas finas e o valor em monoespaçada.
- **Equilíbrio:** assimétrico. Um peso visual dominante, uma coluna estreita de dados e um campo de silêncio entre os dois.
- **Regra inegociável:** nada se sobrepõe e nada sai da margem.

## 4. Dados técnicos (use exatamente estes)

### 4.1 Produto
- **Envelope:** 48 (altura) × 34 (largura com a bandeira) × 15 mm (profundidade).
- **Corpo:** 12 × 48 × 15 mm, cantos com raio de 1,6 mm.
- **Bandeira (guia de luz):** 22 × 19 × 2,5 mm. Fica de 2 a 21 mm abaixo do topo e sai pela lateral direita do corpo.
- **Montagem interna:** a placa fica em pé dentro do corpo, com os componentes voltados para a bandeira. A raiz da bandeira entra no corpo até encostar na face dos LEDs, e a luz entra pela borda. A raiz pode ter no máximo cerca de 3 mm de espessura.
- **Base:** junta corpo/tampa a 6 mm da base; janela do USB-C na tampa inferior.
- **Fixação:** ímã NdFeB Ø10 × 1,5 mm com fita VHB, nas costas do corpo.
- **LEDs:** a 3, 10 e 17 mm do topo da placa (D3 topo, D2 meio, D1 baixo). A placa começa 2 mm abaixo do topo do corpo.

### 4.2 Placa de circuito
- **Dimensões:** 11,0 × 44,0 × 0,8 mm, cantos com raio de 1 mm.
- **Laminado e acabamento:** FR-4 de 2 camadas, cobre de 35 µm (1 oz) com planos de GND, máscara preta fosca, acabamento ENIG.
- **Regras de roteamento:** trilha de 0,20 mm, isolamento de 0,15 mm, vias de 0,6/0,3 mm (18 vias).
- **Montagem:** SMT só na face de cima. Na face de baixo ficam só os 5 pads SWD (3V3, SWDIO, SWCLK, NRST, GND) e a serigrafia "IND rev A".
- **Posição dos componentes (de cima para baixo):** D3, D2, D1 no centro; coluna esquerda com U3, R3, C3 a C5; coluna direita com C6 a C8 e C2; U1 a 26 mm do topo; U2 e U4 lado a lado a 32 mm; C1, R1 e R2 a 34,7 mm; USB-C na borda inferior, sobressaindo 0,7 mm.
- **Perfil:** altura total de 4,1 mm com o USB-C.
- **Verificação:** ERC e DRC sem erros no KiCad 9.
- **Pinagem do SK6805-EC20 (vista de topo):** 3 GND e 2 DOUT em cima; 4 DIN e 1 VDD embaixo. Ilhas de 0,6 × 0,6 mm; corpo de 2,0 × 2,0 × 0,65 mm.
- **Energia:** LEDs 45 mA (3 × 3 × 5 mA), MCU + USB 10 mA, buffer de nível + LDO 2 mA. Pico de 57 mA, frente a 500 mA disponíveis no USB.

### 4.3 Componentes (catálogo JLCPCB)
| Ref | Qtd | Função | Peça | Encaps. | LCSC |
|---|---|---|---|---|---|
| U1 | 1 | Microcontrolador M0+, USB sem cristal | STM32C071F8P6 | TSSOP-20 | C43650205 |
| D1–D3 | 3 | LED RGB endereçável, 5 mA/canal | SK6805-EC20 | 2020 | C2890036 |
| U2 | 1 | Regulador linear 3,3 V, 600 mA | AP2112K-3.3 | SOT-23-5 | C51118 |
| U3 | 1 | Buffer 3,3 → 5 V para o dado dos LEDs | 74AHCT1G125 | SC-70-5 | C53114384 |
| U4 | 1 | Proteção ESD de D+/D− e VBUS | USBLC6-2SC6 | SOT-23-6 | C7519 |
| J1 | 1 | Receptáculo USB-C, 16 pinos | TYPE-C-31-M-12 (HRO) | SMD + THT | C165948 |
| C1 | 1 | 10 µF 10 V X5R, entrada VBUS | CL10A106KP8NNNC | 0603 | C19702 |
| C2 | 1 | 1 µF 25 V X5R, saída 3,3 V | CL05A105KA5NQNC | 0402 | C52923 |
| C3–C8 | 6 | 100 nF 16 V X7R, desacoplamento | CL05B104KO5NNNC | 0402 | C1525 |
| R1, R2 | 2 | 5,1 kΩ 1 %, CC do USB-C | 0402WGF5101TCE | 0402 | C25905 |
| R3 | 1 | 33 Ω 1 %, série no dado dos LEDs | 0402WGF330JTCE | 0402 | C25105 |

### 4.4 Mecânica e acessórios (todos marcados como **proposta**)
| Item | Descrição | Especificação | Processo |
|---|---|---|---|
| M1 | Corpo | PC/ABS grafite, 12 × 48 × 15 mm | injeção / impressão 3D |
| M2 | Tampa inferior | PC/ABS grafite, janela USB-C | injeção / impressão 3D |
| M3 | Bandeira / guia de luz | PC difusor, 22 × 19 × 2,5 mm | injeção / impressão 3D |
| M4 | Ímã de fixação | NdFeB N52 Ø10 × 1,5 mm, revestido de Ni | comprado |
| M5 | Fita dupla face | VHB acrílica, disco Ø10 mm | corte |
| A1 | Cabo | USB-C ↔ USB-A/C, 1,5 m | comprado |
| A2 | Embalagem | caixa kraft com berço | comprado |

**Materiais e processos (lâmina 04):**
- Corpo e tampa: PC/ABS, injeção com textura fina.
- Bandeira: policarbonato difusor, injeção, guia de luz pela borda.
- Placa: FR-4, cobre e máscara preta; laminação, ENIG e SMT.
- Contatos do USB-C: liga de cobre e aço inox; estampagem e solda THT.
- Fixação: ímã NdFeB sinterizado e revestido de níquel, com fita VHB.

### 4.5 Protocolo USB (HID de 8 bytes, sem Report ID)
| Op | Comando | Bytes |
|---|---|---|
| 01 | cor fixa | `01 LED R G B` |
| 02 | fade | `02 LED R G B t` |
| 03 | strobe | `03 LED R G B t 00 n` |
| 04 | wave | `04 tipo R G B 00 n v` |
| 06 | padrão | `06 id n` |
| 80 | versão | `80` → `80 VV` |
| ·· | estado | proposto |

Exemplo para a lâmina 06, cor fixa azul no LED do topo: `01 03 00 00 FF 00 00 00` (op, led, R, G, B). Destaque o byte `FF` em azul.

### 4.6 Estados e curvas de brilho em 4 s
| Estado | Cor | Forma no tempo |
|---|---|---|
| LIVRE | verde | constante e fraco (~28%) |
| PROCESSANDO | azul | "respiração": senoide com período de 2,4 s |
| ATENÇÃO | âmbar | pisca 1 Hz, 50% do tempo aceso |
| ERRO | magenta | strobe 4 Hz, flashes curtos |
| EM REUNIÃO | vermelho | constante a 100% |

### 4.7 Custos (US$; componentes pela JLCPCB em 08/11/2026; o resto estimado)
| Item | Lote 5 | Piloto 100 | Série 1000 |
|---|---|---|---|
| Componentes eletrônicos (BOM × lote) | 21,96 | 310,48 | 2.771,40 |
| Fabricação da placa (2 camadas, 0,8 mm, preta, ENIG) | 18,00 | 45,00 | 180,00 |
| Montagem: setup | 8,00 | 8,00 | 25,00 |
| Montagem: estêncil | 1,50 | 1,50 | 7,00 |
| Montagem: taxa de peças extended (6 × US$ 3) | 18,00 | 18,00 | 18,00 |
| Solda manual THT: setup | 3,50 | 3,50 | 3,50 |
| Frete internacional | 25,00 | 45,00 | 180,00 |
| Ferramental de injeção (molde família, 3 cavidades) | — | — | 6.500,00 |
| Montagem: juntas SMD (86 × US$ 0,0017) | 0,73 | 14,62 | 146,20 |
| Montagem: juntas THT (4 × US$ 0,0173) | 0,35 | 6,92 | 69,20 |
| Corpo + tampa (resina 3D \| injeção PC/ABS) | 17,00 | 290,00 | 300,00 |
| Bandeira (resina polida \| injeção PC difusor) | 11,00 | 190,00 | 150,00 |
| Ímã + disco VHB | 0,85 | 12,00 | 80,00 |
| Cabo USB-C 1,5 m | 8,00 | 120,00 | 850,00 |
| Embalagem | 3,00 | 40,00 | 250,00 |
| Montagem final e teste | — | 50,00 | 300,00 |
| **Subtotal** | 136,89 | 1.155,02 | 11.830,30 |
| **Impostos de importação (estimativa)** | 99,39 | 1.117,52 | 8.281,21 |
| **TOTAL DO LOTE** | **236,28** | **2.272,54** | **20.111,51** |
| **Por unidade** | **US$ 47,26** (≈ R$ 259,91) | **US$ 22,73** (≈ R$ 124,99) | **US$ 20,11** (≈ R$ 110,61) |

- **Composição do lote mínimo:** componentes 9%, taxas e frete 31%, mecânica e acessórios 17%, impostos 42%.
- **Nota do lote de 1000:** o molde de US$ 6.500 pesa US$ 6,50 por peça; sem ele, a unidade cai para cerca de US$ 9,06.
- **Regra de imposto usada:** II de 60% menos US$ 30, mais ICMS de 20% por dentro (regime simplificado, remessa até US$ 3.000). No lote de 1000, importação formal com carga indicativa de 70%. Câmbio de referência: R$ 5,50 por dólar.

### 4.8 Plano de negócio (R$)
- **Ciclo de vida de 5 anos**, do lançamento até a substituição pela rev B. Unidades por ano: 300 / 1.200 / 2.400 / 2.800 / 1.300, total de 8.000. As fases:

| Fase | Anos | O que acontece |
|---|---|---|
| Introdução | 1 | lote piloto, venda direta a desenvolvedores, preço cheio, comunidade e reviews |
| Crescimento | 2 e 3 | molde, marketplaces, B2B, kits para times, integrações abertas |
| Maturidade | 4 | custo mínimo, revendas, rev B (multiagente, USB-C 2.0 sem LDO) |
| Declínio | 5 | liquidação de estoque, suporte de firmware, peças de reposição |

- **Investimento no ano 0:** total de **R$ 70.422**.
  - Molde: R$ 35.750.
  - Engenharia e protótipos: R$ 15.000.
  - Ensaios EMC de pré-conformidade: R$ 8.000.
  - Marca (INPI), site, fotos e lançamento: R$ 7.000.
  - Capital de giro (3 meses de estoque): R$ 4.672.
- **Premissas:**
  - Custo unitário: R$ 49,84 em lotes de 1000; R$ 62,30 no ano 1.
  - Comissão de canal: 14%.
  - Frete absorvido: R$ 14,00 por pedido.
  - Simples Nacional, alíquota efetiva: 8%.
  - Garantia e devoluções: 3%.
  - Despesas fixas por ano: R$ 30.000 / 30.000 / 27.000 / 24.000 / 15.000.
  - TMA: 14% a.a.
- **Fluxo de caixa ao preço sugerido de R$ 179:**

| | Ano 0 | Ano 1 | Ano 2 | Ano 3 | Ano 4 | Ano 5 |
|---|---|---|---|---|---|---|
| Receita | | 53.700 | 214.800 | 429.600 | 501.200 | 232.700 |
| Custos variáveis | | −36.314 | −130.306 | −260.612 | −304.047 | −141.165 |
| Despesas fixas | | −30.000 | −30.000 | −27.000 | −24.000 | −15.000 |
| Resultado operacional | | −12.614 | 54.494 | 141.988 | 173.153 | 76.535 |
| Investimento e giro | −70.422 | −10.279 | −14.951 | −4.984 | 18.689 | 16.197 |
| Fluxo de caixa livre | −70.422 | −22.894 | 39.543 | 137.004 | 191.842 | 92.733 |
| Acumulado | −70.422 | −93.316 | −53.773 | 83.231 | 275.073 | 367.806 |
| Acumulado descontado (14%) | −70.422 | −90.504 | −60.078 | 32.396 | 145.982 | 194.145 |

- **Indicadores:**
  - VPL a 14% a.a.: **R$ 194.145**.
  - TIR: **61,3% a.a.**, 47 pontos acima da TMA.
  - Payback simples: **2,4 anos**; payback descontado: **2,6 anos**.
  - ROI no ciclo: **522%**, calculado como a soma dos fluxos dos anos 1 a 5 dividida pelo investimento do ano 0, menos 1.
- **Preço:**
  - Preço sugerido: **R$ 179** (≈ US$ 33), margem líquida unitária de 35%.
  - Preço mínimo, em que o VPL é zero e a TIR é igual à TMA: **R$ 128,63**. Margem do sugerido sobre o mínimo: 39%.
  - Com 60% do volume previsto: VPL de R$ 54.337 e TIR de 30,6%.
  - Volume de equilíbrio a R$ 179: 44% do previsto.
- **Matriz de VPL (R$ mil), preço × volume:**

| Volume | R$ 149 | R$ 179 | R$ 199 | R$ 229 |
|---|---|---|---|---|
| 50% | −38 | 19 | 58 | 116 |
| 70% | 8 | 89 | 143 | 224 |
| 100% | 79 | 194 | 271 | 387 |
| 130% | 149 | 299 | 399 | 550 |

- **Composição de R$ 179 por unidade no ano de maturidade:** custo do produto R$ 49,84; frete R$ 14,00; canal R$ 25,06; impostos R$ 14,32; garantia R$ 5,37; fixos rateados R$ 8,57; margem R$ 61,84.

## 5. Estrutura das 14 lâminas

1. **CAPA (noite).**
   - À direita, o produto de frente em escala grande (~4,2:1), com a bandeira acesa em azul (processando). A luz parte de três pontos brilhantes na raiz e se espalha por um degradê que esmaece para a ponta, com halo azul.
   - À esquerda, o título `INDICADOR` em Jura Light gigante e espaçado, com um fio azul abaixo.
   - Nota em itálico: *"três pontos de luz para saber o que a máquina está fazendo, sem olhar para a tela."*
   - Coluna de 5 especificações: envelope, luz, controle, conexão, placa.
   - Linha final: `REV A · ESTUDO CONCEITUAL · 2026-11-08`.
2. **VISTAS DO PRODUTO (papel).**
   - Vistas frontal, lateral esquerda e superior, em escala 3,2:1 no 1.º diedro.
   - Cotas: 48, 34, 15, 12, 22, 19 e 2,5.
   - Placa, LEDs e USB-C desenhados em tracejado oculto.
   - Isometria à direita.
   - Nota: *"A raiz da bandeira entra no corpo até encostar na face dos LEDs: a luz entra pela borda."*
3. **PLACA · TRÊS VISTAS (papel).**
   - Face de cima com componentes, perfil com as alturas reais e face de baixo com os pads SWD, tudo em escala 5:1, com máscara preta e ilhas douradas.
   - Chamadas com linhas de chamada para D3, D2, D1, U3, U1, U2, U4 e J1.
   - Cotas: 11,0, 44,0, 0,8 e 4,1.
   - Ficha da placa (seção 4.2).
   - Detalhe do LED SK6805-EC20 em 14:1, com a pinagem.
4. **COMPONENTES E MATERIAIS (papel).**
   - Tabela 4.3 com um ícone de cada encapsulamento em escala 6:1.
   - Coluna de materiais: amostras de cor em quadrado, nome do material e processo.
   - Barra de energia empilhada, em escala de 0 a 60 mA.
5. **EM FUNCIONAMENTO (noite).**
   - Cinco produtos lado a lado, um por estado, cada um com seu halo.
   - Abaixo de cada um, o nome do estado e a curva de brilho em 4 s (tabela 4.6).
   - Faixa de prioridade no rodapé.
   - Nota: *"uma cor por estado; a forma no tempo diz a urgência."*
6. **SISTEMA (papel).**
   - Diagrama "do evento à luz": as cinco fontes, o daemon Linux e o aparelho tracejado (STM32 → 74AHCT → D1 → D2 → D3).
   - Tabela do protocolo.
   - Relatório HID de exemplo, byte a byte.
7. **PLACA · RENDERS (papel).** Três imagens fotorrealistas: face de cima, face de baixo e isometria em luz de estúdio. Use a legenda *"ray tracing sobre a geometria exportada do KiCad"*.
8. **PRODUTO · RENDERS I (papel).** P1 grande: três quartos, processando. P2: frente, em reunião, fundo escuro. P3: base com o USB-C.
9. **PRODUTO · EM USO E MONTAGEM (papel).** P4: em cima de um monitor, livre. P5: os cinco estados lado a lado. P6: vista explodida (placa, corpo, bandeira apagada, tampa).
10. **LISTA DE MATERIAL (papel).** Grupos: eletrônica, placa, mecânica, acessórios. Colunas: item, descrição, especificação, quantidade, origem/código, processo. Os itens "proposta" vão em tinta mais clara.
11. **CUSTOS (papel).**
    - Tabela 4.7 à esquerda.
    - À direita, três números grandes (custo por unidade nos três lotes), cada um com uma barrinha vertical na cor de um estado.
    - Barra de composição do lote mínimo.
    - Nota sobre o peso do molde.
12. **PLANO DE NEGÓCIO · CICLO DE VIDA (papel).** Gráfico de barras das unidades por ano com as faixas de fase; investimento do ano 0; premissas.
13. **PLANO DE NEGÓCIO · RETORNO (papel).** Tabela de fluxo de caixa; indicadores em destaque (VPL, TIR, payback, ROI); curva de caixa acumulado descontado, marcando o payback em 2,6 anos.
14. **PLANO DE NEGÓCIO · PREÇO (papel).** Preço sugerido em destaque; curva de VPL × preço com o mínimo em R$ 129; matriz de VPL preço × volume; barra de composição dos R$ 179.

## 6. Adaptação ao PÚBLICO-ALVO

Os números não mudam. Mudam a capa, a ordem de destaque e as frases curtas:

| Público | Ênfase | Lâminas protagonistas | Tom das notas |
|---|---|---|---|
| Engenheiros de hardware/firmware | arquitetura, pinagem, alturas, energia, protocolo | 03, 04, 06, 07 | seco e preciso, como num datasheet |
| Líderes técnicos e gestores | problema resolvido, integração com as ferramentas, custo por unidade | 01, 05, 06, 11 | benefício operacional ("menos espera, menos interrupção") |
| Investidores e aceleradoras | mercado, ciclo de vida, retorno, risco | 01, 08, 12, 13, 14 | resultado e premissas explícitas |
| Compradores B2B de TI | uso em equipe, padronização, preço por volume | 05, 09, 11, 14 | prático, com foco em escala |
| Comunidade maker | hardware aberto, como fabricar, BOM | 03, 04, 07, 10 | convidativo, "faça o seu" |

Se o público não for técnico, acrescente no máximo uma frase de contexto por lâmina técnica e um mini-glossário (HID, ENIG, TIR, VPL) discreto no rodapé da lâmina onde o termo aparece. Não remova lâminas: mude só o peso visual.

## 7. Imagens fotorrealistas (lâminas 7 a 9)

Se você puder gerar imagens, siga estas especificações. Se não puder, deixe um retângulo cinza `#D6D2C8` com a legenda "render pendente" e escreva, para cada imagem, um briefing de render pronto para Blender ou KeyShot.

**Placa:**
- Máscara preta fosca com leve verniz, ilhas ENIG douradas, serigrafia branca.
- Componentes reais: TSSOP-20 de epóxi preto, SOT-23 e SC-70 com terminais estanhados, capacitores 0402/0603 de cerâmica bege, USB-C de aço inox polido.
- LEDs 2020 brancos com difusor.
- Fundo infinito marfim.

**Produto:**
- Corpo em PC/ABS grafite `≈ #2A2C2F` acetinado, com ranhura fina na junta a 6 mm da base.
- Bandeira em policarbonato difusor acesa pela borda: brilho mais forte na raiz, saturado na cor do estado, sem estourar para o branco.
- Cenas claras em estúdio marfim; cenas de estado em estúdio escuro com luz de recorte.
- No monitor, o produto fica em cima da borda superior, com a bandeira para fora.

**Proibido:** logotipos ou marcas de terceiros, inclusive no produto e no monitor; pessoas; texto inventado sobre o produto.

## 8. Regras de honestidade

- Não invente dados. Se algo não estiver neste prompt, escreva "a definir" em tinta clara.
- Mecânica, materiais do corpo, renders e valores fora do catálogo da JLC são **proposta ou estimativa**. Diga isso nas legendas (ex.: "proposta, a validar no protótipo").
- Os renders são conceituais, não fotos de um protótipo real.
- Valores de imposto e câmbio são premissas de 08/11/2026 e precisam ser revistos antes de qualquer decisão.

## 9. Checklist de qualidade (rode antes de entregar)

- [ ] As 14 lâminas existem, na ordem, com o fólio `NN / 14` correto.
- [ ] Todos os números conferem com as seções 4.1 a 4.8.
- [ ] Nenhum texto sobrepõe outro, nenhum elemento sai da margem de 16 mm, nenhuma cota cruza um desenho.
- [ ] As cotas estão do lado de fora das peças e as vistas estão alinhadas por linhas de chamada.
- [ ] As cores de estado aparecem só como emissão ou como marcador de dado.
- [ ] Há no máximo duas notas em serifa itálica por lâmina e nenhum parágrafo.
- [ ] O PDF final tem menos de 30 MB (imagens em JPEG de alta qualidade).
- [ ] A ênfase segue a linha da tabela da seção 6 correspondente ao PÚBLICO-ALVO escolhido.

## 10. Entregáveis

1. `indicador-conceito.pdf`: A3 paisagem, 14 lâminas.
2. Um parágrafo explicando as escolhas feitas para o PÚBLICO-ALVO.
3. Se a SAÍDA incluir código: um script reprodutível (ex.: Python com reportlab) com os dados em estruturas separadas do desenho, para que custos e preços possam ser atualizados sem mexer no layout.

=====
