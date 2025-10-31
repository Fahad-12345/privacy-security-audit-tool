import os

def generate_html_report(results):
    css = """
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; background: #f8f9fa; }
        h1 { color: #2c3e50; }
        h2 { color: #34495e; border-bottom: 2px solid #ddd; padding-bottom: 5px; }
        .section { background: white; padding: 15px; margin-bottom: 20px; border-radius: 8px;
                   box-shadow: 0 2px 6px rgba(0,0,0,0.1); }
        .suggestion { margin: 5px 0; }
        table { width: 100%; border-collapse: collapse; margin-top: 10px; }
        th, td { border: 1px solid #ccc; padding: 8px; text-align: left; }
        th { background: #eaeaea; }
        .btn-download {
            display: inline-block;
            padding: 10px 15px;
            margin: 10px 0;
            font-size: 14px;
            background: #3498db;
            color: white;
            text-decoration: none;
            border-radius: 5px;
        }
        .btn-download:hover { background: #2980b9; }
         /* ---------------------------- */
    /* Overall Security Rating Style */
    /* ---------------------------- */
    .rating-box {
        text-align: center;
        padding: 30px 15px;
        border-radius: 12px;
        color: white;
        font-weight: bold;
        font-size: 20px;
        box-shadow: 0 3px 10px rgba(0,0,0,0.15);
    }

    .rating-box.good {
        background: linear-gradient(135deg, #27ae60, #2ecc71);
    }

    .rating-box.moderate {
        background: linear-gradient(135deg, #f39c12, #f1c40f);
    }

    .rating-box.critical {
        background: linear-gradient(135deg, #c0392b, #e74c3c);
    }

    .rating-icon {
        display: block;
        font-size: 40px;
        margin-bottom: 10px;
    }
    </style>
    """
    # Helper: build signal lists
    def render_signals(all_possible, detected):
        html = "<ul>"
        for sig in all_possible:
            if sig in detected:
                html += f"<li>✅ {sig}</li>"
            else:
                html += f"<li>❌ {sig}</li>"
        html += "</ul>"
        return html

# Determine overall rating
    score = 0
    gdpr_signals = len(results.get("gdpr_signals", []))
    ccpa_signals = len(results.get("ccpa_signals", []))
    headers = results.get("security_headers", {})

    # Scoring logic
    score += gdpr_signals * 2
    score += ccpa_signals * 1.5
    score += sum(1 for v in headers.values() if v and "❌" not in str(v))  # each valid header = +1

    if score >= 10:
        rating_text, rating_class = "Good (Strong Privacy & Security)", "good"
    elif score >= 5:
        rating_text, rating_class = "Moderate (Partial Compliance)", "moderate"
    else:
        rating_text, rating_class = "Critical (High Risk / Poor Compliance)", "critical"
    
    # Build HTML
    html = f"""
    <html>
    <head>
        <meta charset="UTF-8">
        <title>Privacy Audit Report</title>
        {css}
        <script>
            function downloadPDF() {{
                const element = document.body;
                const opt = {{
                    margin:       0.5,
                    filename:     'privacy_audit_report.pdf',
                    image:        {{ type: 'jpeg', quality: 0.98 }},
                    html2canvas:  {{ scale: 2 }},
                    jsPDF:        {{ unit: 'in', format: 'letter', orientation: 'portrait' }}
                }};
                html2pdf().from(element).set(opt).save();
            }}
        </script>
        <script src="https://cdnjs.cloudflare.com/ajax/libs/html2pdf.js/0.10.1/html2pdf.bundle.min.js"></script>
    </head>
    <body>
        <h1>Privacy Audit Report</h1>
        <a class="btn-download" href="#" onclick="downloadPDF()">⬇ Download PDF</a>

        <div class="section">
            <h2>Website</h2>
            <p>{results['website']}</p>
        </div>

        <div class="section">
            <h2>Privacy Policy</h2>
            <p>Status: {"Found - " + results['privacy_policy_link'] if results['privacy_policy_found'] else "Not Found"}</p>
        </div>

        <div class="section">
            <h2>Terms & Conditions</h2>
            <p>Status: {"Found - " + results['terms_conditions_link'] if results['terms_conditions_found'] else "Not Found"}</p>
        </div>

        <div class="section">
            <h2>Forms</h2>
            <p>Total Forms: {results['forms_found']}</p>
            {"<table><tr><th>Action</th><th>Method</th><th>Inputs</th></tr>" + "".join(
                f"<tr><td>{f['action']}</td><td>{f['method']}</td><td>{', '.join(f['inputs'])}</td></tr>"
                for f in results['forms_details']
            ) + "</table>" if results['forms_found'] > 0 else "<p>No forms detected</p>"}
        </div>

        <div class="section">
            <h2>Cookie Banner</h2>
            <p>Status: {"Present" if results['cookie_banner'] else "Not Detected"}</p>
        </div>

         <div class="section">
            <h2>Compliance Checks</h2>
            <p><b>GDPR:</b> {results.get('gdpr_compliant', 'Not Checked')}</p>
            {render_signals(
                ["Cookie banner present", "Privacy Policy present", "Form with consent checkbox detected",
                 "Content-Security-Policy header present", "Strict-Transport-Security header present"],
                results.get("gdpr_signals", [])
            )}
            <p><b>CCPA:</b> {results.get('ccpa_compliant', 'Not Checked')}</p>
            {render_signals(
                ["'Do Not Sell' clause in Privacy Policy", "Cookie banner detected", "US-specific Privacy Policy link"],
                results.get("ccpa_signals", [])
            )}
        </div>

        <div class="section">
            <h2>Security Headers</h2>
            {"<table><tr><th>Header</th><th>Value</th></tr>" + "".join(
                f"<tr><td>{k}</td><td>{v if v else '❌ Missing'}</td></tr>"
                for k, v in results['security_headers'].items()
            ) + "</table>" if results['security_headers'] else "<p>No headers detected</p>"}
        </div>

        <div class="section">
            <h2>Suggestions</h2>
            {"<br>".join(f"<div class='suggestion'>{s}</div>" for s in results['suggestions'])}
        </div>

        <div class="section">
    <h2>Overall Security Rating</h2>
    <div class="rating-box good">
        <span class="rating-icon">🟩</span>
        Good (Strong Privacy & Security)
    </div>
</div>


        <footer style="margin-top:30px; font-size:12px; color:#888;">
            Generated by Privacy Audit Tool
        </footer>
    </body>
    </html>
    """
    return html

