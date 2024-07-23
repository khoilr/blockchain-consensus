# %%
import hashlib
import random
import time
from collections import defaultdict
from typing import List

import matplotlib.pyplot as plt
import numpy as np
from scipy.stats import entropy


class Transaction:
    def __init__(self, sender: str, recipient: str, amount: float):
        self.sender = sender
        self.recipient = recipient
        self.amount = amount
        self.timestamp = time.time()


class Block:
    def __init__(self, index: int, transactions: List[Transaction], timestamp: int, previous_hash: str):
        self.index = index
        self.transactions = transactions
        self.timestamp = timestamp
        self.previous_hash = previous_hash
        self.hash = self.calculate_hash()
        self.size = len(str(transactions)) + 256  # Simulating block size (including header)

    def calculate_hash(self):
        block_string = f"{self.index}{self.transactions}{self.timestamp}{self.previous_hash}"
        return hashlib.sha256(block_string.encode()).hexdigest()


class Blockchain:
    def __init__(self):
        self.chain: List[Block] = [self.create_genesis_block()]
        self.difficulty = 4
        self.pending_transactions = []
        self.nodes = []

    def create_genesis_block(self):
        return Block(0, [], int(time.time()), "0")

    def get_latest_block(self):
        return self.chain[-1]

    def add_block(self, new_block):
        new_block.previous_hash = self.get_latest_block().hash
        new_block.hash = new_block.calculate_hash()
        self.chain.append(new_block)

    def is_chain_valid(self):
        for i in range(1, len(self.chain)):
            current_block = self.chain[i]
            previous_block = self.chain[i - 1]
            if (
                current_block.hash != current_block.calculate_hash()
                or current_block.previous_hash != previous_block.hash
            ):
                return False
        return True


class Node:
    def __init__(self, node_id, blockchain, stake=0):
        self.node_id = node_id
        self.blockchain = blockchain
        self.stake = stake
        self.mempool = []
        self.blocks_mined = 0
        self.balance = 1000  # Initial balance
        self.connections = set()  # For network topology
        self.transactions_processed = 0

    def add_transaction_to_mempool(self, transaction):
        self.mempool.append(transaction)

    def mine_block(self):
        last_block = self.blockchain.get_latest_block()
        new_block = Block(len(self.blockchain.chain), self.mempool[:100], int(time.time()), last_block.hash)
        self.mempool = self.mempool[100:]
        self.blocks_mined += 1
        return new_block


def propagate_block(node, block, propagation_delay=0.1):
    time.sleep(propagation_delay)  # Simulating network delay
    for connected_node in node.connections:
        connected_node.blockchain.add_block(block)
        connected_node.transactions_processed += len(block.transactions)


def simulate_network(consensus_type, num_nodes, num_blocks, transaction_rate, difficulty):
    blockchain = Blockchain()
    nodes = [Node(i, blockchain, stake=random.randint(1, 100)) for i in range(num_nodes)]
    blockchain.nodes = nodes

    block_times = []
    mempool_sizes = []
    node_contributions = defaultdict(int)
    transaction_latencies = []
    network_load = []
    block_sizes = []
    fork_events = 0

    start_time = time.time()

    for _ in range(num_blocks):
        block_start_time = time.time()

        # Simulate transactions
        for _ in range(transaction_rate):
            sender = random.choice(nodes)
            recipient = random.choice(nodes)
            amount = random.randint(1, 10)
            transaction = Transaction(sender.node_id, recipient.node_id, amount)
            for node in nodes:
                node.add_transaction_to_mempool(transaction)

        # PoS: Select validator based on stake
        winner = random.choices(nodes, weights=[node.stake for node in nodes])[0]
        winning_block = winner.mine_block()
        blockchain.add_block(winning_block)
        node_contributions[winner.node_id] += 1
        winner.balance += 10  # Staking reward
        propagate_block(winner, winning_block)

        block_time = time.time() - block_start_time
        block_times.append(block_time)
        mempool_sizes.append(sum(len(node.mempool) for node in nodes) / num_nodes)
        block_sizes.append(winning_block.size)

        # Calculate transaction latency
        for tx in winning_block.transactions:
            transaction_latencies.append(time.time() - tx.timestamp)

        # Calculate network load
        network_load.append(len(winning_block.transactions) / block_time)

    end_time = time.time()
    total_time = end_time - start_time

    # Calculate metrics
    avg_block_time = sum(block_times) / len(block_times)
    avg_mempool_size = sum(mempool_sizes) / len(mempool_sizes)
    tps = sum(node.transactions_processed for node in nodes) / total_time
    avg_latency = sum(transaction_latencies) / len(transaction_latencies)
    avg_network_load = sum(network_load) / len(network_load)
    avg_block_size = sum(block_sizes) / len(block_sizes)
    gini_coefficient = calculate_gini_coefficient(list(node_contributions.values()))
    entropy_value = calculate_entropy(list(node_contributions.values()))

    print(f"\n{consensus_type} Simulation Results:")
    print(f"Total time: {total_time:.2f} seconds")
    print(f"Average block time: {avg_block_time:.2f} seconds")
    print(f"Average mempool size: {avg_mempool_size:.2f}")
    print(f"Transactions per second: {tps:.2f}")
    print(f"Average transaction latency: {avg_latency:.2f} seconds")
    print(f"Average network load: {avg_network_load:.2f} tx/s")
    print(f"Average block size: {avg_block_size:.2f} bytes")
    print(f"Gini coefficient (decentralization): {gini_coefficient:.4f}")
    print(f"Entropy (decentralization): {entropy_value:.4f}")
    print(f"Number of fork events: {fork_events}")
    print(f"Chain valid: {blockchain.is_chain_valid()}")

    return (
        block_times,
        mempool_sizes,
        node_contributions,
        tps,
        gini_coefficient,
        avg_latency,
        avg_network_load,
        entropy_value,
        fork_events,
        avg_block_size,
    )


def calculate_gini_coefficient(values):
    sorted_values = sorted(values)
    height, area = 0, 0
    for value in sorted_values:
        height += value
        area += height - value / 2.0
    fair_area = height * len(values) / 2
    return (fair_area - area) / fair_area


def calculate_entropy(values):
    probabilities = [v / sum(values) for v in values]
    return entropy(probabilities, base=2)


def plot_results(pos_results):
    fig, axs = plt.subplots(3, 3, figsize=(20, 20))

    # Plot block times
    axs[0, 0].plot(pos_results[0], label="PoS")
    axs[0, 0].set_title("Block Times")
    axs[0, 0].set_xlabel("Block Number")
    axs[0, 0].set_ylabel("Time (s)")
    axs[0, 0].legend()

    # Plot mempool sizes
    axs[0, 1].plot(pos_results[1], label="PoS")
    axs[0, 1].set_title("Mempool Sizes")
    axs[0, 1].set_xlabel("Block Number")
    axs[0, 1].set_ylabel("Number of Transactions")
    axs[0, 1].legend()

    # Plot node contributions
    axs[0, 2].bar(pos_results[2].keys(), pos_results[2].values(), alpha=0.5, label="PoS")
    axs[0, 2].set_title("Node Contributions")
    axs[0, 2].set_xlabel("Node ID")
    axs[0, 2].set_ylabel("Blocks Created")
    axs[0, 2].legend()

    # Plot trilemma metrics
    axs[1, 0].remove()
    axs[1, 0] = fig.add_subplot(332, projection="polar")
    pos_metrics = [pos_results[3] / 100, 1 - pos_results[4], 1 / pos_results[5]]
    angles = np.linspace(0, 2 * np.pi, 3, endpoint=False)
    angles = np.concatenate((angles, [angles[0]]))
    pos_metrics.append(pos_metrics[0])
    axs[1, 0].plot(angles, pos_metrics, "o-", linewidth=2, label="PoS")
    axs[1, 0].set_thetagrids(angles[:-1] * 180 / np.pi, ["Scalability", "Decentralization", "Security"])
    axs[1, 0].legend(loc="upper right", bbox_to_anchor=(1.3, 1.1))

    # Plot network load
    axs[1, 1].plot(pos_results[6], label="PoS")
    axs[1, 1].set_title("Network Load")
    axs[1, 1].set_xlabel("Block Number")
    axs[1, 1].set_ylabel("Transactions per Second")
    axs[1, 1].legend()

    # Plot entropy
    axs[1, 2].set_title("Entropy (Decentralization)")
    axs[1, 2].set_ylabel("Entropy")

    # Plot fork events
    axs[2, 0].set_title("Fork Events")
    axs[2, 0].set_ylabel("Number of Forks")

    # Plot block sizes
    axs[2, 1].plot(pos_results[9], label="PoS")
    axs[2, 1].set_title("Block Sizes")
    axs[2, 1].set_xlabel("Block Number")
    axs[2, 1].set_ylabel("Size (bytes)")
    axs[2, 1].legend()

    plt.tight_layout()
    plt.show()


# Run simulations
pos_results = simulate_network("PoS", num_nodes=10, num_blocks=100, transaction_rate=10, difficulty=4)

# Plot results
plot_results(pos_results)

# %%
