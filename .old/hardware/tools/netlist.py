"""Fonte única da verdade do circuito: componentes, footprints, LCSC e ligações.

Usado por gen_sch.py (esquemático KiCad) e gen_pcb.py (placa).
Pinos são referenciados pelo NÚMERO do pino no símbolo/footprint.
"""

STD = "/usr/share/kicad/symbols/"

# ref: (lib, símbolo, valor, footprint, lcsc, {pino: rede | None=NC}, posição no esquemático)
PARTS = {
    # --- Entrada USB-C ------------------------------------------------------
    "J1": ("Connector", "USB_C_Receptacle_USB2.0_16P", "USB-C",
           "Connector_USB:USB_C_Receptacle_HRO_TYPE-C-31-M-12", "C165948",
           {"S1": "GND", "A1": "GND", "A4": "VBUS", "A5": "CC1", "B5": "CC2",
            "A7": "USB_DM", "B7": "USB_DM", "A6": "USB_DP", "B6": "USB_DP",
            "A8": None, "B8": None}, (40.64, 76.2)),
    "R1": ("Device", "R", "5.1k", "Resistor_SMD:R_0402_1005Metric", "C25905",
           {"1": "CC1", "2": "GND"}, (76.2, 60.96)),
    "R2": ("Device", "R", "5.1k", "Resistor_SMD:R_0402_1005Metric", "C25905",
           {"1": "CC2", "2": "GND"}, (86.36, 60.96)),
    "U4": ("Power_Protection", "USBLC6-2SC6", "USBLC6-2SC6",
           "Package_TO_SOT_SMD:SOT-23-6", "C7519",
           {"1": "USB_DP", "6": "USB_DP", "3": "USB_DM", "4": "USB_DM",
            "5": "VBUS", "2": "GND"}, (81.28, 99.06)),
    "C1": ("Device", "C", "10uF", "Capacitor_SMD:C_0603_1608Metric", "C19702",
           {"1": "VBUS", "2": "GND"}, (101.6, 60.96)),
    # --- Regulador 3,3 V ----------------------------------------------------
    "U2": ("Regulator_Linear", "AP2112K-3.3", "AP2112K-3.3",
           "Package_TO_SOT_SMD:SOT-23-5", "C51118",
           {"1": "VBUS", "3": "VBUS", "2": "GND", "5": "+3V3"}, (124.46, 60.96)),
    "C2": ("Device", "C", "1uF", "Capacitor_SMD:C_0402_1005Metric", "C52923",
           {"1": "+3V3", "2": "GND"}, (147.32, 60.96)),
    # --- MCU ----------------------------------------------------------------
    "U1": ("MCU_ST_STM32C0", "STM32C071F8Px", "STM32C071F8P6",
           "Package_SO:TSSOP-20_4.4x6.5mm_P0.65mm", "C43650205",
           {"4": "+3V3", "5": "GND", "6": "NRST", "14": "LED_DIN_3V3",
            "16": "USB_DM", "17": "USB_DP", "18": "SWDIO", "19": "SWCLK",
            "1": None, "2": None, "3": None, "7": None, "8": None, "9": None,
            "10": None, "11": None, "12": None, "13": None, "15": None, "20": None},
           (190.5, 81.28)),
    "C3": ("Device", "C", "100nF", "Capacitor_SMD:C_0402_1005Metric", "C1525",
           {"1": "+3V3", "2": "GND"}, (157.48, 60.96)),
    "C4": ("Device", "C", "100nF", "Capacitor_SMD:C_0402_1005Metric", "C1525",
           {"1": "NRST", "2": "GND"}, (226.06, 60.96)),
    # --- Conversor de nível 3,3 V -> 5 V para os LEDs -------------------------
    "U3": ("74xGxx", "74AHCT1G125", "74AHCT1G125",
           "Package_TO_SOT_SMD:SOT-353_SC-70-5", "C53114384",
           {"1": "GND", "2": "LED_DIN_3V3", "3": "GND", "4": "LED_DIN_5V",
            "5": "VBUS"}, (55.88, 134.62)),
    "C5": ("Device", "C", "100nF", "Capacitor_SMD:C_0402_1005Metric", "C1525",
           {"1": "VBUS", "2": "GND"}, (30.48, 134.62)),
    "R3": ("Device", "R", "33", "Resistor_SMD:R_0402_1005Metric", "C25105",
           {"1": "LED_DIN_5V", "2": "LED1_DIN"}, (86.36, 134.62)),
    # --- LEDs: 1 = baixo, 2 = meio, 3 = topo (cadeia na mesma ordem) ----------
    "D1": ("indicador", "SK6805-EC20", "SK6805-EC20",
           "indicador:LED_SK6805-EC20_2.0x2.0mm", "C2890036",
           {"1": "VBUS", "3": "GND", "4": "LED1_DIN", "2": "LED2_DIN"}, (116.84, 134.62)),
    "D2": ("indicador", "SK6805-EC20", "SK6805-EC20",
           "indicador:LED_SK6805-EC20_2.0x2.0mm", "C2890036",
           {"1": "VBUS", "3": "GND", "4": "LED2_DIN", "2": "LED3_DIN"}, (162.56, 134.62)),
    "D3": ("indicador", "SK6805-EC20", "SK6805-EC20",
           "indicador:LED_SK6805-EC20_2.0x2.0mm", "C2890036",
           {"1": "VBUS", "3": "GND", "4": "LED3_DIN", "2": None}, (208.28, 134.62)),
    "C6": ("Device", "C", "100nF", "Capacitor_SMD:C_0402_1005Metric", "C1525",
           {"1": "VBUS", "2": "GND"}, (132.08, 154.94)),
    "C7": ("Device", "C", "100nF", "Capacitor_SMD:C_0402_1005Metric", "C1525",
           {"1": "VBUS", "2": "GND"}, (177.8, 154.94)),
    "C8": ("Device", "C", "100nF", "Capacitor_SMD:C_0402_1005Metric", "C1525",
           {"1": "VBUS", "2": "GND"}, (223.52, 154.94)),
    # --- Pads SWD (face de baixo, sem componente montado) ----------------------
    "TP1": ("Connector", "TestPoint", "3V3", "TestPoint:TestPoint_Pad_D1.0mm", "",
            {"1": "+3V3"}, (254.0, 50.8)),
    "TP2": ("Connector", "TestPoint", "SWDIO", "TestPoint:TestPoint_Pad_D1.0mm", "",
            {"1": "SWDIO"}, (254.0, 63.5)),
    "TP3": ("Connector", "TestPoint", "SWCLK", "TestPoint:TestPoint_Pad_D1.0mm", "",
            {"1": "SWCLK"}, (254.0, 76.2)),
    "TP4": ("Connector", "TestPoint", "NRST", "TestPoint:TestPoint_Pad_D1.0mm", "",
            {"1": "NRST"}, (254.0, 88.9)),
    "TP5": ("Connector", "TestPoint", "GND", "TestPoint:TestPoint_Pad_D1.0mm", "",
            {"1": "GND"}, (254.0, 101.6)),
    # --- Bandeiras de alimentação (só esquemático) ---------------------------
    "#FLG01": ("power", "PWR_FLAG", "PWR_FLAG", "", "", {"1": "VBUS"}, (25.4, 30.48)),
    "#FLG02": ("power", "PWR_FLAG", "PWR_FLAG", "", "", {"1": "GND"}, (40.64, 30.48)),
}

LIB_PATHS = {"indicador": None}  # resolvido em relação a hardware/lib
