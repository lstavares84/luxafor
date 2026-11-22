/* GERADO por tools/gen_tables.py. Não editar à mão. */
#pragma once
#include <stdint.h>

typedef enum {
  SIGNA_ST_OFF = 0,
  SIGNA_ST_SALA_LIVRE = 1,
  SIGNA_ST_SALA_PRESTES = 2,
  SIGNA_ST_SALA_OCUPADO = 3,
  SIGNA_ST_IA_DESOCUPADA = 4,
  SIGNA_ST_IA_PROCESSANDO = 5,
  SIGNA_ST_IA_ATENCAO = 6,
  SIGNA_ST_IA_ERRO = 7,
  SIGNA_ST_IA_LIMITE_5H = 8,
  SIGNA_ST_IA_LIMITE_SEMANAL = 9,
  SIGNA_ST_COUNT
} signa_state_t;

enum { SIGNA_W_CONST = 0, SIGNA_W_BREATH = 1, SIGNA_W_PULSE = 2, SIGNA_W_DOUBLE = 3 };

typedef struct {
  uint8_t r, g, b;
  uint8_t wave;
  uint8_t table;
  uint16_t period_ms, on_ms, gap_ms;
  uint16_t hi_q12, lo_q12;
} signa_state_desc_t;

extern const uint16_t signa_gamma_lut[257];
extern const uint16_t signa_breath_tab[2][257];
extern const signa_state_desc_t signa_states[SIGNA_ST_COUNT];
