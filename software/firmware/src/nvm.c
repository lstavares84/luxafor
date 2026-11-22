#include "nvm.h"
#include <stdbool.h>
#include <string.h>
#include "board.h"
#include "nvm_log.h"

static uint8_t pending[6];
static volatile bool has_pending;

static const nvm_log_t *log_ctx(void) {
  static nvm_log_t n;
  n.page = board_nvm_page();
  n.size = board_nvm_size();
  n.erase = board_flash_erase_nvm;
  n.prog64 = board_flash_prog64_nvm;
  return &n;
}

void nvm_serial_boot(uint8_t serial[6]) {
  if (nvm_log_load(log_ctx(), serial)) return;
  /* padrão: 6 bytes do UID dobrados (lote/wafer/X/Y). Único por chip, estável. */
  uint8_t uid[12];
  board_uid(uid);
  for (int i = 0; i < 6; i++) serial[i] = (uint8_t)(uid[i] ^ uid[i + 6]);
}

void nvm_serial_request_write(const uint8_t serial[6]) {
  memcpy(pending, serial, 6);
  has_pending = true;
}

void nvm_task(void) {
  if (!has_pending) return;
  uint8_t s[6];
  memcpy(s, pending, 6);
  has_pending = false;
  (void)nvm_log_store(log_ctx(), s); /* falha: o valor em RAM continua, e o próximo boot lê o anterior */
}
