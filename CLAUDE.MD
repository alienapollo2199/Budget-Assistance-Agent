# Budget Assistant Agent

Multi-GL budget guidance system: analyze 115+ GL accounts across 124 BUs to generate HTML budget recommendations for the new fiscal year.

## Overview

Uses **two-path pattern detection** to distinguish one-time events (reimbursements, recoveries) from recurring costs:
- **Path A (Keep)**: Reversals, corrections, accrual reversals → KEEP in baseline
- **Path B (Exclude)**: Reimbursements, refunds, paybacks → EXCLUDE from baseline (non-recurring)

**Recommended Budget** = Total Actuals − Exclusions − (30% contingency for departures)

## Quick Start

```bash
pip install -r requirements.txt

# Analyze GL 7560
python run.py GL7560 data/SampleTransactions.xlsx

# List all enabled GLs
python run.py --list-gls

# Open generated HTML report
open output/gl_7560_analysis.html
```

## Directory Structure

```
├── claude.md                    # This file
├── README.md                    # User guide
├── run.py                       # Entry point
├── src/
│   ├── analyzer.py              # Core analysis engine
│   ├── gl_registry.py           # Load GL rules from JSON
│   └── html_exporter.py         # Generate HTML reports
├── gl_rules/                    # GL definitions (JSON)
│   ├── gl_7560.json
│   ├── gl_7555.json
│   └── ...                      # (115 GLs total)
├── data/
│   └── SampleTransactions.xlsx  # Sample input
├── output/                      # Generated HTML reports
└── .claude/
    └── skills/budget-guidance/  # Claude Code skill
```

## How It Works

### GL Rules (JSON)

Define each GL's analysis rules in `gl_rules/gl_XXXX.json`:

```json
{
  "code": "XXXX",
  "name": "GL Account Name",
  "cost_driver": "What drives costs",
  "path_a": {
    "keywords": ["reversal", "correction"],
    "action": "KEEP"
  },
  "path_b": {
    "keywords": ["reimburse", "refund"],
    "action": "EXCLUDE"
  },
  "confidence_criteria": {
    "HIGH": "Clear keyword + employee name",
    "MEDIUM": "Keyword present, missing context",
    "LOW": "Generic entry, ambiguous"
  },
  "contingency_buffer_pct": 0.30,
  "enabled": true
}
```

### Analysis Process

1. Load GL rules from JSON (only relevant GL loads)
2. Read Excel file with columns: Voucher Date, Voucher Desc, Amount
3. Identify negative amounts (Path A/B candidates)
4. Pattern match against keywords/regex
5. Apply priority: Path B takes precedence if both match
6. Calculate metrics: total, exclusions, contingency, adjusted budget
7. Generate interactive HTML report

### HTML Output

Each report includes:
- **Key Metrics**: Total actuals, exclusions, scrubbed baseline, adjusted budget
- **Exclusion Table**: Detailed list with confidence ratings (High/Medium/Low)
- **Budget Recommendation**: Suggested budget for next fiscal year
- **Contingency Analysis**: Reserve for expected departures

## Adding a New GL (Scaling to 115+)

### Simple: Add JSON rule file (2 minutes)

```bash
cat > gl_rules/gl_XXXX.json << 'EOF'
{
  "code": "XXXX",
  "name": "Your GL Name",
  "path_a": { "keywords": ["reversal", ...] },
  "path_b": { "keywords": ["reimburse", ...] },
  "contingency_buffer_pct": 0.30
}
EOF
```

Done. `gl_registry.py` auto-loads it, and `run.py` can analyze immediately.

### Advanced: Custom analyzer (if GL needs special logic)

1. Create `src/glxxxx_analyzer.py`
2. Inherit from `BaseGLAnalyzer`
3. Override `analyze()` method
4. Update `run.py` routing

## Code Standards

- **Python**: PEP 8, keep functions focused
- **No comments** unless logic is non-obvious
- **JSON rules**: Define GL logic here, not in code
- **Error handling**: Graceful failures with clear messages

## Key Modules

| Module | Purpose |
|--------|---------|
| `analyzer.py` | Core pattern matching (don't modify unless needed) |
| `gl_registry.py` | Load GL rules from JSON files |
| `html_exporter.py` | Generate interactive HTML reports |
| `run.py` | Agent entry point, GL routing |

## Confidence Levels

- **HIGH**: Explicit keyword + employee name (high confidence exclusion)
- **MEDIUM**: Keyword present, missing employee context (medium confidence)
- **LOW**: Generic entry, ambiguous description (flag for manual review)

## Dependencies

- Python 3.11+
- pandas, openpyxl, regex (see `requirements.txt`)
