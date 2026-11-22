#include <stdio.h>
#include <string.h>
#include "../src/nvm_log.h"

static uint8_t page[2048];
static int erases, fail_after = -1, progs;
static bool er(void) { memset(page, 0xFF, sizeof page); erases++; return true; }
static bool pg(uint32_t off, uint64_t v) {
  if (fail_after >= 0 && progs++ >= fail_after) return false; /* simula corte de energia */
  for (int i = 0; i < 8; i++) page[off + i] &= (uint8_t)(v >> (8 * i)); /* flash só zera bits */
  return true;
}
static int fails, checks;
#define CHECK(c, m) do { checks++; if (!(c)) { fails++; printf("FALHA nvm: %s\n", m); } } while (0)

int main(void) {
  nvm_log_t n = {page, sizeof page, er, pg};
  uint8_t s[6], o[6];
  memset(page, 0xFF, sizeof page);
  CHECK(!nvm_log_load(&n, o), "página vazia = sem serial");
  for (int i = 0; i < 1000; i++) {
    for (int k = 0; k < 6; k++) s[k] = (uint8_t)(i * 7 + k);
    CHECK(nvm_log_store(&n, s), "grava");
    CHECK(nvm_log_load(&n, o) && !memcmp(o, s, 6), "relê o último");
  }
  CHECK(erases == 1000 / 128, "128 gravações por apagamento");
  /* corte de energia entre as duas metades: continua valendo o anterior */
  uint8_t prev[6]; memcpy(prev, s, 6);
  s[0] ^= 0xFF; progs = 0; fail_after = 1;
  CHECK(!nvm_log_store(&n, s), "gravação interrompida falha");
  CHECK(nvm_log_load(&n, o) && !memcmp(o, prev, 6), "serial anterior sobrevive ao corte");
  fail_after = -1;
  CHECK(nvm_log_store(&n, s) && nvm_log_load(&n, o) && !memcmp(o, s, 6), "próxima gravação ok");
  printf("nvm: %d verificações, %d falhas\n", checks, fails);
  return fails != 0;
}
