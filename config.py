import json
import os
import shutil

CONFIG_FILE = "config.json"
SAMPLE_FILE = "sample.config.json"

def load_config():
    if not os.path.exists(CONFIG_FILE):
        if os.path.exists(SAMPLE_FILE):
            shutil.copy(SAMPLE_FILE, CONFIG_FILE)
            print(f"[INFO] '{CONFIG_FILE}' was missing. Created from '{SAMPLE_FILE}'.")
        else:
            raise FileNotFoundError(f"Missing '{CONFIG_FILE}' and no '{SAMPLE_FILE}' to copy from.")

    with open(CONFIG_FILE, "r", encoding="utf-8") as f:
        config = json.load(f)

    # Validare
    required_fields = ['qrCode', 'phoneNumber', 'password']
    missing = [field for field in required_fields if field not in config or not config[field]]
    if missing:
        raise ValueError(f"The configuration could not be loaded: Missing fields - {', '.join(missing)}")

    return config

cfg = load_config()

QR_CODE = cfg["qrCode"]
PHONE_NUMBER = cfg["phoneNumber"]
PASSWORD = cfg["password"]

# Constants
OAUTH2_BASE_URL = 'https://auth.profi.lobyco.net/oauth2'
GAMES_BASE_URL = 'https://api.profi.lobyco.net/game/mobile-app/v1/games'
LOGIN_FORM_URL = 'https://idp.profi.lobyco.net/api/web/v1/session'
REDIRECT_URI = 'https://mobile-app/auth-redirect'
CLIENT_ID = 'mobile-app'
CHECKIN_URL = 'https://api.profi.lobyco.net/payment/mobile-app/v1/checkin'