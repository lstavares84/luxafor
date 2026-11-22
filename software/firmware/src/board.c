#include "board.h"
#include "stm32c0xx.h"

extern uint8_t _nvm_start[];
static volatile uint32_t ms_ticks;

void SysTick_Handler(void) { ms_ticks++; }
uint32_t board_millis(void) { return ms_ticks; }
uint32_t tusb_time_millis_api(void) { return ms_ticks; }

void board_init(void) {
  /* 1 wait state + prefetch antes de subir para 48 MHz (DS14693: >24 MHz exige 1 WS) */
  FLASH->ACR = (FLASH->ACR & ~FLASH_ACR_LATENCY) | FLASH_ACR_LATENCY_0 | FLASH_ACR_PRFTEN | FLASH_ACR_ICEN;
  while ((FLASH->ACR & FLASH_ACR_LATENCY) != FLASH_ACR_LATENCY_0) {}
  /* HSISYS = HSI48 / 1 (reset: /4 = 12 MHz). SYSCLK = HSISYS = 48 MHz. */
  RCC->CR = (RCC->CR & ~RCC_CR_HSIDIV) | (0u << RCC_CR_HSIDIV_Pos);
  /* oscilador dedicado do USB, aparado pelo CRS a partir do SOF (sem cristal) */
  RCC->CR |= RCC_CR_HSIUSB48ON;
  while (!(RCC->CR & RCC_CR_HSIUSB48RDY)) {}
  RCC->CCIPR2 &= ~RCC_CCIPR2_USBSEL; /* USB <- HSIUSB48 */
  SystemCoreClockUpdate();

  RCC->IOPENR |= RCC_IOPENR_GPIOAEN;
  RCC->AHBENR |= RCC_AHBENR_DMA1EN;
  RCC->APBENR1 |= RCC_APBENR1_USBEN | RCC_APBENR1_CRSEN | RCC_APBENR1_PWREN;
  RCC->APBENR2 |= RCC_APBENR2_SPI1EN | RCC_APBENR2_SYSCFGEN;

  /* CRS: sincroniza no USB SOF (SYNCSRC = 10), RELOAD/FELIM de reset servem para 48 MHz/1 kHz */
  CRS->CFGR = (CRS->CFGR & ~CRS_CFGR_SYNCSRC) | CRS_CFGR_SYNCSRC_1;
  CRS->CR |= CRS_CR_AUTOTRIMEN | CRS_CR_CEN;

  SysTick_Config(SystemCoreClock / 1000u);
  NVIC_SetPriority(USB_DRD_FS_IRQn, 1);
}

void board_uid(uint8_t uid[12]) {
  const volatile uint8_t *p = (const volatile uint8_t *)UID_BASE;
  for (int i = 0; i < 12; i++) uid[i] = p[i];
}

/* ---- flash: só a página do NVM (0x0800F800). A CPU para durante a operação (banco único). ---- */
const uint8_t *board_nvm_page(void) { return _nvm_start; }
uint32_t board_nvm_size(void) { return 2048u; }

static bool flash_wait(void) {
  while (FLASH->SR & (FLASH_SR_BSY1 | FLASH_SR_CFGBSY)) {}
  uint32_t err = FLASH->SR & (FLASH_SR_OPERR | FLASH_SR_PROGERR | FLASH_SR_WRPERR | FLASH_SR_PGAERR |
                              FLASH_SR_SIZERR | FLASH_SR_PGSERR | FLASH_SR_MISERR | FLASH_SR_FASTERR);
  FLASH->SR = err | FLASH_SR_EOP; /* limpa (rc_w1) */
  return err == 0;
}
static void flash_unlock(void) {
  if (FLASH->CR & FLASH_CR_LOCK) { FLASH->KEYR = 0x45670123u; FLASH->KEYR = 0xCDEF89ABu; }
}
static void flash_lock(void) { FLASH->CR |= FLASH_CR_LOCK; }

bool board_flash_erase_nvm(void) {
  uint32_t page = ((uint32_t)_nvm_start - FLASH_BASE) / 2048u;
  __disable_irq();
  flash_unlock();
  bool ok = flash_wait();
  FLASH->CR = (FLASH->CR & ~FLASH_CR_PNB) | FLASH_CR_PER | (page << FLASH_CR_PNB_Pos);
  FLASH->CR |= FLASH_CR_STRT;
  ok = flash_wait() && ok;
  FLASH->CR &= ~(FLASH_CR_PER | FLASH_CR_PNB);
  flash_lock();
  __enable_irq();
  return ok;
}

bool board_flash_prog64_nvm(uint32_t off, uint64_t v) {
  if (off & 7u || off + 8u > 2048u) return false;
  volatile uint32_t *dst = (volatile uint32_t *)(_nvm_start + off);
  __disable_irq();
  flash_unlock();
  bool ok = flash_wait();
  FLASH->CR |= FLASH_CR_PG;
  dst[0] = (uint32_t)v;
  __ISB();
  dst[1] = (uint32_t)(v >> 32);
  ok = flash_wait() && ok;
  FLASH->CR &= ~FLASH_CR_PG;
  flash_lock();
  __enable_irq();
  return ok;
}

void HardFault_Handler(void) { NVIC_SystemReset(); }
void _init(void) {}

/* ---- option bytes: nBOOT_SEL = 0 para o JP1 (PA14/BOOT0) escolher o boot ----
 * Desligado por padrão (SIGNA_AUTO_NBOOT_SEL=0): o caminho recomendado é um passo único com o
 * STM32CubeProgrammer (docs/README.md). Com =1, o firmware faz isso sozinho no 1º boot e reinicia.
 * Só limpa o bit nBOOT_SEL; o resto do OPTR (RDP, BOR, nRST_MODE...) é regravado igual. */
void board_apply_option_bytes(void) {
#if defined(SIGNA_AUTO_NBOOT_SEL) && SIGNA_AUTO_NBOOT_SEL
  if (!(FLASH->OPTR & FLASH_OPTR_nBOOT_SEL)) return;
  __disable_irq();
  flash_unlock();
  if (FLASH->CR & FLASH_CR_OPTLOCK) { FLASH->OPTKEYR = 0x08192A3Bu; FLASH->OPTKEYR = 0x4C5D6E7Fu; }
  if (!flash_wait()) { flash_lock(); __enable_irq(); return; }
  FLASH->OPTR &= ~FLASH_OPTR_nBOOT_SEL;
  FLASH->CR |= FLASH_CR_OPTSTRT;
  if (flash_wait()) FLASH->CR |= FLASH_CR_OBL_LAUNCH; /* recarrega os option bytes = reset */
  flash_lock();
  __enable_irq();
#endif
}
