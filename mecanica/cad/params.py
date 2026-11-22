"""SIGNA Pendente rev B (placa SIGNA rev D) - parametros unicos (mm).
Base: LUXCLONE Pendente rev A (Pendente rev A, fonte original fora deste repositório). Mudancas rev B: placa rev D (botao S1 na
borda de baixo, LEDs +2,2 mm), botao P06 atraves do tampao, rebaixo na flange para o plugue,
cabo USB-C realista (plugue oco + lingua do receptaculo) para checar o encaixe.
Sistema de coordenadas do produto: Z para cima (tampa em cima), Y para a frente
(lado dos LEDs, oposto ao monitor), X lateral. Z=0 = face inferior do tampao.
"""
REV = "B"
DATE = "2026-11-22"

# ---- placa rev D (fonte: luxpcb-revD/project/luxflag.kicad_pcb) ----
PCB_W, PCB_L, PCB_T = 11.0, 44.0, 0.8
USB_OVERHANG = 0.65          # receptaculo passa da borda (modelo HRO, lib/3d)
USB_TOP = 3.26               # altura da carcaca USB-C acima da face superior (HRO TYPE-C-31-M-12)
LED_FROM_EDGE = (5.2, 12.2, 19.2)   # rev D: +2,2 mm (botao S1 na borda)
LED_H = 0.84                 # WS2816B-2020: 2,2 x 2,0 x 0,84 (datasheet C4154877)
PCB_Y0 = -2.40               # face inferior da placa em Y (eixo do USB-C ~ no eixo do tubo)
# rev D: orelhas no topo da placa (|x| 7,6, altura 1,0) apoiam no fundo das fendas da flange e
# ficam sob o ressalto da tampa (Z 52,0) com folga 0,25 -> batente axial (peso, botao, extracao do cabo)
EAR_X_OUT, EAR_H, EAR_GAP_TOP = 7.6, 1.0, 0.25
EAR_SLOT_X_OUT = 7.75        # fundo lateral da fenda da orelha na flange
PCB_Z0 = 50.0 + 2.0 - EAR_GAP_TOP - 44.0   # = 7,75 (FLANGE_Z0 + FLANGE_T - folga - PCB_L)
GROOVE_FLOOR_GAP = 0.30      # a borda de baixo da placa NAO apoia (o batente e a orelha)

# ---- botao (rev D): S1 ALPS SKRTLAE010 na borda de baixo, face dos LEDs ----
SW_STEM_H = 1.70             # eixo da haste acima da face da placa (datasheet)
SW_STEM_OUT = 0.24           # haste passa da borda da placa (S1 em y=1,8 na placa)
SW_TRAVEL = 0.20             # curso eletrico (datasheet)
SW_BODY = (4.5, 3.3)         # largura x altura do corpo
USB_AXIS_H = USB_TOP / 2     # eixo da boca USB-C acima da face da placa

# ---- P06 botao (PC opalino, injetado / SLA) atraves do tampao ----
BTN_SHAFT_D, BTN_HOLE_D = 3.0, 3.2     # haste / furo no tampao (folga radial 0,1)
BTN_COLLAR_D, BTN_CB_D = 4.4, 4.8      # colar de retencao / rebaixo no topo do tampao
BTN_CB_DEPTH = 1.0
BTN_COLLAR_T = 0.7
BTN_PUSH_D = 2.2                        # empurrador (toca a haste Ø2 do S1)
BTN_PROUD = 0.30                        # quanto o botao sai abaixo do tampao (achar no tato)
BTN_GAP = 0.40                          # folga nominal empurrador-haste (tubo +/-0,2 e placa +/-0,2 -> 0,0..0,8)

# ---- tubo difusor (PC opalino extrudado) ----
TUBE_OD, TUBE_ID = 16.0, 13.0
TUBE_Z0 = 2.0
TUBE_L = 48.0                # Z 2..50
TUBE_ID_TOL = 0.15           # tolerancia tipica de tubo extrudado (+/-)

# ---- tampao inferior (PC opalino, injetado / SLA) ----
PLUG_FL_D, PLUG_FL_T = 16.0, 2.0
PLUG_SPIG_D, PLUG_SPIG_L = 12.85, 3.7   # 0,3 abaixo do berco: o tampao sempre aperta o tubo (absorve tolerancia de comprimento)
PLUG_EDGE_R = 0.8
POST_D, POST_POS = 3.0, (0.0, -4.4)     # pino do berco (press-fit com nervuras)
SOCKET_D, SOCKET_DEPTH = 2.9, 3.8

# ---- berco / espinha (PC branco refletivo) ----
CAR_R = 6.30                 # envelope (folga radial 0,2 no tubo)
CAR_Z0 = 6.0
FLANGE_D, FLANGE_T = 16.0, 2.0
FLANGE_Z0 = TUBE_Z0 + TUBE_L # 50
GROOVE_W = PCB_T + 0.10      # ranhura da placa 0,90
GROOVE_X_IN = 5.00           # inicio da ranhura (|x|)
GROOVE_X_OUT = PCB_W / 2 + 0.15
LIP_X = 5.25                 # labio sobre a face superior (evita pads de U3)
RAIL_Y_TOP = -0.90
SNAP_R = 8.45                # ressalto do encaixe (ranhura da tampa r=8,5)
SNAP_W, SNAP_H = 3.0, 0.7

# ---- tampa (Al 6061-T6 anodizado preto) ----
CAP_OD = 19.0
CAP_Z0 = 46.0                # tubo entra 4 mm
CAP_L = 32.0                 # Z 46..78
CB_D = 16.25                 # rebaixo do tubo (tubo 16 +/-0,15)
CB_DEPTH = 6.0               # 4 (tubo) + 2 (flange)
SNAP_GROOVE_D, SNAP_GROOVE_W = 17.0, 0.8
BORE_D = 13.6                # cavidade do plugue USB-C do cabo
TOP_HOLE_D = 12.8            # passa um plugue padrao (<= 12,3 x 6,8)
TOP_WALL = 3.5
CAP_TOP_R = 1.5
CAP_BOT_CH = 0.3
# variante impressa (MJF PA12 / SLA): folgas extras
PRINT_EXTRA = 0.12

# ---- passa-cabo (TPE 60A bipartido) ----
GR_BODY_D = TOP_HOLE_D - 0.1
GR_BARB_D, GR_BARB_H = 13.5, 1.0
GR_FL_D, GR_FL_T = 15.0, 1.2
GR_BOOT_L, GR_BOOT_D0, GR_BOOT_D1 = 9.0, 8.0, 5.6
GR_CABLE_D = 3.3            # rev B: aperta cabos de Ø3,5 a Ø4,0 (era 3,6)
GR_BOOT_RELIEF_D = 6.4       # aceita o alivio do plugue do cabo
GR_SLIT = 0.3


# ---- cabo USB-C tipico (C01, comprado; modelo de referencia) ----
PLUG_BODY = (11.6, 6.4, 17.0) # sobremolde (L x E x C), cantos r 2,8 (passa no furo Ø12,8)
PLUG_BODY_R = 2.8
PLUG_SHELL = (8.25, 2.4, 6.65) # casca do plugue USB-C (spec), comprimento exposto
PLUG_CAV = (6.95, 1.0)        # abertura interna do plugue (recebe a lingua 6,69 x 0,70)
PLUG_DEPTH = 6.20             # insercao nominal da casca no receptaculo
REC_CAV = (8.34, 2.56, 6.60)  # cavidade do receptaculo (spec USB-C) e profundidade no modelo HRO
REC_TONGUE = (6.69, 0.70, 1.0) # lingua L x E, recuo da ponta em relacao a boca
BOOT = (6.0, 4.2, 7.0)        # alivio de tensao: Ø base, Ø ponta, comprimento
CABLE_D = 3.8                 # capa do cabo

# derivados
TUBE_TOP = TUBE_Z0 + TUBE_L
PCB_TOP_Z = PCB_Z0 + PCB_L
USB_MOUTH_Z = PCB_TOP_Z + USB_OVERHANG
CAP_TOP = CAP_Z0 + CAP_L
BORE_Z0 = FLANGE_Z0 + FLANGE_T
BORE_Z1 = CAP_TOP - TOP_WALL

# derivados rev B
PLUG_TOP = PLUG_FL_T + PLUG_SPIG_L               # 5,7
PCB_FRONT_Y = PCB_Y0 + PCB_T                     # face dos componentes
BTN_Y = PCB_FRONT_Y + SW_STEM_H                  # eixo do botao / haste do S1
SW_TIP_Z = PCB_Z0 - SW_STEM_OUT                  # ponta da haste do S1
USB_Y = PCB_FRONT_Y + USB_AXIS_H                 # eixo do plugue
CABLE_Z0 = CAP_TOP - 2.5                         # inicio da capa do cabo (dentro do alivio)
CABLE_RISE = 150.0                               # Z onde o cabo comeca a curvar (borda do monitor)
