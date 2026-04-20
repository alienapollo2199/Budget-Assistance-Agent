"""Budget Assistant - GL Account Analysis Framework

A specialized framework for analyzing General Ledger accounts to create clean baselines for budget planning.
Supports GL 7560 (Professional Membership Dues) and GL 7555 (Professional Courses, Pre Designation).

Project: Budget Assistant
"""

__version__ = "1.0.0"
__author__ = "GL Analysis Team"

from .analyzer import BaseGLAnalyzer

__all__ = ["BaseGLAnalyzer"]
