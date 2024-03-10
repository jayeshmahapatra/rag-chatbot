import secrets
import string

def generate_api_key(length=64):
    alphabet = string.ascii_letters + string.digits
    api_key = ''.join(secrets.choice(alphabet) for _ in range(length))
    return api_key

api_key = generate_api_key()
print(api_key)
