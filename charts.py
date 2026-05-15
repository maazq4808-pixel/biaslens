import matplotlib.pyplot as plt

def plot_charts(x, y, bias_flags, threshold, col_name):
    # Red bars indicate biased groups, green indicates unbiased
    plt.figure(figsize=(10, 6))
    bars = plt.bar(x, y, color=["red" if flag else "green" for flag in bias_flags])
    # Threshold line marks the 80% of max rate cutoff
    plt.axhline(y=threshold, color='grey', linestyle='--', label='Bias Threshold')
    plt.xlabel(col_name.title())
    plt.ylabel("Success Rate (%)")
    plt.title(f"Bias Detection for {col_name.title()}")
    plt.legend()
    plt.xticks(rotation=45, ha="right")
    plt.tight_layout()
    plt.savefig(f"chart_{col_name}.png")
    plt.show()

def plot_bias_charts(all_findings):
    # Group findings by demographic column and plot one chart per column
    demographic_groups = set(f["demographic_col"] for f in all_findings)
    for cols in demographic_groups:
        group_findings = [f for f in all_findings if f["demographic_col"] == cols]
        groups = [f["group"] for f in group_findings]
        rates = [f["rate"] for f in group_findings]
        bias_flags = [f["bias_detected"] for f in group_findings]
        # Bias threshold: any group below 80% of the top rate is flagged
        threshold = max(rates) * 0.80
        plot_charts(groups, rates, bias_flags, threshold, cols)
