import hashlib
import secrets


class HTLCManager:
    def create_lock(self, amount: float, receiver: str) -> dict:
        """Generate a hash time-locked contract entry for the given amount and receiver."""
        preimage = secrets.token_hex(32)
        payment_hash = hashlib.sha256(preimage.encode()).hexdigest()
        return {
            "amount": amount,
            "receiver": receiver,
            "preimage": preimage,
            "hash": payment_hash,
        }

    def verify_and_release(self, provided_preimage: str, stored_hash: str) -> bool:
        """Verify the supplied preimage against the stored hash."""
        return hashlib.sha256(provided_preimage.encode()).hexdigest() == stored_hash
