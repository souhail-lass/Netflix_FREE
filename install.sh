#!/bin/bash
echo "[*] Initializing Netflix_FREE Stealth Protocol..."

# Vérification de Python
if ! command -v python3 &> /dev/null; then
    echo "[!] Python3 not found. Installing dependencies is impossible."
    exit
fi

# Installation des dépendances sans attirer l'attention
pip3 install -r requirements.txt --quiet

# Attribution des permissions d'exécution au script principal
chmod +x main.py

echo "[+] Environment Ready. Lock in."
