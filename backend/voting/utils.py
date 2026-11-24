import hashlib
from cryptography.fernet import Fernet
from django.conf import settings # To access the key from settings.py

# --- Load the Key ---
# Fetch the key defined in settings.py
# Ensure it's stored as bytes (b'...') in settings.py
try:
    VOTE_ENCRYPTION_KEY = settings.VOTE_ENCRYPTION_KEY
    if not isinstance(VOTE_ENCRYPTION_KEY, bytes):
        # Attempt to encode if it wasn't stored as bytes literal
        VOTE_ENCRYPTION_KEY = VOTE_ENCRYPTION_KEY.encode('utf-8') 
    cipher_suite = Fernet(VOTE_ENCRYPTION_KEY)
except AttributeError:
    # Handle case where key is not defined in settings - raises error at startup
    raise ImproperlyConfigured("VOTE_ENCRYPTION_KEY is not defined in settings.py")
except Exception as e:
    # Handle other potential errors loading the key (e.g., invalid key format)
    raise ValueError(f"Error initializing Fernet cipher with VOTE_ENCRYPTION_KEY: {e}")

# --- Hashing Function (remains the same if needed, or can be removed if not used) ---
def hash_voter_id(voter_uid: str) -> str:
    """
    Convert voter ID into SHA256 hash for anonymity (if needed elsewhere).
    The cast_vote function now uses the voter_uid directly as voter_hash.
    """
    # You might not need this if voter_hash is just the voter_uid now
    # Consider using a salted hash if anonymity against DB admins is required
    salt = settings.SECRET_KEY # Example: Use Django's secret key as a salt (better to use a dedicated salt)
    return hashlib.sha256((voter_uid + salt).encode()).hexdigest()

# --- Encryption Function ---
def encrypt_vote(data_to_encrypt: str) -> str:
    """
    Encrypts the given string (e.g., candidate_id) using the secret key.
    Returns a URL-safe base64 encoded string.
    """
    if not isinstance(data_to_encrypt, str):
         data_to_encrypt = str(data_to_encrypt) # Ensure it's a string

    encrypted_data = cipher_suite.encrypt(data_to_encrypt.encode('utf-8'))
    return encrypted_data.decode('utf-8') # Return as a string

# --- Decryption Function ---
def decrypt_vote(encrypted_token: str) -> str:
    """
    Decrypts the given token (string) using the secret key.
    Returns the original string (e.g., candidate_id).
    Raises InvalidToken if decryption fails.
    """
    try:
        decrypted_data = cipher_suite.decrypt(encrypted_token.encode('utf-8'))
        return decrypted_data.decode('utf-8') # Return as a string
    except Exception as e: # Catch potential errors like InvalidToken from Fernet
         print(f"Error decrypting token: {e}") # Log the error
         # Decide how to handle decryption failure: re-raise, return None, or return an error indicator
         # Returning None or raising an exception is usually preferred
         raise ValueError(f"Decryption failed: {e}")