#pragma once
#include <stdint.h>
/* serial de 6 bytes: registro na flash ou, se vazio, derivado do UID de 96 bit */
void nvm_serial_boot(uint8_t serial[6]);
void nvm_serial_request_write(const uint8_t serial[6]); /* chamado pelo motor; grava no laço principal */
void nvm_task(void);
