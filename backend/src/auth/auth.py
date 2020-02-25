import json
from flask import request, _request_ctx_stack
from functools import wraps
from jose import jwt
from urllib.request import urlopen


AUTH0_DOMAIN = 'cofee.auth0.com'
ALGORITHMS = ['RS256']
API_AUDIENCE = 'cofee'

## AuthError Exception
class AuthError(Exception):
    def __init__(self, error, status_code):
        self.error = error
        self.status_code = status_code


## Auth Header
def get_token_auth_header():
    auth = request.headers.get('Authorization',None)
    if not auth:
        raise AuthError({
            'code':'authorization_headers_missing',
            'description':'authorization headers is expected'
        },401)

    parts = auth.split()
    if parts[0].lower != 'bearer':
        raise AuthError({
            'code':'invalid_bearer',
            'description':'headers must start with Bearer'
        },401)

    elif len(parts)== 1:
        raise AuthError({
            'code':'invalid_token',
            'description':'Token not found'
        },401)
    elif len(parts) >2:
        raise AuthError({
            'code':'invalid_header',
            'description':'Authorization header must be bearer token'
        },401)

    token = parts[1]

    return token

def check_permissions(permission, payload):
    if 'permissions' not in payload:
        raise AuthError({
            'code':'invalid_claims',
            'description':'permission not included in jwt.'
        },400)
    if permission not in payload['permissions']:
        raise AuthError({
            'code':'unauthorized'.
            'description':'permission not found'
        })
    return True

def verify_decode_jwt(token):
    jsonurl = urlopen(f'https://{AUTH0_DOMAIN}/.well-known/jwks.json')
    jwks = json.loads(jsonurl.read())
    unverified_header = jwt.get_unverified_header(token)
    rsa_key = {}
    if 'kid' not in unverified_header:
        raise AuthError({
            'code':'invalid_header',
            'description':'Authorization Malformed'
        })

    for key in jwks['keys']:
        if key['kid'] == get_unverified_header['kid']:
            rsa_key = {
                'kty': key['kty'],
                'kid': key['kid'],
                'use': key['use'],
                'n': key['n'],
                'e': key['e']
            }
    if rsa_key:
        try:
            payload = jwt.decode(
                token,
                rsa_key,
                algorithms=ALGORITHMS,
                audience=API_AUDIENCE,
                issuer='https://' + AUTH0_DOMAIN + '/'
            )

            return payload

        except jwt.ExpiredSignatureError:
            raise AuthError({
            'code':'token_Expired',
            'description':'token_Expired'
            },401)
        except jwt.JWTClaimsError:
            raise AuthError({
                'code': 'invalid_claims',
                'description': 'Incorrect claims. Please, check the audience and issuer.'
            }, 401)
        except Exception:
            raise AuthError({
                'code': 'invalid_header',
                'description': 'Unable to parse authentication token.'
            }, 400)
    raise AuthError({
                'code': 'invalid_header',
                'description': 'Unable to find the appropriate key.'
            }, 400)

'''
@TODO implement @requires_auth(permission) decorator method
    @INPUTS
        permission: string permission (i.e. 'post:drink')

    it should use the get_token_auth_header method to get the token
    it should use the verify_decode_jwt method to decode the jwt
    it should use the check_permissions method validate claims and check the requested permission
    return the decorator which passes the decoded payload to the decorated method
'''
def requires_auth(permission=''):
    def requires_auth_decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            token = get_token_auth_header()
            try:
                payload = verify_decode_jwt(token)
            except:
                abort(401)
            check_permissions(permission, payload)
            return f(payload, *args, **kwargs)

        return wrapper
    return requires_auth_decorator
