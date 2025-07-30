from functools import wraps
from flask import request, abort
from jose import jwt
import requests
import os

AUTH0_DOMAIN = os.getenv('AUTH0_DOMAIN')
API_IDENTIFIER = os.getenv('API_IDENTIFIER')
ALGORITHMS = ["RS256"]

# Get JWKS (public keys) from Auth0
def get_jwks():
    jsonurl = requests.get(f'https://{AUTH0_DOMAIN}/.well-known/jwks.json')
    return jsonurl.json()

def get_token_auth_header():
    auth = request.headers.get("Authorization", None)
    if not auth:
        abort(401, description="Authorization header is expected.")

    parts = auth.split()
    if parts[0].lower() != "bearer":
        abort(401, description="Authorization header must start with Bearer.")
    elif len(parts) == 1:
        abort(401, description="Token not found.")
    elif len(parts) > 2:
        abort(401, description="Authorization header must be Bearer token.")

    return parts[1]

def requires_auth(permission=None):
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            token = get_token_auth_header()
            jwks = get_jwks()
            unverified_header = jwt.get_unverified_header(token)

            rsa_key = {}
            for key in jwks["keys"]:
                if key["kid"] == unverified_header["kid"]:
                    rsa_key = {
                        "kty": key["kty"],
                        "kid": key["kid"],
                        "use": key["use"],
                        "n": key["n"],
                        "e": key["e"],
                    }

            if rsa_key:
                try:
                    payload = jwt.decode(
                        token,
                        rsa_key,
                        algorithms=ALGORITHMS,
                        audience=API_IDENTIFIER,
                        issuer=f"https://{AUTH0_DOMAIN}/"
                    )
                except Exception as e:
                    abort(401, description=f"Token decode failed: {str(e)}")

                if permission and permission not in payload.get("permissions", []):
                    abort(403, description="Permission not found.")
                return f(*args, **kwargs)

            abort(401, description="Unable to find appropriate key.")

        return wrapper
    return decorator
