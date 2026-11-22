/* Codificação WS2816B: ordem GRB, MSB primeiro, e margens de tempo a 12 MHz ±1 %. */
#include <stdio.h>
#include "../src/ws2816.h"

static int fails, checks;
#define CHECK(c, m) do { checks++; if (!(c)) { fails++; printf("FALHA ws: %s\n", m); } } while (0)

static double high_ns(uint16_t f, double fspi) { int n = 0; for (int b = 15; b >= 0; b--) { if ((f >> b) & 1) n++; else break; } return n * 1e9 / fspi; }
static int low_after_high(uint16_t f) { int seen0 = 0; for (int b = 15; b >= 0; b--) { if (!((f >> b) & 1)) seen0 = 1; else if (seen0) return 0; } return 1; }

int main(void) {
  uint16_t rgb[SIGNA_NLEDS][3] = {{0x8001, 0x00FF, 0xF000}, {0, 0, 0}, {0xFFFF, 0xFFFF, 0xFFFF}};
  uint16_t out[WS_FRAMES];
  ws2816_encode(rgb, out);
  CHECK(out[0] == 0 && out[WS_FRAMES - 1] == 0, "quadros de guarda em 0");
  /* LED 1: G = 0x00FF primeiro */
  int ok = 1;
  for (int b = 0; b < 16; b++) ok &= out[1 + b] == ((0x00FF >> (15 - b)) & 1 ? WS_BIT1 : WS_BIT0);
  CHECK(ok, "G vem primeiro, MSB primeiro");
  ok = 1;
  for (int b = 0; b < 16; b++) ok &= out[17 + b] == ((0x8001 >> (15 - b)) & 1 ? WS_BIT1 : WS_BIT0);
  CHECK(ok, "R em segundo");
  ok = 1;
  for (int b = 0; b < 16; b++) ok &= out[33 + b] == ((0xF000 >> (15 - b)) & 1 ? WS_BIT1 : WS_BIT0);
  CHECK(ok, "B em terceiro");
  CHECK(out[1 + 96] == WS_BIT1 && out[WS_FRAMES - 2] == WS_BIT1, "LED 3 branco");
  CHECK(low_after_high(WS_BIT0) && low_after_high(WS_BIT1), "pulso único por bit");
  for (double tol = -0.01; tol <= 0.0101; tol += 0.01) {
    double f = 12e6 * (1 + tol), cyc = 16e9 / f;
    double t0h = high_ns(WS_BIT0, f), t1h = high_ns(WS_BIT1, f);
    printf("  fSPI %.2f MHz: T0H %.0f ns, T0L %.0f ns, T1H %.0f ns, T1L %.0f ns, ciclo %.0f ns\n",
           f / 1e6, t0h, cyc - t0h, t1h, cyc - t1h, cyc);
    CHECK(t0h >= 200 && t0h <= 320 && cyc - t0h >= 800 && cyc - t0h <= 1200, "bit 0 dentro do datasheet");
    CHECK(t1h >= 520 && t1h <= 800 && cyc - t1h >= 480 && cyc - t1h <= 1000, "bit 1 dentro do datasheet");
    CHECK(cyc >= 1250, "ciclo >= 1,25 us");
  }
  double frame_us = (WS_FRAMES * 16) / 12.0;
  printf("  quadro: %u palavras, %.0f us; intervalo 2 ms deixa %.0f us em baixo (> 280 us)\n", WS_FRAMES, frame_us, 2000 - frame_us);
  CHECK(2000 - frame_us > 280, "reset > 280 us entre quadros");
  printf("ws: %d verificações, %d falhas\n", checks, fails);
  return fails != 0;
}
