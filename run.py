#!/usr/bin/env python
"""
GL 7560 Professional Membership Dues Analysis
Implements the skill logic to scrub historical data and create a clean baseline for budgeting.

Usage: python run.py
"""

import pandas as pd
import re
from datetime import datetime
import os
import sys

def analyze_gl7560_dues(df):
    """
    Analyze Professional Membership Dues (GL 7560) transactions using the skill logic.
    
    Path A (KEEP): Reversals, Accrual Reversals, JE Corrections, Cancellations
    Path B (EXCLUDE): Reimbursements, Paybacks, Recoveries from departing employees
    
    Returns: Dictionary with analysis results
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
    
    # Define keywords for detection (from skill)
    reversal_keywords = ['accrual rev', 'reversal', 'je correction', 'cancel', 'correction']
    reimbursement_keywords = ['payback', 'recovery', 'settlement']
    
    # Regex pattern for flexible "reimburse" variants (catches: reimburse, reinburse, reimbursement, etc.)
    reimburse_pattern = re.compile(r're[i]?mbu[r]?s[e]?m?ent?', re.IGNORECASE)
    
    # Calculate total actuals
    total_actuals = df['Amount'].sum()
    analysis['total_actuals'] = total_actuals
    
    # Process each row
    for idx, row in df.iterrows():
        amount = row['Amount']
        description = str(row['Voucher Desc']).lower() if pd.notna(row['Voucher Desc']) else ""
        date = row['Voucher Date']
        
        # Only analyze negative amounts (credits)
        if amount < 0:
            # Check both Path A and Path B patterns
            is_reversal = any(keyword in description for keyword in reversal_keywords)
            # Check for reimbursement using both keyword and flexible regex pattern
            is_reimbursement = reimburse_pattern.search(description) is not None or any(keyword in description for keyword in reimbursement_keywords)
            
            # Priority rule: If both patterns present, reimbursement wins (Path B takes precedence)
            if is_reimbursement:
                # Path B: EXCLUDE this entry (takes priority over reversal/correction)
                # Determine confidence level based on skill criteria
                if 'employee payback' in description or ('reimbursement' in description and '-' in description):
                    confidence = 'High'
                elif 'reimburse' in description:
                    confidence = 'Medium'
                else:
                    confidence = 'Low'
                
                analysis['exclusions'].append({
                    'Date': date,
                    'Amount': amount,
                    'Description': row['Voucher Desc'],
                    'Reason': 'Reimbursement / One-Time Recovery',
                    'Confidence': confidence
                })
            elif is_reversal:
                # Path A: KEEP this entry (only if not a reimbursement)
                analysis['kept_entries'].append({
                    'Date': date,
                    'Amount': amount,
                    'Description': row['Voucher Desc'],
                    'Path': 'A (Keep)',
                    'Reason': 'Reversal/Correction Entry'
                })
    
    # Calculate scrubbed baseline (total minus exclusions)
    excluded_total = sum(exc['Amount'] for exc in analysis['exclusions'])
    analysis['scrubbed_baseline'] = total_actuals - excluded_total
    
    # Calculate 30% contingency buffer based on total exclusions for future departures
    # Use absolute value of exclusions to get positive contingency amount
    analysis['contingency_buffer'] = abs(excluded_total) * 0.30
    
    # Calculate adjusted baseline (scrubbed minus contingency)
    analysis['adjusted_baseline'] = analysis['scrubbed_baseline'] - analysis['contingency_buffer']
    
    return analysis

def print_analysis_report(analysis):
    """Print formatted analysis report following skill output requirements"""
    
    print("\n" + "="*80)
    print("GL 7560 - PROFESSIONAL MEMBERSHIP DUES ANALYSIS REPORT")
    print("="*80)
    
    # Requirement 1: Total Actuals
    print(f"\n1. TOTAL ACTUALS (Raw Sum of All Transactions):")
    print(f"   ${analysis['total_actuals']:,.2f}")
    
    # Requirement 3: Exclusion List
    print(f"\n2. EXCLUSION LIST - PATH B (One-Time Recoveries to EXCLUDE):")
    print(f"   Count: {len(analysis['exclusions'])} items")
    
    if analysis['exclusions']:
        exclusions_df = pd.DataFrame(analysis['exclusions'])
        print("\n" + exclusions_df.to_string(index=False))
        excluded_total = sum(exc['Amount'] for exc in analysis['exclusions'])
        print(f"\n   Total Excluded: ${excluded_total:,.2f}")
    else:
        print("   No exclusions identified.")
    
    # Show Path A entries for reference
    if analysis['kept_entries']:
        print(f"\n3. KEPT ENTRIES - PATH A (Reversals/Corrections to KEEP):")
        print(f"   Count: {len(analysis['kept_entries'])} items")
        kept_df = pd.DataFrame(analysis['kept_entries'])
        print("\n" + kept_df.to_string(index=False))
    
    # Requirement 2: Scrubbed Baseline
    print(f"\n4. SCRUBBED BASELINE (After Excluding One-Time Recoveries):")
    print(f"   ${analysis['scrubbed_baseline']:,.2f}")
    
    # Requirement 4: Future Departure Contingency
    print(f"\n5. FUTURE DEPARTURE CONTINGENCY (30% of Exclusions Buffer):")
    print(f"   ${analysis['contingency_buffer']:,.2f}")
    print(f"   (Reserved for expected employee departures next year)")
    
    # Requirement 5: Adjusted Budget Baseline
    print(f"\n6. ADJUSTED BUDGET BASELINE (For Next Year Budget):")
    print(f"   ${analysis['adjusted_baseline']:,.2f}")
    print(f"   (Recommended budget amount)")
    
    # Requirement 6: Budget Advisory
    if analysis['exclusions']:
        excluded_total = sum(exc['Amount'] for exc in analysis['exclusions'])
        print(f"\n7. BUDGET ADVISORY:")
        print(f"   Since ${-excluded_total:,.2f} was recovered from departing employees")
        print(f"   last year, we have removed it from the baseline. We have also reserved")
        print(f"   ${analysis['contingency_buffer']:,.2f} (30% of exclusions) for expected departures")
        print(f"   next year, resulting in an adjusted baseline of ${analysis['adjusted_baseline']:,.2f}")
        print(f"   to ensure the department stays within budget for current headcount.")
    
    print("\n" + "="*80 + "\n")

def main():
    try:
        # Load the Excel file from data directory (default or from command line)
        filename = sys.argv[1] if len(sys.argv) > 1 else "SampleTransactions.xlsx"
        excel_path = f"data/{filename}"
        
        if not os.path.exists(excel_path):
            print(f"[ERROR] File not found: {excel_path}")
            sys.exit(1)
        
        df = pd.read_excel(excel_path)
        print(f"[OK] Successfully loaded: {excel_path}")
        
        # Convert Date column to datetime if it exists
        if 'Voucher Date' in df.columns:
            df['Voucher Date'] = pd.to_datetime(df['Voucher Date'])
        
        # Display the transaction data
        print("\n" + "="*80)
        print("TRANSACTION DATA")
        print("="*80)
        print(df.to_string(index=False))
        
        # Perform analysis
        results = analyze_gl7560_dues(df)
        
        # Print report
        print_analysis_report(results)
        
        return results
    
    except Exception as e:
        print(f"[ERROR] Error processing file: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
