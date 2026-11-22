#include "ws2816.h"

void ws2816_encode(const uint16_t rgb16[SIGNA_NLEDS][3], uint16_t out[WS_FRAMES]) {
  static const uint8_t order[3] = {1, 0, 2}; /* G, R, B */
  uint32_t n = 0;
  out[n++] = 0;
  for (uint32_t led = 0; led < SIGNA_NLEDS; led++)
    for (uint32_t k = 0; k < 3; k++) {
      uint16_t v = rgb16[led][order[k]];
      for (int b = 15; b >= 0; b--) out[n++] = (v >> b) & 1u ? WS_BIT1 : WS_BIT0;
    }
  out[n] = 0;
}
