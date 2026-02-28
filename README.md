# PS1 OSD Launcher

Launcher minimalista com interface fiel à BIOS do PlayStation 1, feito para rodar em **Raspberry Pi 5** sem desktop, sem X11, sem RetroArch como frontend.

Faz parte do projeto **PS1 Pro** — uma modernização de um PlayStation 1 original com Raspberry Pi 5 interno, mantendo a identidade visual e a experiência do console.

> Post do projeto: [douglasdans.dev/blog/2026/01/ps1-pro-01](https://douglasdans.dev/blog/2026/01/ps1-pro-01/)

---

## O que resolve

O PS1 Pro roda **Raspberry Pi OS Lite** sem interface gráfica. O RetroArch era iniciado diretamente via systemd, não havia forma de instalar e acessar outros apps (Duckstation, PPSSPP, scripts de manutenção) sem teclado ou software adicional.

Este launcher resolve isso: é o **ponto central de acesso ao sistema**, controlável apenas com o controle, e permite abrir qualquer app configurado num arquivo `.ini`.

---

## Funcionalidades

- Intro da Sony (vídeo `assets/intro.mp4`) antes do menu
- Menu OSD visual fiel à BIOS original do PS1
  - Background roxo, fonte pixel, seletor arco-íris, label "MAIN MENU"
- Navegação 100% por controle — sem teclado, sem mouse
- Suporte universal a controles via **SDL2 GameController API** + [SDL_GameControllerDB](https://github.com/mdqinc/SDL_GameControllerDB)
  - PS (DualShock/DualSense), Xbox One/Series, 8BitDo, e qualquer controle no banco de 2200+ mapeamentos
- Apps configuráveis via `apps.ini` — adicione RetroArch, emuladores standalone, scripts ou qualquer comando
- Auto-update via `git pull` no boot — push do seu PC, Pi atualiza sozinho
- Iniciado automaticamente via **systemd** no boot

---

## Como funciona

```
Boot
 └── systemd: git pull (auto-update)
      └── python3 launcher.py
            ├── mpv: toca intro.mp4 (se existir)
            └── pygame: menu OSD
                  ├── lê apps.ini
                  ├── navega com controle
                  └── seleciona app
                        ├── libera o display (DRM)
                        ├── subprocess: executa o app
                        └── volta ao menu quando o app fechar
```

---

## Requisitos

### Hardware
- Raspberry Pi 5 (testado com 4GB)
- Controle USB ou Bluetooth (PS, Xbox, 8BitDo, genérico)

### Sistema
- Raspberry Pi OS Lite (Bookworm)
- Sem desktop, sem X11

### Dependências
```
python3-pygame
mpv
```

---

## Estrutura

```
ps1-osd-laucher/
├── launcher.py               # Entry point
├── apps.ini                  # Configuração de apps (editável)
├── assets/
│   ├── ps1-bios.jpg          # Background do menu
│   ├── intro.mp4             # Intro Sony — adicionar manualmente
│   ├── gamecontrollerdb.txt  # Mapeamentos SDL2 (2200+ controles)
│   └── fonts/
│       └── PressStart2P.ttf  # Fonte do menu
├── src/
│   ├── config.py             # Leitura do apps.ini
│   ├── intro.py              # Reprodução da intro
│   ├── controller.py         # Input normalizado (SDL2 GameController API)
│   └── menu.py               # Menu OSD pygame
├── systemd/
│   └── ps1-osd-laucher.service
└── install.sh                # Script de instalação no Pi
```

---

## Configurar apps (`apps.ini`)

```ini
[apps]
RetroArch    = retroarch
Duckstation  = duckstation-qt
PPSSPP       = ppsspp
Desligar     = sudo shutdown -h now
Reiniciar    = sudo reboot
```

- **Chave** = nome exibido no menu
- **Valor** = comando shell executado
- A ordem no arquivo define a ordem no menu
- Edite via SSH e reinicie o service para aplicar

---

## Instalação no Pi

### 1. Clonar o repositório
```bash
git clone https://github.com/seu-usuario/ps1-osd-laucher.git /home/douglasdans/ps1-osd-laucher
cd /home/douglasdans/ps1-osd-laucher
```

### 2. Adicionar a intro (opcional)
```bash
# Na sua máquina:
scp intro.mp4 douglasdans@<ip-do-pi>:/home/douglasdans/ps1-osd-laucher/assets/
```

### 3. Rodar o instalador
```bash
bash install.sh
```

O `install.sh` faz:
- Instala `python3-pygame` e `mpv`
- Copia o service para `/etc/systemd/system/`
- Dá permissão de `shutdown`/`reboot` sem senha
- Habilita e inicia o service

### 4. Desabilitar o service anterior (se houver)
```bash
sudo systemctl disable retroarch.service
sudo systemctl stop retroarch.service
```

---

## Atualizar o projeto

Do seu PC/WSL:
```bash
git push
```

No próximo boot, o Pi faz `git pull` automaticamente antes de iniciar o launcher. Para forçar imediatamente:
```bash
# No Pi:
cd /home/douglasdans/ps1-osd-laucher && git pull
sudo systemctl restart ps1-osd-laucher
```

---

## Desenvolvimento local (WSL / Linux)

```bash
# Instalar dependências
sudo apt install python3-pygame mpv

# Rodar
python3 launcher.py
```

No WSL com WSLg, abre uma janela pygame normal. No Pi, usa KMSDRM direto no framebuffer. O controle detectado por plataforma automaticamente — teclado funciona como fallback (setas + Enter + Escape).

---

## Mapeamento de controle

| Ação | PS | Xbox | Teclado |
|---|---|---|---|
| Navegar | D-pad ↑↓ | D-pad ↑↓ | ↑↓ |
| Confirmar | X (Cruz) | A | Enter |
| Voltar / Sair | O (Círculo) | B | Escape |

Funciona com qualquer controle no [SDL_GameControllerDB](https://github.com/mdqinc/SDL_GameControllerDB).

---

## Logs e debug

```bash
# Ver logs em tempo real
sudo journalctl -u ps1-osd-laucher -f

# Ver últimas 50 linhas
sudo journalctl -u ps1-osd-laucher -n 50 --no-pager

# Reiniciar manualmente
sudo systemctl restart ps1-osd-laucher
```
