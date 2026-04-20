# Budget Assistant - GL Account Analysis Framework

## Project Overview

**Budget Assistant** is a specialized framework for analyzing General Ledger (GL) accounts to scrub historical data and create clean baselines for budget planning. It implements domain-specific analysis skills for different GL accounts using a consistent pattern detection methodology.

## Supported GL Accounts

### GL 7560: Professional Membership Dues
- **Description**: CPA, CFA, CBV professional memberships and designations
- **Primary Driver**: Employee Headcount / Professional Designations
- **Skill File**: [GL7560_ProfessionalDues_Skill.md](docs/GL7560_ProfessionalDues_Skill.md)
- **Analysis Script**: `src/gl7560_analysis.py` (via `run.py GL7560 <filename>`)

### GL 7555: Professional Courses, Pre Designation
- **Description**: Pre-designation training, courses, and professional development
- **Primary Driver**: Employee Development / Training Programs
- **Skill File**: [GL7555_ProfessionalCourses_Skill.md](docs/GL7555_ProfessionalCourses_Skill.md)
- **Analysis Script**: `src/gl7555_analysis.py` (via `run.py GL7555 <filename>`)

---

## Directory Structure

```
GL7560/
├── claude.md                          # This file - project guide
├── README.md                          # Quick start guide
├── run.py                             # Main entry point
│
├── src/                               # Source code
│   ├── __init__.py
│   ├── analyzer.py                    # Core analysis engine
│   ├── gl7560_analysis.py             # GL 7560 specific logic
│   └── gl7555_analysis.py             # GL 7555 specific logic
│
├── docs/                              # Documentation
│   ├── GL7560_ProfessionalDues_Skill.md        # GL 7560 skill & logic
│   └── GL7555_ProfessionalCourses_Skill.md     # GL 7555 skill & logic
│
├── data/                              # Input data (sample Excel files)
│   ├── SampleTransactions.xlsx
│   └── SampleTransactions2.xlsx
│
├── output/                            # Analysis results
│   └── analysis_output.txt            # Latest analysis report
│
├── tests/                             # Test suite
│   └── gl_7560_test/
│
└── .venv/                             # Python virtual environment
    ├── Scripts/                       # Executables & pip
    ├── Lib/                           # Installed packages
    └── pyvenv.cfg                     # Environment config
```

---

## Core Analysis Logic

Both GL accounts follow the same **two-path detection framework**:

### Path A: Reversals & Corrections (KEEP)
- Keywords: `Accrual Rev`, `Reversal`, `JE Correction`, `Cancel`
- Action: Do NOT exclude (used to net entries to zero)

### Path B: Reimbursements & Paybacks (EXCLUDE)
- Keywords: `reimburse` (variants), `payback`, `recovery`, `settlement`, `claw back`
- Action: Exclude from baseline (one-time recovery events)
- **Priority**: Path B takes precedence if both patterns detected

---

## Output Metrics

Every analysis report includes:

1. **Total Actuals** - Raw sum of all transactions
2. **Exclusion List** - Path B items with confidence ratings (High/Medium/Low)
3. **Scrubbed Baseline** - Total minus Path B exclusions
4. **Future Departure Contingency** - 30% of exclusion total
5. **Adjusted Budget Baseline** - Scrubbed baseline minus contingency (recommended budget)
6. **Budget Advisory** - Narrative summary for stakeholders

---

## Quick Start

### Setup (One-time)
```powershell
# Activate virtual environment (do NOT reinstall pip)
& .\.venv\Scripts\Activate.ps1
```

### Run Analysis
```powershell
# GL 7560 - Professional Membership Dues
python run.py SampleTransactions.xlsx

# GL 7555 - Professional Courses (when implemented)
python run.py GL7555 SampleTransactions.xlsx
```

### View Results
```powershell
# Display the analysis output
Get-Content .\output\analysis_output.txt
```

---

## Development Workflow

### Adding a New GL Account Skill

1. **Create Skill Documentation**
   ```
   docs/GL{CODE}_{Name}_Skill.md
   ```
   - Define Path A & B patterns
   - Document confidence level criteria
   - Specify output requirements

2. **Implement Analysis Module**
   ```
   src/gl{code}_analysis.py
   ```
   - Inherit from `analyzer.py` base class
   - Implement account-specific pattern matching
   - Generate formatted report

3. **Update `run.py`**
   - Add GL code routing logic
   - Map to new analysis module

4. **Add Tests**
   ```
   tests/gl_{code}_test/
   ```

### Code Style & Standards

- **Python**: PEP 8 compliance via `black` formatter
- **Pandas**: Use DataFrame operations for scalability
- **Regex**: Comment complex patterns, use verbose flag when appropriate
- **Documentation**: Docstrings for all functions, inline comments for business logic
- **Error Handling**: Graceful failures with informative error messages

---

## Key Concepts

### Confidence Levels
- **High**: Explicit employee name + clear reimbursement descriptor
- **Medium**: "Reimburse" keyword present but lacks employee context
- **Low**: Generic negative entry, ambiguous description (flag for manual review)

### Contingency Buffer
- Calculated as 30% of total exclusions
- Reserves funds for expected future employee departures
- Subtracted from scrubbed baseline to yield adjusted budget

### Priority Rules
- Reimbursement patterns override reversal/correction patterns
- All negative amounts are analyzed for both Path A & B
- Exclusions only applied to Path B items

---

## Example Workflow

**Input**: Excel file with GL transactions
```
Date | Reference | Description | Amount
-----|-----------|-------------|--------
2025-02-21 | 3880652 | Mark Smith reimbursement of CPA Dues | -102.68
2025-04-01 | 3937093 | Annual CPA Practice License Renewal | +81.25
...
```

**Processing**:
1. Load transactions
2. Scan for negative amounts
3. Pattern match against Path A (reversals) and Path B (reimbursements)
4. Apply priority rule: Path B wins if both detected
5. Calculate metrics and confidence levels

**Output**: Formatted report with 6 key sections

---

## Environment Details

- **Python**: 3.11+
- **Dependencies**: pandas, openpyxl, regex
- **Virtual Environment**: `.venv/` (pre-configured, do NOT reinstall)
- **Activation**: 
  ```powershell
  & .\.venv\Scripts\Activate.ps1
  ```

---

## Support

For questions about specific GL account skills, refer to:
- `docs/GL7560_ProfessionalDues_Skill.md`
- `docs/GL7555_ProfessionalCourses_Skill.md`

For code issues or enhancements, review the implementation in `src/`.
