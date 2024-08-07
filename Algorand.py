import hashlib
import math
import time
import random
from typing import List

from ecdsa import SECP256k1, SigningKey, VerifyingKey

from transaction import Transaction


class Block:
    def __init__(
        self,
        transactions: List[Transaction],
        previous_hash: str,
        vrf_proof,
        verify_key: VerifyingKey,
    ):
        self.transactions = transactions
        self.previous_hash = previous_hash
        self.timestamp = int(time.time())
        self.vrf_proof = vrf_proof
        self.verify_key = verify_key
        self.hash = self.calculate_hash()

    def calculate_hash(self) -> str:
        block_data = f"{self.transactions}{self.previous_hash}{self.timestamp}{self.vrf_proof}{self.verify_key}"
        return hashlib.sha256(block_data.encode()).hexdigest()

    def is_valid(self, previous_hash: str):
        return (
            self.hash == self.calculate_hash() and self.previous_hash == previous_hash
        )

    def __repr__(self):
        return f"""Block (
                    timestamp={self.timestamp},
                    hash={self.hash},
                    previous_hash={self.previous_hash},
                    vrf_proof={self.vrf_proof},
                    verify_key={self.verify_key},
                )"""


class Blockchain:
    def __init__(self):
        self.chain: List[Block] = []

        self.create_genesis_block()

    def create_genesis_block(self) -> None:
        genesis_block = Block([], "0", "0", "0")
        self.chain.append(genesis_block)

    def add_block(self, block: Block) -> None:
        if block.is_valid(self.get_last_block().hash):
            self.chain.append(block)

    def get_last_block(self) -> Block:
        return self.chain[-1]

    def get_new_block_index(self) -> int:
        return len(self.chain)

    def is_valid(self) -> bool:
        return all(
            self.chain[i].is_valid(
                target=self.target_from_difficulty(),
                previous_hash=self.chain[i - 1].hash,
            )
            for i in range(1, len(self.chain))
        )


class Account:
    def __init__(self, stake):
        self.signing_key = SigningKey.generate(curve=SECP256k1)
        self.verify_key = self.signing_key.verifying_key
        self.stake = stake
        self.total_rewards = 0

    def generate_key_pair(self):
        return self.signing_key.to_string().hex(), self.verify_key.to_string().hex()

    def prove(self, message):
        # Hash the message
        message_hash = hashlib.sha256(message).digest()

        # Sign the hash
        signature = self.signing_key.sign(message_hash)

        return signature.hex(), self.verify_key

    def verify(self, message: bytes, signature, verify_key):
        verify_key = VerifyingKey.from_string(
            bytes.fromhex(verify_key.to_string().hex()), curve=SECP256k1
        )
        message_hash = hashlib.sha256(message).digest()
        try:
            return verify_key.verify(bytes.fromhex(signature), message_hash)
        except Exception:
            return False

    def __repr__(self):
        return f"Account(verify_key={self.verify_key.to_string().hex()})"


class Algorand(Blockchain):
    def __init__(
        self,
        accounts: List[Account],
        initial_supply: float,
        inflation_rate: float,
    ):
        super().__init__()

        self.accounts = accounts
        self.total_supply = initial_supply
        self.inflation_rate = inflation_rate
        self.current_round = 0
        self.base_reward = (self.total_supply * self.inflation_rate) / (
            365 * 24 * 60
        )  # Per minute

        # Calculate thresholds after committee and proposers sizes are defined
        self.proposer_threshold = 20 / len(accounts)
        self.committee_threshold = self.committee_size / len(accounts)

    @property
    def total_stake(self):
        return sum(account.stake for account in self.accounts)

    @property
    def committee_size(self):
        return max(math.isqrt(len(self.accounts)), 100)

    @property
    def proposers_size(self):
        return max(math.isqrt(len(self.accounts)), 10)

    def select_accounts(
        self,
        seed: bytes,
        threshold: float,
        is_select_proposers: bool,
    ) -> List[Account]:
        weights = [account.stake for account in self.accounts]
        total_weight = sum(weights)

        # Normalize weights
        normalized_weights = [w / total_weight for w in weights]

        # Use VRF to determine eligibility
        eligible_accounts = []
        for account, weight in zip(self.accounts, normalized_weights):
            signature, verify_key = account.prove(seed)
            vrf_output = int(signature, 16)
            if vrf_output / (2**256) < weight * threshold:
                eligible_accounts.append(account)

        # If not enough eligible accounts, add more based on stake weight
        size = self.proposers_size if is_select_proposers else self.committee_size
        if len(eligible_accounts) < size:
            additional_accounts = random.choices(
                self.accounts,
                weights=weights,
                k=size - len(eligible_accounts),
            )
            eligible_accounts.extend(additional_accounts)

        # If more than needed, randomly select the required number
        if len(eligible_accounts) > size:
            eligible_accounts = random.sample(eligible_accounts, size)

        return eligible_accounts

    def propose_block(
        self,
        proposer: Account,
        transactions: List[Transaction],
    ) -> Block:
        previous_hash = self.get_last_block().hash
        vrf_proof, verify_key = proposer.prove(previous_hash.encode())
        return Block(transactions, previous_hash, vrf_proof, verify_key)

    def validate_block(self, block: Block, proposer: Account) -> bool:
        if block.previous_hash != self.get_last_block().hash:
            return False
        if not proposer.verify(
            block.previous_hash.encode(),
            block.vrf_proof,
            block.verify_key,
        ):
            return False

        # Additional validation checks can be added here
        return True

    def byzantine_agreement(
        self,
        proposed_blocks: List[Block],
        committee: List[Account],
    ) -> Block:
        if not proposed_blocks:
            return None

        total_stake = sum(member.stake for member in committee)
        threshold = total_stake * 2 / 3

        # Step 1: Soft Vote
        votes = {block.hash: 0 for block in proposed_blocks}

        for member in committee:
            chosen_block = max(
                proposed_blocks,
                key=lambda b: hash(b.hash + str(member.stake)),
            )
            votes[chosen_block.hash] += member.stake

        winner = max(votes, key=votes.get)
        winner_stake = 0

        for member in committee:
            propose = random.choices([True, False], weights=[0.8, 0.2], k=1)[0]
            if propose:
                winner_stake += member.stake

        if winner_stake > threshold:
            return next(block for block in proposed_blocks if block.hash == winner)

        return None

        # # Step 2: Certify Vote
        # cert_votes = {block.hash: 0 for block in proposed_blocks}

        # for member in committee:
        #     if soft_votes[soft_winner] > threshold:
        #         # If there's a clear winner in soft vote, everyone votes for it
        #         chosen_block = soft_winner
        #     else:
        #         # Otherwise, vote for the block with highest hash value
        #         chosen_block = max(
        #             proposed_blocks, key=lambda b: hash(b.hash + str(member.stake))
        #         )
        #     cert_votes[chosen_block.hash] += member.stake

        # cert_winner = max(cert_votes, key=cert_votes.get)

        # print(cert_votes[cert_winner])
        # print(threshold)

        # # Step 3: Check for supermajority
        # if cert_votes[cert_winner] > threshold:
        #     return next(block for block in proposed_blocks if block.hash == cert_winner)

        # If no supermajority, go to next round (in real Algorand, this would start a new BA⋆ round)

    def distribute_rewards(self, block: Block, committee: List[Account]):
        total_reward = self.base_reward
        proposer_reward = total_reward * 0.8  # 80% to proposer
        committee_reward = total_reward * 0.2  # 20% split among committee

        proposer = next(
            account
            for account in self.accounts
            if account.verify_key == block.verify_key
        )
        proposer.stake += proposer_reward
        proposer.total_rewards += proposer_reward

        for member in committee:
            reward = committee_reward / len(committee)
            member.stake += reward
            member.total_rewards += reward

        self.total_supply += total_reward

    def mine_block(self, transactions: List[Transaction]) -> Block:
        seed = hashlib.sha256(
            f"{self.get_last_block().hash}{self.current_round}".encode()
        ).digest()

        proposers = self.select_accounts(
            seed + b"proposer", self.proposer_threshold, True
        )
        committee = self.select_accounts(
            seed + b"committee", self.committee_threshold, False
        )

        proposed_blocks = []
        for proposer in proposers:
            block = self.propose_block(proposer, transactions)
            if self.validate_block(block, proposer):
                proposed_blocks.append(block)

        self.current_round += 1

        winner = self.byzantine_agreement(proposed_blocks, committee)

        if winner:
            self.add_block(winner)
            self.distribute_rewards(winner, committee)
            return winner

        return None

    def simulate_51_percent_attack(self, attacker: Account):
        print("Simulating 51% attack...")
        attacker_stake = attacker.stake
        honest_stake = self.total_stake - attacker_stake

        if attacker_stake > honest_stake:
            print(
                f"Attacker has {attacker_stake / self.total_stake:.2%} of the total stake."
            )

            proposer_successes = 0
            committee_controls = 0
            rounds = 1000

            for _ in range(rounds):
                seed = hashlib.sha256(str(random.random()).encode()).digest()
                proposers = self.select_accounts(
                    seed + b"proposer",
                    self.proposer_threshold,
                    True,
                )
                committee = self.select_accounts(
                    seed + b"committee",
                    self.committee_threshold,
                    False,
                )

                if attacker in proposers:
                    proposer_successes += 1

                attacker_committee_stake = sum(
                    member.stake for member in committee if member == attacker
                )
                if (
                    attacker_committee_stake
                    > sum(member.stake for member in committee) * 2 / 3
                ):
                    committee_controls += 1

            print(f"Probability of being a proposer: {proposer_successes / rounds:.2%}")
            print(
                f"Probability of controlling committee: {committee_controls / rounds:.2%}"
            )
            print(
                "Even with majority stake, the attacker cannot consistently control the protocol."
            )
        else:
            print("Attacker doesn't have enough stake for a 51% attack.")

        return False

    def simulate_nothing_at_stake(self, attacker: Account):
        print("Simulating Nothing-at-Stake attack...")

        seed = hashlib.sha256(str(random.random()).encode()).digest()
        proposers = self.select_accounts(
            seed + b"proposer",
            self.proposer_threshold,
            True,
        )
        committee = self.select_accounts(
            seed + b"committee",
            self.committee_threshold,
            False,
        )

        if attacker in proposers:
            block1 = self.propose_block(attacker, [Transaction("main", "chain", 1)])
            block2 = self.propose_block(attacker, [Transaction("fork", "chain", 1)])

            winner = self.byzantine_agreement([block1, block2], committee)

            print("In Algorand:")
            print(
                "1. Only one block can be finalized per round through Byzantine agreement."
            )
            print("2. Proposing multiple blocks doesn't increase chances of reward.")
            print(
                f"3. Result: {'Two blocks proposed, but only one finalized' if winner else 'No block finalized due to conflicting proposals'}"
            )
        else:
            print("Attacker was not selected as a proposer in this round.")

        return False

    def simulate_long_range_attack(self, attacker: Account):
        print("Simulating Long-Range attack...")
        fork_point = max(0, len(self.chain) - 100)  # Try to fork from 1000 blocks ago
        honest_chain = self.chain[:]
        attacker_chain = self.chain[:fork_point]

        if not attacker_chain:
            print("Not enough blocks in the chain to perform a long-range attack.")
            return False

        for i in range(fork_point, len(honest_chain)):
            seed = hashlib.sha256(f"{attacker_chain[-1].hash}{i}".encode()).digest()
            proposers = self.select_accounts(
                seed + b"proposer",
                self.proposer_threshold,
                True,
            )
            committee = self.select_accounts(
                seed + b"committee",
                self.committee_threshold,
                False,
            )

            if attacker in proposers:
                fake_block = self.propose_block(
                    attacker, [Transaction("fake", "transaction", 1)]
                )
                if self.byzantine_agreement([fake_block], committee):
                    attacker_chain.append(fake_block)
                else:
                    print(f"Failed to reach consensus on attacker's block at round {i}")
                    break
            else:
                print(f"Attacker not selected as proposer for round {i}")
                break

        if len(attacker_chain) > len(honest_chain):
            print("In a longest-chain protocol, this attack might succeed.")

        print("In Algorand:")
        print(
            "1. Blocks are final after Byzantine agreement, preventing reorganization."
        )
        print("2. Attacker can't reconstruct historical committees or proposers.")
        print("3. State proofs provide additional security against long-range attacks.")

        return False

    def simulate_sybil_attack(self, attacker: Account):
        print("Simulating Sybil attack...")
        original_stake = attacker.stake
        sybil_accounts = [Account(original_stake / 10) for _ in range(10)]

        def measure_influence(accounts):
            proposer_selections = 0
            committee_selections = 0
            rounds = 1000

            for _ in range(rounds):
                seed = hashlib.sha256(str(random.random()).encode()).digest()
                proposers = self.select_accounts(
                    seed + b"proposer",
                    self.proposer_threshold,
                    True,
                )
                committee = self.select_accounts(
                    seed + b"committee",
                    self.committee_threshold,
                    False,
                )

                proposer_selections += sum(1 for acc in accounts if acc in proposers)
                committee_selections += sum(1 for acc in accounts if acc in committee)

            return proposer_selections / rounds, committee_selections / rounds

        original_proposer_influence, original_committee_influence = measure_influence(
            [attacker]
        )
        sybil_proposer_influence, sybil_committee_influence = measure_influence(
            sybil_accounts
        )

        print(f"Original proposer influence: {original_proposer_influence:.2%}")
        print(f"Sybil proposer influence: {sybil_proposer_influence:.2%}")
        print(f"Original committee influence: {original_committee_influence:.2%}")
        print(f"Sybil committee influence: {sybil_committee_influence:.2%}")
        print("In Algorand:")
        print("1. Influence is directly proportional to stake, not number of accounts.")
        print(
            "2. Splitting stake across multiple accounts doesn't increase overall influence."
        )

        return False

    def simulate_attacks(self):
        attacker = max(self.accounts, key=lambda a: a.stake)
        attacks = [
            self.simulate_51_percent_attack,
            self.simulate_nothing_at_stake,
            self.simulate_long_range_attack,
            self.simulate_sybil_attack,
        ]
        attack = random.choice(attacks)
        attack(attacker)
        print()


def main():
    accounts = [Account(random.uniform(100, 10000)) for _ in range(100)]
    algorand = Algorand(accounts, initial_supply=1000000, inflation_rate=0.05)

    # Mine 100 blocks
    for i in range(100):
        transactions = [
            Transaction(
                f"account_{i}",
                f"account_{(i+1)%100}",
                random.uniform(1, 100),
                random.uniform(1, 100),
            )
            for i in range(5)
        ]
        block = algorand.mine_block(transactions)
        # print(block)
        # if i % 10 == 0:
        #     algorand.simulate_attacks()

    print(algorand)


if __name__ == "__main__":
    main()
