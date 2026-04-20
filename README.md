# Budget Assistant Agent

**Multi-GL Budget Guidance** – Analyze 115+ GL accounts to generate budget recommendations for the new fiscal year.

Budget Assistant analyzes historical GL transactions to distinguish one-time events (reimbursements, recoveries) from recurring costs, generating **interactive HTML reports** with budget recommendations across all GL accounts.

## Quick Start

### Install
```bash
pip install -r requirements.txt
```

### Run Analysis
```bash
# Analyze GL 7560 (Professional Membership Dues)
python run.py GL7560 data/SampleTransactions.xlsx

# View HTML report
open output/gl_7560_analysis.html
```

### List Available GLs
```bash
python run.py --list-gls
```

## Supported GL Accounts

| GL Code | Description | Cost Driver |
|---------|-------------|-------------|
| **7560** | Professional Membership Dues | Employee Headcount |
| **7555** | Professional Courses & Training | Employee Development |
| **...** | (115+ GL accounts) | Various |

## How It Works

The agent uses **two-path pattern detection**:

- **Path A (Keep)**: Reversals, corrections, accrual reversals
- **Path B (Exclude)**: Reimbursements, refunds, recoveries (one-time events)

**Recommended Budget** = Total Actuals - Exclusions - (30% contingency for departures)

## Output

Interactive HTML reports (`output/gl_XXXX_analysis.html`) include:

- **Key Metrics**: Total actuals, exclusions, scrubbed baseline, adjusted budget
- **Exclusion Table**: Details of excluded items with confidence levels
- **Budget Recommendation**: Suggested budget for next fiscal year
- **Contingency Analysis**: Reserve calculation for expected departures

## Project Structure

```
src/               – Analysis engine, GL registry, HTML exporter
gl_rules/          – GL-specific rules (JSON) - scales to 115+ accounts
.claude/skills/    – Claude Code skill definitions
data/              – Sample input files
output/            – Generated HTML reports
```

## Token Efficiency

GL rules are stored as **JSON** (not code), enabling the agent to:
- Load only relevant GL rules when analyzing
- Scale to 115+ GL accounts without token bloat
- Keep agent context focused and responsive

## Documentation

- **[claude.md](claude.md)** – Architecture, adding new GLs, code standards
- **[run.py](run.py)** – Agent entry point and routing logic

