/* Registro do serial em uma página de flash, com nivelamento de desgaste.
 * Cada gravação ocupa 16 bytes (2 palavras de 64 bit, a unidade de programação do STM32C0).
 * A página de 2 KB guarda 128 gravações antes de precisar ser apagada.
 * Registro: 'S''G' | seq(16) | serial[6] | crc16(10 bytes) | 0x00000000 (selo de gravação completa).
 * Sem registro válido: o firmware usa um serial derivado do UID do chip. */
#pragma once
#include <stdbool.h>
#include <stdint.h>

#define NVM_REC_SIZE 16u

typedef struct {
  const uint8_t *page;  /* página mapeada em memória (flash ou buffer no teste) */
  uint32_t size;        /* múltiplo de 16 */
  bool (*erase)(void);  /* apaga a página inteira (bytes = 0xFF) */
  bool (*prog64)(uint32_t off, uint64_t v); /* programa 8 bytes alinhados */
} nvm_log_t;

bool nvm_log_load(const nvm_log_t *n, uint8_t serial[6]);
bool nvm_log_store(const nvm_log_t *n, const uint8_t serial[6]);
uint16_t nvm_crc16(const uint8_t *p, uint32_t len);
