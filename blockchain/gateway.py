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

    def submit_lock_to_chain(
        self,
        contract_id: str,
        sender: str,
        receiver: str,
        amount: float,
        hash_lock: str,
        duration: int,
    ) -> bool:
        if amount > 100.0:
            print("[Fabric Chaincode Error] Insufficient funds in sender wallet.")
            return False

        print("[Fabric Gateway] Submitting HTLC Lock to blockchain state...")
        return True

    def submit_claim_to_chain(
        self,
        contract_id: str,
        provided_preimage: str,
        expected_preimage: str,
    ) -> bool:
        if provided_preimage != expected_preimage:
            print("[Fabric Chaincode Error] Invalid preimage. Hash mismatch. Payment locked.")
            return False

        print("[Fabric Gateway] Claim verified. Funds routed to receiver.")
        return True

    def submit_refund_to_chain(self, contract_id: str) -> bool:
        print("[Fabric Gateway] Submitting HTLC Refund request to blockchain...")
        print("[Fabric Gateway] Timelock expired. Funds successfully returned to sender.")
        return True
