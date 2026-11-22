# Caderno conceitual · SIGNA rev C (nome provisório · a verificar no INPI)

Caderno de 14 lâminas A3 paisagem, sistema visual "Metrologia Luminosa", para **investidores**.

## Entregáveis
| arquivo | o que é |
|---|---|
| `signa-conceito.pdf` | o caderno (14 lâminas, A3 paisagem) |
| `premissas.md` | ficha de premissas: tudo o que foi estimado, com o raciocínio; cotações com fonte e data |
| `escolhas_design.md` | escolhas de design e justificativa do sistema de estados (SALA + IA) |
| `preview/lamina_NN.png` | prévias das lâminas |
| `verificacao.json` | saída da verificação automática (sobreposição, margem, glifos, itálicos) |

## Trocar o nome do produto
O nome fica em uma única variável: `"nome"` em `dados/produto.json` (hoje `"SIGNA"`; nome provisório, a verificar no INPI). Alterar esse campo e rodar `python3 gera_premissas.py && python3 caderno.py && python3 preview.py 110` atualiza capa, rodapé de todas as lâminas, ficha de premissas e o nome do arquivo `<nome>-conceito.pdf`.

## Como regenerar (dados separados do desenho)
```bash
python3 modelo.py          # dados/*.json -> dados/resultados.json (custos, fluxo, VPL, TIR, payback, preço mínimo)
python3 gera_premissas.py  # premissas.md a partir dos mesmos dados
python3 prep_imagens.py    # img/*.png -> img/jpg/*.jpg (halo, composição sobre papel/noite)
python3 caderno.py         # desenha o PDF e roda a verificação
python3 preview.py 110     # PNG das lâminas
```
Para atualizar preços, edite só `dados/custos.json`, `dados/negocio.json` ou `dados/jlc_precos_2026-11-22.json` e rode de novo: o layout (`caderno.py`, `lib_metrologia.py`) não muda.

- `dados/produto.json`: identidade (`nome`), modos SALA e IA, alocação dos 3 LEDs, especificações
- `dados/bom.json`: lista de material por grupo, com status Q/E/P
- `dados/custos.json`: câmbio, faixas de preço, custos fixos e por unidade, regras de importação
- `dados/negocio.json`: volumes, fases, canal, impostos (Simples Anexo II), investimentos, riscos
- `dados/energia.json`: balanço de consumo
- `dados/placa.json`: geometria da placa extraída do KiCad (`extrai_placa.py`)
- `render/`: cenas Blender (`scenes.py`). A geometria do Pendente usada nos renders estava em `/workspace/pendente/export` (fora deste repositório); o conjunto atual está em `mecanica/`. Os PNG/JPG e o PDF já gerados estão versionados aqui

Requisitos: Python 3, reportlab, fonttools, pymupdf, Pillow, numpy; Blender 4.2 (renders); KiCad 9 (só para `extrai_placa.py`).
Fontes (OFL, Google Fonts): Jura, Geist Mono, Work Sans, Instrument Serif; instâncias estáticas em `fontes/`.
