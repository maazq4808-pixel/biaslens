import os
from dotenv import load_dotenv
from anthropic import Anthropic

load_dotenv()

# Initialize the Anthropic client using the API key stored in .env
client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))


def generate_explanation(finding):
    # Pull the relevant fields out of the finding dict for use in the prompt
    col = finding["demographic_col"]
    group = finding["group"]
    rate = finding["rate"]
    ratio = finding["ratio"]
    bias = finding["bias_detected"]

    # Build a prompt that gives the model all the context it needs.
    # We ask for plain English because the output is meant for non-technical HR managers,
    # not data analysts — so no statistics jargon.
    prompt = f"""You are an HR bias analyst. A hiring dataset was analyzed using the 80% rule for disparate impact.

Here is one finding:
- Demographic category: {col}
- Group: {group}
- Success rate: {rate}%
- Ratio to best-performing group: {ratio}%
- Bias detected: {bias}

Write a 2-3 sentence plain English explanation of this finding for a non-technical HR manager. No jargon, no statistics terminology. If bias was detected, tell them be factual, dont be too dramatic, give a short fctual answer. If no bias was detected, keep it brief and reassuring."""

    # Send the prompt to Claude and limit the response to 200 tokens,
    # which is enough for a short 2-3 sentence explanation
    response = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=200,
        messages=[
            {"role": "user", "content": prompt}
        ])

    # The response is a list of content blocks; we want the text of the first (and only) one
    return response.content[0].text

def generate_all_explanations(all_findings):
    # Loop over every finding and attach a plain-English explanation to it.
    # We modify the dicts in-place by adding an "explanation" key,
    # then return the same list so callers get back the enriched findings.
    for i in all_findings:
        explanation = generate_explanation(i)
        i["explanation"] = explanation

    return all_findings


if __name__ == "__main__":
    test_findings = [
        {
            "group": "Female",
            "rate": 10.95,
            "ratio": 33.12,
            "demographic_col": "sex",
            "bias_detected": True
        },
        {
            "group": "Male",
            "rate": 30.57,
            "ratio": 100.0,
            "demographic_col": "sex",
            "bias_detected": False
        }
    ]

    results = generate_all_explanations(test_findings)

    for finding in results:
        print(f"\n--- {finding['group']} ---")
        print(finding["explanation"])
