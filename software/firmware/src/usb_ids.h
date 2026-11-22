/* Identidade USB.
 * TODO(Lucas): decidir o VID:PID definitivo. Opções: PID próprio no pid.codes (grátis, hardware aberto),
 * VID da USB-IF (US$ 6.000) ou sub-licença de PID de um fabricante de chip.
 *   Padrão: 1209:0001 = "pid.codes Test PID" — SÓ para testes, não pode ir em unidade distribuída.
 *   make USB_IDS=luxafor: 04d8:f372 (o do Luxafor Flag) — só no protótipo pessoal, para testar
 *   software que procura esse par. Nunca em produto vendido. */
#pragma once
#if defined(SIGNA_IDS_LUXAFOR)
#define SIGNA_USB_VID 0x04D8
#define SIGNA_USB_PID 0xF372
#define SIGNA_USB_BCD 0x3C00
#else
#define SIGNA_USB_VID 0x1209 /* TODO: VID/PID definitivo */
#define SIGNA_USB_PID 0x0001 /* TODO: pid.codes test PID, só para desenvolvimento */
#define SIGNA_USB_BCD 0x0001
#endif
#define SIGNA_USB_MANUFACTURER "SIGNA"
#define SIGNA_USB_PRODUCT "SIGNA rev C"
