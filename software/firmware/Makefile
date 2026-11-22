# SIGNA rev C firmware — make            (gera build/signa.elf/.bin/.hex)
#                        make test       (testes de host com ASan/UBSan)
#                        make USB_IDS=luxafor   (04d8:f372, só protótipo pessoal)
#                        make AUTO_NBOOT_SEL=1  (firmware zera nBOOT_SEL no 1º boot)
PREFIX ?= arm-none-eabi-
CC = $(PREFIX)gcc
OBJCOPY = $(PREFIX)objcopy
SIZE = $(PREFIX)size
TP = third_party
TUSB = $(TP)/tinyusb/src
B = build

SRC = src/main.c src/board.c src/engine.c src/signa_tables.c src/ws2816.c src/ws2816_encode.c \
      src/nvm.c src/nvm_log.c src/usb_descriptors.c \
      $(TP)/cmsis-device-c0/Source/Templates/system_stm32c0xx.c \
      $(TUSB)/tusb.c $(TUSB)/common/tusb_fifo.c $(TUSB)/device/usbd.c \
      $(TUSB)/class/hid/hid_device.c \
      $(TUSB)/portable/st/stm32_fsdev/dcd_stm32_fsdev.c $(TUSB)/portable/st/stm32_fsdev/fsdev_common.c
ASM = $(TP)/cmsis-device-c0/Source/Templates/gcc/startup_stm32c071xx.s

DEFS = -DSTM32C071xx -DCFG_TUSB_MCU=OPT_MCU_STM32C0
ifeq ($(AUTO_NBOOT_SEL),1)
DEFS += -DSIGNA_AUTO_NBOOT_SEL=1
endif
ifeq ($(USB_IDS),luxafor)
DEFS += -DSIGNA_IDS_LUXAFOR
endif
INC = -Isrc -I$(TUSB) -I$(TP)/cmsis-device-c0/Include -I$(TP)/CMSIS_5/CMSIS/Core/Include
CPU = -mcpu=cortex-m0plus -mthumb
CFLAGS = $(CPU) -std=gnu11 -Os -g3 -Wall -Wextra -ffunction-sections -fdata-sections -fno-common $(DEFS) $(INC)
LDFLAGS = $(CPU) -Tld/stm32c071g8.ld -Wl,--gc-sections -Wl,-Map=$(B)/signa.map -nostartfiles \
          --specs=nano.specs --specs=nosys.specs -Wl,--print-memory-usage

OBJ = $(patsubst %.c,$(B)/%.o,$(SRC)) $(patsubst %.s,$(B)/%.o,$(ASM))

all: $(B)/signa.bin $(B)/signa.hex
	@$(SIZE) $(B)/signa.elf

$(B)/%.o: %.c
	@mkdir -p $(dir $@)
	$(CC) $(CFLAGS) -c $< -o $@
$(B)/%.o: %.s
	@mkdir -p $(dir $@)
	$(CC) $(CPU) -c $< -o $@
$(B)/signa.elf: $(OBJ) ld/stm32c071g8.ld
	$(CC) $(LDFLAGS) $(OBJ) -o $@
$(B)/signa.bin: $(B)/signa.elf
	$(OBJCOPY) -O binary $< $@
$(B)/signa.hex: $(B)/signa.elf
	$(OBJCOPY) -O ihex $< $@

tables:
	python3 tools/gen_tables.py
test:
	$(MAKE) -C tests run

# Gravação (ver docs/README.md)
flash-dfu: $(B)/signa.bin
	dfu-util -a 0 -d 0483:df11 -s 0x08000000:leave -D $<
flash-swd: $(B)/signa.elf
	openocd -f interface/stlink.cfg -f target/stm32c0x.cfg -c "program $< verify reset exit"

clean:
	rm -rf $(B)
	$(MAKE) -C tests clean
.PHONY: all tables test flash-dfu flash-swd clean
