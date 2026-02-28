# PS1 Launcher — Plano de Ação

## Visão Geral

Launcher para Raspberry Pi 5 com identidade visual da BIOS do PlayStation 1.
Iniciado automaticamente via systemd no RPi OS Lite (sem desktop).
Desenvolvido no Ubuntu/WSL2, transferido para o Pi via SSH.

---

## Estrutura de Arquivos

```
ps1-osd-laucher/
├── launcher.py               # Entry point principal
├── apps.ini                  # Configuração de aplicativos (editável)
├── assets/
│   ├── intro.mp4             # Intro Sony (a adicionar)
│   ├── ps1-bios.jpg          # Background do menu OSD
│   └── fonts/
│       └── PressStart2P.ttf  # Fonte padrão
├── src/
│   ├── intro.py              # Módulo de reprodução do vídeo
│   ├── menu.py               # Módulo do menu OSD
│   ├── controller.py         # Módulo de input do controle
│   └── config.py             # Módulo de leitura do apps.ini
├── systemd/
│   └── ps1-osd-laucher.service  # Unit file para o Pi
├── PLAN.md
└── AGENTS.md
```

---

## Fases de Desenvolvimento

### Fase 0 — Setup do ambiente
- [ ] Instalar dependências Python: `pygame`, `configparser` (nativo)
- [ ] Baixar fonte Press Start 2P (Google Fonts)
- [ ] Verificar pygame rodando no WSL2 via WSLg
- [ ] Criar estrutura de pastas do projeto

### Fase 1 — Config reader (`src/config.py`)
- [ ] Ler `apps.ini` com `configparser`
- [ ] Retornar lista de `(nome, comando)` para o menu
- [ ] Suportar entradas como `shutdown`, `reboot`, comandos shell comuns

**Formato do apps.ini:**
```ini
[apps]
RetroArch = retroarch
Duckstation = duckstation-qt
PPSSPP = ppsspp
Desligar = sudo shutdown -h now
Reiniciar = sudo reboot
```

### Fase 2 — Intro Sony (`src/intro.py`)
- [ ] Verificar se `assets/intro.mp4` existe
- [ ] Chamar `mpv` via subprocess e aguardar finalização
- [ ] No Pi: adicionar flag `--vo=drm`
- [ ] No WSL/dev: rodar sem flag (janela normal)
- [ ] Tratar caso em que o arquivo não existe (pular silenciosamente)

### Fase 3 — Controller (`src/controller.py`)
- [ ] Inicializar `pygame.joystick`
- [ ] Mapear eventos: D-pad cima/baixo, botão confirmar (X/A), botão voltar (O/B)
- [ ] Fallback para teclado (setas + Enter) para dev no WSL
- [ ] Funcionar com controles PS e Xbox sem configuração extra

### Fase 4 — Menu OSD (`src/menu.py`)
- [ ] Carregar `ps1-bios.jpg` como background em 1920x1080
- [ ] Renderizar lista de apps do `apps.ini` com fonte Press Start 2P
- [ ] Desenhar seletor (retângulo/highlight roxo) sobre item ativo
- [ ] Navegar com D-pad, confirmar seleção, executar comando via subprocess
- [ ] Após app fechar, voltar ao menu
- [ ] Sem animações — interface estática fiel ao estilo da BIOS PS1

### Fase 5 — Entry point (`launcher.py`)
- [ ] Detectar plataforma (Linux/WSL vs Pi) via `platform.system()`
- [ ] Setar variáveis de ambiente SDL conforme plataforma
- [ ] Chamar intro → menu em sequência
- [ ] Tratar SIGTERM para shutdown limpo

### Fase 6 — Deploy no Pi
- [ ] Criar `systemd/ps1-osd-laucher.service`
- [ ] Configurar autologin no tty1
- [ ] Testar transição launcher → app → launcher
- [ ] Ajustar permissões para `sudo shutdown` sem senha (sudoers)

---

## Dependências

### Python
```
pygame>=2.5.0
```

### Sistema (Pi)
```
mpv
python3-pygame
```

### Fontes
- [Press Start 2P](https://fonts.google.com/specimen/Press+Start+2P) — baixar TTF e colocar em `assets/fonts/`

---

## Notas de Desenvolvimento (WSL2)

- WSL2 com WSLg suporta GUI nativa — pygame abre janela normalmente
- Não setar `SDL_VIDEODRIVER=kmsdrm` no ambiente de dev (só no Pi)
- O comando `mpv` no WSL abre em janela normal (sem `--vo=drm`)
- Testar controller físico: WSL2 pode não passar o joystick — usar teclado como fallback durante dev
- Para testar resolução 1080p no WSL: `pygame.display.set_mode((1920, 1080))`  pode abrir maior que o monitor, usar `(960, 540)` durante dev se necessário

---

## Notas do Pi

- Systemd unit com `After=multi-user.target`
- `Environment=SDL_VIDEODRIVER=kmsdrm`
- `Environment=SDL_FBDEV=/dev/fb0`
- Usuário precisa estar no grupo `video` e `input`
