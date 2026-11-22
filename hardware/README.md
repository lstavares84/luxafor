# Hardware SIGNA

A placa atual é a **[rev D](revD/)**: STM32C071G8U6, 3× WS2816B-2020 (16 bits por canal), botão S1 na borda de baixo, pontos de teste no verso e orelhas na ponta do USB para travar a placa no berço.

| Item | Valor |
|---|---|
| Placa | 11 × 44 mm (15,2 mm nas orelhas), FR-4, 2 camadas, 0,8 mm |
| MCU | STM32C071G8U6 (UFQFPN-28), USB FS sem cristal, DFU na ROM |
| LEDs | 3× WS2816B-2020, dado em PA7 via SN74AHCT1G125 |
| Botão | S1 ALPS SKRTLAE010 em PA14: alterna OCUPADO/LIVRE; segurado ao ligar, entra em DFU (`nBOOT_SEL = 0`) |
| Estado | KiCad 9.0.2, ERC 0, DRC 0 erros — **ainda não fabricada nem testada em silício** |

Arquivos de fabricação, esquemático, BOM, gerbers, renders e o que mudou em relação à rev C: [`revD/README.md`](revD/README.md) e [`revD/CHANGELOG.md`](revD/CHANGELOG.md).

A montagem 3D integrada (placa + corpo + cabo) está em [`mecanica/`](../mecanica/).

Revisões anteriores (rev A / indicador, rev B e rev C) e as ferramentas da rev A foram para [`.old/hardware/`](../.old/hardware/).
