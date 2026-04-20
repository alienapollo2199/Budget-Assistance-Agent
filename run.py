#!/usr/bin/env python
"""
Budget Assistant Agent - Multi-GL Budget Guidance System

Analyzes GL accounts using JSON-defined rules to generate interactive HTML budget reports.

Usage:
    python run.py GL7560 data/SampleTransactions.xlsx
    python run.py GL7555 data/your_file.xlsx
    python run.py --list-gls
"""

import sys
import os
import pandas as pd

from src.gl_registry import GLRegistry
from src.analyzer import BaseGLAnalyzer
from src.html_exporter import HTMLExporter


def load_excel_file(filepath):
    """Load and validate Excel file with GL transactions."""
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"Data file not found: {filepath}")
    
    df = pd.read_excel(filepath)
    
    required_cols = {'Voucher Date', 'Voucher Desc', 'Amount'}
    missing = required_cols - set(df.columns)
    if missing:
        raise ValueError(f"Excel file missing columns: {missing}")
    
    if 'Voucher Date' in df.columns:
        df['Voucher Date'] = pd.to_datetime(df['Voucher Date'])
    
    print(f"✓ Loaded {len(df)} transactions from {filepath}")
    return df


def analyze_gl(gl_code, df, gl_rules):
    """Analyze GL transactions using rules from registry."""
    analyzer = BaseGLAnalyzer(
        gl_code=gl_rules['code'],
        gl_description=gl_rules['name'],
        account_driver=gl_rules.get('cost_driver', 'Unknown')
    )
    
    # Override keywords from JSON rules
    analyzer.reversal_keywords = gl_rules['path_a'].get('keywords', analyzer.reversal_keywords)
    analyzer.reimbursement_keywords = gl_rules['path_b'].get('keywords', analyzer.reimbursement_keywords)
    
    analysis = analyzer.analyze(df)
    print(f"✓ Analysis complete: {len(analysis['exclusions'])} exclusions found")
    
    return analysis


def main():
    """Main entry point for Budget Assistant Agent."""
    
    if len(sys.argv) < 2:
        print_usage()
        sys.exit(1)
    
    # Check for --list-gls flag
    if sys.argv[1] == '--list-gls':
        list_enabled_gls()
        return
    
    gl_code = sys.argv[1]
    data_file = sys.argv[2] if len(sys.argv) > 2 else 'data/SampleTransactions.xlsx'
    
    try:
        # Load GL rules from registry
        registry = GLRegistry('gl_rules')
        gl_rules = registry.get_gl(gl_code)
        print(f"✓ Loaded GL {gl_code}: {gl_rules['name']}")
        
        # Load transaction data
        df = load_excel_file(data_file)
        
        # Perform analysis
        print(f"Analyzing GL {gl_code}...")
        analysis = analyze_gl(gl_code, df, gl_rules)
        
        # Export to HTML
        exporter = HTMLExporter('output')
        html_path = exporter.export(analysis, gl_code)
        print(f"✓ Generated report: {html_path}")
        
        # Print summary
        print_summary(analysis, gl_code, gl_rules)
        
    except FileNotFoundError as e:
        print(f"❌ Error: {e}")
        sys.exit(1)
    except ValueError as e:
        print(f"❌ Error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


def list_enabled_gls():
    """List all available GL accounts."""
    try:
        registry = GLRegistry('gl_rules')
        gls = registry.list_enabled_gls()
        
        if not gls:
            print("No GL accounts found in gl_rules/")
            return
        
        print(f"\n📋 Available GL Accounts ({len(gls)} total):\n")
        
        for gl_code in gls:
            gl_rules = registry.get_gl(gl_code)
            driver = gl_rules.get('cost_driver', 'Unknown')
            print(f"  GL {gl_code}: {gl_rules['name']}")
            print(f"           Driver: {driver}\n")
    
    except Exception as e:
        print(f"❌ Error listing GLs: {e}")
        sys.exit(1)


def print_summary(analysis, gl_code, gl_rules):
    """Print analysis summary to console."""
    total = analysis['total_actuals']
    excluded = sum(e['Amount'] for e in analysis['exclusions'])
    scrubbed = analysis['scrubbed_baseline']
    contingency = analysis['contingency_buffer']
    adjusted = analysis['adjusted_baseline']
    
    print("\n" + "="*70)
    print(f"GL {gl_code} - BUDGET ANALYSIS SUMMARY")
    print("="*70)
    print(f"Total Actuals:           ${total:>15,.2f}")
    print(f"Exclusions (Path B):     ${-excluded:>15,.2f}")
    print(f"Scrubbed Baseline:       ${scrubbed:>15,.2f}")
    print(f"Contingency (30%):       ${contingency:>15,.2f}")
    print(f"─" * 70)
    print(f"Recommended Budget:      ${adjusted:>15,.2f}")
    print("="*70)
    print(f"\nFull report: output/gl_{gl_code}_analysis.html\n")


def print_usage():
    """Print usage information."""
    print("""
Budget Assistant Agent - Multi-GL Budget Guidance System

Usage:
    python run.py GL<CODE> [data_file.xlsx]
    python run.py --list-gls

Examples:
    python run.py GL7560 data/SampleTransactions.xlsx
    python run.py GL7555 data/your_transactions.xlsx
    python run.py --list-gls

Columns required in Excel file:
    - Voucher Date
    - Voucher Desc
    - Amount

For more information, see README.md or CLAUDE.md
    """)


if __name__ == "__main__":
    main()
