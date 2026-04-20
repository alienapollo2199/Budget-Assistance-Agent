# Budget Assistant

**Professional GL Account Analysis** – Scrub historical ledger data to create clean budgeting baselines.

*Budget Assistant* analyzes General Ledger accounts to identify exclusions and reimbursements, generating clean baselines for next year's budget planning.

## Supported GL Accounts

| GL Code | Description | Driver |
|---------|-------------|--------|
| **7560** | Professional Membership Dues | Headcount / Designations |
| **7555** | Professional Courses, Pre Designation | Employee Development |

## Quick Start

### 1. Activate Environment
```powershell
& .\.venv\Scripts\Activate.ps1
```

### 2. Run Analysis
```powershell
python run.py SampleTransactions.xlsx
```

### 3. View Results
```powershell
Get-Content .\output\analysis_output.txt
```

## Key Metrics

Every analysis report provides:
- **Total Actuals** – Raw sum of all transactions
- **Scrubbed Baseline** – After removing reimbursements (Path B)  
- **Exclusion List** – Items removed with confidence ratings
- **30% Contingency Buffer** – Reserve for expected departures
- **Adjusted Budget Baseline** – Final recommended budget

## Documentation

- **[claude.md](claude.md)** – Full project guide, architecture, and development workflow
- **[docs/GL7560_ProfessionalDues_Skill.md](docs/GL7560_ProfessionalDues_Skill.md)** – GL 7560 analysis logic
- **[docs/GL7555_ProfessionalCourses_Skill.md](docs/GL7555_ProfessionalCourses_Skill.md)** – GL 7555 analysis logic

## Analysis Workflow

Both accounts implement a **two-path detection framework**:

| Path | Type | Keywords | Action |
|------|------|----------|--------|
| **A** | Reversals | Reversal, JE Correction, Accrual Rev, Cancel | KEEP in baseline |
| **B** | Reimbursements | Reimburse, Payback, Recovery, Settlement | EXCLUDE from baseline |

Priority: If both patterns found, **Path B takes precedence**.

## Directory Structure

```
src/                 – Core analysis modules (analyzer.py, gl7560/7555_analysis.py)
docs/                – Skill documentation (GL7560, GL7555)
data/                – Input Excel files
output/              – Analysis reports
tests/               – Test suite
```

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines on adding new GL accounts or extending existing skills.

