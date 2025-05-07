import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# Load scraped data
df = pd.read_csv('results.csv')

# Identify numeric columns (exclude non-numeric metadata)
non_numeric = ['team', 'player', 'nationality', 'position', 'age']
num_cols = [c for c in df.columns if c not in non_numeric]

# Convert numeric columns to floats
df[num_cols] = df[num_cols].apply(pd.to_numeric, errors='coerce')

# 1) Top 3 highest and lowest for each statistic
with open('top_3.txt', 'w', encoding='utf-8') as f:
    for col in num_cols:
        series = df[['player', col]].dropna()
        # Highest 3
        top3 = series.nlargest(3, col)
        # Lowest 3
        bottom3 = series.nsmallest(3, col)
        f.write(f"Statistic: {col}\n")
        f.write("Top 3:\n")
        for _, row in top3.iterrows():
            f.write(f"  {row['player']}: {row[col]}\n")
        f.write("Bottom 3:\n")
        for _, row in bottom3.iterrows():
            f.write(f"  {row['player']}: {row[col]}\n")
        f.write("\n")

# 2) Median, mean, std for each statistic: overall and per team
teams = ['all'] + sorted(df['team'].unique())
records = []
for team in teams:
    sub = df if team == 'all' else df[df['team'] == team]
    stats = {'team': team}
    for col in num_cols:
        stats[f'{col}_median'] = sub[col].median()
        stats[f'{col}_mean'] = sub[col].mean()
        stats[f'{col}_std'] = sub[col].std()
    records.append(stats)

results2 = pd.DataFrame(records).set_index('team')
results2.to_csv('results2.csv')

# 3) Plot histograms for each statistic (overall + per team)
for col in num_cols:
    # Overall league
    plt.figure()
    df[col].hist(bins=20)
    plt.title(f'Distribution of {col} (All Players)')
    plt.xlabel(col)
    plt.ylabel('Count')
    plt.tight_layout()
    plt.savefig(f'hist_all_{col}.png')
    plt.close()
    # Per-team histograms
    for team in df['team'].unique():
        subset = df[df['team'] == team]
        if subset[col].dropna().empty:
            continue
        plt.figure()
        subset[col].hist(bins=20)
        plt.title(f'{col} Distribution - {team}')
        plt.xlabel(col)
        plt.ylabel('Count')
        plt.tight_layout()
        safe_team = team.replace(' ', '').replace('/', '')
        plt.savefig(f'hist_{safe_team}_{col}.png')
        plt.close()

# 4) Identify team with highest mean for each statistic
with open('best_team_per_stat.txt', 'w') as f:
    team_means = df.groupby('team')[num_cols].mean()
    for col in num_cols:
        best_team = team_means[col].idxmax()
        f.write(f"{col}: {best_team} (mean = {team_means[col].max():.2f})\n")

# Display a snippet of results2
results2.head(5)