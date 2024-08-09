# blockchain-consensus

## Efficiency Comparison (TPS/Energy) by Consensus Type

![alt text](efficiency_comparison_log.png)

The bar graph shows the efficiency comparison (in terms of Transactions Per Second (TPS) per unit of energy) across three different consensus types: PoW (Proof-of-Work), PoS (Proof-of-Stake), and Algorand.

Key observations:

- The efficiency of Algorand is significantly higher than both PoW and PoS, as indicated by the much taller blue bar for Algorand compared to the other two.
- The efficiency of PoS is also higher than that of PoW, but the difference is not as dramatic as the gap between Algorand and the other two.
- The y-axis is on a logarithmic scale, which means the differences in efficiency between the consensus types are quite substantial. For example, the efficiency of Algorand appears to be around 3-4 orders of magnitude higher than that of PoW.

This plot suggests that Algorand is the most efficient consensus mechanism in terms of the ratio of TPS to energy consumption, outperforming both PoW and PoS by a large margin. This is an important consideration for blockchain applications where energy efficiency and scalability are crucial factors.

The stark contrast in efficiency between the consensus types highlights the need to carefully evaluate the trade-offs and select the most appropriate consensus mechanism that aligns with the specific requirements and constraints of the blockchain application.

## Energy Consumption Distribution by Consensus Type

![alt text](energy_distribution_log.png)
The image shows the distribution of energy consumption for three different consensus types: PoW (Proof-of-Work), PoS (Proof-of-Stake), and Algorand.

Key observations:

- The distribution for PoW has a much wider spread and a significantly higher peak compared to the other two consensus types. This indicates that PoW has a higher overall energy consumption and a wider range of energy usage values.
- The distribution for PoS is narrower and more concentrated, suggesting a lower overall energy consumption and less variability in energy usage compared to PoW.
- The distribution for Algorand is also narrower and more concentrated, with the lowest overall energy consumption among the three consensus types.

The violin plots provide a clear visual representation of the differences in energy consumption patterns across the consensus mechanisms. PoW exhibits the highest and most variable energy consumption, while PoS and Algorand show progressively lower and more consistent energy usage.

This information is crucial when evaluating the sustainability and scalability of blockchain networks, as energy consumption is a critical factor in the selection of an appropriate consensus mechanism. The data suggests that Algorand may be the most energy-efficient choice among the three, which could be an important consideration for blockchain applications with stringent energy requirements.

## Relationship between Number of Miners and Total Time

![alt text](miners_vs_time_log.png)

The image shows the relationship between the number of miners and the total time required to complete the blockchain network operations. This is an important aspect of understanding the scalability of different consensus mechanisms.
Key observations:

- The x-axis represents the number of miners on a logarithmic scale, ranging from 100 to 10,000.
- The y-axis shows the total time required, also on a logarithmic scale, ranging from 0.1 seconds to 1000 seconds.
- The data points are color-coded based on the consensus type (PoW, PoS, or Algorand) and sized based on the number of blocks processed.
- For PoW, the data points are generally clustered in the top-left region, indicating higher total time and fewer miners.
- The PoS and Algorand data points are more evenly distributed, suggesting these consensus mechanisms can handle a wider range of miner counts with lower total time.
- As the number of miners increases, the total time tends to decrease for all consensus types, indicating improved scalability with more miners.
- However, the rate of improvement and the overall performance vary significantly between the consensus mechanisms, with Algorand showing the best scalability.

This plot provides valuable insights into how the number of miners impacts the total time required for the blockchain network to operate. It highlights the differences in scalability between PoW, PoS, and Algorand, with Algorand demonstrating the most favorable relationship between miner count and total time. This information is crucial when selecting the appropriate consensus mechanism for a blockchain application that requires efficient and scalable performance.

## Total Rewards vs Hash Rate/Stake by Consensus Type

![alt text](rewards_vs_hash_rate_stake_log.png)

The image shows the relationship between the total rewards received by participants and their hash rate (for Proof-of-Work) or stake (for Proof-of-Stake and Algorand) across the three consensus types: PoW, PoS, and Algorand.

Key observations:

- The x-axis represents the hash rate (for PoW) or stake (for PoS and Algorand) on a logarithmic scale, ranging from 10^6 to 10^18.
- The y-axis shows the total rewards received by the participants, also on a logarithmic scale, ranging from 10^-4 to 10^4.
- The data points are color-coded based on the consensus type, with blue for PoW (hash rate), orange for PoS (stake), and green for Algorand (stake).
- For PoW, the data points form a clear and relatively linear relationship between hash rate and total rewards, suggesting a direct correlation between the two.
- The PoS and Algorand data points exhibit a more scattered pattern, indicating a less direct relationship between stake and total rewards.
- The PoS and Algorand data points appear to have a higher concentration at the lower end of the stake spectrum, while the PoW data points are more evenly distributed across the hash rate range.

This plot provides insights into the different reward structures and incentive mechanisms employed by the three consensus mechanisms. The linear relationship for PoW suggests a more straightforward reward system based on hash rate, while the more scattered patterns for PoS and Algorand suggest more complex reward dynamics that may involve factors beyond just the stake.

The differences in the distribution and trends of the data points can help researchers and developers understand the incentive structures and participation dynamics of each consensus type, which is crucial for designing effective and fair blockchain systems.

## Scalability: TPS vs Number of Miners

![alt text](scalability_tps_vs_miners_log.png)

The image shows the relationship between the number of miners and the average transactions per second (TPS) for the three consensus types: PoW, PoS, and Algorand.

Key observations:

- The x-axis represents the number of miners on a logarithmic scale, ranging from 10 to 10,000.
- The y-axis shows the average TPS, also on a logarithmic scale, ranging from 100 to 100,000.
- The data points are color-coded based on the consensus type, with blue for PoW, orange for PoS, and green for Algorand.
- For PoW, the data points are clustered in the lower left region, indicating relatively lower TPS and fewer miners.
- The PoS and Algorand data points are more widely distributed, covering a larger range of both miner counts and TPS values.
- As the number of miners increases, the average TPS tends to increase for all consensus types, suggesting improved scalability.
- However, the rate of improvement and the overall TPS levels vary significantly between the consensus mechanisms, with Algorand demonstrating the best scalability, followed by PoS and then PoW.

This plot provides valuable insights into the scalability of the different consensus mechanisms. It highlights the ability of each consensus type to handle increasing transaction volumes as the network size grows. The superior performance of Algorand in terms of achieving higher TPS with a larger number of miners suggests that it may be the most scalable option among the three consensus types examined.

This information is crucial for blockchain applications that require high throughput and the ability to scale effectively as the network expands. The comparative analysis of the consensus types can help developers and decision-makers select the most appropriate consensus mechanism that aligns with their scalability requirements.

## Average Time vs Energy Consumption by Consensus Type

![alt text](time_vs_energy_log.png)

## Distribution of Average TPS by Consensus Type

![alt text](tps_distribution_log.png)
