"""
HTML report generator for GL account analysis.
Produces interactive, styled HTML reports for budget guidance.
"""

from datetime import datetime
import os


class HTMLExporter:
    """Export GL analysis results to formatted HTML reports."""
    
    def __init__(self, output_dir="output"):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
    
    def export(self, analysis, gl_code, filename):
        """Generate HTML report from analysis results."""
        html = self._build_html(analysis, gl_code)
        output_path = os.path.join(self.output_dir, f"{gl_code}_analysis.html")
        
        with open(output_path, 'w') as f:
            f.write(html)
        
        return output_path
    
    def _build_html(self, analysis, gl_code):
        """Build HTML document with analysis results."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        total = analysis['total_actuals']
        excluded = sum(e['Amount'] for e in analysis['exclusions'])
        scrubbed = analysis['scrubbed_baseline']
        contingency = analysis['contingency_buffer']
        adjusted = analysis['adjusted_baseline']
        
        exclusions_html = self._build_exclusions_table(analysis['exclusions'])
        
        return f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>GL {gl_code} Analysis Report</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; 
                background: #f5f5f5; padding: 20px; }}
        .container {{ max-width: 1200px; margin: 0 auto; background: white; 
                     border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.1);
                     padding: 40px; }}
        h1 {{ color: #1a1a1a; margin-bottom: 10px; }}
        .meta {{ color: #666; font-size: 14px; margin-bottom: 30px; }}
        .metrics {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
                   gap: 20px; margin-bottom: 40px; }}
        .metric {{ background: #f9f9f9; border-left: 4px solid #2563eb; 
                  padding: 20px; border-radius: 4px; }}
        .metric-label {{ color: #666; font-size: 13px; text-transform: uppercase; 
                       margin-bottom: 8px; }}
        .metric-value {{ font-size: 28px; font-weight: 600; color: #1a1a1a; }}
        .metric.warning {{ border-left-color: #f59e0b; }}
        .metric.success {{ border-left-color: #10b981; }}
        .section {{ margin-bottom: 40px; }}
        .section-title {{ font-size: 18px; font-weight: 600; 
                        color: #1a1a1a; margin-bottom: 20px; 
                        border-bottom: 2px solid #e5e7eb; padding-bottom: 10px; }}
        table {{ width: 100%; border-collapse: collapse; }}
        th {{ background: #f3f4f6; padding: 12px; text-align: left; 
             font-weight: 600; border-bottom: 2px solid #e5e7eb; }}
        td {{ padding: 12px; border-bottom: 1px solid #e5e7eb; }}
        tr:hover {{ background: #f9fafb; }}
        .confidence-high {{ background: #d1fae5; color: #065f46; padding: 4px 8px; 
                          border-radius: 4px; font-size: 12px; font-weight: 500; }}
        .confidence-medium {{ background: #fef3c7; color: #92400e; padding: 4px 8px;
                            border-radius: 4px; font-size: 12px; font-weight: 500; }}
        .confidence-low {{ background: #fee2e2; color: #7f1d1d; padding: 4px 8px;
                         border-radius: 4px; font-size: 12px; font-weight: 500; }}
        .amount {{ font-family: 'Monaco', 'Courier New', monospace; 
                  text-align: right; font-weight: 500; }}
        .advisory {{ background: #eff6ff; border-left: 4px solid #2563eb; 
                   padding: 20px; border-radius: 4px; line-height: 1.6; color: #1e40af; }}
        .no-data {{ color: #999; font-style: italic; padding: 20px; text-align: center; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>GL {gl_code} Budget Analysis Report</h1>
        <div class="meta">
            <strong>Generated:</strong> {timestamp}<br>
            <strong>GL Code:</strong> GL {gl_code}
        </div>
        
        <div class="metrics">
            <div class="metric">
                <div class="metric-label">Total Actuals</div>
                <div class="metric-value">${total:,.2f}</div>
            </div>
            <div class="metric warning">
                <div class="metric-label">Excluded Amount</div>
                <div class="metric-value">${-excluded:,.2f}</div>
            </div>
            <div class="metric">
                <div class="metric-label">Scrubbed Baseline</div>
                <div class="metric-value">${scrubbed:,.2f}</div>
            </div>
            <div class="metric warning">
                <div class="metric-label">Contingency (30%)</div>
                <div class="metric-value">${contingency:,.2f}</div>
            </div>
            <div class="metric success">
                <div class="metric-label">Adjusted Budget</div>
                <div class="metric-value">${adjusted:,.2f}</div>
            </div>
        </div>
        
        <div class="section">
            <div class="section-title">Exclusion Details (Path B)</div>
            {exclusions_html}
        </div>
        
        <div class="section">
            <div class="advisory">
                <strong>Budget Recommendation:</strong><br><br>
                For the new year, recommend a budget of <strong>${adjusted:,.2f}</strong>.<br>
                This accounts for the ${-excluded:,.2f} in one-time recoveries from last year
                and reserves ${contingency:,.2f} (30% contingency) for anticipated departures.
            </div>
        </div>
    </div>
</body>
</html>
"""
    
    def _build_exclusions_table(self, exclusions):
        """Build HTML table for exclusion list."""
        if not exclusions:
            return '<p class="no-data">No exclusions identified.</p>'
        
        rows = []
        for exc in exclusions:
            conf_class = f"confidence-{exc['Confidence'].lower()}"
            rows.append(f"""
            <tr>
                <td>{exc['Date'].strftime('%Y-%m-%d') if hasattr(exc['Date'], 'strftime') else exc['Date']}</td>
                <td>{exc['Description']}</td>
                <td class="amount">${exc['Amount']:,.2f}</td>
                <td><span class="{conf_class}">{exc['Confidence']}</span></td>
            </tr>
            """)
        
        return f"""
        <table>
            <thead>
                <tr>
                    <th>Date</th>
                    <th>Description</th>
                    <th>Amount</th>
                    <th>Confidence</th>
                </tr>
            </thead>
            <tbody>
                {''.join(rows)}
            </tbody>
        </table>
        """
