import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from bias_detection import detect_columns, detect_outcomes, detect_bias
from explanations import generate_all_explanations
from report import generate_report

st.title("Hiring Bias Detector")
st.write("This tool helps HR professionals detect hidden bias in their hiring data. Simply upload a CSV file containing your hiring records and the tool will identify any demographic groups that may be facing unfair treatment in your hiring process.")
st.write("The tool uses the 80% rule for disparate impact, which compares the success rates of different demographic groups. If a group's success rate is less than 80% of the best-performing group, it may indicate potential bias that warrants further investigation.")

uploaded_file = st.file_uploader("upload your dataset here(csv)", type=["csv", "xlsx", "xls", "data"])

if uploaded_file is not None:
    # Bug fix: the uploader accepts xlsx/xls but pd.read_csv would crash on those formats.
    # Read the file with the correct parser based on the file extension.
    filename = uploaded_file.name.lower()
    if filename.endswith(".xlsx") or filename.endswith(".xls"):
        df = pd.read_excel(uploaded_file)
    else:
        df = pd.read_csv(uploaded_file)

    st.write("Dataset preview:")
    st.dataframe(df.head())

    # Auto-detect which columns contain demographic categories and which is the outcome
    demographic_cols = detect_columns(df)
    outcomes = detect_outcomes(df)

    if len(outcomes) == 0:
        st.error("Could not detect an outcome column. Make sure your dataset has a column named something like 'income', 'hired', 'approved', or 'outcome'.")
    else:
        outcome_col = outcomes[0]

        # Run the 80% rule bias check for every detected demographic column
        all_findings = []
        for col in demographic_cols:
            findings = detect_bias(df, col, outcome_col)
            all_findings.extend(findings)

        st.subheader("Bias Charts")

        # Draw one bar chart per demographic column.
        # Red bars = biased groups (below 80% threshold), green = unbiased.
        for col in demographic_cols:
            # Collect results for just this demographic column
            group_findings = [f for f in all_findings if f["demographic_col"] == col]  # Bug fix: was f["demographic_cols"] (extra 's')

            if not group_findings:
                continue

            groups = [f["group"] for f in group_findings]
            rates = [f["rate"] for f in group_findings]
            bias_flags = [f["bias_detected"] for f in group_findings]

            # 80% of the best rate is the cutoff; groups below this line are flagged
            threshold = max(rates) * 0.80

            fig, ax = plt.subplots(figsize=(10, 6))
            ax.bar(groups, rates, color=["red" if flag else "green" for flag in bias_flags])
            ax.axhline(y=threshold, color="grey", linestyle="--", label="Bias Threshold (80% rule)")
            ax.set_xlabel(col.title())
            ax.set_ylabel("Success Rate (%)")
            ax.set_title(f"Bias Detection for {col.title()}")
            ax.legend()
            plt.xticks(rotation=45, ha="right")
            plt.tight_layout()

            fig.savefig(f"chart_{col}.png", bbox_inches="tight")
            st.pyplot(fig)
            plt.close(fig)

        all_findings = generate_all_explanations(all_findings)
        for finding in all_findings:
            st.write(f"**{finding['group']} ({finding['demographic_col']})**")
            st.write(finding["explanation"])

        generate_report(all_findings)
        st.download_button(
            label="Download PDF Report",
            data=open("report.pdf", "rb"),
            file_name="BiasLens_Report.pdf",
            mime="application/pdf",
        )