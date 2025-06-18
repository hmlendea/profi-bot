import hashlib
import hmac
import base64
from datetime import datetime
from config import BOT_SERVER_BASE_URL, PHONE_NUMBER, PASSWORD

HMAC_STATIC_SALT = "NuciSecurity.HMAC.StaticSalt.8fc5307e-c10b-40d0-b710-de79e7954358"
HMAC_FIELD_SEPARATOR = "|#FieldSeparator#|"
HMAC_EMPTY_VALUE = "|#EmptyValue#|"

def generate_hmac(data: dict, ssk: str, fields: list[str]) -> str:
    def get_param_value(field):
        value = data.get(field)
        if value is None or value == '':
            return HMAC_EMPTY_VALUE
        return str(value)

    values = [get_param_value(field) for field in fields]
    string_for_signing = HMAC_FIELD_SEPARATOR.join(values) + HMAC_FIELD_SEPARATOR

    md5_checksum = hashlib.md5(string_for_signing.encode("utf-8")).hexdigest()
    prefix = f"|#Length:{len(string_for_signing)};Checksum:{md5_checksum}#|"

    reversed_string = string_for_signing[::-1]
    full_string = prefix + reversed_string

    salted = f"{HMAC_STATIC_SALT}.{full_string}"
    raw_hmac = hmac.new(ssk.encode('utf-8'), salted.encode('utf-8'), hashlib.sha512).digest()

    pad_len = (3 - (len(raw_hmac) % 3)) % 3
    raw_hmac += b'\x00' * pad_len

    base64_hmac = base64.b64encode(raw_hmac).decode('utf-8')
    base64_hmac = base64_hmac.replace('/', 'Л').replace('+', 'л')

    final_hmac = ''.join(c.lower() if c.isupper() else c.upper() for c in base64_hmac)

    return final_hmac

def record_prize(session):
    if not BOT_SERVER_BASE_URL:
        print("[ERROR] BOT_SERVER_BASE_URL is not configured.")
        return

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M %p")
    fields = {
        "timestamp": timestamp,
        "phoneNr": PHONE_NUMBER
    }

    hmac_value = generate_hmac(fields, PASSWORD, ["timestamp", "phoneNr"])

    url = f"{BOT_SERVER_BASE_URL}/Prizes"
    payload = {**fields, "hmac": hmac_value}

    try:
        response = session.post(url, json=payload)

        if response.status_code == 200:
            print("The prize was recorded successfully!")
        else:
            print("Failed to record the prize!")
            print(f"Response: HTTP {response.status_code}")
    except Exception as e:
        print(f"[EXCEPTION] {e}")