# SIGNA: montagem 3D integrada (mecânica rev B + placa rev D + cabo USB-C)

Gerado em 2026-11-22. Parte do Pendente rev A (a fonte original desse CAD não está neste repositório; o conjunto SIGNA está aqui e **não altera** aquele projeto).
Placa: [`hardware/revD/`](../hardware/revD/) (ver o [`CHANGELOG.md`](../hardware/revD/CHANGELOG.md)). Unidades: mm. Projeção 1º diedro (ABNT). Cotas e notas em português.

## Entregáveis
| Arquivo | Conteúdo |
|---|---|
| `signa_conjunto.step` | **Conjunto único** (~14 MB): P01–P06, a placa rev D completa (trilhas, pads, serigrafia, modelos de J1/LEDs/MCU/S1/passivos) e o cabo USB-C (casca, sobremolde, alívio, capa Ø3,8 com curvas, 225 mm) |
| `signa_conjunto.glb` | O mesmo conjunto para ver no navegador (~9 MB; ex.: gltf-viewer.donmccurdy.com ou `<model-viewer>`) |
| `export/step/*.step`, `export/stl/*.stl`, `export/3mf/*.3mf` | Peças avulsas: P01 tubo, P02 tampa Al, P02b tampa impressa, P03 berço, P04 tampão, P05 passa-cabo, **P06 botão (novo)**, E01 placa, C01 cabo |
| `renders/iso.png` | Vista isométrica (fundo claro, botão visível embaixo) |
| `renders/explodida.png` | Vista explodida com a placa ao lado |
| `renders/corte.png` | Corte com a placa dentro, o plugue encaixado e o botão |
| `renders/detalhe_usbc.png`, `renders/detalhe_usbc_anotado.png` | Detalhe do encaixe do USB-C (corte), com chamadas |
| `renders/em_uso.png`, `renders/livre.png` | Em uso no monitor: OCUPADO (#FF3B2F) e LIVRE (#2FD28A) |
| `desenhos/LXP-*.pdf`, `desenhos/LXP-*.png`, `desenhos/LXP-*.dxf`, `desenhos/SIGNA_revB_desenhos_completos.pdf` | A00 conjunto, P01–P05 atualizados, **P06 novo** |
| `bom/bom_completa.md`, `bom/bom_completa.csv` | BOM completa com S1, R5, P06 e a especificação do cabo |
| `docs/verificacao_montagem.txt`, `docs/verificacao_montagem.json` | Interferências e folgas medidas no CAD |

## O que mudou em relação ao Pendente rev A
1. **Placa rev D com orelhas (batente axial).** As orelhas apoiam nas fendas da flange do berço (Z 50,75) e ficam 0,25 abaixo do ressalto da tampa. Assim o botão (1,6 N) e a extração do cabo (8–20 N) não deslocam a placa. Na rev A, nada segurava a placa por cima. A placa subiu 0,75 (PCB_Z0 = 7,75).
2. **P03 berço:** fundo da ranhura 0,30 abaixo da placa (sem apoio duplo). Recorte da flange com 12,2 de largura + 2 fendas para as orelhas. O alívio THT do J1 agora atravessa a flange. O rebaixo para sobremolde da flange foi removido: a boca do USB-C fica 0,40 acima da flange.
3. **P04 tampão:** furo Ø3,2 coaxial com a haste do S1 + rebaixo Ø4,8 × 1,0.
4. **P06 botão (novo):** pino de PC opalino Ø3,0 com colar Ø4,4 retido por gravidade e empurrador Ø2,2. Fica 0,40 abaixo da haste do S1 e sai 0,3 abaixo do tampão.
5. **P05 passa-cabo:** furo Ø3,6 → **Ø3,3**, para apertar cabos de Ø3,5 a Ø4,0.
6. **Cabo C01 modelado:** casca 8,25 × 2,4 inserida 6,2, sobremolde 11,6 × 6,4 × 17 (r 2,8; diagonal 11,65 passa no furo Ø12,8), alívio Ø6,0→Ø4,2 × 7, capa Ø3,8. Trajeto: sobe 150 → curva r12 → 26 na horizontal → curva r10 → desce 90 atrás do monitor.
7. LED → difusor: 7,27 mm (altura real do WS2816B: 0,84).

## Verificação (resumo de `docs/verificacao_montagem.txt`)
- **0 interferências não intencionais.** As intencionais: press-fit tampão × berço (1,40 mm³), aperto do passa-cabo no cabo (27,6 mm³) e sobremolde/alívio/capa (mesmo objeto).
- Placa: orelhas–tampa 0,25 (3D 0,155); fundo da ranhura 0,30; fenda lateral 0,15/lado; folga por face na ranhura 0,05; placa–tubo 0,499; placa–tampão 2,05; LED–difusor 7,265; corpo do S1–tubo 3,68.
- Botão: P06–haste do S1 0,40 nominal (0,0–0,8 no pior caso); radial no furo 0,10; colar 0,20; P06–berço 0,695; P06–placa 0,94; curso até acionar ≤ 1,0.
- USB-C: casca–cavidade 0,045 (largura) / 0,080 (altura); língua–interior do plugue 0,091; ponta–fundo 0,40; sobremolde–flange 0,85, –boca 0,45, –tampa 0,97; alívio–passa-cabo 0,66; casca–PCB 0,52; sobremolde no furo Ø12,8 0,57/lado.
- Massa estimada ≈ 20 g sem o cabo.

## Regenerar
```
cd cad
python3 build.py            # STEP/STL/3MF por peça + ../signa_conjunto.step
python3 check.py            # ../docs/verificacao_montagem.*
python3 meshes.py           # malhas para o Blender (export/mesh)
B=/opt/blender-4.2.3-linux-x64/blender
for s in iso explodida corte detalhe_usbc em_uso livre glb; do $B -b --python render_blender.py -- $s 96; done
python3 drawings.py         # desenhos LXP-A00, P01–P06
cd ../bom && python3 gerar_bom.py
```
A placa (`cad/board/signa-revD-pcb.step`) vem de `kicad-cli pcb export step --subst-models` na rev D.

## Decisões em aberto (Lucas)
1. **Ergonomia do botão embaixo:** apertar a base de um pendente pendurado exige segurar o tubo com os dedos (1,6 N contra ~0,2 N de peso). Alternativa: S1 com força menor, ou botão na tampa (exigiria flex/fio).
2. **DFU pelo botão:** exige `nBOOT_SEL = 0` gravado na produção.
3. **Cabo:** casca exposta ≥ 5,8; sobremolde ≤ 11,6 × 6,4; sobremolde + alívio ≤ ~24,5; alívio ≤ Ø6,4 na ponta; capa Ø3,5–4,0. Exigir amostra do fornecedor.
4. Painelização com orelhas (placa de 15,2 mm de largura).
