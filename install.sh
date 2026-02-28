#!/bin/bash
# Roda no Pi após git clone/pull

set -e

INSTALL_DIR="/home/douglasdans/ps1-launcher"

echo ">>> Instalando dependências..."
sudo apt install -y python3-pygame mpv

echo ">>> Copiando service..."
sudo cp "$INSTALL_DIR/systemd/ps1-launcher.service" /etc/systemd/system/

echo ">>> Permissão de shutdown sem senha..."
echo "douglasdans ALL=(ALL) NOPASSWD: /sbin/shutdown, /sbin/reboot" | sudo tee /etc/sudoers.d/ps1-launcher > /dev/null

echo ">>> Habilitando e iniciando service..."
sudo systemctl daemon-reload
sudo systemctl enable ps1-launcher
sudo systemctl start ps1-launcher

echo ">>> Pronto! Status:"
sudo systemctl status ps1-launcher
