import hashlib
import random


class Transaction:
    def __init__(self, sender: str, receiver: str, amount: float, fee: float):
        self.sender = sender
        self.receiver = receiver
        self.amount = amount
        self.fee = fee

    def to_bytes(self):
        return f"{self.sender}->{self.receiver}:{self.amount}".encode()

    def __repr__(self):
        return f"{self.sender} -> {self.receiver}: {self.amount}"


def generate_transactions():
    return [
        Transaction(
            sender=hashlib.sha256(f"{random.getrandbits(256)}".encode()).hexdigest(),
            receiver=hashlib.sha256(f"{random.getrandbits(256)}".encode()).hexdigest(),
            amount=random.uniform(1, 1000),
            fee=random.uniform(0.01, 0.1),
        )
        for _ in range(random.randint(1, 1000))
    ]
