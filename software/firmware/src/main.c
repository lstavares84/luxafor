/* SIGNA rev C — firmware. Laço único sem RTOS: USB (TinyUSB), motor de 1 ms, quadro dos LEDs a cada 2 ms.
 *
 * Gravação por USB (DFU da ROM, AN2606): com a flash vazia o chip entra sozinho no bootloader.
 * Depois da 1ª gravação, para o JP1 (PA14/BOOT0 a 3V3) voltar a funcionar é preciso
 * nBOOT_SEL = 0 nos option bytes (ver docs/README.md, "Option bytes"). O firmware não mexe
 * nos option bytes: é um passo único de fábrica, feito pelo STM32CubeProgrammer.
 */
#include "board.h"
#include "engine.h"
#include "nvm.h"
#include "tusb.h"
#include "ws2816.h"

void usb_set_serial(const uint8_t s[6]);

#define FRAME_MS 2u

static void on_serial_changed(const uint8_t s[6]) { nvm_serial_request_write(s); }

int main(void) {
  board_init();
  board_apply_option_bytes();
  uint8_t serial[6];
  nvm_serial_boot(serial);
  usb_set_serial(serial); /* o descritor mostra o serial do boot, como no Flag */
  const engine_hooks_t hooks = {on_serial_changed};
  engine_init(serial, &hooks);
  ws2816_init();
  tusb_init();

  uint32_t last = board_millis(), last_frame = 0;
  bool frame_pending = true;
  for (;;) {
    tud_task();

    uint32_t now = board_millis();
    while ((int32_t)(now - last) > 0) { engine_tick_1ms(); last++; }

    if (engine_output_dirty()) frame_pending = true;
    if (frame_pending && (now - last_frame) >= FRAME_MS && !ws2816_busy()) {
      uint16_t rgb[SIGNA_NLEDS][3];
      engine_output16(rgb);
      if (ws2816_show(rgb)) { frame_pending = false; last_frame = now; }
    }

    if (tud_hid_ready()) {
      uint8_t r[SIGNA_REPORT_LEN];
      if (engine_pop_report(r)) tud_hid_report(0, r, sizeof r);
    }
    nvm_task();
  }
}

/* ---- callbacks TinyUSB ---- */
void tud_hid_set_report_cb(uint8_t instance, uint8_t report_id, hid_report_type_t type, const uint8_t *buf, uint16_t len) {
  (void)instance; (void)report_id; (void)type;
  uint8_t r[SIGNA_REPORT_LEN] = {0};
  if (len > SIGNA_REPORT_LEN) len = SIGNA_REPORT_LEN;
  for (uint16_t i = 0; i < len; i++) r[i] = buf[i];
  engine_handle_report(r);
}

uint16_t tud_hid_get_report_cb(uint8_t instance, uint8_t report_id, hid_report_type_t type, uint8_t *buf, uint16_t reqlen) {
  (void)instance; (void)report_id; (void)type; (void)buf; (void)reqlen;
  return 0; /* STALL: o host lê pelo endpoint IN */
}

void USB_DRD_FS_IRQHandler(void) { tusb_int_handler(0, true); }
