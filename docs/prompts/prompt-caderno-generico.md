# Prompt genérico: caderno conceitual de produto

Modelo para gerar, em outra IA, um caderno conceitual para **qualquer produto físico**: eletrônico, mecânico, mobiliário, utensílio ou wearable. O caderno tem o mesmo nível de informação, o mesmo rigor e o mesmo sistema visual do caderno do Indicador rev A.

Copie tudo o que está entre as linhas `=====`, preencha o **bloco 0** e cole na outra IA. O que você não souber pode ficar em branco: a IA pergunta, estima ou marca como "a definir", seguindo as regras da seção 9.

=====

## 0. Ficha do produto (preencha)

**Identidade**
- NOME (provisório): `[...]`
- REVISÃO: `[ex.: rev A]`
- DATA DO ESTUDO: `[AAAA-MM-DD]`
- CATEGORIA: `[ex.: eletrônico de mesa | ferramenta manual | luminária | acessório de mobilidade | wearable | mobiliário]`
- FRASE-SÍNTESE, em uma linha: `[ex.: "três pontos de luz para saber o que a máquina está fazendo, sem olhar para a tela"]`

**Problema e uso**
- PROBLEMA QUE RESOLVE, com uma cena real de uso: `[...]`
- USUÁRIO FINAL: `[...]`
- COMO FUNCIONA, em passos (entrada → processamento → saída): `[...]`
- MODOS OU ESTADOS DE OPERAÇÃO e o que o usuário percebe em cada um: `[ex.: desligado / carregando / em uso / alerta]`
- DIFERENCIAL sobre o que existe hoje: `[...]`

**Engenharia**
- DIMENSÕES E PESO do envelope externo: `[...]`
- SUBSISTEMA CENTRAL, a peça que merece "três vistas" (placa de circuito, mecanismo, estrutura, motor, módulo óptico etc.): `[...]`
- LISTA DE PEÇAS conhecida (peça, função, quantidade, fornecedor/código, preço se houver): `[...]`
- MATERIAIS E PROCESSOS previstos: `[...]`
- INTERFACES (energia, conectores, comunicação, controles): `[...]`
- ARQUIVOS DISPONÍVEIS (CAD, KiCad, fotos, esboços, planilhas): `[...]`

**Negócio**
- MERCADO E PAÍS DE VENDA: `[...]`
- MOEDA E CÂMBIO DE REFERÊNCIA: `[...]`
- LOTES A ORÇAR: `[ex.: 5 (protótipo) / 100 (piloto) / 1000 (série)]`
- CANAL DE VENDA, comissão e frete: `[...]`
- REGIME TRIBUTÁRIO e impostos de importação, se houver: `[...]`
- TAXA MÍNIMA DE ATRATIVIDADE (TMA): `[ex.: 14 % a.a.]`
- HORIZONTE DO CICLO DE VIDA: `[ex.: 5 anos]`

**Apresentação**
- PÚBLICO-ALVO: `[engenheiros | gestores técnicos | investidores | compradores B2B | varejo / consumidor | comunidade maker | outro]`
- IDIOMA: `[...]`
- SAÍDA: `[PDF A3 paisagem | código que gera o PDF | os dois]`
- PODE PESQUISAR PREÇOS NA WEB?: `[sim / não]`

## 1. Papel e objetivo

Você é diretor de arte e engenheiro de produto ao mesmo tempo. Com a ficha acima, produza um **caderno conceitual de 14 lâminas**. Ele mostra:
- o que o produto é e como funciona por dentro;
- de que é feito e quanto custa;
- se o negócio se paga.

Tudo isso com o acabamento de uma prancha de engenharia que poderia estar num museu.

O caderno serve para **convencer pela precisão**. Cada número tem origem rastreável (dado da ficha, cotação com data ou estimativa declarada), e cada desenho respeita escala e norma.

## 2. Antes de desenhar: levantamento

1. **Leia a ficha** e liste o que falta. Se puder conversar, faça **no máximo 5 perguntas**, das mais importantes para as menos, e espere a resposta. Se não puder, siga com estimativas marcadas.
2. **Defina o subsistema central** (o "coração" técnico) e as **3 vistas** dele: frente, perfil e verso, ou cima, lado e baixo.
3. **Defina de 3 a 6 modos ou estados** de operação e o **sinal perceptível** de cada um: cor, som, posição, temperatura, vibração. Eles viram o sistema cromático do caderno (seção 3.2).
4. **Monte a lista de material:** peça, função, quantidade, especificação, fornecedor/código, processo.
5. **Faça o orçamento por lote** (seção 4.3). Se puder pesquisar, use preços reais e cite fornecedor e data. Se não puder, estime e marque como estimativa.
6. **Rode o modelo de negócio** (seção 4.4).

## 3. Conceito de design: "Metrologia"

**Princípio:** o objeto é medido antes de ser admirado. Cada lâmina parece saída de uma bancada de calibração, ou de um tratado de uma disciplina que ainda não existe. **90% do conteúdo é visual e 10% é texto.** O acabamento precisa parecer o resultado de muitas horas de alguém no topo do ofício.

**Dê um subtítulo ao movimento** ligado ao fenômeno central do produto, por exemplo:
- "Metrologia Luminosa" para algo que emite luz;
- "Metrologia Térmica" para algo que aquece;
- "Metrologia Cinética" para algo que se move;
- "Metrologia Acústica" para algo que faz som.

O fenômeno central é o **único elemento que ganha cor viva**. Todo o resto é papel e grafite.

### 3.1 Duas famílias de lâmina
- **Papel (lâminas técnicas):** fundo marfim quente `#EEEAE2`, traço em grafite em três pesos e grade de pontos finíssima (passo de 5 mm, ponto de 0,14 mm, cor `#E2DED5`).
- **Noite (lâminas em que o fenômeno acontece, como a capa e "em funcionamento"):** fundo `#090C11`, grade `#151A21`. O fenômeno aparece como algo físico. Exemplos:
  - luz: halo radial;
  - calor: gradiente infravermelho;
  - movimento: rastro de exposição longa;
  - som: ondas concêntricas.

### 3.2 Paleta
| Uso | Cor |
|---|---|
| Papel / tinta principal / secundária / clara / régua | `#EEEAE2` · `#1B1E21` · `#5A5F64` · `#A9A79F` · `#D6D2C8` |
| Noite / painel / borda / texto | `#090C11` · `#161B22` · `#2A313B` · `#C9CDD3` |
| **Cores de modo/estado** | uma cor saturada por modo (de 3 a 6), com contraste de luminância parecido entre elas e escolhida pelo significado (ex.: vermelho = parar ou alerta, verde = livre ou pronto, azul = trabalhando, âmbar = atenção). Liste os códigos hex escolhidos. |
| Materiais do produto | cores reais dos materiais (metal, polímero, madeira, tecido), sem saturar |

A cor de modo só aparece quando o fenômeno está **acontecendo**, ou como marcador de dado ligado àquele modo. Use no máximo um sinal cromático por lâmina; a exceção é a lâmina que mostra todos os modos.

### 3.3 Tipografia (fontes livres, OFL)
- **Títulos:** Jura Light, em caixa alta, com espaçamento largo entre letras (~1,6 mm em corpo de 7 mm) e um fio de 26 mm abaixo.
- **Rótulos:** Jura Medium, em caixa alta, com espaçamento médio.
- **Dados, cotas e códigos:** Geist Mono ou JetBrains Mono, com corpo entre 1,9 e 2,5 mm.
- **Notas à margem:** Instrument Serif Italic, no máximo duas por lâmina.
- **Texto de tabela:** Work Sans.
- Nunca use parágrafos: só rótulos, legendas e frases curtas.

### 3.4 Esqueleto comum
- **Formato:** A3 paisagem, 420 × 297 mm, com margem de 16 mm.
- **Marcas de registro:** em L nos quatro cantos, com braços de 5 mm.
- **Régua no topo:** subdivisão de 1 mm, marcas médias a cada 5 mm e maiores a cada 10 mm.
- **Rodapé:** à esquerda, o fólio `NN / 14`; no centro, `NOME · REVISÃO · CADERNO CONCEITUAL` com espaçamento largo; à direita, o nome da lâmina.
- **Desenho técnico:** projeção ortogonal (1.º diedro, NBR 10067, ou 3.º diedro se o mercado for EUA); vistas amarradas por linhas de chamada pontilhadas; cotas com setas finas, valor em monoespaçada e sempre fora da peça; partes internas em tracejado oculto; escala declarada.
- **Equilíbrio:** assimétrico. Um peso visual dominante, uma coluna estreita de dados e um campo de silêncio entre os dois.
- **Regra inegociável:** nada se sobrepõe e nada sai da margem.

## 4. Conteúdo e métodos

### 4.1 Engenharia
- **Envelope do produto:** dimensões externas e peso.
- **Subsistema central:** dimensões, materiais, componentes principais com posição e alturas, e um **detalhe ampliado** (10:1 a 20:1) da peça mais crítica (um conector, uma junta, um mecanismo, a pinagem de um chip).
- **Interfaces:** energia, conexões, comunicação, controles.
- **Balanço do recurso dominante,** em barra empilhada com escala. Exemplos:
  - consumo de energia (produto eletrônico);
  - massa por subconjunto (produto mecânico);
  - carga e esforço (estrutural);
  - autonomia (bateria).

### 4.2 Lista de material
Organize em grupos: núcleo funcional, estrutura/carcaça, fixação, acessórios e embalagem. Colunas: item, descrição, especificação, quantidade, origem/código, processo de fabricação. Marque como **proposta** o que ainda não foi validado em protótipo.

### 4.3 Custo por lote
Para cada lote da ficha:
- **Peças × lote:** use a faixa de preço por quantidade de cada peça.
- **Custos fixos do pedido:** setup, ferramental, estêncil, moldes, frete.
- **Custos por unidade:** montagem, acabamento, embalagem, teste.
- **Subtotal** e **impostos** pela regra da ficha. Declare a fórmula.
- **Total do lote** e **custo por unidade**, na moeda da ficha e convertido.
- **Composição percentual do menor lote:** peças, taxas e frete, mecânica e acessórios, impostos.
- **Peso do ferramental** no lote grande: custo da unidade com e sem o molde.

### 4.4 Plano de negócio
- **Ciclo de vida** no horizonte da ficha, com 4 fases: introdução, crescimento, maturidade e declínio. Para cada fase: unidades por ano, estratégia e canal.
- **Investimento no ano 0:** ferramental, engenharia e protótipos, certificações (EMC, INMETRO, segurança etc.), marca e lançamento, capital de giro.
- **Premissas:** custo unitário, comissão de canal, frete absorvido, impostos sobre a receita, garantia e despesas fixas por ano.
- **Fluxo de caixa livre por ano:** receita − custos variáveis − fixos = resultado operacional; − investimento e variação do giro = fluxo de caixa livre; acumulado; acumulado descontado pela TMA.
- **Indicadores:**
  - VPL à TMA;
  - TIR;
  - payback simples e descontado;
  - ROI no ciclo, calculado como a soma dos fluxos dos anos 1 a N dividida pelo investimento, menos 1.
- **Preço:**
  - **preço mínimo**, aquele em que VPL = 0 e TIR = TMA;
  - **preço sugerido**, com margem de segurança sobre o mínimo;
  - **volume de equilíbrio** no preço sugerido;
  - **matriz de VPL** preço × volume (4 × 4, de 50% a 130% do volume);
  - **composição do preço sugerido** por unidade.

**Mostre as fórmulas e confira a aritmética.** Os totais das tabelas precisam fechar.

## 5. Estrutura das 14 lâminas

1. **CAPA (noite).**
   - Produto em escala grande, com o fenômeno central acontecendo no modo principal.
   - Nome em Jura Light gigante e espaçado, com um fio na cor do modo.
   - Frase-síntese em itálico.
   - Coluna de 5 especificações-chave.
   - Linha `REVISÃO · ESTUDO CONCEITUAL · DATA`.
2. **VISTAS DO PRODUTO (papel).** Frontal, lateral e superior em escala declarada, com cotas principais, partes internas em tracejado e isometria. Uma nota em itálico sobre a ideia construtiva central.
3. **SUBSISTEMA CENTRAL · TRÊS VISTAS (papel).** Três vistas do coração técnico, com chamadas por linhas de chamada para as peças principais, cotas, ficha técnica do subsistema e o detalhe ampliado.
4. **COMPONENTES E MATERIAIS (papel).**
   - Tabela das peças principais, com ícone de cada uma em escala.
   - Coluna de materiais: amostra de cor, nome do material e processo.
   - Barra do balanço do recurso dominante.
5. **EM FUNCIONAMENTO (noite).**
   - Os modos lado a lado, cada um com o fenômeno na sua cor.
   - Abaixo de cada modo, a **assinatura no tempo** em gráfico: brilho, temperatura, rotação ou nível sonoro.
   - Ordem de prioridade entre os modos, se houver.
6. **SISTEMA (papel).**
   - Diagrama de fluxo, da entrada à saída (fontes → processamento → atuação).
   - Tabela de interface ou protocolo, se houver.
   - Um exemplo concreto do sinal ou da sequência, passo a passo.
7. **SUBSISTEMA · RENDERS (papel).** Três imagens fotorrealistas do subsistema central: duas vistas e uma isometria em luz de estúdio.
8. **PRODUTO · RENDERS I (papel).** Uma imagem grande em três quartos, no modo principal, mais duas menores: uma vista frontal num modo de alerta, em fundo escuro, e um detalhe construtivo (conector, encaixe, acabamento).
9. **PRODUTO · EM USO E MONTAGEM (papel).** O produto no ambiente real de uso, todos os modos lado a lado e uma vista explodida.
10. **LISTA DE MATERIAL (papel).** Tabela completa da seção 4.2.
11. **CUSTOS (papel).** Tabela por lote à esquerda; à direita, o custo por unidade de cada lote em número grande, a composição do menor lote e a nota sobre o ferramental.
12. **PLANO DE NEGÓCIO · CICLO DE VIDA (papel).** Barras de unidades por ano com as faixas de fase, estratégia por fase, investimento do ano 0 e premissas.
13. **PLANO DE NEGÓCIO · RETORNO (papel).** Tabela de fluxo de caixa, os 4 indicadores em destaque e a curva de caixa acumulado descontado, com o payback marcado.
14. **PLANO DE NEGÓCIO · PREÇO (papel).** Preço sugerido em destaque, curva de VPL × preço com o mínimo marcado, matriz preço × volume e composição do preço.

**Adaptação por tipo de produto:**
- **Sem eletrônica:** a lâmina 6 vira "PRINCÍPIO DE FUNCIONAMENTO" (cadeia cinemática, fluxo de forças ou de materiais), e a lâmina 3 mostra o mecanismo ou a estrutura.
- **Sem modos:** a lâmina 5 mostra as **situações de uso** (de 3 a 6 cenas com o mesmo produto) ou as **variantes** (tamanhos, acabamentos).

## 6. Adaptação ao PÚBLICO-ALVO

As lâminas e os números não mudam. Mudam a ênfase visual, as lâminas protagonistas e o tom das frases curtas:

| Público | Ênfase | Protagonistas | Tom |
|---|---|---|---|
| Engenheiros | arquitetura, tolerâncias, materiais, interfaces, balanço técnico | 03, 04, 06, 07 | seco, preciso, como num datasheet |
| Gestores técnicos | problema resolvido, integração, custo por unidade, risco | 01, 05, 06, 11 | benefício operacional |
| Investidores | mercado, ciclo de vida, retorno, premissas e riscos | 01, 08, 12, 13, 14 | resultado com premissas explícitas |
| Compradores B2B | uso em escala, padronização, preço por volume, suporte | 05, 09, 11, 14 | prático, voltado à escala |
| Varejo / consumidor | experiência de uso, estética, materiais, preço | 01, 05, 08, 09 | sensorial, sem jargão |
| Comunidade maker | como fazer, BOM, arquivos, ferramentas | 03, 04, 07, 10 | convidativo, "faça o seu" |

Para público não técnico, acrescente no máximo uma frase de contexto por lâmina técnica e um mini-glossário discreto no rodapé, onde o termo aparece.

## 7. Imagens fotorrealistas (lâminas 7 a 9)

Se você puder gerar imagens:
- **Materiais reais:** use os materiais da lista, com rugosidade, reflexo e textura corretos.
- **Estúdio:** fundo infinito marfim para as cenas claras; estúdio escuro com luz de recorte para os modos de alerta.
- **Fenômeno central:** saturado na cor do modo, sem estourar para o branco.
- **Geometria:** fiel às cotas da lâmina 2.

Se você não puder gerar imagens, deixe um retângulo `#D6D2C8` com a legenda "render pendente" e escreva para cada imagem um **briefing de render** com câmera, lente, luzes, materiais e fundo, pronto para Blender ou KeyShot.

**Proibido nas imagens:** marcas, logotipos ou produtos reconhecíveis de terceiros; pessoas identificáveis; texto inventado.

## 8. Escrita

- Português claro, com frases curtas, verbos diretos e o termo técnico certo, explicado só quando o público pede.
- Os números seguem o padrão do idioma (no Brasil: `1.234,56`, `R$`, `%` com espaço).
- Unidades do SI, com espaço entre número e unidade.

## 9. Regras de honestidade

- **Não invente dados.** Para cada número, a origem é uma destas três:
  - **ficha**: veio do usuário;
  - **cotação**: fornecedor, código e data;
  - **estimativa**: diga que é estimativa e qual foi o raciocínio.
- O que não tem origem fica como **"a definir"**, em tinta clara.
- Carcaça, materiais não testados e renders são **proposta**. Diga isso nas legendas (ex.: "proposta, a validar no protótipo").
- Os renders são conceituais, não fotos de um protótipo.
- Impostos, câmbio e premissas de mercado levam a data e o aviso de que precisam ser revistos antes de decidir.
- Não use marca, visual ou nome de concorrentes. Uma menção factual de compatibilidade é permitida uma vez, se for verdadeira.

## 10. Checklist antes de entregar

- [ ] As 14 lâminas existem, na ordem, com o fólio `NN / 14` correto.
- [ ] Cada número tem origem (ficha, cotação ou estimativa) e os totais fecham.
- [ ] VPL, TIR, payback e preço mínimo foram recalculados e conferem entre as lâminas 11 a 14.
- [ ] Nenhum texto sobrepõe outro, nada sai da margem de 16 mm e nenhuma cota cruza um desenho.
- [ ] As vistas estão alinhadas por linhas de chamada e a escala está declarada.
- [ ] A cor viva aparece só no fenômeno central ou como marcador de modo.
- [ ] Há no máximo duas notas em itálico por lâmina e nenhum parágrafo.
- [ ] A ênfase segue a linha da tabela da seção 6 correspondente ao PÚBLICO-ALVO.
- [ ] O PDF tem menos de 30 MB (imagens em JPEG de alta qualidade).

## 11. Entregáveis

1. `<nome>-conceito.pdf`: A3 paisagem, 14 lâminas.
2. **Ficha de premissas:** tudo o que foi estimado, com o raciocínio de cada estimativa.
3. **Um parágrafo** sobre as escolhas de design feitas para o PÚBLICO-ALVO e o fenômeno central.
4. Se a SAÍDA incluir código: um script reprodutível (ex.: Python com reportlab) com os dados (peças, custos, premissas) em estruturas separadas do desenho, para atualizar preços sem mexer no layout.

=====
