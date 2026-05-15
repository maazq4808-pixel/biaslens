# BiasLens — Hiring Bias Detection Tool

A web-based tool that helps HR professionals detect hidden bias in their hiring data. Upload any CSV or Excel dataset and BiasLens will automatically identify demographic groups being unfairly treated using the legal 80% rule for disparate impact.

## What It Does

- Accepts CSV and Excel file uploads through a browser interface
- Auto-detects demographic columns (gender, race, marital status, education)
- Auto-detects outcome columns (hired, approved, selected)
- Calculates success rates for each demographic group
- Flags groups falling below the 80% disparate impact threshold
- Generates AI-powered plain-English explanations using the Anthropic Claude API
- Displays interactive bar charts showing bias visually
- Produces a downloadable PDF report with all findings

## Tech Stack

- Python
- Pandas (data analysis)
- Matplotlib (charts)
- Streamlit (web frontend)
- Anthropic Claude API (AI explanations)
- FPDF (PDF report generation)

## How To Run

1. Clone this repo: `git clone https://github.com/maazq4808-pixel/biaslens.git`
2. Install dependencies: `pip install pandas matplotlib streamlit anthropic python-dotenv fpdf`
3. Create a `.env` file with your Anthropic API key: `ANTHROPIC_API_KEY=your-key-here`
4. Run the app: `streamlit run app.py`
5. Upload a CSV or Excel file with hiring data and view the results

## How It Works

BiasLens uses the 80% rule (also known as the four-fifths rule) for disparate impact analysis. For each demographic category, it compares every group's success rate to the best-performing group. If any group's rate falls below 80% of the best group's rate, it flags potential bias.

## Project Structure

- `app.py` — Streamlit web frontend
- `bias_detection.py` — Core bias detection logic
- `charts.py` — Matplotlib chart generation
- `explanations.py` — AI-powered explanation generator using Claude API
- `report.py` — PDF report builder

## Author

Built by Maaz as a portfolio project — University of Southern Mississippi, Computer Science