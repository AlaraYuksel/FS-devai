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


def main():
    parser = argparse.ArgumentParser(description="Uygulama için CLI")
    subparsers = parser.add_subparsers(dest="command", help="Kullanılabilir komutlar")

if __name__ == "__main__":
    main()