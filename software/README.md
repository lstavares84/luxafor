# SIGNA — software

Luz de status USB-C: a sala vê se você está livre, prestes a entrar em reunião ou ocupado (Google/Outlook), e você acompanha Claude, ChatGPT e Grok (opt-in). Firmware compatível com o protocolo HID do Luxafor Flag.
A placa atual é a [rev D](../hardware/revD/) (o firmware nasceu na rev C, com os mesmos pinos de USB e LEDs; a rev D acrescenta o botão S1 em PA14).

- Como compilar, gravar e configurar: [`docs/README.md`](docs/README.md)
- Arquitetura, protocolo e decisões: [`docs/arquitetura.md`](docs/arquitetura.md)

Estado em 22/11/2026: firmware compila (17,5 KB de flash) e passa nos testes de host; app com 32 testes passando. **Nada foi testado em silício ainda.**
