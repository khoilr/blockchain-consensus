import asyncio
import hashlib
import os
import random
import time

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

from Algorand import Account, Algorand
from PoW import Miner, ProofOfWork
from transaction import Transaction

ALGORAND_ENERGY_PER_TRANSACTION = 0.1
POW_ENERGY_PER_HASH = 0.1

sns.set_theme(style="ticks")


def plot_comparisons(results):
    # Create 'images' folder if it doesn't exist
    if not os.path.exists("images"):
        os.makedirs("images")

    # Flatten the results list and create a DataFrame
    df = pd.DataFrame([item for sublist in results for item in sublist])

    # Set up the plot style
    sns.set_style("whitegrid")
    sns.set_palette("deep")
    plt.rcParams["font.size"] = 12
    plt.rcParams["axes.labelsize"] = 14
    plt.rcParams["axes.titlesize"] = 16
    plt.rcParams["xtick.labelsize"] = 12
    plt.rcParams["ytick.labelsize"] = 12

    # 1. Performance metrics across different scales
    metrics = ["avg_time", "avg_energy", "avg_tps"]
    fig, axes = plt.subplots(3, 1, figsize=(15, 20))
    fig.suptitle("Performance Metrics Across Different Scales", fontsize=20)

    for i, metric in enumerate(metrics):
        sns.lineplot(data=df, x="num_miners", y=metric, hue="consensus", style="num_blocks", markers=True, ax=axes[i])
        axes[i].set_title(f'{metric.replace("_", " ").title()} vs Number of Miners')
        axes[i].set_xlabel("Number of Miners")
        axes[i].set_ylabel(metric.replace("_", " ").title())
        axes[i].set_xscale("log")
        axes[i].set_yscale("log")  # Use log scale for y-axis
        axes[i].legend(title="Consensus (Blocks)", bbox_to_anchor=(1.05, 1), loc="upper left")

    plt.tight_layout()
    plt.savefig("images/performance_metrics.png", dpi=300, bbox_inches="tight")
    plt.close()

    # 2. Scalability comparison
    fig, axes = plt.subplots(2, 2, figsize=(20, 20))
    fig.suptitle("Scalability Comparison", fontsize=20)

    for ax in axes.flatten():
        ax.set_xscale("log")
        ax.set_yscale("log")

    sns.scatterplot(
        data=df, x="num_miners", y="total_time", hue="consensus", size="num_blocks", sizes=(20, 500), ax=axes[0, 0]
    )
    axes[0, 0].set_title("Total Time vs Number of Miners")
    axes[0, 0].set_xlabel("Number of Miners")
    axes[0, 0].set_ylabel("Total Time (s)")

    sns.scatterplot(
        data=df, x="num_miners", y="total_energy", hue="consensus", size="num_blocks", sizes=(20, 500), ax=axes[0, 1]
    )
    axes[0, 1].set_title("Total Energy vs Number of Miners")
    axes[0, 1].set_xlabel("Number of Miners")
    axes[0, 1].set_ylabel("Total Energy (kWh)")

    sns.scatterplot(
        data=df, x="num_blocks", y="total_time", hue="consensus", size="num_miners", sizes=(20, 500), ax=axes[1, 0]
    )
    axes[1, 0].set_title("Total Time vs Number of Blocks")
    axes[1, 0].set_xlabel("Number of Blocks")
    axes[1, 0].set_ylabel("Total Time (s)")

    sns.scatterplot(
        data=df, x="num_blocks", y="total_energy", hue="consensus", size="num_miners", sizes=(20, 500), ax=axes[1, 1]
    )
    axes[1, 1].set_title("Total Energy vs Number of Blocks")
    axes[1, 1].set_xlabel("Number of Blocks")
    axes[1, 1].set_ylabel("Total Energy (kWh)")

    plt.tight_layout()
    plt.savefig("images/scalability_comparison.png", dpi=300, bbox_inches="tight")
    plt.close()

    # 3. Efficiency comparison
    plt.figure(figsize=(15, 10))
    sns.scatterplot(
        data=df, x="avg_time", y="avg_energy", hue="consensus", size="num_miners", style="num_blocks", sizes=(20, 500)
    )
    plt.title("Efficiency Comparison: Average Time vs Average Energy")
    plt.xlabel("Average Time per Block (s)")
    plt.ylabel("Average Energy per Block (kWh)")
    plt.xscale("log")
    plt.yscale("log")
    plt.legend(title="Consensus (Miners, Blocks)", bbox_to_anchor=(1.05, 1), loc="upper left")
    plt.tight_layout()
    plt.savefig("images/efficiency_comparison.png", dpi=300, bbox_inches="tight")
    plt.close()

    # 4. TPS comparison
    plt.figure(figsize=(15, 10))
    sns.boxenplot(data=df, x="consensus", y="avg_tps", hue="num_blocks")
    plt.title("TPS Comparison Across Consensus Mechanisms and Block Numbers")
    plt.xlabel("Consensus Mechanism")
    plt.ylabel("Average TPS")
    plt.yscale("log")  # Use log scale for y-axis
    plt.legend(title="Number of Blocks", bbox_to_anchor=(1.05, 1), loc="upper left")
    plt.tight_layout()
    plt.savefig("images/tps_comparison.png", dpi=300, bbox_inches="tight")
    plt.close()

    # 5. Heatmap of correlations
    plt.figure(figsize=(12, 10))
    corr = df[["num_miners", "num_blocks", "avg_time", "avg_energy", "avg_tps"]].corr()
    sns.heatmap(corr, annot=True, cmap="coolwarm", vmin=-1, vmax=1, center=0)
    plt.title("Correlation Heatmap of Metrics")
    plt.tight_layout()
    plt.savefig("images/correlation_heatmap.png", dpi=300)
    plt.close()

    # 6. Distribution of metrics
    fig, axes = plt.subplots(2, 2, figsize=(20, 20))
    fig.suptitle("Distribution of Metrics", fontsize=20)

    sns.histplot(data=df, x="avg_time", hue="consensus", multiple="stack", kde=True, ax=axes[0, 0])
    axes[0, 0].set_title("Distribution of Average Time")
    axes[0, 0].set_xlabel("Average Time (s)")
    axes[0, 0].set_xscale("log")

    sns.histplot(data=df, x="avg_energy", hue="consensus", multiple="stack", kde=True, ax=axes[0, 1])
    axes[0, 1].set_title("Distribution of Average Energy")
    axes[0, 1].set_xlabel("Average Energy (kWh)")
    axes[0, 1].set_xscale("log")

    sns.histplot(data=df, x="avg_tps", hue="consensus", multiple="stack", kde=True, ax=axes[1, 0])
    axes[1, 0].set_title("Distribution of Average TPS")
    axes[1, 0].set_xlabel("Average TPS")
    axes[1, 0].set_xscale("log")

    sns.scatterplot(
        data=df, x="num_miners", y="num_blocks", hue="consensus", size="avg_tps", sizes=(20, 500), ax=axes[1, 1]
    )
    axes[1, 1].set_title("Number of Miners vs Number of Blocks (size: Avg TPS)")
    axes[1, 1].set_xlabel("Number of Miners")
    axes[1, 1].set_ylabel("Number of Blocks")
    axes[1, 1].set_xscale("log")
    axes[1, 1].set_yscale("log")

    plt.tight_layout()
    plt.savefig("images/metric_distributions.png", dpi=300, bbox_inches="tight")
    plt.close()

    print("All plots have been saved in the 'images' folder.")


async def run_algorand(num_miners, num_blocks, num_transactions):
    accounts = [Account(stake=random.randint(1, 100_000_000)) for _ in range(num_miners)]
    algorand = Algorand(accounts)

    times = []
    tps = []
    energy_consumptions = []

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

        block_energy = len(transactions) * ALGORAND_ENERGY_PER_TRANSACTION
        energy_consumptions.append(block_energy)

        print(f"Algorand Block Index: {block_index}")
        print(f"Block Info: {block}")
        print(f"Time consumption: {time_consumption}")
        print("=====================")

    return "algorand", times, tps, energy_consumptions, algorand, accounts


async def run_pow(num_miners, num_blocks, num_transactions):
    miners = [Miner(hash_rate=random.randint(1, 100_000_000)) for _ in range(num_miners)]
    pow = ProofOfWork(miners, difficulty=2)

    times = []
    tps = []
    energy_consumptions = []

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

        # Calculate energy consumption for this block
        total_hash_rate = sum(miner.hash_rate for miner in miners)
        hashes_performed = total_hash_rate * time_consumption
        block_energy = hashes_performed * POW_ENERGY_PER_HASH
        energy_consumptions.append(block_energy)

        print(f"PoW Block Index: {block_index}")
        print(f"Block Info: {block}")
        print(f"Time consumption: {time_consumption}")
        print("=====================")

    return "pow", times, energy_consumptions, tps, pow, miners


async def compare_consensus_mechanisms(num_miners: int, num_blocks: int, num_transactions=50):
    # Run Algorand and PoW concurrently
    algorand_task = asyncio.create_task(run_algorand(num_miners, num_blocks, num_transactions))
    pow_task = asyncio.create_task(run_pow(num_miners, num_blocks, num_transactions))

    # Wait for both tasks to complete
    results = await asyncio.gather(algorand_task, pow_task)

    # Process results
    results_list = []
    for (
        consensus_type,
        times,
        energy_consumptions,
        tps,
        chain,
        users,
    ) in results:
        total_time = sum(times)
        total_energy = sum(energy_consumptions)

        avg_time = total_time / num_blocks
        avg_energy = total_energy / num_blocks
        avg_tps = num_transactions / avg_time

        results_list.append(
            {
                "consensus": consensus_type,
                "num_miners": num_miners,
                "num_blocks": num_blocks,
                "times": times,
                "total_time": total_time,
                "avg_time": avg_time,
                "energy": energy_consumptions,
                "total_energy": total_energy,
                "avg_energy": avg_energy,
                "tps": tps,
                "avg_tps": avg_tps,
                "chain": chain,
                "users": users,
            }
        )

    return results_list


async def main():
    results = []
    for num_miners in [100, 1_000, 10_000]:
        for num_blocks in [100, 1_000, 10_000]:
            print(f"Running comparison with {num_miners} miners and {num_blocks} blocks")
            result = await compare_consensus_mechanisms(num_miners=num_miners, num_blocks=num_blocks)
            results.append(result)

    plot_comparisons(results)


if __name__ == "__main__":
    asyncio.run(main())
