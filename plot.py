import os

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns


# Function to save plots
def save_plot(fig, filename):
    # Create 'images' folder if it doesn't exist
    if not os.path.exists("images"):
        os.makedirs("images")

    fig.savefig(f"images/{filename}.png", dpi=300, bbox_inches="tight")
    plt.close(fig)


def plot_comparisons(results):
    df = pd.DataFrame(results)

    # 1. Total Time vs Number of Blocks
    fig, ax = plt.subplots(figsize=(12, 6))
    sns.lineplot(
        data=df, x="num_blocks", y="total_time", hue="consensus", style="consensus", markers=True, ci=None, ax=ax
    )
    ax.set_title("Total Time vs Number of Blocks")
    ax.set_xlabel("Number of Blocks")
    ax.set_ylabel("Total Time")
    ax.set_yscale("log")
    ax.set_xscale("log")
    ax.legend(title="Consensus")
    save_plot(fig, "total_time_vs_blocks")

    # 2. Total Energy vs Number of Blocks
    fig, ax = plt.subplots(figsize=(12, 6))
    sns.lineplot(
        data=df, x="num_blocks", y="total_energy", hue="consensus", style="consensus", markers=True, ci=None, ax=ax
    )
    ax.set_title("Total Energy Consumption vs Number of Blocks")
    ax.set_xlabel("Number of Blocks")
    ax.set_ylabel("Total Energy Consumption")
    ax.set_yscale("log")
    ax.set_xscale("log")
    ax.legend(title="Consensus")
    save_plot(fig, "total_energy_vs_blocks")

    # 3. Average TPS vs Number of Miners
    fig, ax = plt.subplots(figsize=(12, 6))
    sns.lineplot(data=df, x="num_miners", y="avg_tps", hue="consensus", style="consensus", markers=True, ci=None, ax=ax)
    ax.set_title("Average TPS vs Number of Miners")
    ax.set_xlabel("Number of Miners")
    ax.set_ylabel("Average TPS")
    ax.set_xscale("log")
    ax.legend(title="Consensus")
    save_plot(fig, "avg_tps_vs_miners")

    # 4. Average Time per Block vs Number of Miners
    fig, ax = plt.subplots(figsize=(12, 6))
    sns.lineplot(
        data=df, x="num_miners", y="avg_time", hue="consensus", style="consensus", markers=True, ci=None, ax=ax
    )
    ax.set_title("Average Time per Block vs Number of Miners")
    ax.set_xlabel("Number of Miners")
    ax.set_ylabel("Average Time per Block")
    ax.set_xscale("log")
    ax.legend(title="Consensus")
    save_plot(fig, "avg_time_vs_miners")

    # 5. Energy Efficiency (TPS/Energy) vs Number of Miners
    df["energy_efficiency"] = df["avg_tps"] / df["avg_energy"]
    fig, ax = plt.subplots(figsize=(12, 6))
    sns.lineplot(
        data=df, x="num_miners", y="energy_efficiency", hue="consensus", style="consensus", markers=True, ci=None, ax=ax
    )
    ax.set_title("Energy Efficiency vs Number of Miners")
    ax.set_xlabel("Number of Miners")
    ax.set_ylabel("Energy Efficiency (TPS/Energy)")
    ax.set_xscale("log")
    ax.set_yscale("log")
    ax.legend(title="Consensus")
    save_plot(fig, "energy_efficiency_vs_miners")

    # 6. Scalability: TPS vs Number of Blocks
    fig, ax = plt.subplots(figsize=(12, 6))
    sns.lineplot(data=df, x="num_blocks", y="avg_tps", hue="consensus", style="consensus", markers=True, ci=None, ax=ax)
    ax.set_title("Scalability: TPS vs Number of Blocks")
    ax.set_xlabel("Number of Blocks")
    ax.set_ylabel("Average TPS")
    ax.set_xscale("log")
    ax.legend(title="Consensus")
    save_plot(fig, "scalability_tps_vs_blocks")

    # 7. Energy Consumption Distribution
    fig, ax = plt.subplots(figsize=(12, 6))
    sns.boxplot(data=df, x="consensus", y="total_energy", ax=ax)
    ax.set_title("Energy Consumption Distribution by Consensus")
    ax.set_xlabel("Consensus Mechanism")
    ax.set_ylabel("Total Energy Consumption")
    ax.set_yscale("log")
    save_plot(fig, "energy_consumption_distribution")

    # 8. Time Efficiency vs Energy Efficiency
    fig, ax = plt.subplots(figsize=(12, 6))
    sns.scatterplot(
        data=df,
        x="avg_time",
        y="avg_energy",
        hue="consensus",
        style="consensus",
        size="num_miners",
        sizes=(50, 200),
        ax=ax,
    )
    ax.set_title("Time Efficiency vs Energy Efficiency")
    ax.set_xlabel("Average Time per Block")
    ax.set_ylabel("Average Energy per Block")
    ax.set_xscale("log")
    ax.set_yscale("log")
    ax.legend(title="Consensus")
    save_plot(fig, "time_vs_energy_efficiency")
