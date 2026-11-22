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
    "U1": ("MCU_ST_STM32C0", "STM32C071G8Ux", "STM32C071G8U6",
           "Package_DFN_QFN:QFN-28_4x4mm_P0.5mm", "C44521811",
           {"3": "+3V3", "4": "GND", "5": "NRST", "13": "LED_DIN_3V3",
            "18": "USB_DM", "19": "USB_DP", "20": "SWDIO", "21": "SWCLK_BOOT0",
            "1": None, "2": None, "6": None, "7": None, "8": None, "9": None,
            "10": None, "11": None, "12": None, "14": None, "15": None, "16": None,
            "17": None, "22": None, "23": None, "24": None, "25": None, "26": None,
            "27": None, "28": None},
           (190.5, 81.28)),
    "C3": ("Device", "C", "100nF", "Capacitor_SMD:C_0402_1005Metric", "C1525",
           {"1": "+3V3", "2": "GND"}, (157.48, 60.96)),
    "C4": ("Device", "C", "100nF", "Capacitor_SMD:C_0402_1005Metric", "C1525",
           {"1": "NRST", "2": "GND"}, (226.06, 60.96)),
    # --- Conversor de nível 3,3 V -> 5 V para os LEDs -------------------------
    "U3": ("74xGxx", "74AHCT1G125", "SN74AHCT1G125DBVR",
           "Package_TO_SOT_SMD:SOT-23-5", "C7484",
           {"1": "GND", "2": "LED_DIN_3V3", "3": "GND", "4": "LED_DIN_5V",
            "5": "VBUS"}, (55.88, 134.62)),
    "C5": ("Device", "C", "100nF", "Capacitor_SMD:C_0402_1005Metric", "C1525",
           {"1": "VBUS", "2": "GND"}, (30.48, 134.62)),
    "R3": ("Device", "R", "33", "Resistor_SMD:R_0402_1005Metric", "C25105",
           {"1": "LED_DIN_5V", "2": "LED1_DIN"}, (86.36, 134.62)),
    # --- LEDs WS2816B-2020: 1 = baixo, 2 = meio, 3 = topo; DI/DO + BI/BO (BI do 1º no GND) ---
    "D1": ("indicador", "WS2816B-2020", "WS2816B-2020",
           "indicador:LED_WS2816B-2020_2.2x2.0mm", "C4154877",
           {"3": "VBUS", "6": "GND", "2": "LED1_DIN", "1": "GND", "4": "LED2_DIN", "5": "LED2_BIN"},
           (116.84, 134.62)),
    "D2": ("indicador", "WS2816B-2020", "WS2816B-2020",
           "indicador:LED_WS2816B-2020_2.2x2.0mm", "C4154877",
           {"3": "VBUS", "6": "GND", "2": "LED2_DIN", "1": "LED2_BIN", "4": "LED3_DIN", "5": "LED3_BIN"},
           (162.56, 134.62)),
    "D3": ("indicador", "WS2816B-2020", "WS2816B-2020",
           "indicador:LED_WS2816B-2020_2.2x2.0mm", "C4154877",
           {"3": "VBUS", "6": "GND", "2": "LED3_DIN", "1": "LED3_BIN", "4": None, "5": None},
           (208.28, 134.62)),
    "C6": ("Device", "C", "100nF", "Capacitor_SMD:C_0402_1005Metric", "C1525",
           {"1": "VBUS", "2": "GND"}, (132.08, 154.94)),
    "C7": ("Device", "C", "100nF", "Capacitor_SMD:C_0402_1005Metric", "C1525",
           {"1": "VBUS", "2": "GND"}, (177.8, 154.94)),
    "C8": ("Device", "C", "100nF", "Capacitor_SMD:C_0402_1005Metric", "C1525",
           {"1": "VBUS", "2": "GND"}, (223.52, 154.94)),
    # --- SWD: Tag-Connect TC2030-IDC-NL (face de baixo, sem componente) -------
    # pinagem TC2030-CTX: 1 VCC, 2 SWDIO, 3 nRESET, 4 SWCLK, 5 GND, 6 SWO (NC)
    "J2": ("Connector_Generic", "Conn_01x06", "TC2030-SWD",
           "Connector:Tag-Connect_TC2030-IDC-NL_2x03_P1.27mm_Vertical", "",
           {"1": "+3V3", "2": "SWDIO", "3": "NRST", "4": "SWCLK_BOOT0", "5": "GND",
            "6": None}, (254.0, 76.2)),
    # --- BOOT0 (PA14) para o bootloader DFU: jumper de solda NA + 1k p/ 3V3 -----
    "R4": ("Device", "R", "1k", "Resistor_SMD:R_0402_1005Metric", "C11702",
           {"1": "+3V3", "2": "BOOT_PU"}, (231.14, 101.6)),
    "JP1": ("Jumper", "SolderJumper_2_Open", "BOOT0",
            "Jumper:SolderJumper-2_P1.3mm_Open_RoundedPad1.0x1.5mm", "",
            {"1": "BOOT_PU", "2": "SWCLK_BOOT0"}, (246.38, 101.6)),
    # --- rev D: botão lateral (OCUPADO/LIVRE em uso; BOOT0/DFU ao ligar) --------
    # S1 em paralelo com JP1: fechado, puxa PA14/SWCLK/BOOT0 a 3V3 por R4 (1k) + R5 (1k).
    # R5 em série protege o pino do MCU (ESD vindo pelo botão) sem pôr capacitância no SWCLK.
    "S1": ("Switch", "SW_Push", "SKRTLAE010",
           "indicador:SW_SKRTLAE010_JLC", "C110293",
           {"1": "BOOT_PU", "2": "BTN"}, (231.14, 121.92)),
    "R5": ("Device", "R", "1k", "Resistor_SMD:R_0402_1005Metric", "C11702",
           {"1": "BTN", "2": "SWCLK_BOOT0"}, (254.0, 121.92)),
    # --- rev D: pontos de teste (face de baixo, sem componente) ----------------
    "TP1": ("Connector", "TestPoint", "VBUS", "TestPoint:TestPoint_Pad_D1.0mm", "",
            {"1": "VBUS"}, (271.78, 50.8)),
    "TP2": ("Connector", "TestPoint", "LED_DIN", "TestPoint:TestPoint_Pad_D1.0mm", "",
            {"1": "LED_DIN_5V"}, (271.78, 63.5)),
    "TP3": ("Connector", "TestPoint", "GND", "TestPoint:TestPoint_Pad_D1.0mm", "",
            {"1": "GND"}, (271.78, 76.2)),
    # --- Bandeiras de alimentação (só esquemático) ---------------------------
    "#FLG01": ("power", "PWR_FLAG", "PWR_FLAG", "", "", {"1": "VBUS"}, (25.4, 30.48)),
    "#FLG02": ("power", "PWR_FLAG", "PWR_FLAG", "", "", {"1": "GND"}, (40.64, 30.48)),
}

LIB_PATHS = {"indicador": None}  # resolvido em relação a hardware/lib
