#include "ws2816.h"
#include "stm32c0xx.h"

#define DMAMUX_REQ_SPI1_TX 17u /* RM0490 / stm32c0xx_hal_dma.h: DMA_REQUEST_SPI1_TX */

static uint16_t buf[WS_FRAMES];
static bool started;

void ws2816_init(void) {
  /* PA7 = AF0 (SPI1_MOSI), alta velocidade, pull-down para a linha ficar em 0 fora dos quadros */
  GPIOA->MODER = (GPIOA->MODER & ~(3u << (7 * 2))) | (2u << (7 * 2));
  GPIOA->OSPEEDR |= 3u << (7 * 2);
  GPIOA->PUPDR = (GPIOA->PUPDR & ~(3u << (7 * 2))) | (2u << (7 * 2));
  GPIOA->AFR[0] &= ~(0xFu << (7 * 4));

  /* SPI1 mestre, só transmissão (BIDIMODE + BIDIOE), 16 bit, fPCLK/4 = 12 MHz, CPOL=0 CPHA=0, NSS por software */
  SPI1->CR1 = 0;
  SPI1->CR2 = (0xFu << SPI_CR2_DS_Pos) | SPI_CR2_TXDMAEN;
  SPI1->CR1 = SPI_CR1_BIDIMODE | SPI_CR1_BIDIOE | SPI_CR1_MSTR | SPI_CR1_SSM | SPI_CR1_SSI |
              (1u << SPI_CR1_BR_Pos);
  SPI1->CR1 |= SPI_CR1_SPE;

  /* DMAMUX canal 0 -> DMA1 canal 1 */
  DMAMUX1_Channel0->CCR = DMAMUX_REQ_SPI1_TX;
  DMA1_Channel1->CCR = 0;
  DMA1_Channel1->CPAR = (uint32_t)&SPI1->DR;
}

bool ws2816_busy(void) {
  if (!started) return false;
  if (!(DMA1->ISR & DMA_ISR_TCIF1)) return true;
  if ((SPI1->SR & SPI_SR_FTLVL) || (SPI1->SR & SPI_SR_BSY)) return true;
  return false;
}

bool ws2816_show(const uint16_t rgb16[SIGNA_NLEDS][3]) {
  if (ws2816_busy()) return false;
  ws2816_encode(rgb16, buf);
  DMA1_Channel1->CCR = 0;
  DMA1->IFCR = DMA_IFCR_CGIF1;
  DMA1_Channel1->CMAR = (uint32_t)buf;
  DMA1_Channel1->CNDTR = WS_FRAMES;
  DMA1_Channel1->CCR = DMA_CCR_MINC | DMA_CCR_DIR | DMA_CCR_PSIZE_0 | DMA_CCR_MSIZE_0 | DMA_CCR_EN;
  started = true;
  return true;
}
