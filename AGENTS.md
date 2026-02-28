# PS1 Launcher — Escopo para Agentes de IA

Este arquivo descreve o projeto para assistentes de IA (Claude Code, etc.) que trabalham neste repositório.

---

## O que é este projeto

Um launcher minimalista com identidade visual da BIOS do PlayStation 1, feito para rodar em **Raspberry Pi 5** com **RPi OS Lite** (sem desktop, sem X11).

O launcher:
1. Exibe a intro Sony do PS1 (vídeo `assets/intro.mp4`)
2. Mostra um menu OSD estilo BIOS PS1, navegável por controle
3. Permite configurar apps via `apps.ini`
4. Executa o app selecionado e retorna ao menu quando ele fecha
5. É iniciado automaticamente via **systemd** no boot

---

## Stack Técnica

| Componente | Tecnologia |
|---|---|
| Linguagem | Python 3.11+ |
| Rendering | pygame 2.5+ com SDL2 |
| Display no Pi | `SDL_VIDEODRIVER=kmsdrm` (sem X11) |
| Playback de vídeo | mpv via subprocess |
| Input de controle | `pygame.joystick` |
| Configuração de apps | `configparser` (INI nativo Python) |
| Inicialização no Pi | systemd service unit |
| Fonte | Press Start 2P (TTF em `assets/fonts/`) |

---

## Resolução e Visual

- **Resolução alvo:** 1920x1080 (1080p)
- **Background:** `assets/ps1-bios.jpg` — imagem estática da tela da BIOS PS1
- **Fonte:** Press Start 2P — usada para todos os textos do menu
- **Seletor:** retângulo/highlight roxo sobre o item ativo
- **Sem animações** — interface estática, sem transições, sem partículas

---

## Estrutura de Módulos

### `launcher.py`
Entry point. Responsável por:
- Detectar plataforma (`platform.system()`)
- Setar variáveis de ambiente SDL antes do `pygame.init()`
- Chamar intro → menu em sequência
- Tratar encerramento limpo (SIGTERM)

### `src/config.py`
Lê `apps.ini` e retorna lista de apps.
- Input: caminho para o `.ini`
- Output: lista de tuplas `(nome_exibido, comando_shell)`
- Não tem dependências externas além de `configparser`

### `src/intro.py`
Reproduz o vídeo da intro via mpv.
- Verifica existência de `assets/intro.mp4` antes de tentar
- No Pi: `mpv --vo=drm --fullscreen assets/intro.mp4`
- Em dev (WSL/Linux desktop): `mpv --fullscreen assets/intro.mp4`
- Usa `subprocess.run()` — bloqueia até o vídeo terminar

### `src/controller.py`
Abstrai input de controle e teclado.
- Inicializa `pygame.joystick` para o primeiro controle conectado
- Mapeia: D-pad cima/baixo → navegar, X/A → confirmar, O/B → voltar
- Fallback teclado: setas cima/baixo → navegar, Enter → confirmar, Escape → voltar
- Retorna eventos normalizados (não expõe pygame diretamente)

### `src/menu.py`
Renderiza e gerencia o menu OSD.
- Carrega `ps1-bios.jpg` como background
- Recebe lista de apps de `config.py`
- Loop principal: renderiza → processa input → executa app selecionado
- Execução de app: `subprocess.run(comando, shell=True)` — bloqueia até fechar
- Após retorno do app: volta ao loop do menu

---

## Arquivo de Configuração (`apps.ini`)

```ini
[apps]
RetroArch = retroarch
Duckstation = duckstation-qt
PPSSPP = ppsspp
Desligar = sudo shutdown -h now
Reiniciar = sudo reboot
```

- Seção obrigatória: `[apps]`
- Chave = nome exibido no menu
- Valor = comando shell a executar
- Ordem no arquivo = ordem no menu

---

## Detecção de Plataforma

```python
import platform, os

IS_PI = platform.system() == "Linux" and os.path.exists("/dev/fb0")

if IS_PI:
    os.environ["SDL_VIDEODRIVER"] = "kmsdrm"
    os.environ["SDL_FBDEV"] = "/dev/fb0"
    os.environ["SDL_AUDIODRIVER"] = "alsa"
```

A detecção de `/dev/fb0` diferencia Pi de WSL/desktop Linux.

---

## Convenções de Código

- Python puro, sem frameworks além de pygame
- Sem type hints obrigatórios, mas bem-vindos em funções públicas
- Cada módulo em `src/` é independente e testável isoladamente
- Sem logging verboso — `print()` apenas para erros críticos
- Comentários só onde a lógica não é óbvia
- Sem abstrações prematuras — manter simples

---

## Assets Necessários

| Arquivo | Status | Descrição |
|---|---|---|
| `assets/ps1-bios.jpg` | ✅ presente | Background do menu OSD |
| `assets/intro.mp4` | ⏳ a adicionar | Intro Sony em 1080p |
| `assets/fonts/PressStart2P.ttf` | ⏳ a adicionar | Fonte do menu |

---

## Ambiente de Desenvolvimento

- **Dev:** Ubuntu via WSL2 com WSLg (suporte a GUI nativa)
- **Deploy:** Raspberry Pi 5, RPi OS Lite, sem desktop
- **Transferência:** SSH/SCP ou git

No WSL, pygame abre janela normal. No Pi, usa KMSDRM (framebuffer direto).
Não setar variáveis SDL de Pi no ambiente de dev.

---

## Systemd Unit (Pi)

Arquivo: `systemd/ps1-launcher.service`

```ini
[Unit]
Description=PS1 Launcher
After=multi-user.target

[Service]
Type=simple
User=pi
Environment=SDL_VIDEODRIVER=kmsdrm
Environment=SDL_FBDEV=/dev/fb0
Environment=SDL_AUDIODRIVER=alsa
ExecStart=/usr/bin/python3 /home/pi/ps1-launcher/launcher.py
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
```

---

## O que NÃO está no escopo

- Sem suporte a mouse ou touch
- Sem scraper de capas ou metadados de jogos
- Sem animações no menu (BIOS PS1 é estática)
- Sem UI de configuração — editar `apps.ini` manualmente via SSH
- Sem suporte multi-idioma
- Sem autenticação ou multi-usuário
