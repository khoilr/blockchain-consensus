import seaborn as sns
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np


def save_plot(name):
    plt.tight_layout()
    plt.savefig(f"{name}.png", dpi=300, bbox_inches="tight")
    plt.close()


def plot_time_vs_energy(df):
    plt.figure(figsize=(12, 8))
    sns.scatterplot(
        data=df,
        x="avg_time",
        y="avg_energy",
        hue="consensus",
        size="num_miners",
        sizes=(50, 500),
    )
    plt.title("Average Time vs Energy Consumption by Consensus Type")
    plt.xlabel("Average Time (s)")
    plt.ylabel("Average Energy Consumption")
    plt.xscale("log")
    plt.yscale("log")
    plt.legend(title="Consensus Type")
    save_plot("time_vs_energy_log")


def plot_tps_distribution(df):
    plt.figure(figsize=(12, 8))
    sns.boxenplot(data=df, x="consensus", y="avg_tps")
    plt.title("Distribution of Average TPS by Consensus Type")
    plt.xlabel("Consensus Type")
    plt.ylabel("Average Transactions per Second (TPS)")
    plt.yscale("log")
    plt.xticks(rotation=45)
    save_plot("tps_distribution_log")


def plot_miners_vs_time(df):
    plt.figure(figsize=(12, 8))
    sns.scatterplot(
        data=df,
        x="num_miners",
        y="total_time",
        hue="consensus",
        size="num_blocks",
        sizes=(50, 500),
    )
    plt.title("Relationship between Number of Miners and Total Time")
    plt.xlabel("Number of Miners")
    plt.ylabel("Total Time (s)")
    plt.xscale("log")
    plt.yscale("log")
    plt.legend(title="Consensus Type")
    save_plot("miners_vs_time_log")


def plot_energy_distribution(df):
    plt.figure(figsize=(12, 8))
    sns.violinplot(data=df, x="consensus", y="total_energy", cut=0)
    plt.title("Energy Consumption Distribution by Consensus Type")
    plt.xlabel("Consensus Type")
    plt.ylabel("Total Energy Consumption")
    plt.yscale("log")
    plt.xticks(rotation=45)
    save_plot("energy_distribution_log")


def plot_efficiency_comparison(df):
    df["efficiency"] = df["avg_tps"] / df["avg_energy"]
    plt.figure(figsize=(12, 8))
    sns.barplot(data=df, x="consensus", y="efficiency")
    plt.title("Efficiency Comparison (TPS/Energy) by Consensus Type")
    plt.xlabel("Consensus Type")
    plt.ylabel("Efficiency (TPS/Energy)")
    plt.yscale("log")
    plt.xticks(rotation=45)
    save_plot("efficiency_comparison_log")


def plot_scalability(df):
    plt.figure(figsize=(12, 8))
    sns.scatterplot(data=df, x="num_miners", y="avg_tps", hue="consensus")
    plt.title("Scalability: TPS vs Number of Miners")
    plt.xlabel("Number of Miners")
    plt.ylabel("Average TPS")
    plt.xscale("log")
    plt.yscale("log")
    plt.legend(title="Consensus Type")
    save_plot("scalability_tps_vs_miners_log")


def plot_time_energy_tradeoff(df):
    plt.figure(figsize=(14, 10))
    sns.scatterplot(
        data=df,
        x="avg_time",
        y="avg_energy",
        hue="consensus",
        size="num_blocks",
        style="consensus",
        sizes=(100, 1000),
    )
    for i, row in df.iterrows():
        plt.annotate(
            f"Miners: {row['num_miners']}",
            (row["avg_time"], row["avg_energy"]),
            xytext=(5, 5),
            textcoords="offset points",
        )
    plt.title("Time and Energy Trade-off by Consensus Type")
    plt.xlabel("Average Time (s)")
    plt.ylabel("Average Energy Consumption")
    plt.xscale("log")
    plt.yscale("log")
    plt.legend(title="Consensus Type")
    save_plot("time_energy_tradeoff_log")


def plot_tps_stability(df):
    df["tps_stability"] = df["tps"].apply(lambda x: np.std(x) / np.mean(x))
    plt.figure(figsize=(12, 8))
    sns.barplot(data=df, x="consensus", y="tps_stability")
    plt.title("TPS Stability by Consensus Type")
    plt.xlabel("Consensus Type")
    plt.ylabel("TPS Stability (Lower is better)")
    plt.xticks(rotation=45)
    save_plot("tps_stability")


def plot_energy_efficiency_over_time(df):
    plt.figure(figsize=(14, 8))
    for _, row in df.iterrows():
        plt.plot(
            row["times"],
            np.cumsum(row["energy"]),
            label=f"{row['consensus']} (Miners: {row['num_miners']})",
        )
    plt.title("Cumulative Energy Consumption over Time")
    plt.xlabel("Time (s)")
    plt.ylabel("Cumulative Energy Consumption")
    plt.yscale("log")
    plt.legend(title="Consensus Type")
    save_plot("energy_efficiency_over_time_log")


def plot_rewards_vs_hash_rate_stake(df):
    plt.figure(figsize=(14, 8))
    for consensus in df["consensus"].unique():
        subset = df[df["consensus"] == consensus]
        hash_rates = []
        stakes = []
        total_rewards = []

        for users in subset["users"]:
            for user in users:
                if consensus == "pow" and user.hash_rate is not None:
                    hash_rates.append(user.hash_rate)
                    total_rewards.append(user.total_rewards)
                elif consensus != "pow" and user.stake is not None:
                    stakes.append(user.stake)
                    total_rewards.append(user.total_rewards)

        if consensus == "pow":
            plt.scatter(
                hash_rates,
                total_rewards,
                label=f"{consensus} (Hash Rate)",
                alpha=0.7,
            )
        else:
            plt.scatter(
                stakes,
                total_rewards,
                label=f"{consensus} (Stake)",
                alpha=0.7,
            )

    plt.title("Total Rewards vs Hash Rate/Stake by Consensus Type")
    plt.xlabel("Hash Rate / Stake")
    plt.ylabel("Total Rewards")
    plt.xscale("log")
    plt.yscale("log")
    plt.legend(title="Consensus Type")
    save_plot("rewards_vs_hash_rate_stake_log")


def plot(consensus_data):
    df = pd.DataFrame(consensus_data)
    sns.set_style("whitegrid")
    plt.rcParams["figure.figsize"] = (12, 8)

    plot_time_vs_energy(df)
    plot_tps_distribution(df)
    plot_miners_vs_time(df)
    plot_energy_distribution(df)
    plot_efficiency_comparison(df)
    plot_scalability(df)
    plot_time_energy_tradeoff(df)
    plot_tps_stability(df)
    plot_energy_efficiency_over_time(df)
    plot_rewards_vs_hash_rate_stake(df)
