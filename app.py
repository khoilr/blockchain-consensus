import asyncio
import hashlib
import random
import time
from pprint import pprint

import matplotlib.pyplot as plt
import seaborn as sns

from Algorand import Account, Algorand
from PoW import Miner, ProofOfWork
from transaction import Transaction

sns.set_theme(style="ticks")


def plot(results):
    # Create a 2x2 subplot structure
    fig, axes = plt.subplots(2, 2, figsize=(12, 8))

    # First subplot: Block Time Comparison
    sns.boxplot(
        data=[results["Algorand"]["tps"], results["PoW"]["tps"]],
        ax=axes[0, 0],
    )
    axes[0, 0].set_title("Block Time Comparison")
    axes[0, 0].set_xticklabels(["Algorand", "PoW"])
    axes[0, 0].set_ylabel("Transactions per Second")

    # Second subplot: Energy Usage
    sns.barplot(
        x=["Algorand", "PoW"],
        y=[results["Algorand"]["energy_usage"], results["PoW"]["energy_usage"]],
        ax=axes[0, 1],
    )
    axes[0, 1].set_title("Energy Usage")
    axes[0, 1].set_ylabel("Energy Units")

    # Third subplot: Decentralization
    sns.barplot(
        x=["Algorand", "PoW"],
        y=[results["Algorand"]["decentralization"], results["PoW"]["decentralization"]],
        ax=axes[1, 0],
    )
    axes[1, 0].set_title("Decentralization")
    axes[1, 0].set_ylabel("Number of Participants")

    # Fourth subplot: TPS Over Time
    sns.lineplot(data=results["Algorand"]["tps"], label="Algorand", ax=axes[1, 1])
    sns.lineplot(data=results["PoW"]["tps"], label="PoW", ax=axes[1, 1])
    axes[1, 1].set_title("TPS Over Time")
    axes[1, 1].set_xlabel("Block Number")
    axes[1, 1].set_ylabel("Transactions per Second")
    axes[1, 1].legend()

    # Adjust the layout
    plt.tight_layout()
    plt.show()


async def run_algorand(num_miners, num_blocks, num_transactions):
    accounts = [Account(stake=random.randint(1, 100_000_000)) for _ in range(num_miners)]
    algorand = Algorand(accounts)

    times = []
    tps = []

    for block_index in range(num_blocks):
        sender = hashlib.sha256(f"{random.choice(accounts).verify_key}".encode()).hexdigest()
        receiver = hashlib.sha256(f"{random.choice(accounts).verify_key}".encode()).hexdigest()

        amount = random.uniform(1, 1000)
        transactions = [
            Transaction(
                sender=sender,
                receiver=receiver,
                amount=amount,
            )
            for _ in range(random.randint(1, num_transactions))
        ]

        start = time.time()
        block = algorand.mine_block(transactions)
        end = time.time()
        time_consumption = end - start
        times.append(time_consumption)
        tps.append(num_transactions / time_consumption)

        print(f"Algorand Block Index: {block_index}")
        print(f"Block Info: {block}")
        print(f"Time consumption: {time_consumption}")
        print("=====================")

    return "algorand", times, tps, algorand, accounts


async def run_pow(num_miners, num_blocks, num_transactions):
    miners = [Miner(hash_rate=random.randint(1, 100_000_000)) for _ in range(num_miners)]
    pow = ProofOfWork(miners, difficulty=2)

    times = []
    tps = []

    for block_index in range(num_blocks):
        sender = hashlib.sha256(f"{random.choice(miners).address}".encode()).hexdigest()
        receiver = hashlib.sha256(f"{random.choice(miners).address}".encode()).hexdigest()

        amount = random.uniform(1, 1000)
        transactions = [
            Transaction(
                sender=sender,
                receiver=receiver,
                amount=amount,
            )
            for _ in range(random.randint(1, num_transactions))
        ]

        start = time.time()
        block = pow.mine_block(transactions)
        end = time.time()
        time_consumption = end - start
        times.append(time_consumption)
        tps.append(num_transactions / time_consumption)

        print(f"PoW Block Index: {block_index}")
        print(f"Block Info: {block}")
        print(f"Time consumption: {time_consumption}")
        print("=====================")

    return "pow", times, tps, pow, miners


async def compare_consensus_mechanisms(num_miners: int, num_blocks: int, num_transactions=50):
    # Run Algorand and PoW concurrently
    algorand_task = asyncio.create_task(run_algorand(num_miners, num_blocks, num_transactions))
    pow_task = asyncio.create_task(run_pow(num_miners, num_blocks, num_transactions))

    # Wait for both tasks to complete
    results = await asyncio.gather(algorand_task, pow_task)

    # Process results
    results_dict = {}
    for (
        consensus_type,
        times,
        tps,
        chain,
        users,
    ) in results:
        avg_time = sum(times) / len(times)
        avg_tps = sum(tps) / len(tps)

        if consensus_type == "algorand":
            energy_usage = avg_time * num_blocks
            decentralization = num_miners
        elif consensus_type == "pow":
            energy_usage = avg_time * num_blocks * num_miners
            decentralization = num_miners

        results_dict[consensus_type] = {
            "times": times,
            "tps": tps,
            "avg_time": avg_time,
            "energy_usage": energy_usage,
            "decentralization": decentralization,
            "avg_tps": avg_tps,
        }

    return results_dict


async def main():
    for num_miners in [100]:
        for num_blocks in [100]:
            print(f"Running comparison with {num_miners} miners and {num_blocks} blocks")
            results = await compare_consensus_mechanisms(num_miners=num_miners, num_blocks=num_blocks)
            pprint(results)


if __name__ == "__main__":
    asyncio.run(main())
