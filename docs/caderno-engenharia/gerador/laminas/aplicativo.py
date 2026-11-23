"""Lâminas do aplicativo de desktop."""
from lib_metrologia import *
from helpers import *
import dados as D


def register(book):
    book.divisor('V', 'APLICATIVO', [
        'Daemon Python para Windows, macOS e Linux: lê Google e Outlook, recebe hooks de IA (opt-in) e envia um comando HID por transição.',
        'Compatível com o SIGNA nativo (0x10/0x11) e com o Luxafor Flag original (detecção pelo 0x1F).',
        '32 testes passando. Segredos no chaveiro do sistema. Extensão de navegador ainda experimental.',
    ], short='APLICATIVO')
    book.add_flow('V  APLICATIVO', 'Arquitetura do aplicativo', l_arq_app)
    book.add_flow('V  APLICATIVO', 'Calendários Google e Outlook', l_cal, 'CALENDÁRIOS')
    book.add_flow('V  APLICATIVO', 'Hooks de IA e extensão', l_hooks, 'HOOKS DE IA')
    book.add_flow('V  APLICATIVO', 'Configuração e instalação', l_cfg)
    book.add_flow('V  APLICATIVO', 'Operação do aplicativo', l_op_app)
    book.add_flow('V  APLICATIVO', 'Compatibilidade com o Flag e segurança', l_seg, 'FLAG E SEGURANÇA')


def l_arq_app(F):
    F.titulo('ARQUITETURA DO APLICATIVO')
    F.glossario('Fonte: signa-sw/docs/arquitetura.md e a árvore app/signa. Estado em 22/11/2026: 32 testes passando.')
    F.para('Pacote Python 3.10+ em app/signa: daemon, CLI, bandeja, servidor local para a extensão e saídas para SIGNA, Luxafor ou simulador ANSI. Fonte única dos estados: data/produto.json (cópia do caderno conceitual).')
    rows = [
        ['signa/engine.py', 'motor de prioridade (sala × IA × modo sala/misto/escada)'],
        ['signa/states.py', 'códigos e nomes dos estados, iguais aos do firmware'],
        ['signa/protocol.py', 'montagem dos relatórios HID de 8 bytes'],
        ['signa/device.py', 'descoberta HID, 0x1F para distinguir SIGNA nativo do Flag'],
        ['signa/calendar_google.py', 'Google Calendar API, OAuth de app instalado, loopback'],
        ['signa/calendar_outlook.py', 'Microsoft Graph, MSAL com fluxo de dispositivo'],
        ['signa/calendar_common.py', 'regras comuns (cancelado, livre, dia inteiro, « talvez »)'],
        ['signa/hooks.py', 'tradutor dos hooks Claude Code e Codex'],
        ['signa/daemon.py, server.py, cli.py, tray.py', 'laço, HTTP local, linha de comando, bandeja'],
        ['signa/config.py, store.py, secrets_store.py', 'config.toml, state.json, chaveiro do sistema'],
        ['app/extension/', 'extensão MV3 para chatgpt.com, claude.ai e grok.com (experimental)'],
        ['app/examples/', 'json de hooks, regra udev, exemplos de atalho'],
    ]
    F.tabela(['Módulo', 'Papel'], rows, [128, 260], fonts=['Mono', 'Work'], wrap_cols={0, 1}, size=6.2, cab_size=5.85)
    F.para('Saídas: SignaOut envia 0x10 ou 0x11; LuxaforOut envia 01/03/04 (ou faz streaming de 01 a 25 Hz); SimOut pinta o terminal. Um comando por transição no SIGNA nativo. O teste tests/test_engine.py cobre todas as combinações de sala × IA nos modos escada e misto.')


def l_cal(F):
    F.titulo('INTEGRAÇÃO COM GOOGLE E OUTLOOK')
    F.glossario('Fonte: arquitetura.md §5 e §6, docs/README.md (comandos de login e opções da sala).')
    rows = [
        ['Google Calendar', 'events.list (singleEvents, orderBy=startTime), escopo calendar.events.readonly, OAuth de app instalado com loopback. Oficial.'],
        ['Outlook / Microsoft 365', 'Graph GET /me/calendarView, escopo Calendars.Read, MSAL com fluxo de dispositivo, Prefer: outlook.timezone="UTC". Oficial.'],
        ['Regras comuns', 'Ignora cancelado, recusado, « livre » (Google transparency=transparent, Graph showAs=free), local de trabalho e dia inteiro (se ignore_all_day). « Talvez » conta como ocupado se tentative_is_busy (configurável).'],
        ['Prestes a entrar', 'lead_minutes, padrão 5 minutos, configurável no app.'],
        ['Manual', 'signa-cli sala ocupado --por 30m, sala livre, sala auto, toggle; bandeja; atalho global (pynput). O manual vence a agenda enquanto estiver ativo.'],
        ['Login', 'signa-cli login google  ·  signa-cli login outlook (código em microsoft.com/devicelogin)'],
        ['Segredos', 'tokens OAuth (Google e cache MSAL) no chaveiro do sistema (keyring). O JSON do cliente OAuth do Google fica fora do repositório (*client_secret*.json no .gitignore). config.toml não tem segredo nenhum.'],
        ['Microfone / câmera', 'não implementado; fonte de « em reunião » a definir por sistema operacional.'],
    ]
    F.tabela(['Tema', 'Comportamento'], rows, [76, 312], wrap_cols={1}, fonts=['Work', 'Work'], size=6.2, cab_size=5.85)


def l_hooks(F):
    F.titulo('HOOKS DE IA E EXTENSÃO DE NAVEGADOR')
    F.glossario('Mapeamento Stop do Claude Code: a arquitetura documenta Stop → DESOCUPADA. Qualquer outro mapeamento (atenção) não está nesta versão.')
    F.para('A IA é opt-in: só entra na escada se o usuário ligar a opção e se a fonte estiver em [ai].sources. Fontes fora dessa lista são ignoradas.')
    rows = [
        ['Claude Code (oficial)', 'Mescle app/examples/claude-code-settings.json em ~/.claude/settings.json. Eventos: UserPromptSubmit / PreToolUse / PostToolUse → PROCESSANDO; PermissionRequest e Notification permission_prompt → ATENÇÃO; Stop e idle_prompt → DESOCUPADA; StopFailure rate_limit → LIMITE; outras falhas → ERRO; SessionEnd remove a sessão. Cada hook custa ≈ 50–100 ms de Python. Há uma variante explícita (claude-code-settings-explicit.json) que chama um estado fixo por evento.'],
        ['Codex CLI (oficial)', 'Copie app/examples/codex-hooks.json para ~/.codex/hooks.json e aprove em /hooks (o Codex só roda hooks revisados). Mesmos nomes + PostModelRequest status=failed → ERRO ou LIMITE. Alternativa mínima: codex-config-notify.toml, só agent-turn-complete → DESOCUPADA.'],
        ['Web ChatGPT, Claude, Grok', 'Extensão MV3: chrome://extensions, modo desenvolvedor, « Carregar sem compactação » em app/extension; colar token.txt nas opções. Heurística: botão « parar » visível = PROCESSANDO; texto de limite = LIMITE; alerta = ERRO; terminou com a aba em segundo plano = ATENÇÃO até você voltar. É experimental: lê o HTML e quebra quando os sites mudarem. Seletores em extension/sites.js.'],
        ['5 h × semanal', 'Claude Code e Codex: pelo texto do erro. Web: pelo texto da página. Heurística, a validar.'],
        ['Expiração', 'PROCESSANDO sem sinal por 15 min → DESOCUPADA (CLI que morreu); ERRO 10 min; LIMITE 5 h dura 5 h; LIMITE semanal dura 24 h; configurável.'],
        ['Contrato dos hooks', 'sempre saem com código 0 e não escrevem no stdout, exceto o {} que o Stop do Codex exige, para nunca bloquear a CLI de IA.'],
    ]
    F.tabela(['Fonte', 'Comportamento'], rows, [76, 312], wrap_cols={1}, fonts=['Work', 'Work'], size=6.15, cab_size=5.85)


def l_cfg(F):
    F.titulo('CONFIGURAÇÃO E INSTALAÇÃO')
    F.glossario('Comandos e opções: signa-sw/docs/README.md. Arquivos de exemplo em app/examples/.')
    F.rotulo('INSTALAR O APLICATIVO')
    F.code_lines([
        'cd app',
        'pip install -e ".[test]"     # ou pip install -e .  (sem testes)',
        'python -m pytest -q          # 32 testes',
        'signa-cli --help',
    ])
    F.rotulo('OPÇÕES RELEVANTES  (config.toml  /  CLI)', gap_before=2.0)
    rows = [
        ['lead_minutes', 'aviso de « prestes a entrar », padrão 5'],
        ['tentative_is_busy', '« talvez » conta como ocupado (configurável)'],
        ['ignore_all_day', 'ignorar eventos de dia inteiro'],
        ['modo de exibição', 'sala  ·  misto  ·  escada  (signa-cli modo --display …)'],
        ['IA', 'off por padrão; signa-cli modo --ia on'],
        ['[ai].sources', 'lista branca das fontes de IA'],
        ['expiração dos relatos', 'PROCESSANDO 15 min, ERRO 10 min, LIMITE 5 h / 24 h'],
        ['[device] luxafor_render', 'stream (padrão, 01 a 25 Hz) ou opcodes (04 wave 5, 03 strobe)'],
        ['VID:PID', 'deve acompanhar o firmware (padrão 1209:0001); ver device.py'],
    ]
    F.tabela(['Opção', 'Significado'], rows, [96, 292], wrap_cols={1}, fonts=['Mono', 'Work'], size=6.2, cab_size=5.85)
    F.para('O servidor local da extensão escuta só em 127.0.0.1, exige o cabeçalho X-Signa-Token (arquivo token.txt com permissão 0600) e Host local (barra DNS rebinding). Só aceita fontes web e estados de IA.')


def l_op_app(F):
    F.titulo('OPERAÇÃO DO APLICATIVO')
    F.glossario('A CLI é a interface estável. A bandeja e os atalhos globais (pynput) chamam as mesmas funções.')
    rows = [
        ['signa-cli login google', 'OAuth do Google Calendar (loopback)'],
        ['signa-cli login outlook', 'mostra um código para microsoft.com/devicelogin'],
        ['signa-cli sala ocupado --por 45m', 'vence a agenda por 45 min'],
        ['signa-cli sala livre', 'livre até signa-cli sala auto'],
        ['signa-cli sala auto', 'volta a seguir a agenda'],
        ['signa-cli toggle', 'para ligar num atalho do sistema'],
        ['signa-cli modo --display misto --ia on', 'modo misto, IA ligada'],
        ['signa-cli status', 'estado atual da sala, da IA e do dispositivo'],
        ['signa-cli devices', 'lista aparelhos; « SIGNA nativo » se o 0x1F responder'],
        ['signa-cli hook claude-code', 'chamado pelos hooks; lê o JSON e decide o estado'],
        ['signa-cli hook codex', 'idem, para o Codex'],
        ['signa-cli ai --source … --state …', 'força um estado de IA de uma fonte'],
        ['signa-cli demo', 'sequência de demonstração na placa ou no simulador'],
        ['bandeja', 'ícone na bandeja do sistema (tray.py) com atalhos de sala e modo'],
    ]
    F.tabela(['Comando', 'Efeito'], rows, [132, 256], fonts=['Mono', 'Work'], wrap_cols={0, 1}, size=6.2, cab_size=5.85)


def l_seg(F):
    F.titulo('COMPATIBILIDADE COM O FLAG E SEGURANÇA')
    F.glossario('Fonte: arquitetura.md §3.1 (detecção 0x1F), §6 (segurança) e docs/README.md (Luxafor Flag original).')
    F.rotulo('LUXAFOR FLAG ORIGINAL')
    F.para('O aplicativo detecta o aparelho pelo opcode 0x1F. Sem a resposta « SG… », trata o dispositivo como Flag e usa o protocolo antigo. Em [device] luxafor_render, o modo stream (padrão) reproduz as curvas mandando 01 a 25 Hz; o modo opcodes usa um comando por estado (04 wave 5 para respiração, 03 strobe para piscar; pulso duplo vira cor fixa). O app nunca manda endereço fora de {1, 2, 3, FF} — inclusive para não reproduzir o travamento do 0x13.')
    F.rotulo('SEGURANÇA E SEGREDOS', gap_before=2.0)
    rows = [
        ['OAuth', 'tokens no chaveiro do sistema: Credential Manager (Windows), Keychain (macOS), Secret Service (Linux)'],
        ['Cliente Google', 'JSON fora do repositório; .gitignore bloqueia *client_secret*.json'],
        ['Servidor local', '127.0.0.1, token 0600, Host local, só estados de IA e fontes web'],
        ['Hooks', 'código de saída 0, stdout silencioso (exceto {} do Stop do Codex)'],
        ['Endereços HID', 'o app nunca envia alvo fora de {1, 2, 3, FF}'],
        ['VID:PID do Flag', 'não usar 04d8:f372 em produto vendido; o make USB_IDS=luxafor é só para o protótipo pessoal'],
    ]
    F.tabela(['Tema', 'Regra'], rows, [68, 320], wrap_cols={1}, fonts=['Work', 'Work'], size=6.2, cab_size=5.85)
