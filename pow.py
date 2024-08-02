import hashlib
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from threading import Event
from typing import List

from transaction import Transaction


class Block:
    def __init__(
        self,
        nonce: int,
        proposer: str,
        transactions: List[Transaction],
        previous_hash: str,
    ):
        self.proposer = proposer
        self.transactions = transactions
        self.previous_hash = previous_hash
        self.timestamp = int(time.time())
        self.nonce = nonce
        self.hash = self.calculate_hash()

    def calculate_hash(self) -> str:
        block_data = (
            str(self.proposer)
            + "".join(tx.to_bytes().decode() for tx in self.transactions)
            + str(self.previous_hash)
            + str(self.nonce)
            + str(self.timestamp)
        )
        return hashlib.sha256(block_data.encode()).hexdigest()

    def is_valid(self, previous_hash: str, difficulty: int) -> bool:
        return (
            self.previous_hash == previous_hash
            and self.hash == self.calculate_hash()
            and self.hash.startswith("0" * difficulty)
        )

    def __repr__(self) -> str:
        return f"""Block (
                    timestamp: {self.timestamp},
                    nonce: {self.nonce},
                    proposer: {self.proposer},
                    previous_hash: {self.previous_hash},
                    hash: {self.hash}
                )"""


class Blockchain:
    def __init__(self, difficulty: int = 4):
        self.chain: List[Block] = []
        self.difficulty = difficulty

        self.create_genesis_block()

    def create_genesis_block(self) -> None:
        genesis_block = Block(0, "0", [], "0")
        self.chain.append(genesis_block)

    def add_block(self, block: Block) -> None:
        if block.is_valid(previous_hash=self.get_last_block().hash, difficulty=self.difficulty):
            self.chain.append(block)

    def get_last_block(self) -> Block:
        return self.chain[-1]

    def get_new_block_index(self) -> int:
        return len(self.chain)

    def is_valid(self) -> bool:
        return all(
            self.chain[i].is_valid(difficulty=self.difficulty, previous_hash=self.chain[i - 1].hash)
            for i in range(1, len(self.chain))
        )


class Miner:
    def __init__(self, hash_rate):
        self.address = hashlib.sha256(bytes(str(time.time()), "utf-8")).hexdigest()
        self.hash_rate = hash_rate

    def mine(
        self,
        stop_event: Event,
        transactions: list,
        previous_hash: str,
        target: str,
        start_nonce=0,
    ):
        nonce = start_nonce
        while not stop_event.is_set():
            new_block = Block(
                nonce=nonce,
                proposer=self.address,
                transactions=transactions,
                previous_hash=previous_hash,
            )
            if new_block.hash.startswith(target * "0"):
                stop_event.set()
                return new_block
            nonce += 1

            # Simulate hash rate
            time.sleep(1 / self.hash_rate)

    def validate_block(self, block: Block, previous_hash: str, difficulty: int):
        return block.is_valid(previous_hash, difficulty=difficulty)


class ProofOfWork(Blockchain):
    def __init__(self, miners: List[Miner], difficulty: int = 4):
        self.miners = miners
        super().__init__(difficulty=difficulty)

    def mine_block(self, transactions: List[Transaction]):
        previous_hash = self.get_last_block().hash
        start_nonce = 0
        stop_event = Event()

        with ThreadPoolExecutor(max_workers=len(self.miners)) as executor:
            futures = [
                executor.submit(miner.mine, stop_event, transactions, previous_hash, self.difficulty, start_nonce)
                for miner in self.miners
            ]

            for future in as_completed(futures):
                block = future.result()
                if block:
                    valid_count = sum(
                        1
                        for miner in self.miners
                        if miner.validate_block(block=block, previous_hash=previous_hash, difficulty=self.difficulty)
                    )
                    if valid_count > len(self.miners) / 2:
                        self.add_block(block)
                        return block
                    else:
                        return None

        return None
