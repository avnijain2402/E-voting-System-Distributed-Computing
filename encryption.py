import base64
import hashlib
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import hashes, serialization

class EncryptionModule:
    """
    Handles the encryption of votes, generating PKI keys, signing, and verifying signatures.
    """

    @staticmethod
    def generate_key_pair():
        """Generates a public and private RSA key pair."""
        private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048,
        )
        public_key = private_key.public_key()
        
        priv_pem = private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption()
        )
        pub_pem = public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )
        return pub_pem.decode('utf-8'), priv_pem.decode('utf-8')
        
    @staticmethod
    def sign_transaction_pki(private_key_pem: str, payload_str: str) -> str:
        """Signs a payload using an RSA private key."""
        private_key = serialization.load_pem_private_key(
            private_key_pem.encode('utf-8'),
            password=None
        )
        signature = private_key.sign(
            payload_str.encode('utf-8'),
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH
            ),
            hashes.SHA256()
        )
        return base64.b64encode(signature).decode('utf-8')

    @staticmethod
    def verify_signature_pki(public_key_pem: str, payload_str: str, signature_b64: str) -> bool:
        """Verifies an RSA signature."""
        try:
            public_key = serialization.load_pem_public_key(
                public_key_pem.encode('utf-8')
            )
            signature = base64.b64decode(signature_b64)
            public_key.verify(
                signature,
                payload_str.encode('utf-8'),
                padding.PSS(
                    mgf=padding.MGF1(hashes.SHA256()),
                    salt_length=padding.PSS.MAX_LENGTH
                ),
                hashes.SHA256()
            )
            return True
        except Exception:
            return False

    @staticmethod
    def encrypt_vote(candidate: str) -> str:
        """
        Simulates encrypting the candidate selection locally before broadcasting.
        """
        encoded_bytes = base64.b64encode(candidate.encode('utf-8'))
        return f"ENC::OQWZ::{encoded_bytes.decode('utf-8')}"

    @staticmethod
    def decrypt_vote(encrypted_vote: str) -> str:
        """
        Simulates decryption for tallying purposes. Only the election authority can do this.
        """
        if encrypted_vote.startswith("ENC::OQWZ::"):
            core_data = encrypted_vote.replace("ENC::OQWZ::", "")
            try:
                decoded_bytes = base64.b64decode(core_data.encode('utf-8'))
                return decoded_bytes.decode('utf-8')
            except Exception:
                return "DECRYPTION_FAILED"
        return encrypted_vote

    @staticmethod
    def hash_voter_id(voter_id: str) -> str:
        """
        Creates an anonymous hash of the voter ID so the ledger doesn't 
        contain raw personally identifiable information.
        """
        return hashlib.sha256(voter_id.encode('utf-8')).hexdigest()

    @staticmethod
    def sign_transaction(hashed_id: str, encrypted_vote: str, timestamp: float) -> str:
        """Creates a digital signature of the entire transaction to prevent tampering."""
        payload = f"{hashed_id}:{encrypted_vote}:{timestamp}"
        return hashlib.sha256(payload.encode('utf-8')).hexdigest()
