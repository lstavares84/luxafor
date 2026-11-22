/* SIGNA rev C — acesso ao hardware (STM32C071G8U6, UFQFPN28).
 * Pinos (luxpcb-revC/tools/netlist.py):
 *   pino 13 = PA7  -> LED_DIN_3V3 -> U3 SN74AHCT1G125 -> R3 33 Ω -> D1.DI (WS2816B-2020 ×3)
 *   pino 18/19 = PA11/PA12 = USB_DM/USB_DP (padrão no UFQFPN28; NÃO ligar o remapeamento PA9/PA10)
 *   pino 20 = PA13 SWDIO, pino 21 = PA14 SWCLK/BOOT0 (JP1 + R4 1 kΩ para 3V3)
 */
#pragma once
#include <stdbool.h>
#include <stdint.h>

void board_init(void);            /* 48 MHz (HSISYS), USB em HSIUSB48 + CRS, SysTick 1 ms */
void board_apply_option_bytes(void); /* só com -DSIGNA_AUTO_NBOOT_SEL=1 (padrão: não mexe) */
uint32_t board_millis(void);
void board_uid(uint8_t uid[12]);
bool board_flash_erase_nvm(void);
bool board_flash_prog64_nvm(uint32_t off, uint64_t v);
const uint8_t *board_nvm_page(void);
uint32_t board_nvm_size(void);
