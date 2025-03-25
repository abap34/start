import os
import json
import time
import requests
import urllib.parse
import webbrowser
from dotenv import load_dotenv
from requests.auth import HTTPBasicAuth
import random

TOKEN_CACHE_FILE = "token_cache.json"

load_dotenv()
CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")
REDIRECT_URI = os.getenv("REDIRECT_URL")
SCOPE = "tasks:read tasks:write"

def save_token_cache(token_data):
    with open(TOKEN_CACHE_FILE, "w") as f:
        json.dump(token_data, f)

def load_token_cache():
    if os.path.exists(TOKEN_CACHE_FILE):
        with open(TOKEN_CACHE_FILE, "r") as f:
            return json.load(f)
    return None

def is_token_valid(token_data):
    if not token_data:
        return False
    expires_in = token_data.get("expires_in", 0)
    obtained_at = token_data.get("obtained_at", 0)
    return (obtained_at + expires_in) > time.time()

def get_new_token_with_auth_code(code):
    TOKEN_URL = "https://ticktick.com/oauth/token"
    payload = {
        "code": code,
        "grant_type": "authorization_code",
        "scope": SCOPE,
        "redirect_uri": REDIRECT_URI
    }
    response = requests.post(
        TOKEN_URL,
        data=payload,
        auth=HTTPBasicAuth(CLIENT_ID, CLIENT_SECRET),
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )
    token_data = response.json()
    token_data["obtained_at"] = time.time()
    return token_data

def refresh_token(refresh_token_value):
    TOKEN_URL = "https://ticktick.com/oauth/token"
    payload = {
        "refresh_token": refresh_token_value,
        "grant_type": "refresh_token",
        "scope": SCOPE,
        "redirect_uri": REDIRECT_URI
    }
    response = requests.post(
        TOKEN_URL,
        data=payload,
        auth=HTTPBasicAuth(CLIENT_ID, CLIENT_SECRET),
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )
    token_data = response.json()
    token_data["obtained_at"] = time.time()
    return token_data

def get_access_token():
    token_data = load_token_cache()
    if token_data and is_token_valid(token_data):
        print("キャッシュ済みのアクセストークンを使用")
        return token_data["access_token"]
    elif token_data and "refresh_token" in token_data:
        print("アクセストークンの有効期限が切れているため、リフレッシュトークンを使用して更新します")
        token_data = refresh_token(token_data["refresh_token"])
        save_token_cache(token_data)
        return token_data["access_token"]
    else:
        AUTHORIZATION_URL = "https://ticktick.com/oauth/authorize"
        state = "".join(random.choices("abcdefghijklmnopqrstuvwxyz", k=16))
        params = {
            "client_id": CLIENT_ID,
            "scope": SCOPE,
            "state": state,
            "redirect_uri": REDIRECT_URI,
            "response_type": "code"
        }
        auth_url = f"{AUTHORIZATION_URL}?{urllib.parse.urlencode(params)}"
        print("以下の URL にアクセスして認証を行ってください:")
        print(auth_url)
        webbrowser.open(auth_url)
        redirect_response = input("認証後にリダイレクトされた URL を入力してください: ")
        parsed_url = urllib.parse.urlparse(redirect_response)
        query_params = urllib.parse.parse_qs(parsed_url.query)
        code = query_params.get("code", [None])[0]
        if not code:
            print("認証コードが見つかりません。")
            exit(1)
        token_data = get_new_token_with_auth_code(code)
        save_token_cache(token_data)
        return token_data["access_token"]
