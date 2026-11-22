/* SIGNA rev C — motor de protocolo e animação (C puro, sem hardware).
 *
 * Compila igual no STM32C071 e no PC (testes em tests/). Recebe relatórios HID de 8 bytes,
 * avança em ticks de 1 ms e entrega a cor de cada LED já em 16 bit com gamma.
 */
#pragma once
#include <stdbool.h>
#include <stdint.h>
#include "signa_tables.h"

#define SIGNA_NLEDS 3          /* 0 = LED 1 (baixo, IA), 1 = LED 2 (meio), 2 = LED 3 (topo) */
#define SIGNA_REPORT_LEN 8

/* Versão devolvida no 0x80 (compatível com o Luxafor Flag fw 0x3c). Decisão do Lucas: manter 0x3c
 * para software antigo que confere a versão, ou usar um valor próprio. A versão real do SIGNA sai no 0x1F. */
#ifndef SIGNA_COMPAT_VERSION
#define SIGNA_COMPAT_VERSION 0x3C
#endif
#define SIGNA_FW_MAJOR 0
#define SIGNA_FW_MINOR 1
#define SIGNA_PROTO_VERSION 1

/* Opcodes Luxafor (compatíveis) */
enum {
  OP_ACK_ONLY = 0x00, OP_STATIC = 0x01, OP_FADE = 0x02, OP_STROBE = 0x03, OP_WAVE = 0x04,
  OP_PATTERN = 0x06, OP_SERIAL_W6 = 0x51, OP_SERIAL_W4 = 0x52, OP_SERIAL_R = 0x62, OP_VERSION = 0x80,
  /* Opcodes nativos SIGNA (faixa 0x10–0x1F: silêncio no Flag original, então são seguros) */
  OP_SIGNA_STATE = 0x10,      /* 10 estado                → os 3 LEDs mostram um estado         */
  OP_SIGNA_MIXED = 0x11,      /* 11 estado_sala estado_ia → LED 3+2 = sala, LED 1 = IA           */
  OP_SIGNA_BRIGHT = 0x12,     /* 12 brilho(0–255)         → escala global                         */
  OP_SIGNA_INFO = 0x1F,       /* 1F                       → 1F 'S' 'G' maj min proto nleds 00     */
};
#define SIGNA_ACK 0x42

typedef struct {
  /* chamado quando o serial em NVM deve ser regravado (0x51/0x52); o firmware grava fora da ISR */
  void (*serial_changed)(const uint8_t serial[6]);
} engine_hooks_t;

void engine_init(const uint8_t boot_serial[6], const engine_hooks_t *hooks);
/* Processa um relatório OUT de 8 bytes (sem Report ID). */
void engine_handle_report(const uint8_t in[SIGNA_REPORT_LEN]);
/* Avança 1 ms. */
void engine_tick_1ms(void);
/* Próximo relatório IN pendente (ACK, eventos, respostas). */
bool engine_pop_report(uint8_t out[SIGNA_REPORT_LEN]);
/* Cor atual por LED, canais R,G,B em 16 bit após gamma e brilho global. */
void engine_output16(uint16_t out[SIGNA_NLEDS][3]);
/* Cor atual antes da gamma (Q8.8) — útil para testes. */
void engine_display_q88(uint16_t out[SIGNA_NLEDS][3]);
/* true quando há mudança de saída desde a última chamada (evita reenviar quadros iguais). */
bool engine_output_dirty(void);

/* utilitários expostos para teste */
uint16_t signa_state_level_q12(signa_state_t st, uint32_t t_ms);
uint16_t signa_gamma16(uint16_t v_q88);
