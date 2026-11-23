# Prompt genérico: caderno de engenharia de produto

## Papel
Você é um time de engenharia de produto sênior (hardware, firmware, mecânica, manufatura, qualidade e gestão de produto). Vai escrever o CADERNO DE ENGENHARIA de [NOME DO PRODUTO]. Ele é a continuação técnica do conceito do produto: o leitor é o engenheiro e o fabricante, não o investidor. Este prompt é autossuficiente. Tudo o que você precisa saber sobre o produto está na seção "Entradas", escrita em texto, e todo o visual está definido na seção "Sistema visual". Não dependa de nenhum anexo, PDF anterior ou arquivo externo para entender o pedido.

## Objetivo
Gerar um PDF completo, sem limite de páginas, que permita a um terceiro FABRICAR, MONTAR, TESTAR, GRAVAR, OPERAR e MANTER o produto sem precisar perguntar nada. Tudo o que o caderno afirmar deve ter fonte nas Entradas ou nos arquivos do projeto que você tiver de fato à mão; o que não tiver fonte vira "A DEFINIR".

## Entradas (preencher em texto, dentro deste prompt)
Escreva cada item por extenso: valores, medidas, listas e decisões. Caminhos de arquivo e links são opcionais, servem só como origem citada; o caderno tem que ser possível só com o texto abaixo. Item deixado em branco vira "A DEFINIR".
- Produto: [nome provisório, status da marca no INPI]
- Conceito resumido: [o que faz, para quem, problema que resolve, modos de uso, diferenciais]
- Estados e comportamento: [cada estado com prioridade, cor em HEX, brilho, animação e temporização]
- Decisões já tomadas: [data, decisão, motivo]
- Decisões em aberto: [pergunta, opções, recomendação]
- Eletrônica: [MCU e componentes principais com part number, alimentação, pinagem, dimensões da placa, camadas, BOM com preços e data, resultados de ERC/DRC; opcional: caminho do projeto KiCad, gerbers, renders]
- Mecânica: [lista de peças com material, processo, cor e medidas principais, folgas críticas, itens comprados com especificação; opcional: caminho do STEP/CAD, desenhos, renders]
- Software/firmware: [arquitetura, protocolo com layout de bytes, VID:PID, memória, atualização, testes existentes]
- Engenharia reversa/referência: [produto de referência, protocolo descoberto, medições feitas]
- Negócio: [público, premissas, custos por lote, preço-alvo, metas, cronograma]
- Repositório: [URL, opcional]

## Regras
1. Não invente números. Valor sem fonte aparece como "A DEFINIR" e vai para a lista de pendências, com responsável e próximo passo.
2. Cada número traz unidade, tolerância e origem (datasheet, medição, simulação, CAD, cotação com data).
3. Cada figura vem de um arquivo real do projeto (render, desenho, captura) ou é desenhada por você a partir dos dados das Entradas (diagrama de blocos, tabela de estados, cotas). Figura sem dado de origem não entra; no lugar dela fica um quadro "FIGURA A DEFINIR" com o que falta. Toda figura tem legenda numerada e referência no texto.
4. Escreva em pt-BR técnico. Termos em inglês só quando forem padrão da indústria, e explicados na primeira vez em que aparecem.
5. Formato: A3 paisagem, seguindo a seção "Sistema visual" abaixo. Cabeçalho com produto, revisão e data; rodapé com página e total; sumário com páginas; controle de revisões.
6. Separe com clareza o que está VALIDADO (medido ou testado), o que está PROJETADO (CAD ou simulação) e o que é HIPÓTESE.
7. Itens de certificação (EMC, segurança, RoHS e outros) entram como "considerações e plano", nunca como certificação obtida.
8. Antes de entregar, renderize páginas de amostra de todas as seções (pelo menos 15, incluindo sumário, tabelas, desenhos e anexos) e confira texto estourado, cortado ou fora da página, sobreposição, imagens distorcidas, acentuação e tamanho de fonte abaixo do mínimo.

## Sistema visual (obrigatório, sem depender de arquivo de referência)
Estilo "Metrologia Luminosa": papel técnico claro, régua milimétrica, muito respiro, tipografia fina e precisa, como uma prancha de instrumento de medição.

**Página**
- A3 paisagem, 420 × 297 mm, margem de 16 mm em todos os lados.
- Fundo papel #EEEAE2, com grade de pontos de 0,07 mm de raio a cada 5 mm, cor #E2DED5.
- Marcas de registro em L nos 4 cantos, fora da margem, com braços de 5 mm, cor #A9A79F.
- Régua no topo, dentro da margem: traço a cada 1 mm, maior a cada 5 mm e maior ainda a cada 10 mm, com números a cada 50 mm. Linha na cor #5A5F64.
- Rodapé numa linha só, acima de um fio #D6D2C8: "NN / total" à esquerda, "[PRODUTO] · CADERNO DE ENGENHARIA · REV. X" no centro e o nome da lâmina à direita. Os três textos nunca colidem; se faltar espaço, o nome da lâmina é abreviado com reticências.
- Título da lâmina em caixa alta, com espaçamento largo entre letras, sublinhado por um traço curto. À direita, o rótulo "METROLOGIA LUMINOSA" em caixa alta pequena, cor secundária.

**Cores**
- Tinta (texto principal) #1B1E21, texto secundário #5A5F64, texto claro #A9A79F.
- Fios e réguas #D6D2C8, grade #E2DED5.
- Lâminas escuras (capa, divisórias de seção, renders de produto aceso): fundo #090C11, painel #161B22, borda #2A313B, texto #C9CDD3, grade #151A21.
- Cores de estado do produto só aparecem quando representam o estado, sempre com o HEX ao lado.

**Fontes (todas livres, Google Fonts)**
- Jura Light: títulos de lâmina. Jura Medium: rótulos, rodapé, capa e cabeçalhos de tabela.
- Work Sans Regular e Medium: texto corrido, tabelas descritivas e legendas.
- Geist Mono Regular e Medium: números, códigos, HEX, bytes, part numbers, comandos e a régua.
- Instrument Serif Italic: só para citações ou destaques pontuais.
- Confira se cada caractere usado (acentos, ×, ±, Ø, °, µ, →) existe na fonte escolhida; se não existir, troque o caractere ou a fonte daquele trecho.

**Tabelas**
- Sem bordas verticais. Fio grosso abaixo do cabeçalho e fios finos #D6D2C8 entre as linhas.
- Cabeçalho em caixa alta, cor secundária. Números alinhados à direita em fonte mono.

**Capa**
- Lâmina escura com o nome do produto grande, o subtítulo "CADERNO DE ENGENHARIA · METROLOGIA LUMINOSA", a revisão, a data e uma imagem do produto, se houver.

## Tipografia e legibilidade (obrigatório)
O caderno precisa ser lido na tela, em parte da tela, sem zoom. Os valores abaixo são os usados no caderno aprovado, em A3 paisagem (420 × 297 mm). O corpo da fonte é dado em pt e em mm (1 mm = 2,835 pt). "Espaçamento" é o espaço extra entre letras (tracking), em mm. "Entrelinha" é a distância entre linhas de base. Use exatamente estes valores; eles são também o mínimo permitido.

**Arquivos de fonte** (Google Fonts, licença livre; incorpore no PDF): `Jura-Light.ttf`, `Jura-Medium.ttf`, `WorkSans-Regular.ttf`, `WorkSans-Medium.ttf`, `GeistMono-Regular.ttf`, `GeistMono-Medium.ttf`, `InstrumentSerif-Italic.ttf`. Não use negrito sintético nem itálico sintético; o peso vem do arquivo.

**Cores de texto:** tinta #1B1E21 (principal), secundária #5A5F64, clara #A9A79F. Em lâmina escura, todo texto usa #C9CDD3 e a régua usa #2A313B.

### Texto da lâmina

| Elemento | Fonte e peso | Corpo | Espaçamento | Entrelinha e espaços | Caixa | Cor |
|---|---|---|---|---|---|---|
| Título da lâmina (1 linha) | Jura Light | 32,6 pt (11,5 mm) | 0,9 mm | linha de base a 38,5 mm do topo da folha | ALTA | tinta |
| Título longo, 1 linha | Jura Light | 28,3 pt (10,0 mm) | 0,4 mm | idem | ALTA | tinta |
| Título longo, 2 linhas | Jura Light | 28,9 pt (10,2 mm) | 0,4 mm | 13 mm entre as linhas | ALTA | tinta |
| Rótulo à direita do título ("METROLOGIA LUMINOSA") | Jura Medium | 19,6 pt (6,9 mm) | 0,6 mm | alinhado à direita, na linha do título | ALTA | secundária |
| Sufixo de continuação | igual ao título | igual | igual | " (cont.)" no fim do título | ALTA | tinta |
| Rótulo de seção (subtítulo dentro da lâmina) | Jura Medium | 19,8 pt (7,0 mm) | 0,45 mm | 4,5 mm + 1,35 × corpo até o conteúdo; exige 30 mm livres abaixo, senão vai para a próxima lâmina | ALTA | tinta |
| Texto corrido | Work Sans Regular | 19,8 pt (7,0 mm) | 0 | entrelinha 1,42 × corpo (9,9 mm); 12,5 mm de linha de base a linha de base entre parágrafos | normal | tinta |
| Destaque dentro do texto | Work Sans Medium | igual ao texto | 0 | igual | normal | tinta |
| Nota de destaque | Instrument Serif Italic | 30,6 pt (10,8 mm) | 0 | 1 a 2 linhas | normal | secundária |

### Tabelas e blocos

| Elemento | Fonte e peso | Corpo | Espaçamento | Entrelinha e espaços | Caixa | Cor |
|---|---|---|---|---|---|---|
| Cabeçalho de tabela | Jura Medium | 16,6 pt (5,85 mm) | 0,25 mm (0,2 mm se quebrar em 2 linhas) | repetido em toda continuação | ALTA | secundária |
| Célula de texto | Work Sans Regular | 18,3 pt (6,45 mm) | 0 | altura mínima da linha 11,5 mm; quebra dentro da célula | normal | tinta |
| Célula numérica, código, HEX, byte, part number | Geist Mono Regular | 18,3 pt (6,45 mm) | 0 | alinhada à direita quando for número | normal | tinta |
| Linha de total ou destaque | Work Sans Medium ou Geist Mono Medium | 18,3 pt (6,45 mm) | 0 | igual | normal | tinta |
| Lista chave e valor: chave | Work Sans Regular | 18,4 pt (6,5 mm) | 0 | coluna da chave com 72 a 78 mm; fio fino entre itens | normal | secundária |
| Lista chave e valor: valor | Geist Mono Regular (dados) ou Work Sans Regular (frases) | 18,4 pt (6,5 mm) | 0 | quebra dentro da coluna | normal | tinta |
| Texto em bloco de diagrama | Work Sans Regular | 17,4 pt (6,15 mm) | 0 | entrelinha 1,35 × corpo; centralizado | normal | tinta |
| Título de bloco de diagrama | Jura Medium | 16,2 pt (5,7 mm) | 0,35 mm | centralizado, 8,5 mm abaixo do topo do bloco | ALTA | secundária |
| Título de caixa | Jura Medium | 17,9 pt (6,3 mm) | 0,45 mm | 3 mm da borda esquerda | ALTA | tinta |
| Listagem de código ou comando | Geist Mono Regular | 18,1 pt (6,4 mm) | 0 | 9,5 mm por linha, recuo de 4 mm | normal | tinta |

### Figuras e desenhos

| Elemento | Fonte e peso | Corpo | Espaçamento | Entrelinha e espaços | Caixa | Cor |
|---|---|---|---|---|---|---|
| Legenda de figura | Geist Mono Regular | 16,7 pt (5,9 mm) | 0 | entrelinha 1,36 × corpo; formato "Fig. N — texto" | normal | secundária |
| Chamada (rótulo com linha guia) | Jura Medium | 18,7 pt (6,6 mm) | 0,4 mm | sub-rótulo opcional logo abaixo | ALTA | tinta |
| Sub-rótulo da chamada | Geist Mono Regular | 16,2 pt (5,7 mm) | 0 | 1,6 mm abaixo da chamada | normal | secundária |
| Cota (número de medida) | Geist Mono Regular | 17,9 pt (6,3 mm) | 0 | centrada na linha de cota; vertical gira 90° | normal | tinta |

### Moldura da lâmina

| Elemento | Fonte e peso | Corpo | Espaçamento | Posição | Caixa | Cor |
|---|---|---|---|---|---|---|
| Número da página | Geist Mono Regular | 19,6 pt (6,9 mm) | 0 | à esquerda, linha de base 1,8 mm acima da margem inferior; formato "NN / total" | — | tinta |
| Rodapé central | Jura Medium | 19,6 pt (6,9 mm) | 0,45 mm (0 se faltar espaço) | centro; "[PRODUTO] · CADERNO DE ENGENHARIA · REV. X" | ALTA | secundária |
| Nome da lâmina no rodapé | Jura Medium | 19,6 pt (6,9 mm) | 0,35 mm (0 se faltar espaço) | à direita; abrevia com "…" se colidir | ALTA | tinta |
| Fio acima do rodapé | — | — | — | 9 mm acima da margem, 0,14 mm de espessura | — | #D6D2C8 |
| Nota de fonte (origem dos dados) | Geist Mono Regular | 16,4 pt (5,8 mm) | 0 | entrelinha 1,34 × corpo; largura total; última linha 11,5 mm acima da margem; começa com "Fonte:" | normal | secundária |
| Números da régua | Geist Mono Regular | 16,2 pt (5,7 mm) | 0 | a cada 50 mm, 7,1 mm abaixo da linha da régua | — | clara |
| Traços da régua | — | — | — | 0,8 mm a cada 1 mm, 1,6 mm a cada 5 mm, 2,6 mm a cada 10 mm | — | secundária |

### Capa e divisórias de seção (lâminas escuras, texto #C9CDD3)

| Elemento | Fonte e peso | Corpo | Espaçamento | Entrelinha e espaços | Caixa | Cor |
|---|---|---|---|---|---|---|
| Nome do produto na capa | Jura Light | 70,9 pt (25 mm), reduzido de 0,5 em 0,5 mm até caber em 208 mm | 4,5 mm | linha de base a 87 mm do topo | como a marca | #C9CDD3 |
| Subtítulo da capa | Jura Medium | 20,4 pt (7,2 mm) | 0 | entrelinha 9,6 mm; "CADERNO DE ENGENHARIA · METROLOGIA LUMINOSA" | ALTA | #C9CDD3 |
| Número da seção na divisória | Jura Light | 79,4 pt (28 mm) | 5,0 mm | algarismos romanos | ALTA | #C9CDD3 |
| Título da seção na divisória | Jura Light | 51,0 pt (18 mm) | 1,4 mm | seguido de uma barra de 60 × 1 mm na cor de destaque do produto | normal | #C9CDD3 |
| Texto de abertura da divisória | Work Sans Regular | 23,0 pt (8,1 mm) | 0 | entrelinha 11,6 mm; 13,5 mm entre parágrafos | normal | #C9CDD3 |
| Identificação do documento | Jura Medium | 19,6 pt (6,9 mm) | 0,6 mm | "ID · REV. X · data", 31,5 mm acima da borda inferior | ALTA | #C9CDD3 |

Regras:
1. Nunca reduza a fonte para caber (as únicas exceções são o título longo e o nome na capa, nos limites das tabelas acima). Se não couber, continue na lâmina seguinte com o mesmo título seguido de "(cont.)". O número de páginas pode crescer à vontade.
2. Tabela que continua repete o cabeçalho na lâmina seguinte. Células longas quebram linha dentro da célula, e tabelas muito largas se dividem em colunas.
3. Parágrafos curtos (até 7 linhas) não se dividem entre lâminas.
4. O título não pode encostar no rótulo do cabeçalho; se faltar espaço, ele quebra em 2 linhas.
5. Anotações dentro de figuras seguem a mesma escala. A figura continua legível e sem distorção.
6. Gere o sumário e o rodapé "N / total" em duas passadas, para que os números de página saiam corretos depois do refluxo.
7. Use as fontes da seção "Sistema visual"; os tamanhos destas tabelas valem para todas as lâminas.
8. Se o PDF passar do limite de anexo (por exemplo, 25 MB), entregue também partes menores separadas no início de uma seção.

## Sumário obrigatório (expanda o quanto precisar)
0. Capa, controle de revisões, mapa do documento, glossário de siglas
1. Visão geral do sistema
   - Recapitulação do conceito (uma lâmina, escrita a partir das Entradas)
   - Diagrama de blocos (hardware, firmware, app, nuvem e integrações)
   - Modos de operação e tabela de estados (prioridade, cor em HEX, comportamento, temporização)
2. Requisitos e especificações
   - Requisitos funcionais e não funcionais, numerados (REQ-xxx), com rastreabilidade até teste
   - Especificações elétricas, ópticas, mecânicas, ambientais e de interface (USB e outras)
   - Restrições normativas e de acessibilidade (por exemplo, fotossensibilidade WCAG < 3 Hz)
3. Eletrônica
   - Esquemático completo (todas as folhas) e explicação por bloco
   - Pinagem do MCU (pino, função, net, observações); árvore de alimentação e orçamento de consumo por estado
   - Temporização de sinais críticos (barramentos, LEDs endereçáveis), ESD e proteções
   - Componentes críticos e alternativas (second source), com estoque e preço datados
   - Layout: dimensões, stackup, regras de projeto, posicionamento, pontos de teste
   - Resultados de ERC e DRC; saídas de fabricação (Gerber, furação, BOM, CPL) e parâmetros do pedido
   - Painelização e restrições de separação
4. Mecânica
   - Lista de peças (Pxx) com material, processo, acabamento, cor, massa e fornecedor-alvo
   - Desenho técnico de cada peça (cotas, tolerâncias, GD&T quando couber)
   - Tabela de folgas e interferências (nominal e pior caso), com a interferência intencional destacada
   - Especificação de itens comprados (cabos, conectores, parafusos), com os limites dimensionais exigidos do fornecedor
   - Montagem integrada: 3D, vista explodida, cortes e detalhes
5. Instruções de montagem
   - Sequência passo a passo com figura em cada etapa, ferramentas, gabaritos, torque e força de prensa
   - Pontos de inspeção dentro da linha e erros comuns (poka-yoke)
6. Firmware
   - Arquitetura, máquina de estados e resolução de prioridades
   - Descritores USB (VID:PID, classe), protocolo completo com layout de bytes, respostas, erros e temporização
   - Memória não volátil, atualização de firmware (DFU/bootloader) e option bytes de produção
   - Build, gravação e verificação (ferramentas, comandos, versões)
   - Estratégia de testes (unitários, em host, hardware-in-the-loop)
7. Software e app
   - Arquitetura, integrações (APIs, autenticação, permissões), configuração e privacidade de dados
   - Instalação, atualização, logs e diagnóstico
8. Manual de operação (usuário final)
   - Instalação física, primeiro uso, significado de cada estado, botões, configuração
   - Solução de problemas (sintoma, causa provável, ação), cuidados e limpeza
9. Teste de produção e qualidade
   - Procedimento de teste final (fixture, pontos de teste, sequência, critérios de passa e falha)
   - Plano de inspeção de recebimento, critérios de aceitação (AQL) e rastreabilidade (número de série, lote)
   - Plano de validação (DVT/PVT): ensaios térmicos, de queda, de tração no cabo, ESD e vida útil
10. Conformidade e segurança: considerações e plano (EMC, segurança elétrica, RoHS/REACH, USB-IF, acessibilidade, marcações e etiquetas)
11. Gestão de produto
    - Status por disciplina (EVT, DVT, PVT, MP) e marcos com datas
    - Custos: BOM por lote, montagem, embalagem, frete, impostos, delta entre revisões
    - Cadeia de suprimentos: fornecedores, lead time, MOQ, riscos de estoque e alternativas
    - Matriz de riscos (probabilidade × impacto, mitigação, dono)
    - Decisões em aberto (pergunta, opções, recomendação, impacto, prazo)
    - Registro de decisões já tomadas (data, decisão, motivo)
    - Gestão de mudanças: revisões (A, B, C, D…) e o que mudou em cada uma
    - Roadmap da próxima revisão
12. Embalagem, etiquetagem e logística (desenho da embalagem, conteúdo da caixa, etiquetas, códigos)
13. Anexos: BOM completa, CPL, relatórios ERC/DRC, relatório de folgas, logs de teste, datasheets referenciados, mapa do repositório, prompt e fontes usadas

## Entregáveis
- PDF final: [caminho/nome-engenharia.pdf]
- Scripts geradores versionados, para regenerar o caderno a cada revisão
- Prévias PNG das páginas representativas
- Relatório final com número de páginas, tamanho, seções com intervalos de páginas, tamanhos de fonte usados (em pt) e a lista de "A DEFINIR"
- Partes do PDF abaixo do limite de anexo, quando o arquivo inteiro passar dele
