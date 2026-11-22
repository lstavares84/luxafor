# [`.old/`](.) — material superado

Esta pasta guarda o que o repositório já teve e deixou de ser o desenho ou o conceito atuais. Nada daqui deve ser usado para fabricar ou apresentar o SIGNA, a menos que você queira consultar a história. O material atual está na raiz: placa em [`hardware/revD/`](../hardware/revD/), mecânica em [`mecanica/`](../mecanica/), software em [`software/`](../software/), caderno em [`docs/caderno-signa/`](../docs/caderno-signa/).

| Caminho | O que era | Por que foi para cá |
|---|---|---|
| `hardware/README.md` | Introdução da **rev A** (STM32C071F8P6 TSSOP-20, 3× SK6805-EC20) | Substituído pelo [`hardware/README.md`](../hardware/README.md) que aponta para a rev D |
| `hardware/indicador/` | Projeto KiCad da rev A | Superada pela rev B, depois C, depois D |
| `hardware/lib/` | Símbolo e footprint SK6805 da rev A | Cada revisão posterior tem a própria pasta lib: `hardware/revB/lib/`, `hardware/revC/lib/` e [`hardware/revD/lib/`](../hardware/revD/lib/) |
| `hardware/tools/` | Geradores da rev A (`hardware/tools/netlist.py`, `hardware/tools/gen_sch.py`, `hardware/tools/gen_pcb.py`, …) | Os geradores atuais estão em [`hardware/revD/tools/`](../hardware/revD/tools/) |
| `hardware/revB/` | Placa 11 × 44 mm com STM32C071G8U6 e 3× SK6805-EC20 (8 bits) | Superada pela rev C (WS2816B de 16 bits) |
| `hardware/revC/` | Placa com WS2816B-2020, ainda sem botão, sem TP e sem orelhas | Superada pela rev D. Foram acrescentados aqui, porque não estavam no `main`, os docs `hardware/revC/docs/firmware_comportamento.md`, `hardware/revC/docs/pendencias.md`, `hardware/revC/docs/captura_logica.md` e `hardware/revC/docs/estoque_stm32c071.json` |
| `design/conceitos/` | Quatro formas exploradas (totem, pendente, bandeirola dobrável, mini letreiro) | O pendente foi o escolhido; a exploração fica como histórico |
| `docs/conceito/` | Caderno conceitual antigo (`docs/conceito/indicador-conceito.pdf`) e os scripts daquele sistema visual | Substituído por [`docs/caderno-signa/`](../docs/caderno-signa/) (caderno SIGNA, 14 lâminas). Os dois prompts ([`prompt-caderno-conceitual.md`](../docs/prompts/prompt-caderno-conceitual.md) e [`prompt-caderno-generico.md`](../docs/prompts/prompt-caderno-generico.md)) **não** vieram para cá: foram para [`docs/prompts/`](../docs/prompts/), porque ainda são úteis |

O protocolo, o [`luxafor.py`](../luxafor.py) e o [`tools/anim.py`](../tools/anim.py) da engenharia reversa do Luxafor Flag **permanecem na raiz** — continuam válidos.
