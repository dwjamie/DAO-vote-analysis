import json
import pandas as pd
import matplotlib.pyplot as plt

# Load the JSON data from a file
with open('data/optimism_analysis.json', 'r') as file:
    voting_data = json.load(file)


print(len([voter for voter in voting_data if voting_data[voter]['vote_count'] > 10]))

# Prepare data for analysis
addresses = []
voting_powers = []
vote_counts = []
win_rates = []

for address, info in voting_data.items():
    addresses.append(address)
    voting_powers.append(info['total_vp'])
    vote_counts.append(info['vote_count'])
    win_rates.append(info['win_rate'])

# Convert to DataFrame for easier plotting
df = pd.DataFrame({
    'Address': addresses,
    'Voting Power': voting_powers,
    'Vote Count': vote_counts,
    'Win Rate': win_rates
})

# 1. Voting Power Distribution
plt.figure(figsize=(10, 6))
plt.hist(df['Voting Power'], bins=30, color='blue', alpha=0.7)
plt.title('Voting Power Distribution')
plt.xlabel('Voting Power')
plt.ylabel('Frequency')
plt.grid(True)
plt.show()

# 2. Participation Patterns
plt.figure(figsize=(10, 6))
plt.scatter(df['Vote Count'], df['Voting Power'], color='green')
plt.title('Participation vs. Voting Power')
plt.xlabel('Vote Count')
plt.ylabel('Voting Power')
plt.grid(True)
plt.show()

# 3. Proposal Win Rates
plt.figure(figsize=(10, 6))
plt.scatter(df['Win Rate'], df['Voting Power'], color='red')
plt.title('Win Rate vs. Voting Power')
plt.xlabel('Win Rate')
plt.ylabel('Voting Power')
plt.grid(True)
plt.show()
