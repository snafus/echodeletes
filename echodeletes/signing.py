import os

from hashlib import blake2b
from hmac import compare_digest

# e.g. base64.encodebytes(os.urandom(34)).strip()
# blake2b needs 64 bytes; 16 from the uuid and remaining 48 from the secret key
SECRET_KEY = os.getenv("ECHODELETES_SIGNINGKEY").encode('utf8')
assert SECRET_KEY is not None
AUTH_SIZE = 16

def sign(message_asbytes, uuid_asbytes):
    """Sign a message using the uuid and secret key"""
    key = uuid_asbytes+SECRET_KEY
    assert len(key) == 64, len(key) 
    h = blake2b(digest_size=AUTH_SIZE, key=uuid_asbytes+SECRET_KEY)
    h.update(message_asbytes)
    return h.hexdigest().encode('utf-8')

def verify(message_asbytes, uuid_asbytes, sig):
    """Verify a signature (in bytes), from the original messge, uuid and secret key"""
    good_sig = sign(message_asbytes, uuid_asbytes)
    return compare_digest(good_sig, sig)
