python
# File ini untuk dijalankan di LAPTOP Anda
# Untuk upload JSON dari MT5 ke internet

import json
import time
import os
from datetime import datetime
import requests
import schedule

# ========== KONFIGURASI ==========
# Path ke file JSON dari MT5 EA
MT5_JSON_PATH = r"C:\Users\YOUR_USERNAME\AppData\Roaming\MetaQuotes\Terminal\YOUR_MT5_ID\MQL5\Files\trade_data.json"

# Pilih salah satu metode upload:
# 1. GITHUB GIST (Recommended)
GITHUB_TOKEN = "your_github_token_here"
GIST_ID = "your_gist_id_here"

# 2. PASTEBIN (Alternatif)
PASTEBIN_API_KEY = "your_pastebin_api_key"

# 3. DROPBOX (Alternatif)
DROPBOX_TOKEN = "your_dropbox_token"

# Interval upload (detik)
UPLOAD_INTERVAL = 5

# ========== FUNGSI UPLOAD ==========
def upload_to_github_gist():
    """Upload JSON ke GitHub Gist"""
    try:
        if not os.path.exists(MT5_JSON_PATH):
            print(f"[{datetime.now()}] File not found: {MT5_JSON_PATH}")
            return False
        
        with open(MT5_JSON_PATH, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Coba parse JSON untuk validasi
        try:
            json.loads(content)
        except:
            print("Invalid JSON content")
            return False
        
        # Update Gist
        url = f"https://api.github.com/gists/{GIST_ID}"
        headers = {
            "Authorization": f"token {GITHUB_TOKEN}",
            "Accept": "application/vnd.github.v3+json"
        }
        
        data = {
            "files": {
                "mt5_trades.json": {
                    "content": content
                }
            }
        }
        
        response = requests.patch(url, headers=headers, json=data)
        
        if response.status_code == 200:
            gist_data = response.json()
            raw_url = gist_data['files']['mt5_trades.json']['raw_url']
            print(f"[{datetime.now()}] ✅ Uploaded to GitHub Gist")
            print(f"       URL: {raw_url}")
            return raw_url
        else:
            print(f"[{datetime.now()}] ❌ Upload failed: {response.text}")
            return False
            
    except Exception as e:
        print(f"[{datetime.now()}] ❌ Error: {str(e)}")
        return False

def upload_to_pastebin():
    """Upload ke Pastebin (alternatif)"""
    try:
        with open(MT5_JSON_PATH, 'r') as f:
            content = f.read()
        
        data = {
            'api_dev_key': PASTEBIN_API_KEY,
            'api_option': 'paste',
            'api_paste_code': content,
            'api_paste_name': 'mt5_trades.json',
            'api_paste_format': 'json',
            'api_paste_private': '1'  # Unlisted
        }
        
        response = requests.post('https://pastebin.com/api/api_post.php', data=data)
        
        if response.text.startswith('https://'):
            print(f"[{datetime.now()}] ✅ Uploaded to Pastebin: {response.text}")
            return response.text
        else:
            print(f"[{datetime.now()}] ❌ Pastebin error: {response.text}")
            return False
            
    except Exception as e:
        print(f"Error: {str(e)}")
        return False

def main():
    """Main upload loop"""
    print("=" * 50)
    print("MT5 JSON Uploader")
    print("=" * 50)
    print(f"Monitoring: {MT5_JSON_PATH}")
    print(f"Interval: {UPLOAD_INTERVAL} seconds")
    print("=" * 50)
    
    last_modified = 0
    
    while True:
        try:
            # Cek jika file ada dan modified
            if os.path.exists(MT5_JSON_PATH):
                current_modified = os.path.getmtime(MT5_JSON_PATH)
                
                if current_modified > last_modified:
                    print(f"\n[{datetime.now()}] 📤 File modified, uploading...")
                    
                    # Pilih metode upload
                    url = upload_to_github_gist()  # Ganti dengan metode lain jika perlu
                    
                    if url:
                        print(f"[{datetime.now()}] ✅ Success!")
                        # Simpan URL untuk nanti
                        with open('upload_url.txt', 'w') as f:
                            f.write(url)
                    
                    last_modified = current_modified
                else:
                    print(f"[{datetime.now()}] ⏳ No changes", end='\r')
            
            time.sleep(UPLOAD_INTERVAL)
            
        except KeyboardInterrupt:
            print("\n\n👋 Uploader stopped by user")
            break
        except Exception as e:
            print(f"\n[{datetime.now()}] ⚠️ Error: {str(e)}")
            time.sleep(10)

if __name__ == "__main__":
    # Cek file path
    if not os.path.exists(MT5_JSON_PATH):
        print(f"❌ ERROR: File not found: {MT5_JSON_PATH}")
        print("\nTolong cari path file JSON Anda:")
        print("1. Buka MT5")
        print("2. Klik: File → Open Data Folder")
        print("3. Navigasi ke: MQL5 → Files")
        print("4. Cari file 'trade_data.json'")
        print("5. Copy full path nya")
    else:
        main()
