"""
GL 7555 - Professional Courses, Pre Designation Analyzer

Specialized analyzer for Professional Courses and Pre-Designation Training.
Inherits base logic from BaseGLAnalyzer.
"""

from .analyzer import BaseGLAnalyzer


class GL7555Analyzer(BaseGLAnalyzer):
    """
    Analyzer for GL 7555: Professional Courses, Pre Designation
    
    Detects reimbursements and reversals in professional training and course costs.
    """
    
    def __init__(self):
        """Initialize GL 7555 specific analyzer."""
        super().__init__(
            gl_code="7555",
            gl_description="Professional Courses, Pre Designation",
            account_driver="Employee Development / Training Programs"
        )
