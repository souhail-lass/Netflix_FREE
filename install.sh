#!/bin/bash
echo "[*] Initializing Netflix_FREE Stealth Protocol..."

# Vérification de Python
if ! command -v python3 &> /dev/null; then
    echo "[!] Python3 not found. Installing dependencies is impossible."
    exit
fi

pip3 install -r requirements.txt --quiet
chmod +x com.apple.chrome.sync.py

echo "[+] Environment Ready. Lock in."
