import hashlib
import random
import time
from typing import List, Optional

import numpy as np

from transaction import Transaction


class Block:
    def __init__(
        self, validator: str, transactions: List[Transaction], previous_hash: str
    ):
        self.validator = validator
        self.transactions = transactions
        self.previous_hash = previous_hash
        self.timestamp = int(time.time())
        self.hash = self.calculate_hash()
        self.total_fees = sum(tx.fee for tx in transactions)

    def calculate_hash(self) -> str:
        block_data = (
            str(self.validator)
            + "".join(tx.to_bytes().decode() for tx in self.transactions)
            + str(self.previous_hash)
            + str(self.timestamp)
        )
        return hashlib.sha256(block_data.encode()).hexdigest()

    def is_valid(self, previous_hash: str) -> bool:
        return (
            self.previous_hash == previous_hash and self.hash == self.calculate_hash()
        )

    def __repr__(self) -> str:
        return f"""Block (
                    timestamp: {self.timestamp},
                    validator: {self.validator},
                    previous_hash: {self.previous_hash},
                    hash: {self.hash},
                    total_fees: {self.total_fees}
                )"""


class Blockchain:
    def __init__(self):
        self.chain: List[Block] = []
        self.create_genesis_block()

    def create_genesis_block(self) -> None:
        genesis_block = Block("0", [], "0")
        self.chain.append(genesis_block)

    def add_block(self, block: Block) -> None:
        if block.is_valid(previous_hash=self.get_last_block().hash):
            self.chain.append(block)

    def get_last_block(self) -> Block:
        return self.chain[-1]

    def get_new_block_index(self) -> int:
        return len(self.chain)

    def is_valid(self) -> bool:
        return all(
            self.chain[i].is_valid(previous_hash=self.chain[i - 1].hash)
            for i in range(1, len(self.chain))
        )


class Validator:
    def __init__(self, stake: float):
        self.address = hashlib.sha256(bytes(str(time.time()), "utf-8")).hexdigest()
        self.stake = stake
        self.slash_count = 0
        self.total_rewards = 0

    def propose_block(
        self, transactions: List[Transaction], previous_hash: str
    ) -> Block:
        return Block(
            validator=self.address,
            transactions=transactions,
            previous_hash=previous_hash,
        )

    def validate_block(self, block: Block, previous_hash: str) -> bool:
        return block.is_valid(previous_hash)


class ProofOfStake(Blockchain):
    def __init__(
        self,
        validators: List[Validator],
        initial_supply: float,
        inflation_rate: float,
    ):
        super().__init__()
        self.validators = validators
        self.total_supply = initial_supply
        self.inflation_rate = inflation_rate
        self.last_finalized_block = 0

    @property
    def total_stake(self) -> float:
        return sum(validator.stake for validator in self.validators)

    @property
    def block_reward(self) -> float:
        """Calculate the block reward based on inflation rate."""
        return (self.total_supply * self.inflation_rate) / 365 * 24

    def select_validator(self) -> Validator:
        """Select a validator based on their stake."""
        selection_point = random.uniform(0, self.total_stake)
        current_point = 0
        for validator in self.validators:
            current_point += validator.stake
            if current_point > selection_point:
                return validator
        return self.validators[-1]  # Fallback to last validator if something goes wrong

    def propose_block(self, transactions: List[Transaction]) -> None:
        """Propose a new block to be added to the chain."""
        proposer = self.select_validator()
        previous_hash = self.chain[-1].hash if self.chain else None
        new_block = proposer.propose_block(transactions, previous_hash)
        if self.validate_block(new_block):
            self.chain.append(new_block)
            self.distribute_rewards(proposer, new_block)
            print(f"Block {len(self.chain)} added by {proposer.address[:8]}")
        else:
            print(f"Block proposed by {proposer.address[:8]} is invalid")

    def validate_block(self, block: Block) -> bool:
        """Validate a proposed block."""
        if len(self.chain) > 0 and block.previous_hash != self.chain[-1].hash:
            return False
        if block.timestamp <= self.chain[-1].timestamp:
            return False
        if block.hash != block.calculate_hash():
            return False
        proposer = next(
            (v for v in self.validators if v.address == block.validator), None
        )
        if not proposer or proposer.stake <= 0:
            return False
        return True

    def distribute_rewards(self, proposer: Validator, block: Block) -> None:
        """Distribute rewards to the block proposer."""
        reward = self.block_reward + sum(tx.fee for tx in block.transactions)
        proposer.stake += reward
        proposer.total_rewards += reward
        self.total_supply += self.block_reward

    def epoch_based_reconfiguration(self, epoch_length: int = 100) -> None:
        """Perform epoch-based reconfiguration."""
        if len(self.chain) % epoch_length == 0:
            print("Performing epoch-based reconfiguration...")
            self.update_validator_set()

    def update_validator_set(self) -> None:
        """Update the validator set based on current stakes."""
        self.validators = sorted(self.validators, key=lambda v: v.stake, reverse=True)[
            :100
        ]  # Keep top 100 validators

    def simulate_network_latency(self) -> float:
        """Simulate network latency."""
        return random.uniform(
            0.1, 2.0
        )  # Return a random latency between 0.1 and 2 seconds

    def simulate_nothing_at_stake_attack(self, attacker: Validator) -> bool:
        """Simulate a Nothing-at-Stake attack."""
        if random.random() < 0.1:  # 10% chance of a fork occurring
            print(f"Nothing-at-Stake attack attempted by {attacker.address[:8]}!")
            fork_chain = self.chain[:-1]  # Create a fork from the previous block
            fork_block = attacker.propose_block([], fork_chain[-1].hash)
            if self.validate_block(fork_block):
                print("Fork created successfully!")
                return True
        return False

    def simulate_long_range_attack(self, attacker: Validator) -> bool:
        """Simulate a Long-Range attack."""
        if (
            len(self.chain) - self.last_finalized_block > 100
        ):  # If there's a long unfinalized chain
            print(f"Long-Range attack attempted by {attacker.address[:8]}!")
            fork_point = random.randint(self.last_finalized_block, len(self.chain) - 1)
            fork_chain = self.chain[:fork_point]
            for _ in range(len(self.chain) - fork_point):
                fork_block = attacker.propose_block([], fork_chain[-1].hash)
                if self.validate_block(fork_block):
                    fork_chain.append(fork_block)
            if len(fork_chain) > len(self.chain):
                print("Long-Range attack successful! Longer chain created.")
                self.chain = fork_chain
                return True
        return False

    def simulate_sybil_attack(self, attacker: Validator) -> bool:
        """Simulate a Sybil attack."""
        if (
            attacker.stake > self.total_stake * 0.1
        ):  # If attacker controls more than 10% of stake
            print(f"Sybil attack attempted by {attacker.address[:8]}!")
            sybil_validators = [Validator(attacker.stake / 10) for _ in range(10)]
            self.validators.extend(sybil_validators)
            print(
                f"Sybil attack successful! {len(sybil_validators)} new validators added."
            )
            return True
        return False

    def simulate_attacks(self) -> bool:
        attacker = random.choice(self.validators)
        attack_type = random.choice(["nothing_at_stake", "long_range", "sybil"])

        if attack_type == "nothing_at_stake":
            return self.simulate_nothing_at_stake_attack(attacker)
        elif attack_type == "long_range":
            return self.simulate_long_range_attack(attacker)
        elif attack_type == "sybil":
            return self.simulate_sybil_attack(attacker)

        return False


def simulate_pos_with_attacks():
    initial_supply = float("1000000")
    inflation_rate = float("0.02")  # 2% annual inflation
    validators = [
        Validator(stake=float(random.randint(1000, 100000))) for _ in range(10)
    ]
    pos_blockchain = ProofOfStake(validators, initial_supply, inflation_rate)

    attack_count = 0
    successful_attacks = 0

    for i in range(1000):  # Simulate 1000 blocks
        transactions = [
            Transaction(
                sender="Alice",
                receiver="Bob",
                amount=float(random.randint(1, 100)),
                fee=float(random.randint(1, 5)),
            )
            for _ in range(10)
        ]
        latency = pos_blockchain.simulate_network_latency()
        time.sleep(latency)
        pos_blockchain.propose_block(transactions)
        pos_blockchain.epoch_based_reconfiguration()

        # Simulate attacks
        if i % 10 == 0:  # Try an attack every 10 blocks
            attack_count += 1
            if pos_blockchain.simulate_attacks():
                successful_attacks += 1

    print(f"Blockchain is valid: {pos_blockchain.is_valid()}")
    print(f"Blockchain length: {len(pos_blockchain.chain)}")
    print(f"Total supply: {pos_blockchain.total_supply}")
    print(f"Total attacks attempted: {attack_count}")
    print(f"Successful attacks: {successful_attacks}")
    for validator in pos_blockchain.validators:
        print(
            f"Validator {validator.address[:8]}: Stake = {validator.stake}, Total Rewards = {validator.total_rewards}"
        )


if __name__ == "__main__":
    simulate_pos_with_attacks()
