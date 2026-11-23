# Caderno de engenharia · SIGNA

141 lâminas em A3 paisagem (420 × 297 mm), no sistema visual **Metrologia Luminosa**. O texto corrido é Work Sans Regular, 19,8 pt. O leitor é quem vai fabricar, montar, gravar, testar e operar o SIGNA: hardware, firmware, mecânica, manufatura e teste. O caderno continua o [caderno conceitual](../caderno-signa/signa-conceito.pdf) (14 lâminas, o mesmo sistema visual).

Nada aqui foi medido em silício. O que as fontes do projeto não fecham aparece como **« a definir »** e entra na lista de pendências.

## As três partes

O PDF único, `signa-engenharia.pdf` (cerca de 39 MB), não entra no repositório. Ele é reconstruído pelo gerador. O que está versionado são as três partes, com a numeração do caderno inteiro:

| Arquivo | Páginas | Conteúdo |
|---|---|---|
| [signa-engenharia-parte1.pdf](signa-engenharia-parte1.pdf) | 1–53 | Capa, controle do documento, sumário, I Sistema, II Eletrônica |
| [signa-engenharia-parte2.pdf](signa-engenharia-parte2.pdf) | 54–98 | III Mecânica, IV Firmware |
| [signa-engenharia-parte3.pdf](signa-engenharia-parte3.pdf) | 99–141 | V Aplicativo, VI Operação e teste, VII Conformidade, custo e riscos, VIII Apêndices, colofão |

| Seção | Páginas |
|---|---|
| Capa, controle e sumário | 1–8 |
| I Sistema | 9–25 |
| II Eletrônica | 26–53 |
| III Mecânica | 54–80 |
| IV Firmware | 81–98 |
| V Aplicativo | 99–108 |
| VI Operação e teste | 109–117 |
| VII Conformidade, custo e riscos | 118–128 |
| VIII Apêndices | 129–140 |
| Colofão | 141 |

Quatro amostras das lâminas estão em [`preview/`](preview/): 1 (capa), 4 (sumário), 22 (escada de prioridade) e 82 (firmware). As outras `preview/lamina_*.png` ficam de fora do git.

## Como reconstruir o PDF único

Na pasta [`gerador/`](gerador/):

```bash
python3 prep_imagens.py && python3 caderno.py
```

`prep_imagens.py` prepara os JPEG em `gerador/img/jpg/`. `caderno.py` desenha `gerador/signa-engenharia.pdf` e grava `gerador/verificacao.json`. Para PNG de conferência: `python3 preview.py 110`.

As fontes de engenharia não estão presas a um caminho. `dados.py` e `prep_imagens.py` leem, nesta ordem, a variável de ambiente, a pasta equivalente neste repositório e, por último, o caminho antigo em `/workspace`:

| Variável | Neste repositório | Reserva |
|---|---|---|
| `SIGNA_REVD` | `hardware/revD` | `/workspace/luxpcb-revD` |
| `SIGNA_SW` | `software` | `/workspace/signa-sw` |
| `SIGNA_MECH` | `mecanica` | `/workspace/signa-3d` |
| `SIGNA_CONC` | `docs/caderno-signa` (se essa pasta não existir, `.old/docs/conceito`) | `/workspace/caderno-revC` |

Os renders dos passos de montagem (`passo1`–`passo5`) continuam em `/workspace/pendente/renders`. Se a pasta não estiver lá, o script deixa os JPEG que já estão em `gerador/img/jpg/`.

Requisitos: Python 3, reportlab, fontTools, pymupdf, Pillow e numpy. As fontes (OFL: Jura, Geist Mono, Work Sans, Instrument Serif) estão em [`gerador/fontes/`](gerador/fontes/).

O prompt para gerar um caderno deste tipo para outro produto está em [`docs/prompts/prompt-caderno-engenharia.md`](../prompts/prompt-caderno-engenharia.md).
