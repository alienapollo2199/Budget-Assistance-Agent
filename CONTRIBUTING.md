# Contributing Guidelines

## Budget Assistant - Adding a New GL Account Skill

Budget Assistant uses a modular, template-driven approach to support multiple GL accounts. Follow these steps to add a new GL account analysis.

### Overview

Each GL account implementation consists of:
1. **Skill Documentation** (`docs/GL{CODE}_{Name}_Skill.md`)
2. **Analyzer Module** (`src/gl{code}_analysis.py`)
3. **Integration** in `run.py` for routing

---

## Step 1: Create Skill Documentation

Create a new file: `docs/GL{CODE}_{Description}_Skill.md`

**Template structure:**
```markdown
# Role: [Description] Analyst (GL {CODE})

## GL Account Metadata
- **GL Code**: {CODE}
- **Description**: {Full description}
- **Primary Driver**: {Cost driver, e.g., "Headcount", "Projects", "Departments"}

## Analysis Logic (The "Skill")

### 1. Detection of Negative Amounts
[Explain Path A and Path B for this account]

#### Path A: Potential Reverse Entries (KEEP)
- **Pattern Match**: [Keywords specific to reversals for this GL]
- **Action**: Keep in calculation

#### Path B: Reimbursements & Paybacks (EXCLUDE)
- **Pattern Match**: [Keywords specific to reimbursements for this GL]
- **Action**: Exclude from baseline

### 2. Future Departure Contingency (30% of Exclusions)
[Explain how the 30% buffer applies to this GL account]

### 3. Exclusion Confidence Levels
[Custom confidence criteria for this GL account]

### 4. Output Requirements
[Specific outputs or variations for this GL]

### 5. Setup Instructions
[Virtual environment and run instructions]
```

**Reference existing skills:**
- [GL7560_ProfessionalDues_Skill.md](docs/GL7560_ProfessionalDues_Skill.md)
- [GL7555_ProfessionalCourses_Skill.md](docs/GL7555_ProfessionalCourses_Skill.md)

---

## Step 2: Create Analyzer Module

Create a new file: `src/gl{code}_analysis.py`

**Minimal template:**
```python
"""
GL {CODE} - {Description} Analyzer

Specialized analyzer for {full description}.
Inherits base logic from BaseGLAnalyzer.
"""

from .analyzer import BaseGLAnalyzer


class GL{CODE}Analyzer(BaseGLAnalyzer):
    """Analyzer for GL {CODE}: {Description}"""
    
    def __init__(self):
        super().__init__(
            gl_code="{CODE}",
            gl_description="{Description}",
            account_driver="{Cost driver}"
        )
```

**If custom pattern matching needed:**
```python
class GL{CODE}Analyzer(BaseGLAnalyzer):
    def __init__(self):
        super().__init__(...)
        # Add custom keywords specific to this GL
        self.reversal_keywords.extend(['custom keyword 1', 'custom keyword 2'])
        self.reimbursement_keywords.extend(['custom keyword 3'])
```

**Reference existing analyzers:**
- [src/gl7560_analysis.py](src/gl7560_analysis.py)
- [src/gl7555_analysis.py](src/gl7555_analysis.py)

---

## Step 3: Update run.py

Add routing logic to `run.py`:

```python
from src.gl{code}_analysis import GL{CODE}Analyzer

def analyze_gl{code}_dues(df):
    """Analyze GL {CODE} transactions."""
    analyzer = GL{CODE}Analyzer()
    analysis = analyzer.analyze(df)
    print(analyzer.generate_report(analysis))
    return analysis

# In main():
if sys.argv[1] == "GL{CODE}":
    gl{code}_dues(df)
```

---

## Step 4: Add Tests

Create test files in `tests/gl_{code}_test/`:

```python
# tests/gl_{code}_test/test_analysis.py
import unittest
import pandas as pd
from src.gl{code}_analysis import GL{CODE}Analyzer

class TestGL{CODE}Analyzer(unittest.TestCase):
    def setUp(self):
        self.analyzer = GL{CODE}Analyzer()
    
    def test_path_b_exclusion(self):
        """Test reimbursement detection."""
        df = pd.DataFrame({
            'Voucher Date': ['2025-01-01'],
            'Voucher Desc': ['Employee reimbursement of course fee'],
            'Amount': [-500.00]
        })
        result = self.analyzer.analyze(df)
        self.assertEqual(len(result['exclusions']), 1)
    
    def test_path_a_kept(self):
        """Test reversal entry kept."""
        df = pd.DataFrame({
            'Voucher Date': ['2025-01-01'],
            'Voucher Desc': ['JE Correction - remove duplicate'],
            'Amount': [-100.00]
        })
        result = self.analyzer.analyze(df)
        self.assertEqual(len(result['kept_entries']), 1)
```

---

## Step 5: Update Documentation

1. Update `claude.md` to include new GL code in supported accounts list
2. Update `README.md` to add to accounts table
3. Add GL code to `src/__init__.py` exports (if applicable)

---

## Code Quality Standards

### Python Style
- Follow **PEP 8**
- Use type hints for function arguments and returns
- Document all classes and functions with docstrings
- Keep functions focused and under 50 lines when possible

### Pattern Matching
- Use regex for complex patterns
- Add comments explaining non-obvious patterns
- Test edge cases (e.g., mixed case, typos)

### Error Handling
```python
try:
    df = pd.read_excel(filepath)
except FileNotFoundError:
    print(f"[ERROR] File not found: {filepath}")
    sys.exit(1)
except Exception as e:
    print(f"[ERROR] Error processing file: {str(e)}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
```

### Documentation
- Include docstrings with Args, Returns, and Raises sections
- Add inline comments for business logic specific to the GL account
- Keep skill.md updated with any logic changes

---

## Testing Checklist

- [ ] Unit tests pass for new GL analyzer
- [ ] Sample data processes without errors
- [ ] Report generates with correct calculations
- [ ] Confidence levels assigned correctly
- [ ] 30% contingency calculation verified
- [ ] Exclusion list matches expected results

---

## Naming Conventions

| Item | Format | Example |
|------|--------|---------|
| GL Code | GL{4-digit} | GL7560 |
| File (analysis) | gl{code}_analysis.py | gl7560_analysis.py |
| File (skill) | GL{code}_{Name}_Skill.md | GL7560_ProfessionalDues_Skill.md |
| Class | GL{Code}Analyzer | GL7560Analyzer |
| Test folder | gl_{code}_test | gl_7560_test |
| Test file | test_analysis.py | test_analysis.py |

---

## Questions?

Refer to:
- **[claude.md](claude.md)** – Full project architecture
- **Existing skills** in `docs/` folder
- **Base analyzer** in `src/analyzer.py`
