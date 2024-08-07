import seaborn as sns
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from collections import Counter
import os


def plot(consensus_data):
    # Create 'images' directory if it doesn't exist
    if not os.path.exists("images"):
        os.makedirs("images")

    # Convert the list of dictionaries to a DataFrame
    df = pd.DataFrame(consensus_data)

    # Set up the plot style
    sns.set(style="whitegrid", font_scale=1.2)

    # Helper functions
    def get_block_sizes(chain):
        return [len(block.transactions) for block in chain]

    def get_user_rewards(users):
        return [user.total_rewards for user in users]

    # Add new columns to the DataFrame
    df["block_sizes"] = df["chain"].apply(get_block_sizes)
    df["user_rewards"] = df["users"].apply(get_user_rewards)
    df["avg_block_size"] = df["block_sizes"].apply(np.mean)
    df["avg_user_reward"] = df["user_rewards"].apply(np.mean)

    # 1. Comparison of key metrics across consensus types
    fig, axes = plt.subplots(2, 2, figsize=(20, 20))
    axes = axes.flatten()

    metrics = ["avg_time", "avg_energy", "avg_tps", "avg_block_size"]
    titles = [
        "Average Block Time",
        "Average Energy Consumption",
        "Average TPS",
        "Average Block Size",
    ]

    for ax, metric, title in zip(axes, metrics, titles):
        sns.barplot(x="consensus", y=metric, data=df, ax=ax)
        ax.set_title(title)
        ax.set_ylabel(metric)
        ax.set_xlabel("Consensus Mechanism")

        # Add text labels
        for i, v in enumerate(df[metric]):
            ax.text(i, v, f"{v:.2f}", ha="center", va="bottom")

    plt.tight_layout()
    plt.savefig("images/key_metrics_comparison.png")
    plt.close()

    # 2. Scatter plot matrix
    sns.pairplot(
        df,
        vars=["num_miners", "num_blocks", "avg_time", "avg_energy", "avg_tps"],
        hue="consensus",
        height=3,
        aspect=1.2,
    )
    plt.suptitle("Relationships Between Key Metrics", y=1.02)
    plt.savefig("images/scatter_plot_matrix.png")
    plt.close()

    # 3. Heatmap of correlations between metrics
    correlation_metrics = [
        "num_miners",
        "num_blocks",
        "avg_time",
        "avg_energy",
        "avg_tps",
        "avg_block_size",
        "avg_user_reward",
    ]
    correlation_df = df[correlation_metrics].corr()
    plt.figure(figsize=(12, 10))
    sns.heatmap(correlation_df, annot=True, cmap="coolwarm", vmin=-1, vmax=1, center=0)
    plt.title("Correlation Heatmap of Blockchain Metrics")
    plt.savefig("images/correlation_heatmap.png")
    plt.close()

    # 4. Line plots showing the effect of num_miners and num_blocks on performance metrics
    fig, axes = plt.subplots(2, 2, figsize=(20, 20))
    axes = axes.flatten()

    for ax, metric, title in zip(axes, metrics, titles):
        for _, row in df.iterrows():
            ax.plot(row["num_miners"], row[metric], "o-", label=row["consensus"])
        ax.set_title(f"{title} vs Number of Miners")
        ax.set_xlabel("Number of Miners")
        ax.set_ylabel(metric)
        ax.legend()

    plt.tight_layout()
    plt.savefig("images/miners_effect_on_metrics.png")
    plt.close()

    # 5. 3D scatter plot
    fig = plt.figure(figsize=(12, 8))
    ax = fig.add_subplot(111, projection="3d")

    for _, row in df.iterrows():
        ax.scatter(
            row["num_miners"], row["num_blocks"], row["avg_tps"], label=row["consensus"]
        )

    ax.set_xlabel("Number of Miners")
    ax.set_ylabel("Number of Blocks")
    ax.set_zlabel("Average TPS")
    ax.legend()
    plt.title("3D Scatter Plot: Miners vs Blocks vs TPS")
    plt.savefig("images/3d_scatter_plot.png")
    plt.close()

    # 6. Grouped bar plot for comparing metrics across consensus types
    melted_df = df.melt(
        id_vars=["consensus", "num_miners", "num_blocks"],
        value_vars=["avg_time", "avg_energy", "avg_tps", "avg_block_size"],
        var_name="metric",
        value_name="value",
    )

    plt.figure(figsize=(15, 8))
    sns.barplot(x="consensus", y="value", hue="metric", data=melted_df)
    plt.title("Comparison of Metrics Across Consensus Types")
    plt.xlabel("Consensus Mechanism")
    plt.ylabel("Value (normalized)")
    plt.legend(title="Metric")
    plt.savefig("images/grouped_bar_plot.png")
    plt.close()

    # 7. Radar chart for comparing key metrics
    def make_spider(row, title, color):
        categories = [
            "avg_time",
            "avg_energy",
            "avg_tps",
            "avg_block_size",
            "num_miners",
        ]
        N = len(categories)

        values = row[categories].values.flatten().tolist()
        values += values[:1]

        angles = [n / float(N) * 2 * np.pi for n in range(N)]
        angles += angles[:1]

        ax = plt.subplot(111, polar=True)
        plt.xticks(angles[:-1], categories)
        ax.plot(angles, values, color=color, linewidth=2, linestyle="solid")
        ax.fill(angles, values, color=color, alpha=0.4)
        plt.title(title)

    plt.figure(figsize=(15, 15))
    for i, (_, row) in enumerate(df.iterrows()):
        plt.subplot(2, 2, i + 1, polar=True)
        make_spider(
            row,
            f"{row['consensus']} (Miners: {row['num_miners']}, Blocks: {row['num_blocks']})",
            plt.cm.Set2(i),
        )

    plt.tight_layout()
    plt.savefig("images/radar_chart.png")
    plt.close()

    print("All plots have been saved in the 'images' directory.")


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
