import seaborn as sns
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from collections import Counter
import os


def plot(consensus_data):
    # Assuming you have a list of dictionaries called 'data'
    # Convert the list of dictionaries to a DataFrame
    df = pd.DataFrame(consensus_data)

    # Set the style for all plots
    sns.set_style("whitegrid")
    sns.set_palette("viridis")
    plt.rcParams["figure.figsize"] = (12, 8)

    # Function to save plots
    def save_plot(name):
        plt.tight_layout()
        plt.savefig(f"{name}.png", dpi=300, bbox_inches="tight")
        plt.close()

    # Figure 1: Comparison of average time and energy consumption by consensus type (log scale)
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
    plt.legend(title="Consensus Type", bbox_to_anchor=(1.05, 1), loc="upper left")
    save_plot("time_vs_energy_log")

    # Figure 2: Distribution of TPS by consensus type (log scale)
    plt.figure(figsize=(12, 8))
    sns.boxenplot(data=df, x="consensus", y="avg_tps")
    plt.title("Distribution of Average TPS by Consensus Type")
    plt.xlabel("Consensus Type")
    plt.ylabel("Average Transactions per Second (TPS)")
    plt.yscale("log")
    plt.xticks(rotation=45)
    save_plot("tps_distribution_log")

    # Figure 3: Relationship between number of miners and total time (log scale)
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
    plt.legend(title="Consensus Type", bbox_to_anchor=(1.05, 1), loc="upper left")
    save_plot("miners_vs_time_log")

    # Figure 4: Energy consumption distribution by consensus type (log scale)
    plt.figure(figsize=(12, 8))
    sns.violinplot(data=df, x="consensus", y="total_energy", cut=0)
    plt.title("Energy Consumption Distribution by Consensus Type")
    plt.xlabel("Consensus Type")
    plt.ylabel("Total Energy Consumption")
    plt.yscale("log")
    plt.xticks(rotation=45)
    save_plot("energy_distribution_log")

    # Figure 5: Heatmap of correlations between numerical variables
    numerical_cols = [
        "num_miners",
        "num_blocks",
        "total_time",
        "avg_time",
        "total_energy",
        "avg_energy",
        "avg_tps",
    ]
    corr_matrix = df[numerical_cols].corr()
    plt.figure(figsize=(12, 10))
    sns.heatmap(corr_matrix, annot=True, cmap="coolwarm", vmin=-1, vmax=1, center=0)
    plt.title("Correlation Heatmap of Numerical Variables")
    save_plot("correlation_heatmap")

    # Figure 6: Efficiency comparison (TPS/Energy) (log scale)
    df["efficiency"] = df["avg_tps"] / df["avg_energy"]
    plt.figure(figsize=(12, 8))
    sns.barplot(data=df, x="consensus", y="efficiency")
    plt.title("Efficiency Comparison (TPS/Energy) by Consensus Type")
    plt.xlabel("Consensus Type")
    plt.ylabel("Efficiency (TPS/Energy)")
    plt.yscale("log")
    plt.xticks(rotation=45)
    save_plot("efficiency_comparison_log")

    # Figure 7: Scalability - TPS vs Number of Miners (log-log scale)
    plt.figure(figsize=(12, 8))
    sns.scatterplot(data=df, x="num_miners", y="avg_tps", hue="consensus")
    plt.title("Scalability: TPS vs Number of Miners")
    plt.xlabel("Number of Miners")
    plt.ylabel("Average TPS")
    plt.xscale("log")
    plt.yscale("log")
    plt.legend(title="Consensus Type", bbox_to_anchor=(1.05, 1), loc="upper left")
    save_plot("scalability_tps_vs_miners_log")

    # Figure 8: Time and Energy Trade-off (log-log scale)
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
    plt.legend(title="Consensus Type", bbox_to_anchor=(1.05, 1), loc="upper left")
    save_plot("time_energy_tradeoff_log")

    # Figure 9: TPS Stability
    df["tps_stability"] = df["tps"].apply(
        lambda x: np.std(x) / np.mean(x)
    )  # Coefficient of variation
    plt.figure(figsize=(12, 8))
    sns.barplot(data=df, x="consensus", y="tps_stability")
    plt.title("TPS Stability by Consensus Type")
    plt.xlabel("Consensus Type")
    plt.ylabel("TPS Stability (Lower is better)")
    plt.xticks(rotation=45)
    save_plot("tps_stability")

    # Figure 10: Energy Efficiency over Time (log scale for y-axis)
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
    plt.legend(bbox_to_anchor=(1.05, 1), loc="upper left")
    save_plot("energy_efficiency_over_time_log")


# Usage example:
# consensus_data = [
#     {
#         "consensus": "PoW",
#         "num_miners": 10,
#         "num_blocks": 100,
#         "times": [1.2, 1.3, 1.1, ...],
#         "total_time": 120.5,
#         "avg_time": 1.205,
#         "energy": [100, 110, 90, ...],
#         "total_energy": 10000,
#         "avg_energy": 100,
#         "tps": [5, 6, 4, ...],
#         "avg_tps": 5,
#         "chain": [...],  # list of Block objects
#         "users": [...],  # list of User objects
#     },
#     # Add more consensus mechanisms here
# ]
# plot(consensus_data)
