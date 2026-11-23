# Gerador do caderno de engenharia · SIGNA

Desenha o caderno de engenharia (A3 paisagem, sistema visual **Metrologia Luminosa**), continuação do caderno conceitual em [`docs/caderno-signa/`](../../caderno-signa/). O público é engenharia: hardware, firmware, mecânica, manufatura e teste. O que as fontes não fecham entra como « a definir ».

O PDF único sai em `signa-engenharia.pdf`, nesta pasta, e não é versionado (cerca de 39 MB). As três partes publicadas e o mapa de seções estão em [`../README.md`](../README.md).

## Como regenerar

```bash
python3 prep_imagens.py && python3 caderno.py
python3 preview.py 110
```

`prep_imagens.py` regrava `img/jpg/` a partir das pastas de origem. `caderno.py` desenha o PDF e atualiza `verificacao.json`. `preview.py` grava um PNG por lâmina em `preview/` (essa pasta também não entra no git; as quatro amostras versionadas ficam em `../preview/`).

## De onde vêm os dados

`dados.py` e `prep_imagens.py` não exigem um checkout em `/workspace`. Cada fonte é, nesta ordem:

1. a variável de ambiente, se estiver definida;
2. a pasta equivalente neste repositório, se existir;
3. o caminho antigo em `/workspace`, só quando as duas anteriores não resolvem.

| Variável | Neste repositório | Reserva |
|---|---|---|
| `SIGNA_REVD` | `hardware/revD` | `/workspace/luxpcb-revD` |
| `SIGNA_SW` | `software` | `/workspace/signa-sw` |
| `SIGNA_MECH` | `mecanica` | `/workspace/signa-3d` |
| `SIGNA_CONC` | `docs/caderno-signa`, ou `.old/docs/conceito` se o caderno atual não estiver na árvore | `/workspace/caderno-revC` |

O caderno conceitual entra por `SIGNA_CONC` (dados e JPEG da lâmina de estados). Não há dependência fixa de uma pasta `caderno-revC`.

Os passos de montagem (`passo1`–`passo5`) ainda são lidos de `/workspace/pendente/renders` e são pulados se a pasta não existir. Os JPEG já preparados em `img/jpg/` cobrem esse caso.

Fontes (OFL, as mesmas do caderno conceitual): Jura, Geist Mono, Work Sans e Instrument Serif, em `fontes/`.

Requisitos: Python 3, reportlab, fontTools, pymupdf, Pillow e numpy.
