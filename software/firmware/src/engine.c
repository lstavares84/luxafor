/* SIGNA rev C — motor de protocolo e animação. Ver engine.h e docs/arquitetura.md.
 * Temporização do Luxafor Flag fw 0x3c (firmware_comportamento.md §5):
 *   fade   : 0,252 ms × tempo por degrau de brilho (|Δ| = max dos 3 canais)
 *   strobe : 65,5 ms × tempo por piscada (50 % aceso — duty a validar), restaura a cor anterior
 *   wave   : ~65 ms × vel por ciclo; só o tipo 5 manda 00 01
 *   rep = 0: infinito; qualquer comando de LED novo interrompe (consultas 00/62/80/1F não interrompem)
 */
#include "engine.h"
#include <string.h>


#define FADE_US_PER_STEP 252u
#define STROBE_US_PER_T 65500u
#define WAVE_US_PER_V 65000u
#define QMAX 65535u
#define C8(x) ((uint16_t)((x) * 257u)) /* 8 bit -> 16 bit linear (255 -> 65535) */

enum { A_NONE, A_FADE, A_STROBE, A_WAVE, A_PATTERN, A_SIGNA };

static const uint16_t PATTERN_MS[9] = {0, 2100, 3600, 11500, 15800, 900, 2600, 1350, 3500};

static struct {
  uint16_t disp[SIGNA_NLEDS][3]; /* cor exibida, 16 bit antes da gamma */
  uint16_t base[SIGNA_NLEDS][3]; /* cor a restaurar no fim de strobe/wave/padrão */
  uint16_t from[SIGNA_NLEDS][3], to[SIGNA_NLEDS][3];
  uint8_t kind, mask, sub, col[3];
  bool infinite, event_at_end;
  uint16_t reps;
  uint32_t el_us, dur_us, period_us;
  /* SIGNA */
  bool mixed;
  uint8_t st_all, st_sala, st_ia;
  uint32_t t_all, t_sala, t_ia;
  uint8_t bright;
  bool dirty;
  uint8_t serial_cur[6], serial_boot[6];
  engine_hooks_t hooks;
  uint8_t q[8][SIGNA_REPORT_LEN];
  uint8_t qh, qt, qn;
} E;

/* ---------------- fila de relatórios IN ---------------- */
static void push(const uint8_t r[SIGNA_REPORT_LEN]) {
  if (E.qn >= 8) return; /* cheia: descarta (host não está lendo) */
  memcpy(E.q[E.qt], r, SIGNA_REPORT_LEN);
  E.qt = (uint8_t)((E.qt + 1) & 7);
  E.qn++;
}
static void push2(uint8_t a, uint8_t b) {
  uint8_t r[SIGNA_REPORT_LEN] = {a, b};
  push(r);
}
static void ack(void) { push2(SIGNA_ACK, 0); }
static void done_event(void) { push2(0x00, 0x01); }

bool engine_pop_report(uint8_t out[SIGNA_REPORT_LEN]) {
  if (!E.qn) return false;
  memcpy(out, E.q[E.qh], SIGNA_REPORT_LEN);
  E.qh = (uint8_t)((E.qh + 1) & 7);
  E.qn--;
  return true;
}

/* ---------------- utilidades ---------------- */
uint16_t signa_gamma16(uint16_t v) {
  uint32_t i = v >> 8, f = v & 0xFF;
  int32_t a = signa_gamma_lut[i], b = signa_gamma_lut[i + 1];
  return (uint16_t)(a + (((b - a) * (int32_t)f) >> 8));
}

static uint16_t scale_q12(uint16_t v, uint16_t q12) { return (uint16_t)(((uint32_t)v * q12) >> 12); }

uint16_t signa_state_level_q12(signa_state_t st, uint32_t t) {
  if ((unsigned)st >= SIGNA_ST_COUNT) return 0;
  const signa_state_desc_t *d = &signa_states[st];
  switch (d->wave) {
    case SIGNA_W_BREATH: {
      uint32_t x = t % d->period_ms;
      uint32_t idx = (x << 16) / d->period_ms; /* Q8.8 em 0..256 */
      uint32_t i = idx >> 8, f = idx & 0xFF;
      const uint16_t *tab = signa_breath_tab[d->table];
      int32_t a = tab[i], b = tab[i + 1];
      uint32_t shape = (uint32_t)(a + (((b - a) * (int32_t)f) >> 8));
      return (uint16_t)(d->lo_q12 + (((4096u - d->lo_q12) * shape) >> 12));
    }
    case SIGNA_W_PULSE:
      return (t % d->period_ms) < d->on_ms ? d->hi_q12 : d->lo_q12;
    case SIGNA_W_DOUBLE: {
      uint32_t tm = t % d->period_ms;
      bool p1 = tm < d->on_ms;
      bool p2 = tm >= (uint32_t)(d->on_ms + d->gap_ms) && tm < (uint32_t)(2u * d->on_ms + d->gap_ms);
      return (p1 || p2) ? d->hi_q12 : d->lo_q12;
    }
    default:
      return d->hi_q12;
  }
}

static void set_led(uint8_t led, uint16_t r, uint16_t g, uint16_t b) {
  if (E.disp[led][0] != r || E.disp[led][1] != g || E.disp[led][2] != b) E.dirty = true;
  E.disp[led][0] = r; E.disp[led][1] = g; E.disp[led][2] = b;
}
static void set_led8(uint8_t led, const uint8_t c[3], uint16_t lvl_q12) {
  set_led(led, scale_q12(C8(c[0]), lvl_q12), scale_q12(C8(c[1]), lvl_q12), scale_q12(C8(c[2]), lvl_q12));
}
static void render_state(uint8_t led, uint8_t st, uint32_t t) {
  const signa_state_desc_t *d = &signa_states[st];
  const uint8_t c[3] = {d->r, d->g, d->b};
  set_led8(led, c, signa_state_level_q12((signa_state_t)st, t));
}

/* HSV (h 0..1535, s=v=máx) -> RGB 8 bit */
static void hue(uint16_t h, uint8_t c[3]) {
  h %= 1536;
  uint8_t s = (uint8_t)(h & 255);
  switch (h >> 8) {
    case 0: c[0] = 255; c[1] = s; c[2] = 0; break;
    case 1: c[0] = (uint8_t)(255 - s); c[1] = 255; c[2] = 0; break;
    case 2: c[0] = 0; c[1] = 255; c[2] = s; break;
    case 3: c[0] = 0; c[1] = (uint8_t)(255 - s); c[2] = 255; break;
    case 4: c[0] = s; c[1] = 0; c[2] = 255; break;
    default: c[0] = 255; c[1] = 0; c[2] = (uint8_t)(255 - s); break;
  }
}
/* triângulo 0→1→0 em Q12 para fase p (Q16) */
static uint16_t tri_q12(uint32_t p16) {
  p16 &= 0xFFFF;
  uint32_t v = p16 < 0x8000 ? p16 * 2 : (0xFFFF - p16) * 2;
  return (uint16_t)(v >> 4);
}

/* ---------------- controle de animação ---------------- */
static void stop_anim(void) {
  if (E.kind == A_STROBE || E.kind == A_WAVE || E.kind == A_PATTERN) {
    /* interrompida: volta para a cor anterior, como no fim natural */
    for (uint8_t i = 0; i < SIGNA_NLEDS; i++) set_led(i, E.base[i][0], E.base[i][1], E.base[i][2]);
  }
  E.kind = A_NONE;
}
static void start_anim(uint8_t kind) {
  stop_anim();
  memcpy(E.base, E.disp, sizeof E.base);
  E.kind = kind;
  E.el_us = 0;
}
static void finish_anim(bool restore) {
  if (restore)
    for (uint8_t i = 0; i < SIGNA_NLEDS; i++) set_led(i, E.base[i][0], E.base[i][1], E.base[i][2]);
  bool ev = E.event_at_end;
  E.kind = A_NONE;
  if (ev) done_event();
}

/* Endereço de LED: 1,2,3,FF agem; 4–6, 0x41, 0x42 = ACK sem efeito (herança do Flag de 6 LEDs);
 * qualquer outro (inclusive 0x13, que trava o original) = silêncio. Nunca indexa com o valor cru. */
typedef enum { ADDR_OK, ADDR_NOP, ADDR_BAD } addr_t;
static addr_t decode_addr(uint8_t a, uint8_t *mask) {
  switch (a) {
    case 0x01: *mask = 1u << 0; return ADDR_OK;
    case 0x02: *mask = 1u << 1; return ADDR_OK;
    case 0x03: *mask = 1u << 2; return ADDR_OK;
    case 0xFF: *mask = 0x07; return ADDR_OK;
    case 0x04: case 0x05: case 0x06: case 0x41: case 0x42: *mask = 0; return ADDR_NOP;
    default: *mask = 0; return ADDR_BAD;
  }
}

static void cmd_static(uint8_t mask, const uint8_t *c) {
  stop_anim();
  for (uint8_t i = 0; i < SIGNA_NLEDS; i++)
    if (mask & (1u << i)) set_led(i, C8(c[0]), C8(c[1]), C8(c[2]));
}

static void cmd_fade(uint8_t mask, const uint8_t *c, uint8_t tempo) {
  stop_anim();
  uint32_t maxd = 0;
  for (uint8_t i = 0; i < SIGNA_NLEDS; i++) {
    if (!(mask & (1u << i))) continue;
    for (uint8_t k = 0; k < 3; k++) {
      int32_t d = (int32_t)(C8(c[k]) >> 8) - (int32_t)(E.disp[i][k] >> 8);
      if (d < 0) d = -d;
      if ((uint32_t)d > maxd) maxd = (uint32_t)d;
    }
  }
  if (maxd == 0 || tempo == 0) { /* cor-alvo = atual: termina na hora */
    cmd_static(mask, c);
    done_event();
    return;
  }
  start_anim(A_FADE);
  E.mask = mask;
  memcpy(E.from, E.disp, sizeof E.from);
  for (uint8_t i = 0; i < SIGNA_NLEDS; i++)
    for (uint8_t k = 0; k < 3; k++) E.to[i][k] = (mask & (1u << i)) ? C8(c[k]) : E.disp[i][k];
  E.dur_us = maxd * tempo * FADE_US_PER_STEP;
  E.event_at_end = true;
}

static void cmd_strobe(uint8_t mask, const uint8_t *c, uint8_t tempo, uint8_t rep) {
  start_anim(A_STROBE);
  E.mask = mask;
  memcpy(E.col, c, 3);
  E.period_us = (uint32_t)(tempo ? tempo : 1) * STROBE_US_PER_T;
  E.reps = rep;
  E.infinite = rep == 0;
  E.event_at_end = !E.infinite;
}

static void cmd_wave(uint8_t type, const uint8_t *c, uint8_t rep, uint8_t vel) {
  start_anim(A_WAVE);
  E.sub = type;
  memcpy(E.col, c, 3);
  E.period_us = (uint32_t)(vel ? vel : 1) * WAVE_US_PER_V;
  E.reps = rep;
  E.infinite = rep == 0;
  E.event_at_end = (type == 5) && !E.infinite;
}

static void cmd_pattern(uint8_t id, uint8_t rep) {
  start_anim(A_PATTERN);
  E.sub = id;
  E.period_us = (uint32_t)PATTERN_MS[id] * 1000u;
  E.reps = rep;
  E.infinite = rep == 0;
  E.event_at_end = (id != 2) && !E.infinite;
}

static bool is_sala(uint8_t s) { return s == SIGNA_ST_OFF || (s >= SIGNA_ST_SALA_LIVRE && s <= SIGNA_ST_SALA_OCUPADO); }
static bool is_ia(uint8_t s) { return s == SIGNA_ST_OFF || (s >= SIGNA_ST_IA_DESOCUPADA && s < SIGNA_ST_COUNT); }

static void signa_enter(void) {
  if (E.kind != A_SIGNA) {
    stop_anim();
    E.kind = A_SIGNA;
    E.t_all = E.t_sala = E.t_ia = 0;
    E.st_all = E.st_sala = E.st_ia = 0xFF; /* força reinício de fase */
  }
}

static void render_signa(void) {
  if (!E.mixed) {
    for (uint8_t i = 0; i < SIGNA_NLEDS; i++) render_state(i, E.st_all, E.t_all);
    return;
  }
  if (E.st_sala == SIGNA_ST_SALA_OCUPADO) { /* OCUPADO trava os 3 LEDs em vermelho (v1) */
    for (uint8_t i = 0; i < SIGNA_NLEDS; i++) render_state(i, SIGNA_ST_SALA_OCUPADO, E.t_sala);
    return;
  }
  render_state(2, E.st_sala, E.t_sala);
  render_state(1, E.st_sala, E.t_sala);
  render_state(0, E.st_ia, E.t_ia);
}

/* ---------------- padrões embutidos (aproximação visual dos do Flag) ---------------- */
static void pattern_render(uint8_t id, uint32_t t) {
  static const uint8_t RED[3] = {255, 0, 0}, YEL[3] = {255, 180, 0}, GRN[3] = {0, 255, 0},
                       BLU[3] = {0, 0, 255}, PNK[3] = {255, 40, 140}, WHT[3] = {255, 255, 255},
                       OFF[3] = {0, 0, 0};
  uint8_t c[3];
  switch (id) {
    case 1: /* semáforo: topo vermelho → + meio amarelo → baixo verde */
      set_led8(2, t < 1400 ? RED : OFF, 4096);
      set_led8(1, (t >= 700 && t < 1400) ? YEL : OFF, 4096);
      set_led8(0, t >= 1400 ? GRN : OFF, 4096);
      break;
    case 2: { /* sobe um a um, fica branco, troca de cor */
      static const uint8_t *cols[3] = {RED, GRN, BLU};
      uint32_t k = t / 1200, s = (t % 1200) / 300;
      const uint8_t *col = s == 3 ? WHT : cols[k % 3];
      for (uint8_t i = 0; i < SIGNA_NLEDS; i++) set_led8(i, (s == 3 || i <= s) ? col : OFF, 4096);
      break;
    }
    case 3: case 6: case 8: { /* arco-íris; 6 termina em azul (h 0→1024) */
      uint32_t span = id == 6 ? 1024u : 1536u;
      for (uint8_t i = 0; i < SIGNA_NLEDS; i++) {
        hue((uint16_t)((t * span) / PATTERN_MS[id] + (id == 6 ? 0u : i * 128u)), c);
        set_led8(i, c, 4096);
      }
      break;
    }
    case 4: { /* 3 cores, forte e depois clareando (mistura para branco) */
      static const uint8_t *cols[3] = {RED, GRN, BLU};
      uint32_t seg = PATTERN_MS[4] / 3, k = t / seg, x = ((t % seg) << 12) / seg;
      const uint8_t *col = cols[k > 2 ? 2 : k];
      for (uint8_t j = 0; j < 3; j++) c[j] = (uint8_t)(col[j] + (((255u - col[j]) * x) >> 12));
      for (uint8_t i = 0; i < SIGNA_NLEDS; i++) set_led8(i, c, 4096);
      break;
    }
    case 5: { /* polícia */
      const uint8_t *col = t < 225 ? RED : (t >= 450 && t < 675) ? BLU : OFF;
      for (uint8_t i = 0; i < SIGNA_NLEDS; i++) set_led8(i, col, 4096);
      break;
    }
    case 7: { /* verde → rosa → azul, com transição suave */
      static const uint8_t *cols[3] = {GRN, PNK, BLU};
      uint32_t k = t / 450, x = ((t % 450) << 12) / 450;
      const uint8_t *a = cols[k > 2 ? 2 : k];
      for (uint8_t i = 0; i < SIGNA_NLEDS; i++) set_led8(i, a, tri_q12(x << 4) / 2 + 2048);
      break;
    }
    default: break;
  }
}

static void wave_render(uint8_t type, uint32_t p16) {
  for (uint8_t i = 0; i < SIGNA_NLEDS; i++) {
    uint16_t l = 0;
    uint32_t third = 0x10000u / 3;
    switch (type) {
      case 1: /* sobe de baixo para cima: cada LED acende na sua janela */
        if (p16 >= i * third && p16 < (i + 1u) * third) l = tri_q12(((p16 - i * third) * 3u));
        break;
      case 2: l = tri_q12(p16 + i * third); break;                  /* vários juntos, defasados */
      case 3: l = p16 >= i * third ? 4096 : 0; break;               /* sobe e enche */
      case 4: l = p16 < 0x8000 ? 4096 : (uint16_t)(((0xFFFFu - p16) * 2u) >> 4); break; /* fixo e apaga */
      default: l = tri_q12(p16); break;                              /* 5: os 3 pulsam juntos */
    }
    set_led8(i, E.col, l);
  }
}

/* ---------------- tick ---------------- */
void engine_tick_1ms(void) {
  switch (E.kind) {
    case A_FADE: {
      E.el_us += 1000;
      if (E.el_us >= E.dur_us) {
        for (uint8_t i = 0; i < SIGNA_NLEDS; i++) set_led(i, E.to[i][0], E.to[i][1], E.to[i][2]);
        finish_anim(false);
        break;
      }
      uint32_t f = (uint32_t)(((uint64_t)E.el_us << 16) / E.dur_us);
      for (uint8_t i = 0; i < SIGNA_NLEDS; i++) {
        uint16_t v[3];
        for (uint8_t k = 0; k < 3; k++) {
          int32_t a = E.from[i][k], b = E.to[i][k];
          v[k] = (uint16_t)(a + (int32_t)(((int64_t)(b - a) * f) >> 16));
        }
        set_led(i, v[0], v[1], v[2]);
      }
      break;
    }
    case A_STROBE: {
      E.el_us += 1000;
      uint32_t n = E.el_us / E.period_us;
      if (!E.infinite && n >= E.reps) { finish_anim(true); break; }
      bool on = (E.el_us % E.period_us) < E.period_us / 2;
      for (uint8_t i = 0; i < SIGNA_NLEDS; i++)
        if (E.mask & (1u << i)) {
          if (on) set_led(i, C8(E.col[0]), C8(E.col[1]), C8(E.col[2]));
          else set_led(i, 0, 0, 0);
        }
      break;
    }
    case A_WAVE: case A_PATTERN: {
      E.el_us += 1000;
      uint32_t n = E.el_us / E.period_us;
      if (!E.infinite && n >= E.reps) { finish_anim(true); break; }
      uint32_t r = E.el_us % E.period_us;
      if (E.kind == A_WAVE) wave_render(E.sub, (uint32_t)(((uint64_t)r << 16) / E.period_us));
      else pattern_render(E.sub, r / 1000u);
      break;
    }
    case A_SIGNA:
      E.t_all++; E.t_sala++; E.t_ia++;
      render_signa();
      break;
    default: break;
  }
}

/* ---------------- parser ---------------- */
void engine_handle_report(const uint8_t in[SIGNA_REPORT_LEN]) {
  uint8_t op = in[0], mask = 0;
  const uint8_t *rgb = &in[2];
  switch (op) {
    case OP_ACK_ONLY:
      ack();
      return;
    case OP_STATIC: case OP_FADE: case OP_STROBE: {
      addr_t a = decode_addr(in[1], &mask);
      if (a == ADDR_BAD) return;          /* silêncio, sem efeito */
      ack();
      if (a == ADDR_NOP) return;
      if (op == OP_STATIC) cmd_static(mask, rgb);
      else if (op == OP_FADE) cmd_fade(mask, rgb, in[5]);
      else cmd_strobe(mask, rgb, in[5], in[7]);
      return;
    }
    case OP_WAVE:
      if (in[1] < 1 || in[1] > 5) return; /* tipo inválido: silêncio */
      ack();
      cmd_wave(in[1], rgb, in[6], in[7]);
      return;
    case OP_PATTERN:
      if (in[1] < 1 || in[1] > 8) return; /* 0 e 9+: silêncio (risco de índice no original) */
      ack();
      cmd_pattern(in[1], in[2]);
      return;
    case OP_SERIAL_W6: case OP_SERIAL_W4: {
      uint8_t n = op == OP_SERIAL_W6 ? 6 : 4;
      uint8_t r[SIGNA_REPORT_LEN] = {op};
      memcpy(&r[1], &in[1], n);           /* eco dos argumentos, como o original */
      if (memcmp(E.serial_cur, &in[1], n) != 0) {
        memcpy(E.serial_cur, &in[1], n);
        if (E.hooks.serial_changed) E.hooks.serial_changed(E.serial_cur);
      }
      push(r);
      return;
    }
    case OP_SERIAL_R: {
      uint8_t r[SIGNA_REPORT_LEN] = {OP_SERIAL_R};
      memcpy(&r[1], E.serial_cur, 4);
      push(r);
      return;
    }
    case OP_VERSION: {
      uint8_t r[SIGNA_REPORT_LEN] = {OP_VERSION, SIGNA_COMPAT_VERSION};
      memcpy(&r[2], E.serial_boot, 4);    /* cópia de boot do serial, como no original */
      push(r);
      return;
    }
    case OP_SIGNA_STATE:
      if (in[1] >= SIGNA_ST_COUNT) return;
      ack();
      signa_enter();
      if (E.mixed || E.st_all != in[1]) E.t_all = 0; /* mesmo estado reenviado: mantém a fase */
      E.mixed = false;
      E.st_all = in[1];
      render_signa();
      return;
    case OP_SIGNA_MIXED:
      if (!is_sala(in[1]) || !is_ia(in[2])) return;
      ack();
      signa_enter();
      if (!E.mixed || E.st_sala != in[1]) E.t_sala = 0;
      if (!E.mixed || E.st_ia != in[2]) E.t_ia = 0;
      E.mixed = true;
      E.st_sala = in[1];
      E.st_ia = in[2];
      render_signa();
      return;
    case OP_SIGNA_BRIGHT:
      ack();
      if (E.bright != in[1]) E.dirty = true;
      E.bright = in[1];
      return;
    case OP_SIGNA_INFO: {
      uint8_t r[SIGNA_REPORT_LEN] = {OP_SIGNA_INFO, 'S', 'G', SIGNA_FW_MAJOR, SIGNA_FW_MINOR,
                                     SIGNA_PROTO_VERSION, SIGNA_NLEDS, 0};
      push(r);
      return;
    }
    default:
      return; /* 0x05, 0x07–0x0F e demais: silêncio */
  }
}

void engine_init(const uint8_t boot_serial[6], const engine_hooks_t *hooks) {
  memset(&E, 0, sizeof E);
  memcpy(E.serial_cur, boot_serial, 6);
  memcpy(E.serial_boot, boot_serial, 6);
  if (hooks) E.hooks = *hooks;
  E.bright = 255;
  E.dirty = true;
}

void engine_display_q88(uint16_t out[SIGNA_NLEDS][3]) { memcpy(out, E.disp, sizeof E.disp); }

void engine_output16(uint16_t out[SIGNA_NLEDS][3]) {
  for (uint8_t i = 0; i < SIGNA_NLEDS; i++)
    for (uint8_t k = 0; k < 3; k++) {
      uint32_t v = ((uint32_t)E.disp[i][k] * (E.bright + 1u)) >> 8;
      out[i][k] = v ? signa_gamma16((uint16_t)v) : 0;
    }
}

bool engine_output_dirty(void) {
  bool d = E.dirty;
  E.dirty = false;
  return d;
}
