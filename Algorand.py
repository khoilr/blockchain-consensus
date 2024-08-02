import hashlib
import math
import time
from decimal import Decimal
import random
from typing import List

import numpy as np
from ecdsa import SECP256k1, SigningKey, VerifyingKey

from transaction import Transaction


class Block:
    def __init__(
        self,
        transactions: List[Transaction],
        previous_hash: str,
        vrf_proof,
        verify_key,
    ):
        self.transactions = transactions
        self.previous_hash = previous_hash
        self.timestamp = int(time.time())
        self.vrf_proof = vrf_proof
        self.verify_key = verify_key
        self.hash = self.calculate_hash()

    def calculate_hash(self) -> str:
        block_data = f"{self.transactions}{self.previous_hash}{self.timestamp}{self.vrf_proof}{self.verify_key}"
        return hashlib.sha256(block_data.encode()).hexdigest()

    def __repr__(self):
        return f"""Block (
                    timestamp={self.timestamp},
                    hash={self.hash},
                    previous_hash={self.previous_hash},
                    vrf_proof={self.vrf_proof},
                    verify_key={self.verify_key},
                )"""


class Blockchain:
    def __init__(self):
        self.chain: List[Block] = []

        self.create_genesis_block()

    def create_genesis_block(self) -> None:
        genesis_block = Block([], "0", "0", "0")
        self.chain.append(genesis_block)

    def add_block(self, block: Block) -> None:
        if block.is_valid(self.get_last_block().hash):
            self.chain.append(block)

    def get_last_block(self) -> Block:
        return self.chain[-1]

    def get_new_block_index(self) -> int:
        return len(self.chain)

    def is_valid(self) -> bool:
        return all(
            self.chain[i].is_valid(target=self.target_from_difficulty(), previous_hash=self.chain[i - 1].hash)
            for i in range(1, len(self.chain))
        )


class Account:
    def __init__(self, stake):
        self.signing_key = SigningKey.generate(curve=SECP256k1)
        self.verify_key = self.signing_key.verifying_key
        self.stake = stake

    def generate_keypair(self):
        return self.signing_key.to_string().hex(), self.verify_key.to_string().hex()

    def prove(self, message):
        # Hash the message
        message_hash = hashlib.sha256(message).digest()

        # Sign the hash
        signature = self.signing_key.sign(message_hash)

        return signature.hex(), self.verify_key.to_string().hex()

    def verify(self, message, signature, verify_key):
        verify_key = VerifyingKey.from_string(bytes.fromhex(verify_key.to_string().hex()), curve=SECP256k1)
        message_hash = hashlib.sha256(message.encode()).digest()
        try:
            return verify_key.verify(bytes.fromhex(signature), message_hash)
        except Exception:
            return False

    def __repr__(self):
        return f"Account({self.address}, {self.stake})"


class Algorand(Blockchain):
    def __init__(self, accounts: List[Account]):
        self.accounts = accounts
        self.current_round = 0

        super().__init__()

    @property
    def total_stake(self):
        return sum(account.stake for account in self.accounts)

    @property
    def committee_size(self):
        return math.isqrt(len(self.accounts))

    def select_committee(self, seed, round_number):
        committee = []
        total_stake = self.total_stake

        for account in self.accounts:
            signature, verify_key = account.prove(seed + round_number.to_bytes(8, "big"))
            vrf_output = int(signature, 16)
            probability = Decimal(account.stake) / Decimal(total_stake)
            threshold = int(probability * 2**256)

            if vrf_output < threshold:
                committee.append(account)

        # If the committee is empty, use weighted choice based on stake
        if not committee:
            stakes = [account.stake for account in self.accounts]
            probabilities = [stake / total_stake for stake in stakes]

            while len(committee) < self.committee_size:
                selected = np.random.choice(self.accounts, p=probabilities)
                if selected not in committee:
                    committee.append(selected)

        return committee

    def select_proposer(self, committee, seed, round_number):
        min_hash = float("inf")
        proposer = None
        verify_key = None

        for account in committee:
            signature, _verify_key = account.prove(seed + b"proposer" + round_number.to_bytes(8, "big"))
            hash_int = int(signature, 16)
            if hash_int < min_hash:
                min_hash = hash_int
                proposer = account
                verify_key = _verify_key

        return proposer, verify_key

    def create_block(self, proposer: Account, transactions):
        previous_hash = self.get_last_block().hash if self.chain else b"0" * 32
        signature, _ = proposer.prove(previous_hash.encode())
        return Block(
            transactions,
            previous_hash,
            signature,
            proposer.verify_key,
        )

    def verify_block(self, committee: List[Account], block: Block):
        proposer_verify_key = block.verify_key

        # Verify proposer
        if proposer_verify_key not in [account.verify_key for account in committee]:
            return False

        # Verify VRF
        for account in committee:
            if not account.verify(block.previous_hash, block.vrf_proof, proposer_verify_key):
                return False

        return True

    def mine_block(self, transactions: List[Transaction]) -> Block:
        seed = hashlib.sha256(f"{random.random()}".encode()).digest()

        committee = self.select_committee(seed, self.current_round)
        proposer, verify_key = self.select_proposer(committee, seed, self.current_round)
        proposed_block = self.create_block(proposer, transactions)

        if self.verify_block(committee, proposed_block):
            self.chain.append(proposed_block)
        else:
            raise ValueError("Invalid block")

        return proposed_block
