#include "nvm_log.h"
#include <string.h>

uint16_t nvm_crc16(const uint8_t *p, uint32_t len) { /* CRC-16/CCITT-FALSE */
  uint16_t c = 0xFFFF;
  while (len--) {
    c ^= (uint16_t)(*p++ << 8);
    for (int i = 0; i < 8; i++) c = (uint16_t)((c & 0x8000) ? (c << 1) ^ 0x1021 : c << 1);
  }
  return c;
}

static bool blank(const uint8_t *r) {
  for (uint32_t i = 0; i < NVM_REC_SIZE; i++) if (r[i] != 0xFF) return false;
  return true;
}
static bool valid(const uint8_t *r) {
  if (r[0] != 'S' || r[1] != 'G') return false;
  if (r[12] | r[13] | r[14] | r[15]) return false;
  uint16_t c = (uint16_t)(r[10] | (r[11] << 8));
  return c == nvm_crc16(r, 10);
}

/* último registro válido (maior seq, comparando com wrap de 16 bit) */
static int find_last(const nvm_log_t *n, uint16_t *seq) {
  int best = -1;
  uint16_t bs = 0;
  for (uint32_t off = 0; off + NVM_REC_SIZE <= n->size; off += NVM_REC_SIZE) {
    const uint8_t *r = n->page + off;
    if (!valid(r)) continue;
    uint16_t s = (uint16_t)(r[2] | (r[3] << 8));
    if (best < 0 || (int16_t)(s - bs) > 0) { best = (int)off; bs = s; }
  }
  if (seq) *seq = bs;
  return best;
}

bool nvm_log_load(const nvm_log_t *n, uint8_t serial[6]) {
  int off = find_last(n, NULL);
  if (off < 0) return false;
  memcpy(serial, n->page + off + 4, 6);
  return true;
}

static uint64_t le64(const uint8_t *b) {
  uint64_t v = 0;
  for (int i = 7; i >= 0; i--) v = (v << 8) | b[i];
  return v;
}

bool nvm_log_store(const nvm_log_t *n, const uint8_t serial[6]) {
  uint16_t seq = 0;
  int last = find_last(n, &seq);
  if (last >= 0 && memcmp(n->page + last + 4, serial, 6) == 0) return true; /* nada a fazer */
  int32_t slot = -1;
  for (uint32_t off = 0; off + NVM_REC_SIZE <= n->size; off += NVM_REC_SIZE)
    if (blank(n->page + off)) { slot = (int32_t)off; break; }
  if (slot < 0) {
    if (!n->erase()) return false;
    slot = 0;
  }
  uint8_t r[NVM_REC_SIZE];
  memset(r, 0, sizeof r);
  r[0] = 'S'; r[1] = 'G';
  seq = (uint16_t)(last >= 0 ? seq + 1 : 1);
  r[2] = (uint8_t)seq; r[3] = (uint8_t)(seq >> 8);
  memcpy(&r[4], serial, 6);
  uint16_t c = nvm_crc16(r, 10);
  r[10] = (uint8_t)c; r[11] = (uint8_t)(c >> 8);
  /* primeira metade, depois a segunda com o selo zerado: corte de energia no meio = registro inválido */
  if (!n->prog64((uint32_t)slot, le64(r))) return false;
  if (!n->prog64((uint32_t)slot + 8, le64(r + 8))) return false;
  return valid(n->page + slot) && memcmp(n->page + slot + 4, serial, 6) == 0;
}
