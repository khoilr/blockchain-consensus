import concurrent.futures
import hashlib
import random
import statistics
import time
from collections import defaultdict
from typing import List
import itertools
import numpy as np


class Transaction:
    def __init__(self, sender, recipient, amount):
        self.sender = sender
        self.recipient = recipient
        self.amount = amount
        self.timestamp = time.time()


class Block:
    def __init__(self, transactions: List[Transaction], previous_hash: str):
        self.timestamp = time.time()
        self.transactions = transactions
        self.previous_hash = previous_hash
        self.nonce = 0
        self.hash = self.calculate_hash()

    def calculate_hash(self):
        block_string = f"{self.timestamp}{self.transactions}{self.previous_hash}{self.nonce}"
        return hashlib.sha256(block_string.encode()).hexdigest()

    def mine(self, difficulty: int):
        while self.hash[:difficulty] != "0" * difficulty:
            self.nonce += 1
            self.hash = self.calculate_hash()


class Blockchain:
    def __init__(self, difficulty: int):
        self.chain = [self.create_genesis_block()]
        self.difficulty = difficulty
        self.mempool: List[Transaction] = []
        self.block_time: int = []
        self.block_sizes: int = []

    def create_genesis_block(self):
        return Block([], "0")

    def get_latest_block(self):
        return self.chain[-1]

    def add_transaction(self, transaction: Transaction):
        self.mempool.append(transaction)

    def mine_pending_transactions(self, miner_reward_address: str):
        start_time = time.time()

        block = Block(self.mempool[:10], self.get_latest_block().hash)
        block.mine(self.difficulty)

        self.chain.append(block)
        self.block_time.append(time.time() - start_time)
        self.block_sizes.append(len(block.transactions))

        self.mempool = self.mempool[10:]
        self.add_transaction(Transaction("Network", miner_reward_address, 1))

        return block

    def validate_chain(self):
        for i in range(1, len(self.chain)):
            current_block = self.chain[i]
            previous_block = self.chain[i - 1]

            if current_block.hash != current_block.calculate_hash():
                return False

            if current_block.previous_hash != previous_block.hash:
                return False

        return True


class Node:
    def __init__(self, blockchain: Blockchain, address: str, hash_power: float):
        self.blockchain = blockchain
        self.address = address
        self.peers = set()
        self.hash_power = hash_power

    def add_peer(self, peer):
        self.peers.add(peer)

    def broadcast_transaction(self, transaction):
        self.blockchain.add_transaction(transaction)
        for peer in self.peers:
            peer.receive_transaction(transaction)

    def receive_transaction(self, transaction):
        self.blockchain.add_transaction(transaction)
        self.blockchain.validate_chain()

    def mine_block(self):
        block = Block(self.blockchain.mempool[:10], self.blockchain.get_latest_block().hash)
        target = "0" * self.blockchain.difficulty

        nonce = 0
        while True:
            block.nonce = nonce
            block.hash = block.calculate_hash()
            if block.hash[: self.blockchain.difficulty] == target:
                return blockre
            nonce += 1

            # Simulate the node's hash power
            if nonce % self.hash_power == 0:
                time.sleep(1)  # Sleep for 1 second after processing 'hash_power' nonces


class Network:
    def __init__(self, num_nodes: int, difficulty: int):
        self.blockchain = Blockchain(difficulty)
        self.nodes = [Node(self.blockchain, f"Node_{i}", random.randint(100, 1000)) for i in range(num_nodes)]

        # Connect nodes in a simple topology
        for node1, node2 in itertools.combinations(self.nodes, 2):
            node1.add_peer(node2)
            node2.add_peer(node1)

    def simulate(self, num_transactions: int, num_blocks: int):
        start_time = time.time()

        for _ in range(num_transactions):
            sender = random.choice(self.nodes).address
            recipient = random.choice(self.nodes).address
            amount = random.uniform(0, 100)
            tx = Transaction(sender, recipient, amount)
            random.choice(self.nodes).broadcast_transaction(tx)

        for _ in range(num_blocks):
            self.mine_next_block()

        end_time = time.time()

        return end_time - start_time

    def mine_next_block(self):
        with concurrent.futures.ThreadPoolExecutor(max_workers=len(self.nodes)) as executor:
            future_to_node = {executor.submit(node.mine_block): node for node in self.nodes}

            for future in concurrent.futures.as_completed(future_to_node):
                node = future_to_node[future]
                try:
                    mined_block = future.result()
                    self.blockchain.chain.append(mined_block)
                    self.blockchain.block_time.append(
                        mined_block.timestamp - self.blockchain.get_latest_block().timestamp
                    )
                    self.blockchain.block_sizes.append(len(mined_block.transactions))
                    self.blockchain.mempool = self.blockchain.mempool[10:]
                    self.blockchain.add_transaction(Transaction("Network", node.address, 1))
                    break  # Stop once a block is mined
                except Exception as exc:
                    print(f"{node.address} generated an exception: {exc}")


# Run the simulation and tests
network = Network(num_nodes=10, difficulty=4)
simulation_time = network.simulate(num_transactions=1000, num_blocks=50)
