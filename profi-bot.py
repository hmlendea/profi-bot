import json
import random
import requests
from urllib.parse import urlencode, parse_qs, urlsplit

# --- Constants ---
OAUTH2_BASE_URL = 'https://auth.profi.lobyco.net/oauth2'
GAMES_BASE_URL = 'https://api.profi.lobyco.net/game/mobile-app/v1/games'
LOGIN_FORM_URL = 'https://idp.profi.lobyco.net/api/web/v1/session'
REDIRECT_URI = 'https://mobile-app/auth-redirect'
CLIENT_ID = 'mobile-app'
CHECKIN_URL = 'https://api.profi.lobyco.net/payment/mobile-app/v1/checkin'
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

    return session.post(f"{OAUTH2_BASE_URL}/token", data=token_data).json()['access_token']

# --- QR Functions ---
def check_in_qr(payment_location, auth_token, session):
    url = f"{CHECKIN_URL}/state?paymentLocation={payment_location}"
    headers = {'Authorization': f'Bearer {auth_token}'}
    response = session.get(url, headers=headers)
    data = response.json()

    print(f"Checked in at payment location {payment_location}! Response: HTTP {response.status_code} - {data.get('messageTitle')} {data.get('messageBody')}")

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
    start_game_response = session.post(f"{GAMES_BASE_URL}/{game_id}/start", headers=headers).json()
    win_status = parse_qs(urlsplit(start_game_response['gameUrl']).query).get('win', [''])[0]
    print(f"Prize won: {win_status}")

# --- Main ---
def load_config():
    with open('config.json') as f:
        return json.load(f)

def validate_config(config):
    if [k for k in ['phoneNumber', 'password', 'qrCode'] if not config.get(k)]:
        print(f"The configuration could not be loaded: Missing fields - {', '.join(missing)}")
        return False
    return True

def main():
    config = load_config()
    if not validate_config(config):
        return

    phone_number = f"4{config['phoneNumber']}"
    password = config['password']
    qr_code = config['qrCode']

    with requests.Session() as session:
        print(f"Authorising +{phone_number}...")
        auth_token = get_auth_token(phone_number, password, session)

        print(f"Playing the daily game...")
        play_game(auth_token, session)

        print(f"Scanning QR code {qr_code}...")
        scan_qr_code(qr_code, auth_token, session)

if __name__ == "__main__":
    main()
