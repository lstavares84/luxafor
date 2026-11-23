"""Manual de operação e teste de produção."""
from lib_metrologia import *
from helpers import *
import dados as D


def register(book):
    book.divisor('VI', 'OPERAÇÃO E TESTE', [
        'Manual de operação para quem usa o SIGNA no dia a dia, e o procedimento de teste com o qual a produção decide passa ou falha.',
        'Os pontos de teste TP1–TP3 existem para a cama de pregos. A placa deve ser gravada e testada antes de entrar no berço.',
        'Correntes de aceite ainda são estimativas de datasheet: confirmar no primeiro lote e então congelar os limites.',
    ], short='OPERAÇÃO E TESTE')
    book.add_flow('VI  OPERAÇÃO E TESTE', 'Manual de operação  ·  instalação', l_manual1, 'MANUAL · INSTALAÇÃO')
    book.add_flow('VI  OPERAÇÃO E TESTE', 'Manual de operação  ·  estados e botão', l_manual2, 'MANUAL · ESTADOS')
    book.add_flow('VI  OPERAÇÃO E TESTE', 'Solução de problemas', l_trouble, 'DIAGNÓSTICO')
    book.add_flow('VI  OPERAÇÃO E TESTE', 'Teste de produção  ·  elétrico', l_teste1, 'TESTE · ELÉTRICO')
    book.add_flow('VI  OPERAÇÃO E TESTE', 'Teste de produção  ·  óptico, mecânico, registro', l_teste2, 'TESTE · ACEITE FINAL')


def l_manual1(F):
    F.titulo('MANUAL DE OPERAÇÃO  ·  INSTALAÇÃO')
    F.glossario('Este manual é para o usuário final. A instalação do firmware e do option byte é assunto de produção, não do dia a dia.')
    F.L.image_fit(JPG('em_uso'), 266, 98, 138, 140, 'uso', anchor='c')
    F.L.caption(266, 90, 'Fig.  —  SIGNA pendurado no monitor, estado OCUPADO.', width=138)
    F.set_box(M, 240, y=F.y, min_y=F.base_min_y)
    rows = [
        ['1', 'Tire o aparelho da caixa pelo tubo, pelas pontas, sem apertar a superfície fosca. Confira se o botão de baixo se move e volta.'],
        ['2', 'Passe o plugue do cabo pelo topo (já deve vir montado). O outro extremo vai a uma porta USB-C do computador, de preferência direta, não a um hub sem alimentação se for testar corrente.'],
        ['3', 'O SIGNA deve enumerar em menos de 2 s. No Linux, lsusb mostra 1209:0001 (desenvolvimento) e um serial de 12 dígitos hex. Sem o aplicativo, a luz pode ficar apagada ou no último estado gravado em RAM (some ao desligar).'],
        ['4', 'Instale o aplicativo (seção V). Faça login no Google e/ou no Outlook. Deixe o modo em « sala » até querer ligar a IA.'],
        ['5', 'Pendure o aparelho no monitor pelo próprio cabo, com os LEDs voltados para a sala e a face mais escura contra a tela. Ajuste a folga do passa-cabo se o cabo escorregar.'],
        ['6', 'Opcional: ligue a IA (signa-cli modo --ia on), instale os hooks do Claude Code ou do Codex, e, se quiser, a extensão experimental.'],
        ['7', 'Opcional: cadastre um atalho do sistema para signa-cli toggle, para marcar OCUPADO sem abrir a agenda.'],
    ]
    F.tabela(['#', 'Passo'], rows, [20, 220], cont_larg=[26, 362],
             wrap_cols={1}, fonts=['Mono', 'Work'], size=6.2, cab_size=5.85)


def l_manual2(F):
    F.titulo('MANUAL DE OPERAÇÃO  ·  ESTADOS E BOTÃO')
    F.glossario('Cores e ritmos vêm de produto.json / signa_tables. O aviso de 5 minutos é configurável no aplicativo (lead_minutes).')
    F.rotulo('O QUE A LUZ QUER DIZER')
    rows = [
        ['Verde baixo contínuo', 'LIVRE  ·  pode interromper'],
        ['Laranja em pulso lento (3 s)', 'PRESTES A ENTRAR  ·  reunião em N minutos (padrão 5)'],
        ['Vermelho fixo forte, os 3 LEDs', 'OCUPADO  ·  em reunião ou foco; a IA some neste estado (v1)'],
        ['Cinza-azulado muito baixo', 'IA DESOCUPADA  (só se a IA estiver ligada e a sala não vencer)'],
        ['Azul em respiração (2,4 s)', 'IA PROCESSANDO'],
        ['Amarelo piscando 1 vez por segundo', 'IA PRECISA DE ATENÇÃO'],
        ['Rosa-choque em flashes curtos, 2,5 vez/s', 'IA ERRO  ·  abaixo de 3 Hz, de propósito'],
        ['Violeta em dois pulsos / violeta baixo fixo', 'IA LIMITE  ·  dois pulsos = janela de 5 h; fixo baixo = teto semanal'],
        ['Topo e meio numa cor, baixo em outra', 'modo misto  ·  sala em cima, IA embaixo — salvo OCUPADO, que trava tudo'],
    ]
    F.tabela(['O que você vê', 'Significado'], rows, [132, 256],
             fonts=['Work', 'Work'], wrap_cols={0, 1}, size=6.2, cab_size=5.85)
    F.rotulo('BOTÃO DE BAIXO', gap_before=2.0)
    F.para('O botão na ponta de baixo deve alternar OCUPADO e LIVRE à mão, sem o computador. Na prática, segura-se o tubo com a outra mão: a chave pede 1,6 N e o aparelho pesa cerca de 0,20 N, então ele subiria se você apertasse no ar. Se o firmware 0.1 ainda não ler o botão (pendência atual), use signa-cli toggle ou a bandeja. Segurar o botão enquanto pluga o cabo é o caminho de recuperação (atualização de firmware / DFU) e só funciona se a produção tiver gravado nBOOT_SEL = 0.')


def l_trouble(F):
    F.titulo('SOLUÇÃO DE PROBLEMAS')
    F.glossario('Se o caso pedir gravação de NVM (serial 0x51/0x52) em uma unidade real, pedir confirmação antes. No original, um teste chegou a zerar o iSerial.')
    rows = [
        ['Não enumerou / lsusb vazio', 'Trocar de porta (evitar reset de software USB). Provar cabo conhecido. Se a unidade nunca foi gravada, ela deve aparecer como 0483:df11 (DFU) e precisa de firmware.'],
        ['Aparece como 0483:df11 o tempo todo', 'Está no bootloader. Soltar o botão, conferir se o JP1 não está fechado, replugar. Se nBOOT_SEL ainda é 1 e a flash tem programa, o JP1/botão não deveriam prendê-lo — gravar nBOOT_SEL = 0 ou regravar o firmware por SWD.'],
        ['Enumerou, mas a luz não acende', 'signa-cli devices e signa-cli demo. Conferir brilho (0x12). Mandar 01 FF FF FF FF (branco) e 01 FF 00 00 00 (apagado).'],
        ['Acendeu verde no comando de vermelho', 'Ordem GRB trocada no firmware desta unidade. Registrar e corrigir ws2816_encode.c; não é defeito do LED.'],
        ['Agenda não muda a luz', 'Login, permissões, fuso, regras de dia inteiro / « talvez ». signa-cli status. O manual ativo vence a agenda: sala auto para soltar.'],
        ['IA não aparece', 'A IA é opt-in. modo --ia on, fonte na lista [ai].sources, hooks instalados (e aprovados, no Codex). No v1, OCUPADO esconde a IA.'],
        ['Extensão não fala com o app', 'Servidor no 127.0.0.1, token.txt nas opções, Host local. Sites mudam: seletores em sites.js.'],
        ['Botão não faz nada', 'Firmware 0.1 ainda pode não ler PA14. Se o gesto de DFU ao ligar também falhar, nBOOT_SEL provavelmente não é 0.'],
        ['A luz treme ou « digitaliza » no fade', 'Inesperado no SIGNA (16 bit + gamma). Se ocorrer, capturar no R3. Num Flag original, o PWM de 8 bit linear é o comportamento normal.'],
        ['O cabo arranca a placa / a tampa', 'Unidade sem orelhas (rev A/C) ou orelhas quebradas no despainel. Não usar; abrir chamado de montagem. Na rev D/B isso é defeito.'],
        ['Travou no meio de um teste HID', 'Não aplicar USBDEVFS_RESET. Pedir o replugue físico do cabo.'],
    ]
    F.tabela(['Sintoma', 'O que fazer'], rows, [92, 296], wrap_cols={1}, fonts=['Work', 'Work'], size=6.2, cab_size=5.85)


def l_teste1(F):
    F.titulo('TESTE DE PRODUÇÃO  ·  ELÉTRICO  (PLACA NUA)')
    F.glossario('Base: pendente/teste.md seções 1–3, acrescida dos opcodes nativos e dos TPs da rev D. Gravação: DFU da ROM ou SWD, e nBOOT_SEL = 0, antes ou neste posto.')
    F.para('Fazer nas placas nuas, antes da montagem no berço (o J2 e os TPs ficam inacessíveis depois). Alimentação de teste: 5,00 V em VBUS. Pontos: TP1 VBUS, TP2 LED_DIN_5V, TP3 GND. Cama de pregos ou ponteiras. Não soldar fios nos pads.')
    F.rotulo('1. ALIMENTAÇÃO E ENUMERAÇÃO')
    rows1 = [
        ['TP1 a TP3', '5,00 V ± a definir (tolerância da fonte de teste ainda não congelada)'],
        ['+3V3 (pad do C2 ou J2-1, se acessível)', 'presença de 3,3 V após o LDO  ·  valor de corte: a definir'],
        ['USB', 'enumerar em < 2 s; descritor HID vendor 0xFF00, 8+8 bytes, EP 0x81/0x01, 1 ms, Full Speed, MaxPower 100 mA; sem erros no dmesg'],
        ['Identidade', 'VID:PID conforme o firmware gravado; iSerial de 12 hex; 0x1F responde « SG » se for build SIGNA'],
    ]
    F.tabela(['Medida', 'Critério'], rows1, [96, 292], wrap_cols={1}, fonts=['Work', 'Work'], size=6.2, cab_size=5.85)
    F.rotulo('2. COMANDOS  (PROTOCOLO COMPATÍVEL)', gap_before=2.0)
    rows2 = [
        ['80 …', 'resposta com versão do firmware (80 3c … no padrão compatível)'],
        ['01 FF FF 00 00', 'os 3 LEDs vermelhos  (se vierem verdes: falha de ordem GRB, não de LED)'],
        ['01 FF 00 FF 00', 'os 3 verdes'],
        ['01 FF 00 00 FF', 'os 3 azuis'],
        ['01 FF FF FF FF', 'branco uniforme'],
        ['02 FF 00 00 FF 20', 'fade suave, sem degraus visíveis (16 bit)'],
        ['01 01 FF 00 00  /  01 02 00 FF 00  /  01 03 00 00 FF', 'cada LED na sua posição (D1 baixo, D3 topo)'],
        ['01 FF 00 00 00', 'tudo apagado'],
        ['10 03  /  10 07', 'OCUPADO vermelho fixo; ERRO a 2,5 Hz (12 flashes em 4,8 s, câmera lenta)'],
    ]
    F.tabela(['Comando (hex)', 'Esperado'], rows2, [126, 262],
             fonts=['Mono', 'Work'], wrap_cols={0, 1}, size=6.2, cab_size=5.85)


def l_teste2(F):
    F.titulo('TESTE DE PRODUÇÃO  ·  CORRENTE, ÓPTICA, MECÂNICA E REGISTRO')
    F.glossario('Fonte: pendente/teste.md seções 4–5 e Registro, mais os critérios da rev B/D (orelhas, botão, nBOOT_SEL). Fotometria numérica: a definir.')
    F.rotulo('3. CORRENTE A 5,00 V  (estimativa — confirmar no 1.º lote e congelar)')
    rows1 = [
        ['Enumerado, LEDs apagados', '≈ 10–15 mA', '> 30 mA'],
        ['Branco 100 %', '≈ 70–80 mA', '> 100 mA (teto do descritor)'],
    ]
    F.tabela(['Estado', 'Esperado', 'Reprova se'], rows1, [120, 96, 172], fonts=['Work', 'Mono', 'Mono'])
    F.rotulo('4. ÓPTICA E MECÂNICA  (PRODUTO MONTADO)', gap_before=2.0)
    rows2 = [
        ['1', 'Em branco 100 %, olhar o tubo a 0,5 m: sem pontos quentes visíveis; ponta inferior (tampão) também acesa.'],
        ['2', 'Girar 360°: a face traseira (lado do monitor) fica mais escura; aceitável se não houver linha escura nítida.'],
        ['3', 'Puxar o cabo com 10 N por 5 s (dinamômetro de mão): o plugue não sai, a tampa não se solta, a placa não se desloca (orelhas).'],
        ['4', 'Balançar e bater de leve: sem ruído (tubo preso entre flange e tampão).'],
        ['5', 'Botão: sai ≈ 0,3 mm, aciona e volta, sem emperrar. (A leitura pelo firmware, quando implementada, deve alternar OCUPADO/LIVRE.)'],
        ['6', 'Conferir anodização e tubo sem riscos; orelhas íntegras; etiqueta de série colada na caixa.'],
        ['7', 'Opcional: gesto DFU — com a unidade já gravada e nBOOT_SEL = 0, segurar o botão, replugar, ver 0483:df11, depois soltar e replugar para voltar ao aplicativo.'],
    ]
    F.tabela(['#', 'Critério'], rows2, [22, 366], wrap_cols={1}, fonts=['Mono', 'Work'])
    F.rotulo('REGISTRO POR UNIDADE', gap_before=2.0)
    F.para('Gravar: número de série, versão do firmware (0x1F e 0x80), corrente apagado e branco, passa/falha de cada item acima, operador, data, e se nBOOT_SEL foi confirmado em 0. Manter o registro junto do lote (não só na caixa).')
