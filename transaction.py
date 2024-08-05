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
