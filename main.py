import random
import requests

from urllib.parse import urlencode, parse_qs, urlsplit
from bot_server import record_prize, get_random_qr

from config import (
    QR_CODE,
    PHONE_NUMBER,
    PASSWORD,
    BOT_SERVER_BASE_URL,
    OAUTH2_BASE_URL,
    GAMES_BASE_URL,
    LOGIN_FORM_URL,
    REDIRECT_URI,
    CLIENT_ID,
    CHECKIN_URL
)

# --- Constants ---
BASE62 = '0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'
BASE67 = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-_.!~'

# --- Utils ---
def get_random_string(alphabet, length):
    return ''.join(random.choice(alphabet) for _ in range(length))

# --- Auth ---
def get_auth_token(phone_number, password, session):
    auth_params = {
        'response_type': 'code',
        'scope': 'checkin offline_access openid',
        'client_id': CLIENT_ID,
        'redirect_uri': REDIRECT_URI,
        'state': get_random_string(BASE62, 14),
        'nonce': get_random_string(BASE67, 32),
        'audience': 'https://api.profi.lobyco.net/promotion'
    }

    response = session.get(f"{OAUTH2_BASE_URL}/auth?{urlencode(auth_params)}")
    login_challenge = parse_qs(urlsplit(response.url).query).get('login_challenge', [''])[0]

    login_payload = {'username': phone_number, 'password': password, 'rememberMe': False}
    response = session.post(f"{LOGIN_FORM_URL}?{urlencode({'login_challenge': login_challenge})}", json=login_payload)

    redirect_to = response.json().get('redirectTo', '')
    for _ in range(3):
        if not redirect_to:
            break
        response = session.get(redirect_to, allow_redirects=False)
        redirect_to = response.headers.get('Location', '')

    final_url = response.headers.get('Location', '')
    code = parse_qs(urlsplit(final_url).query).get('code', [''])[0]

    token_data = {
        'grant_type': 'authorization_code',
        'code': code,
        'client_id': CLIENT_ID,
        'redirect_uri': REDIRECT_URI
    }

    token_response = session.post(f"{OAUTH2_BASE_URL}/token", data=token_data)
    token_response_data = token_response.json()

    if token_response.status_code != 200:
        print("Failed to authenticate!")
        print(f"Response: HTTP {response.status_code} - {token_response_data.get('error')} ({token_response_data.get('error_description')})")

    return token_response_data['access_token']

# --- QR Functions ---
def check_in_qr(payment_location, auth_token, session):
    url = f"{CHECKIN_URL}/state?paymentLocation={payment_location}"
    headers = {'Authorization': f'Bearer {auth_token}'}
    response = session.get(url, headers=headers)
    data = response.json()

    print(f"Checked in at payment location {payment_location}! Response: HTTP {response.status_code} - {data.get('messageTitle')} {data.get('messageBody')}")

def get_qr_code(session):
    qr_code = None

    if BOT_SERVER_BASE_URL is not None:
        print("Fetching a random QR Code...")
        try:
            qr_code = get_random_qr(session)
        except Exception as e:
            print(f"Failed to fetch a random QR Code: {e}")
            print("Using the configured QR Code instead.")

    if qr_code is None:
        return QR_CODE

    return qr_code

def scan_qr_code(qr_code, auth_token, session):
    headers = {'Authorization': f'Bearer {auth_token}'}
    response = session.post(CHECKIN_URL, json={"qrCode": qr_code}, headers=headers)
    data = response.json()

    if response.status_code == 200:
        payment_location = data.get('paymentLocation')
        if payment_location:
            check_in_qr(payment_location, auth_token, session)
    else:
        print("Failed to create the session!")
        print(f"Response: HTTP {response.status_code} - {data.get('messageTitle')} {data.get('messageBody')}")

def play_game(auth_token, session):
    headers = {'Authorization': f'Bearer {auth_token}'}
    response = session.get(f"{GAMES_BASE_URL}/current", headers=headers)

    if response.status_code == 204:
        print('No game available')
        return

    data = response.json()

    game_id = data['gameId']
    start_game_response = session.post(f"{GAMES_BASE_URL}/{game_id}/start", headers=headers)
    start_game_response_data = start_game_response.json()

    game_url = start_game_response_data['gameUrl']

    prize_won = parse_qs(urlsplit(game_url).query).get('win', [''])[0]

    if prize_won == 'true':
        print("You have won this game!")
    else:
        print("You have lost this game!")

    redirect_url = parse_qs(urlsplit(game_url).query).get('redirectUrl', [''])[0]
    redirect_response = session.post(redirect_url, headers=headers)

    if redirect_response.status_code != 200:
        print("Failed to redirect!")
        print(f"Response: HTTP {redirect_response.status_code}")
        return

    if prize_won == "true" and BOT_SERVER_BASE_URL:
        record_prize(session)

# --- Main ---
def main():
    with requests.Session() as session:
        print(f"Authorising +{PHONE_NUMBER}...")
        qr_code = get_qr_code(session)

        if qr_code is None:
            print("Cannot proceed without a QR Code!")
            return

        auth_token = get_auth_token(PHONE_NUMBER, PASSWORD, session)

        print(f"Playing the daily game...")
        play_game(auth_token, session)

        print(f"Scanning QR code {qr_code}...")
        scan_qr_code(qr_code, auth_token, session)

if __name__ == "__main__":
    main()
