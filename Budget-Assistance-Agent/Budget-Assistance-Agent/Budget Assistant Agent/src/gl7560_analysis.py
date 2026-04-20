"""
GL 7560 - Professional Membership Dues Analyzer

Specialized analyzer for Professional Membership Dues (CPA, CFA, CBV, etc.)
Inherits base logic from BaseGLAnalyzer.
"""

from .analyzer import BaseGLAnalyzer


class GL7560Analyzer(BaseGLAnalyzer):
    """
    Analyzer for GL 7560: Professional Membership Dues
    
    Detects reimbursements and reversals in professional membership and designation costs.
    """
    
    def __init__(self):
        """Initialize GL 7560 specific analyzer."""
        super().__init__(
            gl_code="7560",
            gl_description="Professional Membership Dues",
            account_driver="Employee Headcount / Professional Designations"
        )
