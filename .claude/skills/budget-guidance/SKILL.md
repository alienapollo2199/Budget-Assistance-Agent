---
name: budget-guidance
description: Generate budget guidance reports for GL accounts. Analyzes historical transactions to identify one-time events vs. recurring costs, then outputs HTML budget recommendations for the new fiscal year.
argument-hint: "[GL_CODE] [data_file.xlsx]"
disable-model-invocation: true
allowed-tools: Bash(python *)
---

# Budget Guidance Generator

Analyze General Ledger accounts and generate HTML budget recommendations for the new fiscal year.

## Supported GL Accounts

- **GL 7560**: Professional Membership Dues
- **GL 7555**: Professional Courses & Pre-Designation Training
- **(115+ GL accounts total)**

## How It Works

The analysis uses **two-path detection**:

- **Path A (Keep)**: Reversals, corrections, accrual reversals
- **Path B (Exclude)**: Reimbursements, refunds, recoveries (one-time events)

Budget baseline = Actuals - Path B exclusions - (30% contingency for departures)

## Usage

```bash
# Analyze GL 7560 with transaction data
python run.py GL7560 data/SampleTransactions.xlsx

# List all available GL accounts
python run.py --list-gls

# View generated report
open output/gl_7560_analysis.html
```

## Output

HTML report with:
- **Key metrics**: Total actuals, exclusions, scrubbed baseline, adjusted budget
- **Exclusion table**: Detailed list of excluded items with confidence ratings
- **Budget recommendation**: Recommended budget for next fiscal year
- **Contingency analysis**: Reserve amount for expected employee departures

## Adding a New GL Account

1. Create rule file: `gl_rules/gl_XXXX.json`
2. Define patterns for reversals (Path A) and reimbursements (Path B)
3. Run analysis: `python run.py GLXXXX data/your_file.xlsx`

Example rule file:
```json
{
  "code": "XXXX",
  "name": "Account Name",
  "path_a": { "keywords": ["reversal", "correction"] },
  "path_b": { "keywords": ["reimburse", "refund"] },
  "contingency_buffer_pct": 0.30
}
```

## Confidence Levels

- **HIGH**: Clear reimbursement keyword + employee name
- **MEDIUM**: Reimbursement keyword, missing employee context
- **LOW**: Generic entry, ambiguous (flag for review)

## For 115+ GL Accounts

GL rules are stored as JSON (minimal token usage). The agent loads only the relevant GL definition when analyzing, scaling efficiently to 115 × 124 BU combinations.

