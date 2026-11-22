/* Testes de host do motor SIGNA: gcc -fsanitize=address,undefined (ver tests/Makefile). */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "../src/engine.h"
#include "vectors_states.h"

static int fails, checks;
#define CHECK(c, ...) do { checks++; if (!(c)) { fails++; printf("FALHA %s:%d: ", __FILE__, __LINE__); printf(__VA_ARGS__); printf("\n"); } } while (0)

static uint8_t last_serial[6];
static int serial_writes;
static void on_serial(const uint8_t s[6]) { memcpy(last_serial, s, 6); serial_writes++; }
static const uint8_t BOOT[6] = {0, 0, 0, 0, 0x24, 0x98};

static void reset(void) {
  engine_hooks_t h = {on_serial};
  engine_init(BOOT, &h);
  serial_writes = 0;
}
static void send(uint8_t a, uint8_t b, uint8_t c, uint8_t d, uint8_t e, uint8_t f, uint8_t g, uint8_t hh) {
  uint8_t r[8] = {a, b, c, d, e, f, g, hh};
  engine_handle_report(r);
}
static int drain(uint8_t first[8]) { /* devolve nº de relatórios; copia o primeiro */
  uint8_t r[8];
  int n = 0;
  while (engine_pop_report(r)) { if (!n && first) memcpy(first, r, 8); n++; }
  return n;
}
/* avança até o evento 00 01; devolve ms ou -1 */
static int ticks_until_done(int max) {
  uint8_t r[8];
  for (int t = 1; t <= max; t++) {
    engine_tick_1ms();
    while (engine_pop_report(r)) if (r[0] == 0 && r[1] == 1) return t;
  }
  return -1;
}
static uint16_t disp(int led, int ch) { uint16_t d[3][3]; engine_display_q88(d); return d[led][ch]; }

static void t_static_and_addr(void) {
  reset();
  uint8_t r[8];
  send(0x01, 0xFF, 255, 0, 0, 0, 0, 0);
  CHECK(drain(r) == 1 && r[0] == 0x42, "ACK 42 no 01");
  CHECK(disp(0, 0) == 65535 && disp(2, 0) == 65535 && disp(1, 1) == 0, "cor fixa em todos");
  send(0x01, 0x02, 0, 0, 255, 0, 0, 0);
  drain(NULL);
  CHECK(disp(1, 2) == 65535 && disp(1, 0) == 0 && disp(0, 0) == 65535, "LED 2 isolado");
  /* 0x13 trava o original: aqui silêncio e nada muda */
  send(0x01, 0x13, 0, 255, 0, 0, 0, 0);
  CHECK(drain(NULL) == 0 && disp(0, 1) == 0, "0x13 rejeitado com silêncio");
  send(0x01, 0x04, 0, 255, 0, 0, 0, 0);
  CHECK(drain(r) == 1 && r[0] == 0x42 && disp(0, 1) == 0, "0x04 = ACK sem efeito");
  int bad = 0;
  for (int a = 0; a < 256; a++) {
    send(0x01, (uint8_t)a, 1, 2, 3, 0, 0, 0);
    int n = drain(NULL);
    int ok = a == 1 || a == 2 || a == 3 || a == 0xFF || a == 4 || a == 5 || a == 6 || a == 0x41 || a == 0x42;
    if (n != (ok ? 1 : 0)) bad++;
  }
  CHECK(bad == 0, "varredura de endereços: %d respostas erradas", bad);
}

static void t_fade(void) {
  reset();
  send(0x01, 0xFF, 0, 0, 0, 0, 0, 0); drain(NULL);
  send(0x02, 0xFF, 255, 0, 0, 10, 0, 0);
  uint8_t r[8];
  CHECK(drain(r) == 1 && r[0] == 0x42, "ACK do fade");
  int t = ticks_until_done(20000);
  /* 255 × 10 × 0,252 ms = 642,6 ms */
  CHECK(t == 643, "fade 0→255 tempo 10 = %d ms (esperado 643)", t);
  CHECK(disp(0, 0) == 65535, "fade chega na cor-alvo");
  send(0x02, 0xFF, 0, 0, 0, 100, 0, 0); drain(NULL);
  t = ticks_until_done(20000);
  CHECK(t == 6426, "fade 255→0 tempo 100 = %d ms (esperado 6426)", t);
  send(0x02, 0xFF, 0, 0, 0, 100, 0, 0);
  CHECK(drain(NULL) == 2, "fade para a cor atual: ACK + 00 01 imediato");
  /* meio do caminho: linear */
  send(0x02, 0x01, 0, 200, 0, 20, 0, 0); drain(NULL);
  for (int i = 0; i < 504; i++) engine_tick_1ms(); /* metade de 200×20×0,252 = 1008 ms */
  int g = disp(0, 1) >> 8;
  CHECK(g >= 99 && g <= 101, "fade linear no meio: %d", g);
}

static void t_strobe(void) {
  reset();
  send(0x01, 0xFF, 0, 0, 255, 0, 0, 0); drain(NULL);
  send(0x03, 0xFF, 255, 0, 0, 10, 0, 3); drain(NULL);
  engine_tick_1ms();
  CHECK(disp(0, 0) == 65535 && disp(0, 2) == 0, "strobe aceso no início");
  int t = ticks_until_done(20000) + 1;
  CHECK(t == 1965, "strobe 3 × 10 × 65,5 ms = %d ms (esperado 1965)", t);
  CHECK(disp(0, 2) == 65535 && disp(0, 0) == 0, "strobe restaura a cor anterior");
  send(0x03, 0xFF, 255, 0, 0, 1, 0, 0); drain(NULL);
  CHECK(ticks_until_done(10000) == -1, "rep 0 = infinito, sem evento de fim");
  send(0x01, 0x01, 0, 255, 0, 0, 0, 0); drain(NULL);
  for (int i = 0; i < 500; i++) engine_tick_1ms();
  CHECK(disp(0, 1) == 65535 && disp(1, 2) == 65535, "comando novo interrompe o strobe (e restaura)");
}

static void t_wave_pattern(void) {
  reset();
  send(0x04, 5, 0, 255, 0, 0, 2, 10); drain(NULL);
  int t = ticks_until_done(20000);
  CHECK(t == 1300, "wave 5: 2 × 10 × 65 ms = %d ms", t);
  send(0x04, 1, 0, 255, 0, 0, 2, 10); drain(NULL);
  CHECK(ticks_until_done(5000) == -1, "wave 1 não manda 00 01");
  send(0x04, 9, 0, 255, 0, 0, 2, 10);
  CHECK(drain(NULL) == 0, "wave tipo 9: silêncio");
  send(0x06, 5, 2, 0, 0, 0, 0, 0); drain(NULL);
  t = ticks_until_done(20000);
  CHECK(t == 1800, "padrão 5 × 2 = %d ms (esperado 1800)", t);
  send(0x06, 2, 1, 0, 0, 0, 0, 0); drain(NULL);
  CHECK(ticks_until_done(8000) == -1, "padrão 2 sem evento de fim");
  send(0x06, 0, 1, 0, 0, 0, 0, 0);
  CHECK(drain(NULL) == 0, "padrão 0: silêncio");
  send(0x06, 9, 1, 0, 0, 0, 0, 0);
  CHECK(drain(NULL) == 0, "padrão 9: silêncio");
  for (int id = 1; id <= 8; id++) { send(0x06, (uint8_t)id, 0, 0, 0, 0, 0, 0); drain(NULL); for (int i = 0; i < 17000; i++) engine_tick_1ms(); }
  CHECK(1, "padrões 1–8 rodam sem travar");
}

static void t_serial_version(void) {
  reset();
  uint8_t r[8];
  send(0x80, 0, 0, 0, 0, 0, 0, 0);
  CHECK(drain(r) == 1 && r[0] == 0x80 && r[1] == 0x3C && r[2] == 0 && r[5] == 0x00, "0x80 = 80 3c + serial de boot");
  send(0x62, 0, 0, 0, 0, 0, 0, 0);
  CHECK(drain(r) == 1 && r[0] == 0x62 && r[1] == 0 && r[4] == 0, "0x62 lê 4 bytes");
  send(0x51, 1, 2, 3, 4, 5, 6, 0);
  CHECK(drain(r) == 1 && r[0] == 0x51 && r[1] == 1 && r[6] == 6, "0x51 ecoa");
  CHECK(serial_writes == 1 && last_serial[5] == 6, "0x51 grava 6 bytes");
  send(0x51, 1, 2, 3, 4, 5, 6, 0); drain(NULL);
  CHECK(serial_writes == 1, "gravação igual não regrava a flash");
  send(0x52, 9, 9, 9, 9, 0, 0, 0); drain(NULL);
  CHECK(serial_writes == 2 && last_serial[0] == 9 && last_serial[4] == 5 && last_serial[5] == 6, "0x52 grava só 4");
  send(0x62, 0, 0, 0, 0, 0, 0, 0); drain(r);
  CHECK(r[1] == 9 && r[4] == 9, "0x62 lê o valor atual");
  send(0x80, 0, 0, 0, 0, 0, 0, 0); drain(r);
  CHECK(r[2] == 0 && r[5] == 0x00, "0x80 continua com a cópia de boot");
  send(0x1F, 0, 0, 0, 0, 0, 0, 0); drain(r);
  CHECK(r[0] == 0x1F && r[1] == 'S' && r[2] == 'G' && r[6] == 3, "0x1F info SIGNA");
}

static void t_unknown_fuzz(void) {
  reset();
  send(0x05, 0xFF, 0x10, 0, 0, 5, 0, 1);
  CHECK(drain(NULL) == 0, "0x05 inexistente: silêncio");
  send(0x07, 0, 0, 0, 0, 0, 0, 0);
  CHECK(drain(NULL) == 0, "0x07 inexistente: silêncio");
  int resp = 0;
  for (int op = 0x07; op <= 0x0F; op++) { send((uint8_t)op, 0xFF, 1, 1, 1, 1, 1, 1); resp += drain(NULL); }
  CHECK(resp == 0, "0x07–0x0F silêncio");
  srand(1234);
  for (int i = 0; i < 200000; i++) {
    uint8_t r[8];
    for (int k = 0; k < 8; k++) r[k] = (uint8_t)rand();
    if (r[0] == 0x51 || r[0] == 0x52) r[0] = 0x50;
    engine_handle_report(r);
    for (int k = rand() % 4; k > 0; k--) engine_tick_1ms();
    drain(NULL);
  }
  CHECK(1, "fuzz de 200 mil relatórios sem crash (ASan/UBSan)");
}

static void t_states(void) {
  int worst = 0;
  for (int s = 0; s < SIGNA_ST_COUNT; s++)
    for (unsigned i = 0; i < sizeof VEC_T / sizeof VEC_T[0]; i++) {
      int d = (int)signa_state_level_q12((signa_state_t)s, VEC_T[i]) - (int)VEC_L[s][i];
      if (d < 0) d = -d;
      if (d > worst) worst = d;
      CHECK(d <= 8, "estado %d t=%u: C=%u py=%u", s, VEC_T[i], signa_state_level_q12((signa_state_t)s, VEC_T[i]), VEC_L[s][i]);
    }
  printf("  curvas C vs produto.json: erro máx %d/4096\n", worst);

  /* ERRO a 2,5 Hz: 25 subidas em 10 s (< 3 Hz, WCAG 2.3.1) */
  int rises = 0, prev = 0;
  for (uint32_t t = 0; t < 10000; t++) {
    int on = signa_state_level_q12(SIGNA_ST_IA_ERRO, t) > 2048;
    if (on && !prev) rises++;
    prev = on;
  }
  CHECK(rises == 25, "ERRO: %d piscadas em 10 s (esperado 25 = 2,5 Hz)", rises);
}

static void t_mixed(void) {
  reset();
  uint8_t r[8];
  send(0x11, SIGNA_ST_SALA_OCUPADO, SIGNA_ST_IA_ERRO, 0, 0, 0, 0, 0);
  CHECK(drain(r) == 1 && r[0] == 0x42, "ACK 0x11");
  for (int t = 0; t < 1000; t++) {
    engine_tick_1ms();
    if (disp(0, 0) != 65535 || disp(1, 0) != 65535 || disp(2, 0) != 65535) { CHECK(0, "OCUPADO deveria travar os 3 LEDs, t=%d", t); break; }
  }
  CHECK(disp(0, 1) == (59 * 257), "OCUPADO = #FF3B2F nos 3 LEDs (G=%u)", disp(0, 1));
  reset();
  send(0x11, SIGNA_ST_SALA_LIVRE, SIGNA_ST_IA_ERRO, 0, 0, 0, 0, 0); drain(NULL);
  for (int t = 0; t < 50; t++) engine_tick_1ms();
  CHECK(disp(0, 0) == 65535 && disp(0, 2) == 200 * 257, "LED 1 = ERRO aceso em t=50");
  CHECK(disp(2, 1) == (uint16_t)((210u * 257u * 1147u) >> 12), "LED 3 = LIVRE 0,28");
  for (int t = 0; t < 150; t++) engine_tick_1ms();
  CHECK(disp(0, 0) < 65535 / 10, "LED 1 no piso em t=200");
  /* reenviar o mesmo par não reinicia a fase */
  send(0x11, SIGNA_ST_SALA_LIVRE, SIGNA_ST_IA_ERRO, 0, 0, 0, 0, 0); drain(NULL);
  engine_tick_1ms();
  CHECK(disp(0, 0) < 65535 / 10, "mesmo estado mantém a fase");
  send(0x11, SIGNA_ST_IA_ERRO, SIGNA_ST_IA_ERRO, 0, 0, 0, 0, 0);
  CHECK(drain(NULL) == 0, "estado de IA na zona da sala: silêncio");
  send(0x10, SIGNA_ST_COUNT, 0, 0, 0, 0, 0, 0);
  CHECK(drain(NULL) == 0, "estado inexistente: silêncio");
  send(0x10, SIGNA_ST_SALA_OCUPADO, 0, 0, 0, 0, 0, 0); drain(NULL);
  CHECK(disp(0, 0) == 65535 && disp(2, 0) == 65535, "0x10 OCUPADO em todos");
  send(0x12, 0, 0, 0, 0, 0, 0, 0); drain(NULL);
  uint16_t o[3][3]; engine_output16(o);
  CHECK(o[0][0] < 400, "brilho global 0 quase apaga (%u)", o[0][0]);
}

static void t_gamma(void) {
  CHECK(signa_gamma16(0) == 0 && signa_gamma16(65535) >= 65400, "gamma nas pontas");
  int mono = 1;
  for (uint32_t v = 1; v < 65536; v++) if (signa_gamma16((uint16_t)v) < signa_gamma16((uint16_t)(v - 1))) mono = 0;
  CHECK(mono, "gamma monotônica");
  CHECK(signa_gamma16(32768) > 14000 && signa_gamma16(32768) < 15000, "gamma 2,2 no meio = %u", signa_gamma16(32768));
}

int main(void) {
  t_static_and_addr();
  t_fade();
  t_strobe();
  t_wave_pattern();
  t_serial_version();
  t_unknown_fuzz();
  t_states();
  t_mixed();
  t_gamma();
  printf("%d verificações, %d falhas\n", checks, fails);
  return fails ? 1 : 0;
}
