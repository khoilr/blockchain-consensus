import hashlib
import random
import time
from typing import List, Dict

class Transaction:
    def __init__(self, sender: str, recipient: str, amount: float):
        self.sender = sender
        self.recipient = recipient
        self.amount = amount
        self.timestamp = time.time()

    def to_string(self) -> str:
        return f"{self.sender}->{self.recipient}:{self.amount}:{self.timestamp}"

class Block:
    def __init__(self, transactions: List[Transaction], previous_hash: str, miner: str):
        self.transactions = transactions
        self.previous_hash = previous_hash
        self.miner = miner
        self.timestamp = time.time()
        self.nonce = 0
        self.hash = self.calculate_hash()

    def calculate_hash(self) -> str:
        transaction_string = "".join([tx.to_string() for tx in self.transactions])
        block_string = f"{transaction_string}{self.previous_hash}{self.miner}{self.timestamp}{self.nonce}"
        return hashlib.sha256(block_string.encode()).hexdigest()

    def mine_block(self, difficulty: int):
        target = "0" * difficulty
        while self.hash[:difficulty] != target:
            self.nonce += 1
            self.hash = self.calculate_hash()

class Blockchain:
    def __init__(self, difficulty: int):
        self.difficulty = difficulty
        self.pending_transactions: List[Transaction] = []
        self.chain: List[Block] = [self.create_genesis_block()]

    def create_genesis_block(self) -> Block:
        return Block([Transaction("Genesis", "Genesis", 0)], "0" * 64, "Genesis")

    def get_latest_block(self) -> Block:
        return self.chain[-1]

    def add_transaction(self, transaction: Transaction):
        self.pending_transactions.append(transaction)

    def is_chain_valid(self) -> bool:
        for i in range(1, len(self.chain)):
            current_block = self.chain[i]
            previous_block = self.chain[i-1]

            if current_block.hash != current_block.calculate_hash():
                return False

            if current_block.previous_hash != previous_block.hash:
                return False

        return True

class Miner:
    def __init__(self, name: str, hashrate: float):
        self.name = name
        self.hashrate = hashrate
        self.blockchain = Blockchain(4)  # Each miner has their own view of the blockchain

    def mine(self):
        if not self.blockchain.pending_transactions:
            return None

        new_block = Block(
            self.blockchain.pending_transactions,
            self.blockchain.get_latest_block().hash,
            self.name
        )
        new_block.mine_block(self.blockchain.difficulty)
        return new_block

    def receive_block(self, block: Block) -> bool:
        # Verify the block
        if block.previous_hash != self.blockchain.get_latest_block().hash:
            return False
        if block.hash[:self.blockchain.difficulty] != "0" * self.blockchain.difficulty:
            return False

        # Add the block to the chain
        self.blockchain.chain.append(block)
        self.blockchain.pending_transactions = []
        return True

class Network:
    def __init__(self, miners: List[Miner], latency_range: tuple = (0.1, 0.5)):
        self.miners = miners
        self.latency_range = latency_range

    def broadcast_block(self, block: Block, originator: Miner):
        for miner in self.miners:
            if miner != originator:
                # Simulate network latency
                latency = random.uniform(*self.latency_range)
                time.sleep(latency)
                miner.receive_block(block)

    def add_transaction(self, transaction: Transaction):
        for miner in self.miners:
            miner.blockchain.add_transaction(transaction)

    def get_longest_chain(self) -> List[Block]:
        return max(self.miners, key=lambda m: len(m.blockchain.chain)).blockchain.chain

    def synchronize_chains(self):
        longest_chain = self.get_longest_chain()
        for miner in self.miners:
            if len(miner.blockchain.chain) < len(longest_chain):
                miner.blockchain.chain = longest_chain.copy()

def simulate_pow(network: Network, num_blocks: int):
    for _ in range(num_blocks):
        # Add some transactions to the network
        network.add_transaction(Transaction("Alice", "Bob", random.uniform(0.1, 10)))
        network.add_transaction(Transaction("Bob", "Charlie", random.uniform(0.1, 10)))

        mined_block = None
        miner_who_mined = None

        # Miners attempt to mine a block
        for miner in network.miners:
            if random.random() < miner.hashrate:
                mined_block = miner.mine()
                if mined_block:
                    miner_who_mined = miner
                    break

        if mined_block:
            # Broadcast the new block to the network
            network.broadcast_block(mined_block, miner_who_mined)

            # Synchronize chains across all miners
            network.synchronize_chains()

            # Print the result of this round
            print(f"Block mined by: {miner_who_mined.name}")
            print(f"Block hash: {mined_block.hash}")
            print(f"Chain length: {len(network.get_longest_chain())}")
            print("---")

    # Verify final chain validity
    print("Final chain valid:", network.miners[0].blockchain.is_chain_valid())
    print("All miners agree on chain length:", len(set(len(m.blockchain.chain) for m in network.miners)) == 1)

# Simulation parameters
miners = [
    Miner("Miner A", 0.3),
    Miner("Miner B", 0.3),
    Miner("Miner C", 0.2),
    Miner("Miner D", 0.1),
]
network = Network(miners)
num_blocks_to_mine = 10

# Run simulation
simulate_pow(network, num_blocks_to_mine)