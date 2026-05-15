import pandas as pd

# Words that indicate a column is about a protected demographic characteristic
# (things like race, sex, age that hiring decisions legally shouldn't be based on)
protected_keywords = [
    "sex", "gender", "male", "female", "race", "ethnicity", "ethnic",
    "color", "age", "country", "nationality", "national", "origin",
    "native", "religion", "religious", "faith", "disability", "disabled",
    "marital", "married", "veteran", "military", "education", "degree",
    "language",
]

# Words that mean a candidate was successful (hired, approved, etc.)
# These are used to figure out which outcome values count as "positive"
success_keywords = [
    "yes", "hired", "accepted", "approved",
    "selected", "passed", "success", "true",
    "1", ">50", "high", "pass"
]

def detect_columns(df):
    # Scan all columns and find ones that look like demographic categories.
    # A column qualifies if:
    #   - it has fewer than 10 unique values (so it's a category, not a number like salary)
    #   - it's not the "income" column (that's the outcome, not a demographic)
    #   - its name contains one of the protected keywords above
    demographic_cols = []
    for i in df.columns:
        if df[i].nunique() < 10 and i != "income" and any(keyword in i.lower() for keyword in protected_keywords):
            demographic_cols.append(i)
    return demographic_cols

def detect_outcomes(df):
    # Find columns that represent the hiring/outcome decision.
    # We match column names exactly against known outcome-related words.
    outcome_keywords = [
        "income", "salary", "hired", "hiring", "outcome",
        "decision", "result", "status", "approved",
        "rejected", "selected", "wage", "pay","attrition"
    ]
    outcome_cols = []
    for i in df.columns:
        for keyword in outcome_keywords:
            if i.lower() == keyword:
                outcome_cols.append(i)
                break  # stop checking keywords once we matched this column
    return outcome_cols

def contains_success(value):
    # Check whether a single outcome value (e.g. ">50K", "hired") counts as a success.
    # We convert the value to lowercase string and look for any success keyword inside it.
    for keyword in success_keywords:
        if keyword in str(value).lower():
            return True
    return False

def detect_bias(df, demographic_col, outcome_col):
    # Calculate the success rate for each group within a demographic column,
    # then compare every group against the best-performing group.
    # If a group's rate is less than 80% of the best rate, we flag it as biased
    # (this is called the "80% rule" or "four-fifths rule" in employment law).

    rates = {}    # will hold { group_name: success_rate } for each group
    findings = [] # will hold the final result dicts we return

    # Get all unique values in the demographic column (e.g. ["Male", "Female"])
    x = df[demographic_col].unique()
    print(f"\n--- Analyzing bias for: {demographic_col} ---")

    for group in x:
        # Slice the dataframe to only rows belonging to this group
        group_data = df[df[demographic_col] == group]

        # From those rows, keep only the ones where the outcome counts as a success
        success_data = group_data[group_data[outcome_col].apply(contains_success)]

        if len(group_data) == 0:
            continue  # skip groups with no data to avoid division by zero

        # Success rate = how many in this group were successful / total in group
        success_rates = len(success_data) / len(group_data)
        rates[group] = success_rates

    if not rates:
        return []

    # The highest success rate among all groups — this is the benchmark
    best_rate = max(rates.values())

    if best_rate == 0:
        # No group had any successes, so we can't compute meaningful ratios
        print(f"Could not detect any successful outcomes in {demographic_col}")
        return []

    for group, rate in rates.items():
        # ratio = this group's rate as a fraction of the best group's rate
        # A ratio of 1.0 means equal to the best; 0.5 means half as likely to succeed
        ratio = rate / best_rate

        findings.append({
            "group": group,
            "rate": round(rate * 100, 2),          # success rate as a percentage
            "ratio": round(ratio * 100, 2),         # ratio as a percentage (100 = equal to best)
            "demographic_col": demographic_col,
            "bias_detected": ratio < 0.80           # True if this group is below the 80% threshold
        })

        # Print a warning immediately when a group falls below the 80% rule
        if ratio < 0.80:
            print(f"\n⚠ WARNING: {group} — Ratio: {round(ratio * 100, 2)}%")

    return findings

if __name__ == "__main__":
    # Column names for the UCI Adult dataset (the file has no header row, so we supply them)
    column_names = [
        "age", "workclass", "fnlwgt", "education", "education-num",
        "marital-status", "occupation", "relationship", "race", "sex",
        "capital-gain", "capital-loss", "hours-per-week", "native-country",
        "income"
    ]

    # Load the CSV; values are separated by ", " (comma + space), so we set sep accordingly
    df = pd.read_csv("adult.data", header=None, names=column_names, sep=", ", engine="python")

    # Strip leading/trailing whitespace from key columns (the raw file has extra spaces)
    df["sex"] = df["sex"].str.strip()
    df["income"] = df["income"].str.strip()
    df["race"] = df["race"].str.strip()

    # Auto-detect which columns are demographics and which is the outcome
    demographic_cols = detect_columns(df)
    outcome_col = detect_outcomes(df)[0]  # take the first detected outcome column

    # Run bias detection for every demographic column and collect all results
    all_findings = []
    for col in demographic_cols:
        findings = detect_bias(df, col, outcome_col)
        all_findings.extend(findings)  # flatten each list of findings into one big list

    print("\nAll findings:", all_findings)

    # Import chart and explanation modules (kept here to avoid circular imports at top)
    from charts import plot_bias_charts
    from explanations import generate_all_explanations

    # Draw bar charts showing success rates per group
    plot_bias_charts(all_findings)

    # Generate a plain-English explanation for each finding, then print them
    all_findings = generate_all_explanations(all_findings)
    for finding in all_findings:
        print(f"\n---{finding['group']}, {finding['demographic_col']}---")
        print(finding["explanation"])