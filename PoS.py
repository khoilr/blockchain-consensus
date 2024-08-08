import hashlib
import random
import time
from typing import List

from transaction import Transaction


class Block:
    def __init__(self, validator: str, txns: List[Transaction], previous_hash: str):
        self.validator = validator
        self.txns = txns
        self.previous_hash = previous_hash
        self.timestamp = int(time.time())
        self.hash = self.calculate_hash()
        self.total_fees = sum(tx.fee for tx in txns)
        self.votes = {}  # To store votes from validators

    def calculate_hash(self) -> str:
        block_data = (
            str(self.validator)
            + "".join(tx.to_bytes().decode() for tx in self.txns)
            + str(self.previous_hash)
            + str(self.timestamp)
        )
        return hashlib.sha256(block_data.encode()).hexdigest()

    def is_valid(self, previous_hash: str) -> bool:
        return (
            self.previous_hash == previous_hash and self.hash == self.calculate_hash()
        )

    def __repr__(self) -> str:
        return f"Block (timestamp={self.timestamp}, hash={self.hash[:8]}, previous_hash={self.previous_hash[:8]}, num_txns={len(self.txns)})"


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
        self.total_rewards = 0
        self.is_active = True
        self.consecutive_misses = 0

    def propose_block(self, txns: List[Transaction], previous_hash: str) -> Block:
        return Block(
            validator=self.address,
            txns=txns,
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
        self.epoch_length = 100
        self.slashing_percentage = 0.01
        self.min_stake = 1000  # Minimum stake to become a validator
        self.max_validators = 100  # validators
        self.consensus_threshold = 2 / 3

    @property
    def total_stake(self) -> float:
        return sum(validator.stake for validator in self.validators)

    @property
    def block_reward(self) -> float:
        """Calculate the block reward based on inflation rate."""
        return (self.total_supply * self.inflation_rate) / (365 * 24 * 60 * 60)

    def select_validator(self) -> Validator:
        active_validators = [
            v for v in self.validators if v.is_active and v.stake >= self.min_stake
        ]
        random.shuffle(active_validators)

        if not active_validators:
            return None

        selection_point = random.uniform(0, sum(v.stake for v in active_validators))
        current_point = 0
        for validator in active_validators:
            current_point += validator.stake
            if current_point > selection_point:
                return validator

        return active_validators[-1]

    def mine_block(self, txns: List[Transaction]) -> Block:
        proposed_block = self.propose_block(txns)
        self.epoch_based_reconfiguration()

        if proposed_block and self.finalize_block(proposed_block):
            return proposed_block

    def propose_block(self, txns: List[Transaction]) -> Block:
        proposer = self.select_validator()
        if not proposer:
            return None

        previous_block = self.get_last_block()
        new_block = Block(
            txns=txns,
            previous_hash=previous_block.hash,
            validator=proposer.address,
        )

        if self.validate_block(new_block, previous_block):
            return new_block

        return None

    def vote_on_block(self, block: Block) -> bool:
        total_votes = 0
        for validator in self.validators:
            if validator.is_active:
                # In a real system, validators would check the block's validity here
                if random.random() < 0.99:  # 99% chance to vote yes if active
                    block.votes[validator.address] = validator.stake
                    total_votes += validator.stake

        return total_votes / self.total_stake >= self.consensus_threshold

    def validate_block(self, block: Block, previous_block: Block) -> bool:
        if len(self.chain) > 0 and block.previous_hash != previous_block.hash:
            return False
        if block.hash != block.calculate_hash():
            return False

        proposer = next(
            (v for v in self.validators if v.address == block.validator), None
        )
        if not proposer or not proposer.is_active or proposer.stake < self.min_stake:
            return False

        return True

    def distribute_rewards(self, proposer: Validator, block: Block) -> None:
        base_reward = self.block_reward
        fee_reward = sum(tx.fee for tx in block.txns)
        total_reward = base_reward + fee_reward

        proposer_reward = total_reward * 0.7  # 70% to proposer
        voter_reward = total_reward * 0.3  # 30% to voters

        proposer.stake += proposer_reward
        proposer.total_rewards += proposer_reward

        for voter, stake in block.votes.items():
            voter_validator = next(v for v in self.validators if v.address == voter)
            vote_share = stake / sum(block.votes.values())
            reward = voter_reward * vote_share
            voter_validator.stake += reward
            voter_validator.total_rewards += reward

        self.total_supply += base_reward

    def update_validator_set(self) -> None:
        self.validators = sorted(self.validators, key=lambda v: v.stake, reverse=True)
        for i, validator in enumerate(self.validators):
            validator.is_active = (
                i < self.max_validators and validator.stake >= self.min_stake
            )

    def adjust_inflation_rate(self) -> None:
        target_stake_rate = 0.67  # 67% of total supply staked
        current_stake_rate = self.total_stake / self.total_supply

        if current_stake_rate < target_stake_rate:
            self.inflation_rate *= 1.05  # Increase inflation to incentivize staking
        elif current_stake_rate > target_stake_rate:
            self.inflation_rate *= (
                0.95  # Decrease inflation to reduce staking incentive
            )

        self.inflation_rate = max(0.01, min(0.15, self.inflation_rate))

    def process_slashing(self) -> None:
        for validator in self.validators:
            if validator.consecutive_misses >= 3:
                slashed_amount = validator.stake * self.slashing_percentage

                validator.stake -= slashed_amount
                self.total_supply -= slashed_amount

                validator.consecutive_misses = 0

                if validator.stake < self.min_stake:
                    validator.is_active = False

    def finalize_block(self, block: Block) -> bool:
        if self.vote_on_block(block):
            self.add_block(block)
            proposer = next(v for v in self.validators if v.address == block.validator)
            self.distribute_rewards(proposer, block)
            proposer.consecutive_misses = 0
            time.sleep(random.uniform(0.1, 1))
            return True

        return False

    def epoch_based_reconfiguration(self) -> None:
        if len(self.chain) % self.epoch_length == 0:
            self.update_validator_set()
            self.adjust_inflation_rate()
            self.process_slashing()

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
        Validator(stake=float(random.randint(1000, 10_000_000))) for _ in range(10)
    ]
    pos_blockchain = ProofOfStake(validators, initial_supply, inflation_rate)

    attack_count = 0
    successful_attacks = 0

    for i in range(1000):  # Simulate 1000 blocks
        txns = [
            Transaction(
                sender="Alice",
                receiver="Bob",
                amount=float(random.randint(1, 100)),
                fee=float(random.randint(1, 5)),
            )
            for _ in range(10)
        ]

        pos_blockchain.propose_block(txns)
        pos_blockchain.epoch_based_reconfiguration()
        pos_blockchain.finalize_block(i)

        # # Simulate attacks
        # if i % 10 == 0:  # Try an attack every 10 blocks
        #     attack_count += 1
        #     if pos_blockchain.simulate_attacks():
        #         successful_attacks += 1

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
