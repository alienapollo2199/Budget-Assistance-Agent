"""
Budget Assistant - Base GL Account Analyzer

Core analysis engine for budget baseline scrubbing.
Implements common logic for negative amount detection, path categorization,
and report generation across all GL account skills.
"""

import pandas as pd
import re
from datetime import datetime


class BaseGLAnalyzer:
    """
    Base analyzer for GL accounts implementing the two-path detection framework.
    
    Path A: Reversals and corrections (KEEP in baseline)
    Path B: Reimbursements and paybacks (EXCLUDE from baseline)
    """
    
    def __init__(self, gl_code, gl_description, account_driver):
        """
        Initialize analyzer with GL account metadata.
        
        Args:
            gl_code (str): GL account code (e.g., '7560')
            gl_description (str): GL account description
            account_driver (str): Primary cost driver (e.g., 'Employee Headcount')
        """
        self.gl_code = gl_code
        self.gl_description = gl_description
        self.account_driver = account_driver
        
        # Define keywords for pattern detection
        self.reversal_keywords = ['accrual rev', 'reversal', 'je correction', 'cancel', 'correction']
        self.reimbursement_keywords = ['payback', 'recovery', 'settlement', 'claw back']
        
        # Regex pattern for flexible "reimburse" variants
        self.reimburse_pattern = re.compile(r're[i]?mbu[r]?s[e]?m?ent?', re.IGNORECASE)
        
    def analyze(self, df):
        """
        Analyze GL transactions and categorize into Path A and Path B.
        
        Args:
            df (pd.DataFrame): Transaction data with columns 'Amount' and 'Voucher Desc'
            
        Returns:
            dict: Analysis results including totals, exclusions, and baseline calculations
        """
        analysis = {
            'total_actuals': 0,
            'exclusions': [],
            'kept_entries': [],
            'scrubbed_baseline': 0,
            'contingency_buffer': 0,
            'adjusted_baseline': 0,
            'transactions': df.copy()
        }
        
        # Calculate total actuals
        total_actuals = df['Amount'].sum()
        analysis['total_actuals'] = total_actuals
        
        # Process each transaction
        for idx, row in df.iterrows():
            amount = row['Amount']
            description = str(row['Voucher Desc']).lower() if pd.notna(row['Voucher Desc']) else ""
            date = row['Voucher Date']
            
            # Only analyze negative amounts (credits)
            if amount < 0:
                # Check both Path A and Path B patterns
                is_reversal = any(keyword in description for keyword in self.reversal_keywords)
                is_reimbursement = (self.reimburse_pattern.search(description) is not None or 
                                   any(keyword in description for keyword in self.reimbursement_keywords))
                
                # Priority rule: reimbursement wins if both patterns present
                if is_reimbursement:
                    # Path B: EXCLUDE this entry
                    confidence = self._get_confidence_level(description)
                    analysis['exclusions'].append({
                        'Date': date,
                        'Amount': amount,
                        'Description': row['Voucher Desc'],
                        'Reason': 'Reimbursement / One-Time Recovery',
                        'Confidence': confidence
                    })
                elif is_reversal:
                    # Path A: KEEP this entry
                    analysis['kept_entries'].append({
                        'Date': date,
                        'Amount': amount,
                        'Description': row['Voucher Desc'],
                        'Path': 'A (Keep)',
                        'Reason': 'Reversal/Correction Entry'
                    })
        
        # Calculate scrubbed baseline and contingency
        excluded_total = sum(exc['Amount'] for exc in analysis['exclusions'])
        analysis['scrubbed_baseline'] = total_actuals - excluded_total
        analysis['contingency_buffer'] = abs(excluded_total) * 0.30
        analysis['adjusted_baseline'] = analysis['scrubbed_baseline'] - analysis['contingency_buffer']
        
        return analysis
    
    def _get_confidence_level(self, description):
        """
        Determine confidence level for Path B exclusion.
        
        Args:
            description (str): Transaction description (lowercase)
            
        Returns:
            str: Confidence level ('High', 'Medium', or 'Low')
        """
        if 'employee payback' in description or ('reimbursement' in description and '-' in description):
            return 'High'
        elif 'reimburse' in description:
            return 'Medium'
        else:
            return 'Low'
    
    def generate_report(self, analysis):
        """
        Generate formatted analysis report.
        
        Args:
            analysis (dict): Analysis results from analyze() method
            
        Returns:
            str: Formatted report text
        """
        report = []
        report.append("\n" + "="*80)
        report.append(f"GL {self.gl_code} - {self.gl_description.upper()} ANALYSIS REPORT")
        report.append("="*80)
        
        # Section 1: Total Actuals
        report.append(f"\n1. TOTAL ACTUALS (Raw Sum of All Transactions):")
        report.append(f"   ${analysis['total_actuals']:,.2f}")
        
        # Section 2: Exclusion List
        report.append(f"\n2. EXCLUSION LIST - PATH B (One-Time Recoveries to EXCLUDE):")
        report.append(f"   Count: {len(analysis['exclusions'])} items")
        
        if analysis['exclusions']:
            exclusions_df = pd.DataFrame(analysis['exclusions'])
            report.append("\n" + exclusions_df.to_string(index=False))
            excluded_total = sum(exc['Amount'] for exc in analysis['exclusions'])
            report.append(f"\n   Total Excluded: ${excluded_total:,.2f}")
        else:
            report.append("   No exclusions identified.")
        
        # Section 3: Kept Entries (if any)
        if analysis['kept_entries']:
            report.append(f"\n3. KEPT ENTRIES - PATH A (Reversals/Corrections to KEEP):")
            report.append(f"   Count: {len(analysis['kept_entries'])} items")
            kept_df = pd.DataFrame(analysis['kept_entries'])
            report.append("\n" + kept_df.to_string(index=False))
        
        # Section 4: Scrubbed Baseline
        report.append(f"\n4. SCRUBBED BASELINE (After Excluding One-Time Recoveries):")
        report.append(f"   ${analysis['scrubbed_baseline']:,.2f}")
        
        # Section 5: Future Departure Contingency
        report.append(f"\n5. FUTURE DEPARTURE CONTINGENCY (30% of Exclusions Buffer):")
        report.append(f"   ${analysis['contingency_buffer']:,.2f}")
        report.append(f"   (Reserved for expected employee departures next year)")
        
        # Section 6: Adjusted Budget Baseline
        report.append(f"\n6. ADJUSTED BUDGET BASELINE (For Next Year Budget):")
        report.append(f"   ${analysis['adjusted_baseline']:,.2f}")
        report.append(f"   (Recommended budget amount)")
        
        # Section 7: Budget Advisory
        if analysis['exclusions']:
            excluded_total = sum(exc['Amount'] for exc in analysis['exclusions'])
            report.append(f"\n7. BUDGET ADVISORY:")
            report.append(f"   Since ${-excluded_total:,.2f} was recovered from departing employees")
            report.append(f"   last year, we have removed it from the baseline. We have also reserved")
            report.append(f"   ${analysis['contingency_buffer']:,.2f} (30% of exclusions) for expected departures")
            report.append(f"   next year, resulting in an adjusted baseline of ${analysis['adjusted_baseline']:,.2f}")
            report.append(f"   to ensure the department stays within budget for current headcount.")
        
        report.append("\n" + "="*80 + "\n")
        
        return "\n".join(report)
