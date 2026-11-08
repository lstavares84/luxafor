# Luxafor Flag: engenharia reversa

Engenharia reversa do [Luxafor Flag](https://luxafor.com/product/flag2/) (USB `04d8:f372`, firmware `0x3c`): protocolo HID, comportamento dos LEDs e, futuramente, o firmware.

O controle é feito em Python puro via `/dev/hidraw`, sem dependências.

## Conteúdo

| Arquivo | O que é |
|---|---|
| [PROTOCOLO.md](PROTOCOLO.md) | Especificação do protocolo, com cada item marcado como validado visualmente, medido ou em aberto |
| [luxafor.py](luxafor.py) | CLI e biblioteca de controle, com limites de segurança |
| [tools/anim.py](tools/anim.py) | Envia um comando cru e registra os eventos com timestamp |

## Uso rápido

```bash
./luxafor.py version                 # firmware 0x3c
./luxafor.py color top blue          # LEDs: all | bottom | middle | top
./luxafor.py fade all green 20 --wait
./luxafor.py strobe all red 10 3
./luxafor.py wave 1 cyan 5 60
./luxafor.py pattern rainbow --wait  # traffic, police, rainbow, ...
./luxafor.py off
```

Permissão: o usuário precisa de leitura e escrita em `/dev/hidrawN`. Em desktops com systemd isso costuma vir por ACL de sessão; se não vier, use uma regra udev.

## Resumo do que já se sabe

- HID vendor (`0xFF00`), relatórios de 8 bytes sem Report ID. Comandos: `01` cor, `02` fade, `03` strobe, `04` wave, `06` padrão, `80` versão.
- 3 LEDs RGB (baixo, meio, topo) com PWM linear de 8 bits.
- O dispositivo manda o evento `00 01` quando uma animação termina.

## ⚠️ Cuidados

- `01 13 …` (LED `0x13`) **trava o firmware**. Reconecte o aparelho fisicamente e **não** use reset USB por software, que travou o barramento USB do host.
- `51`, `52` e `62` são desconhecidos e podem gravar na memória não volátil. O serial desta unidade virou `000000000000` durante os testes.

## Roadmap

- [x] Descritores USB/HID
- [x] Comandos de LED, tempos e padrões (validados)
- [ ] Opcodes `00`, `51`, `52` e `62`
- [ ] Identificar o MCU (abrir o case, fotos da placa)
- [ ] Ler o firmware via ICSP e verificar se há bootloader
- [ ] Firmware próprio
