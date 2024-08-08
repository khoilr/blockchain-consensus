import asyncio
import random
import time

from tqdm import tqdm
from tabulate import tabulate
from plotting import plot
from Algorand import Account, Algorand
from PoS import ProofOfStake, Validator
from PoW import Miner, ProofOfWork
from transaction import generate_transactions
import numpy as np

ALGORAND_ENERGY_PER_TRANSACTION = (
    0.000000539  # kWh per transaction (source: Algorand Foundation)
)
POS_ENERGY_PER_VALIDATION = 0.000001  # kWh per validation (estimated)
POW_ENERGY_PER_HASH = 0.000000001  # kWh per hash (estimated for modern ASIC miners)
NETWORK_OVERHEAD_FACTOR = 1.1  # 10% additional energy for network overhead


async def run_pos(num_validators, num_blocks):
    # Create validators for PoS
    validators = [
        Validator(stake=random.randint(64000, 200000000)) for _ in range(num_validators)
    ]
    pos = ProofOfStake(validators, initial_supply=1_000_000, inflation_rate=0.02)

    total_stake = sum(validator.stake for validator in validators)

    # Lists to store time, tps, and energy consumption for each block
    times = []
    tps = []
    energy_consumptions = []

    # Progress bar
    pbar = tqdm(total=num_blocks)

    for block_index in range(num_blocks):
        # Generate transactions for the block
        txns = generate_transactions()

        # Measure time to propose block
        start = time.time()
        block = pos.mine_block(txns)
        end = time.time()
        time_consumption = end - start

        # Calculate TPS and energy consumption
        times.append(time_consumption)
        tps.append(len(txns) / time_consumption)

        # Energy consumption for PoS: each validator consumes energy to validate
        block_energy = (
            sum(
                validator.stake / total_stake * POS_ENERGY_PER_VALIDATION
                for validator in validators
            )
            * NETWORK_OVERHEAD_FACTOR
        )
        energy_consumptions.append(block_energy)

        # Update progress bar
        pbar.update(1)
        pbar.set_description(f"PoS {block}")
        pbar.set_postfix(
            {
                "Block Index": block_index,
                "Time": f"{time_consumption:.2f}s",
                "Energy": f"{block_energy:.6f}kWh",
            }
        )

    # Close progress bar
    pbar.close()

    # Return results
    return "pos", times, tps, energy_consumptions, pos, validators


async def run_algorand(num_miners, num_blocks):
    # Create accounts for miners
    accounts = [
        Account(stake=random.randint(64000, 200000000)) for _ in range(num_miners)
    ]
    algorand = Algorand(accounts, initial_supply=1_000_000, inflation_rate=0.02)

    # Lists to store time, tps, and energy consumption for each block
    times = []
    tps = []
    energy_consumptions = []

    # Progress bar
    pbar = tqdm(total=num_blocks)

    for block_index in range(num_blocks):
        # Generate transactions for the block
        txns = generate_transactions()

        # Mine block and measure time
        start = time.time()
        block = algorand.mine_block(txns)  # Mine the block
        end = time.time()
        time_consumption = end - start

        # Calculate TPS and energy consumption
        times.append(time_consumption)
        tps.append(len(txns) / time_consumption)

        # Energy consumption for Algorand: based on number of transactions
        block_energy = len(txns) * ALGORAND_ENERGY_PER_TRANSACTION
        energy_consumptions.append(block_energy)

        # Update progress bar
        pbar.update(1)
        pbar.set_description(f"Algorand {block}")
        pbar.set_postfix(
            {
                "Block_Index": block_index,
                "Time": f"{time_consumption:.2f}s",
                "Energy": f"{block_energy:.6f}kWh",
            }
        )

    # Close progress bar
    pbar.close()

    # Return results
    return "algorand", times, tps, energy_consumptions, algorand, accounts


async def run_pow(num_miners, num_blocks):
    # Create miners with random hash rates
    miners = [Miner(hash_rate=random.uniform(30e12, 1e18)) for _ in range(num_miners)]
    pow = ProofOfWork(
        miners,
        initial_difficulty=1,
        target_block_time=2,
    )

    # Lists to store time, tps, and energy consumption for each block
    times = []
    tps = []
    energy_consumptions = []

    # Create progress bar
    pbar = tqdm(total=num_blocks)

    for block_index in range(num_blocks):
        # Generate transactions for the block
        txns = generate_transactions()

        # Measure time
        start = time.time()
        block = await pow.mine_block(txns)
        end = time.time()
        time_consumption = end - start

        # Calculate TPS and energy consumption
        times.append(time_consumption)
        tps.append(len(txns) / time_consumption)

        # Energy consumption for PoW: based on total hash rate and time
        total_hash_rate = sum(miner.hash_rate for miner in miners)
        hashes_performed = total_hash_rate * time_consumption * pow.difficulty
        block_energy = hashes_performed * POW_ENERGY_PER_HASH * NETWORK_OVERHEAD_FACTOR
        energy_consumptions.append(block_energy)

        # Update progress bar
        pbar.update(1)
        pbar.set_description(f"PoW {block}")
        pbar.set_postfix(
            {
                "Block_Index": block_index,
                "Time": f"{time_consumption:.2f}s",
                "Energy": f"{block_energy:.6f}kWh",
            }
        )

    # Close the progress bar
    pbar.close()

    # Return results
    return "pow", times, energy_consumptions, tps, pow, miners


def gather_result(task_complete, num_entities: int, num_blocks: int):
    consensus_type, times, energy_consumptions, tps, chain, users = (
        task_complete.result()
    )

    total_time = sum(times)
    total_energy = sum(energy_consumptions)

    avg_time = total_time / num_blocks
    avg_energy = total_energy / num_blocks
    avg_tps = sum(len(block.txns) for block in chain.chain) / avg_time

    return {
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


async def compare_consensus_mechanisms(num_entities: int, num_blocks: int):
    # Run Algorand and PoW concurrently
    async with asyncio.TaskGroup() as tg:
        pow_task = tg.create_task(run_pow(num_entities, num_blocks))
        pos_task = tg.create_task(run_pos(num_entities, num_blocks))
        algorand_task = tg.create_task(run_algorand(num_entities, num_blocks))

    results_list = [
        gather_result(pow_task, num_entities, num_blocks),
        gather_result(pos_task, num_entities, num_blocks),
        gather_result(algorand_task, num_entities, num_blocks),
    ]

    print_results_lists = [
        {
            k: v
            for k, v in result.items()
            if k
            in [
                "consensus",
                "num_miners",
                "num_blocks",
                "total_time",
                "avg_time",
                "total_energy",
                "avg_energy",
                "avg_tps",
            ]
        }
        for result in results_list
    ]
    print(tabulate(print_results_lists, headers="keys"))

    return results_list


async def main():
    results = []

    configurations = [
        (num_entities, num_blocks)
        for num_entities in np.logspace(0, 1, num=3, dtype=int)
        for num_blocks in np.logspace(0, 1, num=3, dtype=int)
    ]

    for num_entities, num_blocks in configurations:
        print(f"Running comparison with {num_entities} miners and {num_blocks} blocks")
        result = await compare_consensus_mechanisms(
            num_entities=num_entities, num_blocks=num_blocks
        )
        results.extend(result)
        print()

    plot(results)


if __name__ == "__main__":
    asyncio.run(main())
