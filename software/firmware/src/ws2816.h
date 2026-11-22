/* WS2816B-2020 por SPI1 (MOSI = PA7, AF0) + DMA1 canal 1 (DMAMUX req 17 = SPI1_TX).
 *
 * Cada bit do LED vira um quadro SPI de 16 bit a 12 MHz (48 MHz / 4): 83,3 ns por bit SPI.
 *   bit 0 = 0xE000 -> 3 bits altos = 250 ns  (T0H 200–320 ns)   | baixo 1083 ns (T0L 800–1200 ns)
 *   bit 1 = 0xFF00 -> 8 bits altos = 667 ns  (T1H 520–800 ns)   | baixo  667 ns (T1L 480–1000 ns)
 *   ciclo 1,333 µs (>= 1,25 µs exigido). Reset > 280 µs: o quadro só é reenviado a cada 2 ms.
 * Ordem: G16 R16 B16, MSB primeiro (datasheet: "Data transmit in order of GRB, high bit data at first").
 * Margens com HSISYS ±1 %: T0H 247–253 ns, T1H 660–673 ns — longe dos limites. O buffer AHCT1G125
 * acrescenta ~5 ns de atraso e < 2 ns de distorção de largura (TI SCLS379), desprezível.
 */
#pragma once
#include <stdbool.h>
#include <stdint.h>
#include "engine.h"

#define WS_BITS_PER_LED 48u
#define WS_FRAMES (1u + SIGNA_NLEDS * WS_BITS_PER_LED + 1u) /* 0 inicial + dados + 0 final */
#define WS_BIT0 0xE000u
#define WS_BIT1 0xFF00u

/* Codifica (puro, testável no host). rgb16[led][R,G,B]; LED 0 = D1 (primeiro da cadeia). */
void ws2816_encode(const uint16_t rgb16[SIGNA_NLEDS][3], uint16_t out[WS_FRAMES]);
void ws2816_init(void);
bool ws2816_busy(void);
bool ws2816_show(const uint16_t rgb16[SIGNA_NLEDS][3]); /* false se ainda ocupado */
