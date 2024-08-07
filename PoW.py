import hashlib
import random
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from threading import Event
from typing import List
import asyncio

from transaction import Transaction


class Block:
    def __init__(
        self,
        nonce: int,
        proposer: str,
        txns: List[Transaction],
        previous_hash: str,
    ):
        self.proposer = proposer
        self.txns = txns
        self.previous_hash = previous_hash
        self.timestamp = int(time.time())
        self.nonce = nonce
        self.hash = self.calculate_hash()
        self.total_fees = sum(tx.fee for tx in txns)

    def calculate_hash(self) -> str:
        block_data = (
            str(self.proposer)
            + "".join(tx.to_bytes().decode() for tx in self.txns)
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
        return f"Block (timestamp={self.timestamp}, hash={self.hash[:8]}, previous_hash={self.previous_hash[:8]}, num_txns={len(self.txns)})"


class Blockchain:
    def __init__(self, initial_difficulty: int = 4, target_block_time: int = 10):
        self.chain: List[Block] = []
        self.difficulty = initial_difficulty
        self.target_block_time = target_block_time
        self.create_genesis_block()

    def create_genesis_block(self) -> None:
        genesis_block = Block(0, "0", [], "0")
        self.chain.append(genesis_block)

    def add_block(self, block: Block) -> None:
        if block.is_valid(
            previous_hash=self.get_last_block().hash, difficulty=self.difficulty
        ):
            self.chain.append(block)
            self.adjust_difficulty()

    def get_last_block(self) -> Block:
        return self.chain[-1]

    def get_new_block_index(self) -> int:
        return len(self.chain)

    def is_valid(self) -> bool:
        return all(
            self.chain[i].is_valid(
                difficulty=self.difficulty, previous_hash=self.chain[i - 1].hash
            )
            for i in range(1, len(self.chain))
        )

    def adjust_difficulty(self):
        if len(self.chain) % 2 == 0:
            last_two_blocks = self.chain[-2:]
            average_time = last_two_blocks[1].timestamp - last_two_blocks[0].timestamp

            if average_time < self.target_block_time:
                self.difficulty += 1
            elif average_time > self.target_block_time and self.difficulty > 1:
                self.difficulty -= 1


class Miner:
    def __init__(self, hash_rate, is_malicious=False):
        self.address = hashlib.sha256(bytes(str(time.time()), "utf-8")).hexdigest()
        self.hash_rate = hash_rate
        self.total_rewards = 0
        self.is_malicious = is_malicious

    async def mine(
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
                txns=transactions,
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
    def __init__(
        self,
        miners: List[Miner],
        initial_difficulty: int = 4,
        target_block_time: int = 10,
        initial_reward: float = 50,
    ):
        self.miners = miners
        self.block_reward = initial_reward
        self.halving_interval = 210000
        super().__init__(
            initial_difficulty=initial_difficulty,
            target_block_time=target_block_time,
        )

    async def mine_block(self, transactions: List[Transaction]):
        previous_hash = self.get_last_block().hash
        start_nonce = 0

        stop_event = asyncio.Event()

        async def mine(miner):
            return await miner.mine(
                stop_event, transactions, previous_hash, self.difficulty, start_nonce
            )

        tasks = [asyncio.create_task(mine(miner)) for miner in self.miners]

        done, _ = await asyncio.wait(tasks, return_when=asyncio.FIRST_COMPLETED)

        for task in done:
            block = task.result()
            if block:
                valid_count = sum(
                    1
                    for miner in self.miners
                    if miner.validate_block(
                        block=block,
                        previous_hash=previous_hash,
                        difficulty=self.difficulty,
                    )
                )
                if valid_count > len(self.miners) / 2:
                    self.add_block(block)
                    self.reward_miner(block.proposer, block.total_fees)
                    stop_event.set()  # Signal other miners to stop
                    return block

        # If no block was successfully mined
        stop_event.set()
        return None

    def reward_miner(self, miner_address: str, transaction_fees: float):
        miner = next(m for m in self.miners if m.address == miner_address)
        reward = self.block_reward + transaction_fees
        miner.total_rewards += reward

        if self.get_new_block_index() % self.halving_interval == 0:
            self.block_reward /= 2

    def get_miner_rewards(self):
        return {miner.address: miner.total_rewards for miner in self.miners}

    def simulate_51_percent_attack(self, attacker: Miner):
        """Simulate a 51% attack."""
        if attacker.hash_rate > sum(m.hash_rate for m in self.miners if m != attacker):
            print(f"51% attack attempted by {attacker.address[:8]}!")

            # Check if there are enough blocks to perform the attack
            if len(self.chain) < 10:
                print("Not enough blocks in the chain to perform the attack.")
                return False

            honest_chain_length = len(self.chain)
            attacker_chain = self.chain[:-10]

            # Attacker mines faster than the rest of the network
            for _ in range(11):
                new_block = Block(0, attacker.address, [], attacker_chain[-1].hash)
                attacker_chain.append(new_block)

            if len(attacker_chain) > honest_chain_length:
                print("51% attack successful! Longer chain created.")
                self.chain = attacker_chain
                return True

        return False

    def simulate_selfish_mining(self, attacker: Miner):
        """Simulate selfish mining."""
        if attacker.hash_rate > 0.3 * sum(m.hash_rate for m in self.miners):
            print(f"Selfish mining attempted by {attacker.address[:8]}!")
            private_chain = [self.chain[-1]]
            public_chain_length = len(self.chain)

            while len(private_chain) <= public_chain_length:
                new_block = Block(0, attacker.address, [], private_chain[-1].hash)
                private_chain.append(new_block)

            if len(private_chain) > public_chain_length:
                print("Selfish mining successful! Private chain released.")
                self.chain = private_chain
                return True

        return False

    def simulate_double_spending(self, attacker: Miner):
        """Simulate a double spending attack."""
        if attacker.hash_rate > 0.1 * sum(m.hash_rate for m in self.miners):
            print(f"Double spending attempted by {attacker.address[:8]}!")
            honest_transaction = Transaction(attacker.address, "Merchant", 100, 1)
            conflicting_transaction = Transaction(
                attacker.address, attacker.address, 100, 1
            )

            # Add honest transaction to the main chain
            self.mine_block([honest_transaction])

            # Attacker creates a parallel chain with conflicting transaction
            attacker_chain = self.chain[:-1]
            new_block = Block(
                0, attacker.address, [conflicting_transaction], attacker_chain[-1].hash
            )
            attacker_chain.append(new_block)

            # Attacker tries to extend their chain to be longer
            while len(attacker_chain) <= len(self.chain):
                new_block = Block(0, attacker.address, [], attacker_chain[-1].hash)
                attacker_chain.append(new_block)

            if len(attacker_chain) > len(self.chain):
                print("Double spending successful! Conflicting chain is longer.")
                self.chain = attacker_chain
                return True
        return False

    def simulate_attacks(self):
        """Simulate various attacks on the blockchain."""
        attacker = next((miner for miner in self.miners if miner.is_malicious), None)
        if not attacker:
            return False

        attack_type = random.choice(["51_percent", "selfish_mining", "double_spending"])

        if attack_type == "51_percent":
            return self.simulate_51_percent_attack(attacker)
        elif attack_type == "selfish_mining":
            return self.simulate_selfish_mining(attacker)
        else:
            return self.simulate_double_spending(attacker)


async def simulate_pow_with_attacks():
    honest_miners = [Miner(hash_rate=random.randint(10, 100)) for _ in range(4)]
    attacker = Miner(hash_rate=300, is_malicious=True)  # Attacker with high hash rate
    miners = honest_miners + [attacker]
    pow_blockchain = ProofOfWork(
        miners,
        initial_difficulty=1,
        target_block_time=2,
        initial_reward=100,
    )

    attack_count = 0
    successful_attacks_count = 0

    for i in range(100):  # Simulate 100 blocks
        transactions = [
            Transaction(
                sender="Alice",
                receiver="Bob",
                amount=random.randint(1, 100),
                fee=random.randint(1, 5),
            )
            for _ in range(10)
        ]
        block = await pow_blockchain.mine_block(transactions)
        print(i, block)

        # # Attempt an attack every 10 blocks
        # if _ % 10 == 0:
        #     attack_count += 1
        #     if pow_blockchain.simulate_attacks():
        #         successful_attacks_count += 1

    print(f"Blockchain is valid: {pow_blockchain.is_valid()}")
    print(f"Blockchain length: {len(pow_blockchain.chain)}")
    print(f"Final difficulty: {pow_blockchain.difficulty}")
    print(f"Total attacks attempted: {attack_count}")
    print(f"Successful attacks: {successful_attacks_count}")
    print("Miner rewards:")
    for address, reward in pow_blockchain.get_miner_rewards().items():
        print(f"Miner {address[:8]}: {reward}")


if __name__ == "__main__":
    asyncio.run(simulate_pow_with_attacks())
