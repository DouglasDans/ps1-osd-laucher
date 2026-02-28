#!/bin/bash
# Roda no Pi após git clone/pull

set -e

INSTALL_DIR="/home/douglasdans/ps1-osd-laucher"

echo ">>> Instalando dependências..."
sudo apt install -y python3-pygame mpv

echo ">>> Copiando service..."
sudo cp "$INSTALL_DIR/systemd/ps1-osd-laucher.service" /etc/systemd/system/

echo ">>> Permissão de shutdown sem senha..."
echo "douglasdans ALL=(ALL) NOPASSWD: /sbin/shutdown, /sbin/reboot" | sudo tee /etc/sudoers.d/ps1-osd-laucher > /dev/null

echo ">>> Habilitando e iniciando service..."
sudo systemctl daemon-reload
sudo systemctl enable ps1-osd-laucher
sudo systemctl start ps1-osd-laucher

echo ">>> Pronto! Status:"
sudo systemctl status ps1-osd-laucher
