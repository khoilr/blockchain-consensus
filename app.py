import asyncio
import hashlib
import random
import time

from tqdm import tqdm

from Algorand import Account, Algorand
from plot import plot_comparisons
from PoS import ProofOfStake, Validator
from PoW import Miner, ProofOfWork
from transaction import Transaction
import numpy as np

ALGORAND_ENERGY_PER_TRANSACTION = 0.000003  # kWh per transaction
POW_ENERGY_PER_HASH = 0.0000001  # kWh per hash
POS_ENERGY_PER_VALIDATION = 0.00055  # kWh per validation


async def run_pos(num_validators, num_blocks, num_transactions):
    validators = [Validator(stake=random.randint(1_000, 100_000_000)) for _ in range(num_validators)]
    pos = ProofOfStake(validators)

    times = []
    tps = []
    energy_consumptions = []

    pbar = tqdm(total=num_blocks, desc="PoS Progress")
    for block_index in range(num_blocks):
        sender = random.choice(validators).address
        receiver = random.choice(validators).address

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
        block = pos.propose_block(transactions)
        end = time.time()
        time_consumption = end - start
        times.append(time_consumption)
        tps.append(len(transactions) / time_consumption)

        # Energy consumption for PoS: each validator consumes energy to validate
        block_energy = len(pos.validators) * POS_ENERGY_PER_VALIDATION
        energy_consumptions.append(block_energy)

        pbar.update(1)
        pbar.set_postfix(
            {
                "Block Index": block_index,
                "Txns": len(transactions),
                "Time": f"{time_consumption:.2f}s",
                "Energy": f"{block_energy:.6f} kWh",
            }
        )

    pbar.close()

    return "pos", times, tps, energy_consumptions, pos, validators


async def run_algorand(num_miners, num_blocks, num_transactions):
    accounts = [Account(stake=random.randint(1_000, 100_000_000)) for _ in range(num_miners)]
    algorand = Algorand(accounts)

    times = []
    tps = []
    energy_consumptions = []

    pbar = tqdm(total=num_blocks, desc="Algorand Progress")

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

        # Energy consumption for Algorand: based on number of transactions
        block_energy = len(transactions) * ALGORAND_ENERGY_PER_TRANSACTION
        energy_consumptions.append(block_energy)

        pbar.update(1)
        pbar.set_postfix(
            {
                "Block Index": block_index,
                # "Block": block,
                "Txns": len(transactions),
                "Time": f"{time_consumption:.2f}s",
                "Energy": f"{block_energy:.6f} kWh",
            }
        )

    pbar.close()

    return "algorand", times, tps, energy_consumptions, algorand, accounts


async def run_pow(num_miners, num_blocks, num_transactions):
    miners = [Miner(hash_rate=random.randint(1_000, 1_000_000)) for _ in range(num_miners)]
    pow = ProofOfWork(miners, difficulty=3)

    times = []
    tps = []
    energy_consumptions = []

    pbar = tqdm(total=num_blocks, desc="PoW Progress")
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

        # Energy consumption for PoW: based on total hash rate and time
        total_hash_rate = sum(miner.hash_rate for miner in miners)
        hashes_performed = total_hash_rate * time_consumption
        block_energy = hashes_performed * POW_ENERGY_PER_HASH
        energy_consumptions.append(block_energy)

        pbar.update(1)
        pbar.set_postfix(
            {
                "Block Index": block_index,
                # "Block": block,
                "Txns": len(transactions),
                "Time": f"{time_consumption:.2f}s",
                "Energy": f"{block_energy:.6f} kWh",
            }
        )

    pbar.close()

    return "pow", times, energy_consumptions, tps, pow, miners


async def compare_consensus_mechanisms(num_entities: int, num_blocks: int, num_transactions=50):
    # Run Algorand and PoW concurrently
    algorand_task = asyncio.create_task(run_algorand(num_entities, num_blocks, num_transactions))
    pow_task = asyncio.create_task(run_pow(num_entities, num_blocks, num_transactions))
    pos_task = asyncio.create_task(run_pos(num_entities, num_blocks, num_transactions))

    # Wait for both tasks to complete
    results = await asyncio.gather(algorand_task, pow_task, pos_task)

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
                "num_miners": num_entities,
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

    configurations = [
        (num_entities, num_blocks)
        for num_entities in np.logspace(2, 4, num=10, dtype=int)
        for num_blocks in np.logspace(2, 4, num=10, dtype=int)
    ]

    for num_entities, num_blocks in configurations:
        print(f"Running comparison with {num_entities} miners and {num_blocks} blocks")
        result = await compare_consensus_mechanisms(num_entities=num_entities, num_blocks=num_blocks)
        results.append(result)
        print()

    plot_comparisons(results)


if __name__ == "__main__":
    asyncio.run(main())
