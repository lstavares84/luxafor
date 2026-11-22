# Ficha de premissas · SIGNA rev C · caderno conceitual

Data do estudo: 2026-11-22. Toda premissa abaixo tem uma de três origens: **ficha** (dado do usuário), **cotação** (fornecedor, código e data) ou **estimativa** (com o raciocínio). Impostos, câmbio e mercado foram consultados em 2026-11-22 e **precisam ser revistos antes de qualquer decisão**.

## 0. Ficha do produto (preenchida)

- **NOME:** SIGNA (nome provisório · a verificar no INPI)
- **REVISÃO:** rev C
- **DATA:** 2026-11-22
- **CATEGORIA:** eletrônico de mesa · luz de presença para sala e monitor de IAs
- **FRASE-SÍNTESE:** uma luz para a sala ver seu status — e para você acompanhar suas IAs
- **PROBLEMA:** quem entra na sala não sabe se você está livre, prestes a entrar em reunião ou ocupado; e quem usa Claude, ChatGPT e Grok perde o fio de quando precisam de atenção, erram ou batem o limite
- **USUÁRIO FINAL:** profissional em escritório ou home office que usa Google/Outlook Agenda e trabalha com IAs (Claude, ChatGPT, Grok)
- **COMO FUNCIONA:** app no PC lê Google/Outlook Agenda, chamada/atalho e (opcional) Claude, ChatGPT e Grok → motor de prioridade decide os 3 LEDs (modo sala ou modo misto sala + IA) → envia relatório HID de 8 bytes pelo USB (0xFF todos, ou 0x01–0x03 por LED) → MCU expande 8 → 16 bit com gama; 3 LEDs RGB acendem o difusor sem cintilação
- **MODOS (SALA + IA):** [SALA] LIVRE #2FD28A: contínuo · brilho 0,28 (0xFF (ou 0x02+0x03 misto)); [SALA] PRESTES A ENTRAR #FF8A1A: pulso lento 3,0 s · aviso 5 min (app) (0xFF (ou 0x02+0x03 misto)); [SALA] OCUPADO #FF3B2F: contínuo · brilho 1,0 (0xFF (trava os 3 LEDs; LED 1 da IA some no v1)); [IA] IA DESOCUPADA #7C8EA6: tênue · brilho 0,08 (0xFF (só IA) ou 0x01 (misto)); [IA] PROCESSANDO #3D8BFF: respiração 2,4 s · 0,42 Hz (0xFF (só IA) ou 0x01 (misto)); [IA] PRECISA DE ATENÇÃO #FFE02E: quadrada 1 Hz · 50 % (0xFF (só IA) ou 0x01 (misto)); [IA] ERRO #FF3FC8: strobe 2,5 Hz · pulso 130 ms (0xFF (só IA) ou 0x01 (misto)); [IA] LIMITE ATINGIDO #9B5CFF: 5 h: pulso duplo · sem.: fixo baixo (0xFF (só IA) ou 0x01 (misto))
- **ALOCAÇÃO 3 LEDS:** SALA: 0xFF (3 LEDs) = estado da sala | IA: 0xFF (3 LEDs) = estado da IA | MISTO: LED 3 (topo) + LED 2 (meio) = SALA · LED 1 (baixo) = IA · quando SALA = OCUPADO, a sala vence e trava 0xFF em vermelho #FF3B2F (v1: LED 1 da IA some; não configurável)
- **DIFERENCIAL:** modo SALA (padrão): livre, prestes a entrar em reunião (Google/Outlook) e ocupado; modo IA (opt-in): acompanha Claude, ChatGPT e Grok — inclusive limite de 5 h ou semanal; 3 LEDs independentes (topo+meio = sala, baixo = IA), USB-C HID sem driver, PWM 10 kHz
- **ENVELOPE:** Ø19 × 78 mm (88,2 mm com o passa-cabo), ≈ 20 g sem cabo (estimativa)
- **SUBSISTEMA CENTRAL:** placa rev C, 11 × 44 × 0,8 mm, 2 camadas (KiCad: `.old/hardware/revC/`; a placa atual é `hardware/revD/`)
- **CARCAÇA:** proposta "Pendente" (conjunto atual em `mecanica/`): tubo PC opalino Ø16, tampa Al Ø19, berço, tampão, passa-cabo; não prototipada
- **MERCADO:** Brasil, R$
- **LOTES:** 5 / 100 / 1.000
- **TMA:** 14 % a.a. (ficha)
- **HORIZONTE:** 5 anos (ficha)
- **PÚBLICO-ALVO:** investidores
- **IDIOMA:** pt-BR
- **SAÍDA:** PDF + código
- **PESQUISA DE PREÇOS:** sim

## 1. Câmbio

- US$ 1 = R$ 5,8889 — **cotação**: PTAX venda BCB de 19/11/2026 (última publicada, consultada em 2026-11-22); rever antes de decidir. O fechamento comercial de 20/11/2026 foi R$ 5,9488 (+1,0 %).
- Sensibilidade (estimativa): o custo unitário importado é ~90 % dolarizado; +10 % no dólar ≈ +9 % no custo unitário.

## 2. Custo por lote (lâmina 11)

- **Peças eletrônicas:** cotação: API de peças JLCPCB (selectSmtComponentList), faixa de preço por quantidade, 2026-11-22, US$. Arquivo: `dados/jlc_precos_2026-11-22.json`. Placa por unidade: US$ 3,78 (lote 5), US$ 2,55 (lote 100), US$ 2,17 (lote 1.000).
- **PCB** (4,00 / 15,00 / 60,00 para 5 / 100 / 1.000): estimativa: tabela pública JLCPCB 2 camadas 0,8 mm; painel; não cotado no carrinho.
- **Montagem SMT, custos fixos** (27,50 / 27,50 / 58,00 para 5 / 100 / 1.000): estimativa: setup US$ 8 + estêncil US$ 1,50 + 6 peças 'extended' × US$ 3 (lotes 5 e 100); lote 1000 em PCBA padrão: setup US$ 25 + estêncil US$ 15 + US$ 18.
- **Mecânica** (17,50 / 9,70 / 2,11 para 5 / 100 / 1.000): estimativa: lote 5 = tampa CNC US$ 12 + SLA US$ 3 + tubo US$ 1,50 + passa-cabo impresso US$ 1; lotes 100/1000 = BOM do Pendente (P01–P05), sem cotação.
- **Moldes** (0,00 / 0,00 / 4.000,00 para 5 / 100 / 1.000): estimativa: molde família P03+P04 em alumínio US$ 2.500–4.000 + molde P05 US$ 800–1.500 (faixas de ferramentaria China); adotado US$ 4.000.
- **Cabo** (3,00 / 1,80 / 1,00 para 5 / 100 / 1.000): estimativa: cabo C↔C 1,5 m OEM; pedir amostra.
- **Frete** (30,00 / 60,00 / 300,00 para 5 / 100 / 1.000): estimativa: courier China→Brasil (PCBA + mecânica), ~0,03 kg/un + caixas.
- **Embalagem** (12,00 / 6,00 / 3,20 para 5 / 100 / 1.000): estimativa: caixa kraft + cartão + etiquetas, gráfica BR.
- **Juntas de solda:** 107 × US$ 0.0017 — estimativa: contagem de pads da BOM (QFN-28+EP 29, LEDs 18, USB-C 20, SOT 16, passivos 24) × tarifa pública JLC.
- **Montagem final, gravação e teste:** 20 / 8 / 5 min por unidade × R$ 40,00/h — estimativa: técnico R$ 3.500/mês + encargos ≈ R$ 7.000 / 176 h ≈ R$ 40/h; tempo inclui gravação do firmware por DFU, teste e embalagem.
- **Impostos de importação:** estimativa: RTS = II 60 % + ICMS ~20 % por dentro (fator ×2,0 sobre valor aduaneiro); formal = alíquotas típicas a confirmar por NCM com despachante; molde entra no valor aduaneiro (assist, Acordo de Valoração Aduaneira art. 8). Fator RTS = (1 + 0,60) ÷ (1 − 0,20) − 1 = 100 %. Fator formal = 77,0 % (II 16 %; IPI 15 % sobre valor + II; PIS 2,1 %; COFINS 9,65 %; ICMS 18 % por dentro). Despachante no lote 1.000: R$ 2.500 (estimativa).
- **Limite do RTS:** remessa até US$ 3.000; o lote 1.000 passa disso e vai para importação formal.
- **Não incluídos:** perdas de peças (attrition) da JLC, armazenagem, seguro, IOF sobre o pagamento internacional (alíquota a confirmar).

| lote | total R$ | R$/un. | US$/un. |
|---|---|---|---|
| 5 | 2.293 | 458,60 | 77,88 |
| 100 | 19.097 | 190,97 | 32,43 |
| 1.000 | 112.022 | 112,02 | 19,02 |
| 1.000 sem molde | 70.325 | 70,33 | 11,94 |

## 3. Plano de negócio (lâminas 12 a 14)

- **Volumes:** 500, 1.500, 2.500, 2.500, 1.200 un. nos anos 1–5 (total 8.200). estimativa top-down: 6,6 milhões trabalham no domicílio (IBGE, PNAD Contínua 2025, divulgada em 23/09/2026); pico de 2.500 un./ano = 0,04 % dessa base. Raciocínio: nicho de acessório de mesa; o pico supõe ≈ 1 em cada 2.640 trabalhadores em casa comprando por ano.
- **Custo unitário no plano:** R$ 70,33 = lote 1.000 sem o molde (o molde entra como investimento do ano 0). Supõe compras sempre em lotes de 1.000.
- **Comissão de canal:** 13 % — estimativa: mix 60 % marketplace (tarifa Premium 18 % em eletrônicos, fontes secundárias consultadas em 2026-11-22) + 40 % site próprio (gateway ~5 %) ≈ 12,8 %.
- **Frete absorvido:** R$ 20,00/un. — estimativa: frete grátis subsidiado para pacote de ~150 g.
- **Impostos sobre a receita:** estimativa: Simples Nacional, LC 123/2006 Anexo II (indústria: montagem final no Brasil); alíquota efetiva = (RBT12 × nominal − dedução) / RBT12, com RBT12 ≈ receita do ano. Transição da reforma tributária (LC 214/2025) não modelada. Rever com contador. Alíquotas efetivas resultantes: ano 1 4,5 %, ano 2 6,1 %, ano 3 7,6 %, ano 4 7,6 %, ano 5 5,6 %.
- **Garantia:** 2 % da receita — estimativa: 3 % de trocas × custo de reposição e frete ≈ 2 % da receita.
- **Despesas fixas:** R$ 36.000/ano — estimativa: contador R$ 500/mês + marketing contínuo R$ 1.500/mês + site e ferramentas R$ 300/mês + manutenção de software R$ 700/mês. Não inclui pró-labore do fundador.
- **Capital de giro:** 30 % do CPV do ano — estimativa: ~3,6 meses de estoque e recebíveis (lote de 1.000 un. comprado à frente da venda). Investido no ano 0 (giro do ano 1), ajustado a cada ano pelo giro do ano seguinte e liberado no ano 5.
- **IR/CSLL:** não há linha separada; no Simples Nacional eles estão dentro da alíquota única.

### Investimento do ano 0

| item | R$ | origem |
|---|---|---|
| Ferramental (moldes P03+P04 e P05, com imposto de importação) | 41.696 | calculado: moldes US$ 4.000 × (1 + 77 %) × câmbio (o molde entra no valor aduaneiro) |
| Engenharia: firmware, app, OAuth e hooks/ext. IA (300 h × R$ 100/h) | 30.000 | estimativa: +100 h para OAuth Google/Outlook, hooks CLI e extensão browser de IAs (antes 200 h) |
| Protótipos: 2 rodadas do lote de 5 | 4.586 | calculado: 2 × total do lote 5 (lâmina 11) |
| Pré-ensaio EMC (CISPR 32) e ESD (IEC 61000-4-2) | 9.000 | estimativa: laboratório nacional, ensaio voluntário |
| Anatel: não aplicável (periférico USB com fio, sem rádio) | 0 | Anatel, Requisitos Técnicos Cat. I, nota ORCN de 08/11/2024; confirmar no Mosaico |
| INMETRO: sem certificação compulsória identificada | 0 | estimativa, a confirmar com OCP |
| USB Vendor ID próprio (USB-IF, taxa única) | 35.333 | cotação: usb.org/getting-vendor-id, consultado em 2026-11-22; alternativa pid.codes gratuita só para hardware aberto |
| Marca (INPI) e lançamento (fotos, site, campanha) | 19.500 | estimativa: INPI R$ 1.500 + conteúdo R$ 8.000 + campanha R$ 10.000 |
| Capital de giro inicial | 10.549 | calculado: 30 % do CPV do ano 1 |
| **total** | **150.664** | |

- **Certificações:** Anatel — periféricos USB com fio e sem rádio não são classificáveis como produto para telecomunicações (Requisitos Técnicos Cat. I, nota ORCN de 08/11/2024), logo R$ 0; confirmar no sistema Mosaico. INMETRO — não identificamos certificação compulsória para acessório USB de 5 V; confirmar com um OCP. EMC — ensaio voluntário de pré-conformidade (estimativa R$ 9.000), recomendado antes de exportar (FCC/CE).
- **VID:PID:** o 04d8:f372 pertence a terceiros e não pode ser usado. Caso base: VID próprio da USB-IF, US$ 6.000 taxa única (cotação usb.org, 2026-11-22). Alternativas: pid.codes (gratuito, exige hardware e firmware abertos) ou sublicença de PID do fabricante do MCU (a verificar com a ST). Com pid.codes o investimento cai R$ 35.333 e o preço mínimo cai junto.

## 4. Resultados

- VPL a 14 % a.a.: **R$ 198.454** · TIR: **45,6 %** · payback simples **2,45 anos**, descontado **2,81 anos** · ROI no ciclo **270 %** (soma dos FCL dos anos 1–5 ÷ investimento − 1).
- Preço mínimo (VPL = 0, TIR = 14 %): **R$ 180,61**. Conferência: VPL no mínimo = −R$ 0,53; TIR no mínimo = 14,00 %.
- Preço sugerido: **R$ 229** = mínimo × (1 + 25 %) arredondado para cima com final 9.
- Volume de equilíbrio no preço sugerido: 4.509 un. em 5 anos (55 % do plano, mesmo perfil de anos).
- Referência de mercado: luz 'ocupado' USB de 2 cores, sem software: R$ 146,24 (Amazon.com.br, ASIN B0GPXXQ6ZV, 2026-11-22).

## 5. Riscos

- estoque do MCU: 109 un. na JLC em 2026-11-22; lote 1.000 exige distribuidor (Mouser/DigiKey) ou o par STM32C071GBU6
- carga de importação: 77–100 % sobre o valor aduaneiro; NCM a confirmar
- câmbio: +10 % no dólar sobe o custo unitário ~9 %
- APIs e UIs de terceiros: OAuth Google/Outlook e extensão web (Claude/ChatGPT/Grok) sem API oficial de status
- demanda: nicho duplo (sala + IA); volumes do ciclo são estimativa top-down

## 6. Engenharia e software

- Consumo: 99 mA a 5 V no pior caso, com margem de 30 %; LEDs WS2816B ×3, R+G+B 100 % 60 mA (datasheet WS2816B-2020: Iout típ. 20 mA (R+G+B) por LED × 3); LEDs, quiescente ×3 3 mA (datasheet: IDD < 0,8 mA por LED × 3, arredondado); MCU STM32C071 48 MHz + USB 12 mA (estimativa a partir do DS14693 (run 48 MHz + USB FS)); LDO + buffer + ESD 1 mA (datasheets: AP2112K Iq 55 µA; SN74AHCT1G125 ICC ≤ 10 µA); margem de projeto 30 % 23 mA (estimativa: 30 % sobre 76 mA). valores de datasheet, não medidos.
- Massa ≈ 20 g: estimativa do CAD do Pendente (volumes × densidades), sem cabo.
- Renders: conceituais, gerados a partir do CAD (KiCad → STL → Blender 4.2 Cycles). Não são fotos de protótipo. A carcaça, os materiais e o difusor não foram testados.
- Firmware da rev C e daemon desktop (Google Calendar OAuth, Microsoft Graph/Outlook OAuth, hooks Claude Code, notify Codex CLI, extensão browser para ChatGPT/Claude/Grok web sem API oficial) ainda não foram implementados; a compatibilidade HID parte do protocolo decodificado (0x01–0x04, 0x06, 0x80 testados no Flag; 0x05 e 0x07–0x0F inexistentes).
- **Aviso PRESTES A ENTRAR:** padrão 5 min antes do evento; configurável no app.
- **Trava OCUPADO (v1):** SALA = OCUPADO sempre envia 0xFF em vermelho #FF3B2F e suprime o LED 1 da IA; não configurável nesta versão.
- **Em aberto (a validar):** detecção dos limites de 5 h e semanal nas IAs (Claude, ChatGPT, Grok) e da extensão web (sem API oficial).
