/* Descritores USB do SIGNA: 1 interface HID vendor 0xFF00, 8 bytes IN + 8 bytes OUT, sem Report ID,
 * EP 0x81/0x01 interrupt 1 ms, Full Speed, 100 mA — o mesmo envelope do Luxafor Flag. */
#include <string.h>
#include "tusb.h"
#include "usb_ids.h"

static char serial_str[13] = "000000000000";

void usb_set_serial(const uint8_t s[6]) {
  static const char hx[] = "0123456789ABCDEF";
  for (int i = 0; i < 6; i++) { serial_str[2 * i] = hx[s[i] >> 4]; serial_str[2 * i + 1] = hx[s[i] & 15]; }
  serial_str[12] = 0;
}

static const tusb_desc_device_t desc_device = {
  .bLength = sizeof(tusb_desc_device_t),
  .bDescriptorType = TUSB_DESC_DEVICE,
  .bcdUSB = 0x0200,
  .bDeviceClass = 0, .bDeviceSubClass = 0, .bDeviceProtocol = 0,
  .bMaxPacketSize0 = CFG_TUD_ENDPOINT0_SIZE,
  .idVendor = SIGNA_USB_VID,
  .idProduct = SIGNA_USB_PID,
  .bcdDevice = SIGNA_USB_BCD,
  .iManufacturer = 1, .iProduct = 2, .iSerialNumber = 3,
  .bNumConfigurations = 1,
};
const uint8_t *tud_descriptor_device_cb(void) { return (const uint8_t *)&desc_device; }

static const uint8_t desc_hid_report[] = {
  0x06, 0x00, 0xFF,  /* Usage Page (Vendor 0xFF00) */
  0x09, 0x01,        /* Usage (1) */
  0xA1, 0x01,        /* Collection (Application) */
  0x15, 0x00,        /*   Logical Minimum (0) */
  0x26, 0xFF, 0x00,  /*   Logical Maximum (255) */
  0x75, 0x08,        /*   Report Size (8) */
  0x95, 0x08,        /*   Report Count (8) */
  0x09, 0x01,        /*   Usage (1) */
  0x81, 0x02,        /*   Input (Data,Var,Abs) */
  0x95, 0x08,        /*   Report Count (8) */
  0x09, 0x01,        /*   Usage (1) */
  0x91, 0x02,        /*   Output (Data,Var,Abs) */
  0xC0               /* End Collection */
};
const uint8_t *tud_hid_descriptor_report_cb(uint8_t instance) { (void)instance; return desc_hid_report; }

#define CONFIG_TOTAL_LEN (TUD_CONFIG_DESC_LEN + TUD_HID_INOUT_DESC_LEN)
static const uint8_t desc_configuration[] = {
  TUD_CONFIG_DESCRIPTOR(1, 1, 0, CONFIG_TOTAL_LEN, 0, 100),
  TUD_HID_INOUT_DESCRIPTOR(0, 0, HID_ITF_PROTOCOL_NONE, sizeof(desc_hid_report), 0x01, 0x81, 8, 1),
};
const uint8_t *tud_descriptor_configuration_cb(uint8_t index) { (void)index; return desc_configuration; }

static uint16_t desc_str[32 + 1];
const uint16_t *tud_descriptor_string_cb(uint8_t index, uint16_t langid) {
  (void)langid;
  const char *s;
  switch (index) {
    case 0: desc_str[1] = 0x0409; desc_str[0] = (uint16_t)((TUSB_DESC_STRING << 8) | 4); return desc_str;
    case 1: s = SIGNA_USB_MANUFACTURER; break;
    case 2: s = SIGNA_USB_PRODUCT; break;
    case 3: s = serial_str; break;
    default: return NULL;
  }
  size_t n = strlen(s);
  if (n > 32) n = 32;
  for (size_t i = 0; i < n; i++) desc_str[1 + i] = (uint8_t)s[i];
  desc_str[0] = (uint16_t)((TUSB_DESC_STRING << 8) | (2 * n + 2));
  return desc_str;
}
