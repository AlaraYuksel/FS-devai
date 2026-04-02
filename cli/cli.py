import argparse
import json
import urllib.request
import urllib.parse
import urllib.error
import os

BASE_URL = "http://localhost:8000"
TOKEN_FILE = ".cli_token"

def save_token(token):
    with open(TOKEN_FILE, "w") as f:
        f.write(token)

def load_token():
    if os.path.exists(TOKEN_FILE):
        with open(TOKEN_FILE, "r") as f:
            return f.read().strip()
    return None

def make_request(method, endpoint, data=None, is_form=False, require_auth=False):
    url = f"{BASE_URL}{endpoint}"
    headers = {}
    
    if require_auth:
        token = load_token()
        if not token:
            print("Lütfen giriş yapın (login)")
            return None
        headers["Authorization"] = f"Bearer {token}"
        
    body = None
    if data:
        if is_form:
            # Login işlemi için Form Data
            body = urllib.parse.urlencode(data).encode("utf-8")
            headers["Content-Type"] = "application/x-www-form-urlencoded"
        else:
            # Diğer tüm işlemler için JSON Data
            body = json.dumps(data).encode("utf-8")
            headers["Content-Type"] = "application/json"
            
    req = urllib.request.Request(url, data=body, headers=headers, method=method)
    
    try:
        with urllib.request.urlopen(req) as response:
            return json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        print(f"HTTP Hatası: {e.code}")
    except urllib.error.URLError as e:
        print(f"Bağlantı hatası: {e.reason}")

def register(args):
    data = {
        "username": args.username,
        "email": args.email,
        "disabled": False,
        "hashed_password": args.password
    }
    response = make_request("POST", "/auth/register", data=data)
    if response:
        print(f"Kaydedildi: {response.get('username', args.username)}")



def main():
    parser = argparse.ArgumentParser(description="Uygulama için CLI")
    subparsers = parser.add_subparsers(dest="command", help="Kullanılabilir komutlar")

    parser_register = subparsers.add_parser("register", help="Yeni kullanıcı kaydı")
    parser_register.add_argument("username", type=str, help="Kullanıcı adı")
    parser_register.add_argument("email", type=str, help="E-posta adresi")
    parser_register.add_argument("password", type=str, help="Şifre")

    args = parser.parse_args()

    if args.command == "register":
        register(args)

if __name__ == "__main__":
    main()