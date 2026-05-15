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
    findings_text = ""
    for i, finding in enumerate(all_findings):
        findings_text += f"""
Finding {i+1}:
- Demographic category: {finding['demographic_col']}
- Group: {finding['group']}
- Success rate: {finding['rate']}%
- Ratio to best-performing group: {finding['ratio']}%
- Bias detected: {finding['bias_detected']}
"""

    prompt = f"""You are an HR bias analyst. A hiring dataset was analyzed using the 80% rule for disparate impact.

Here are all the findings:
{findings_text}

For EACH finding, write a 1-2 sentence plain English explanation for a non-technical HR manager. Be factual, not dramatic. No jargon.

Format your response exactly like this:
FINDING 1: Your explanation here.
FINDING 2: Your explanation here.
And so on for each finding."""

    response = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=1500,
        messages=[
            {"role": "user", "content": prompt}
        ]
    )

    response_text = response.content[0].text
    lines = response_text.strip().split("\n")

    finding_index = 0
    for line in lines:
        line = line.strip()
        if line.startswith("FINDING") and ":" in line:
            explanation = line.split(":", 1)[1].strip()
            if finding_index < len(all_findings):
                all_findings[finding_index]["explanation"] = explanation
                finding_index += 1

    for finding in all_findings:
        if "explanation" not in finding:
            if finding["bias_detected"]:
                finding["explanation"] = f"{finding['group']} has a success rate of {finding['rate']}%, which is {finding['ratio']}% of the best-performing group. This falls below the 80% threshold and warrants investigation."
            else:
                finding["explanation"] = f"{finding['group']} has a success rate of {finding['rate']}%, which is within acceptable range. No bias detected."

    return all_findings