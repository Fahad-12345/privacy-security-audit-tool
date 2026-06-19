def generate_html_report(results):
    css = """
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; background: #f8f9fa; }
        h1 { color: #2c3e50; }
        h2 { color: #34495e; border-bottom: 2px solid #ddd; padding-bottom: 5px; }
        .disclaimer {
            background: #fff3cd; border-left: 4px solid #f39c12;
            padding: 12px 15px; border-radius: 6px; margin-bottom: 20px;
            font-size: 13px; color: #7d6608;
        }
        .section { background: white; padding: 15px; margin-bottom: 20px;
                   border-radius: 8px; box-shadow: 0 2px 6px rgba(0,0,0,0.1); }
        .suggestion { margin: 5px 0; }
        .indicator-bar-wrap { background: #eee; border-radius: 8px;
                              height: 14px; width: 100%; margin: 6px 0 12px; }
        .indicator-bar { height: 14px; border-radius: 8px;
                         background: linear-gradient(90deg, #27ae60, #2ecc71); }
        table { width: 100%; border-collapse: collapse; margin-top: 10px; }
        th, td { border: 1px solid #ccc; padding: 8px; text-align: left; }
        th { background: #eaeaea; }
        .btn-download {
            display: inline-block; padding: 10px 15px; margin: 10px 0;
            font-size: 14px; background: #3498db; color: white;
            text-decoration: none; border-radius: 5px;
        }
        .btn-download:hover { background: #2980b9; }
        .rating-box {
            text-align: center; padding: 30px 15px; border-radius: 12px;
            color: white; font-weight: bold; font-size: 20px;
            box-shadow: 0 3px 10px rgba(0,0,0,0.15);
        }
        .rating-box.good    { background: linear-gradient(135deg, #27ae60, #2ecc71); }
        .rating-box.moderate{ background: linear-gradient(135deg, #f39c12, #f1c40f); color: #333; }
        .rating-box.critical{ background: linear-gradient(135deg, #c0392b, #e74c3c); }
        .rating-icon { display: block; font-size: 40px; margin-bottom: 10px; }
    </style>
    """

    # ── Helper: render indicator list ──────────────────────────────────────
    def render_indicators(all_possible, detected):
        html = "<ul>"
        for sig in all_possible:
            tick = "✅" if sig in detected else "❌"
            html += f"<li>{tick} {sig}</li>"
        html += "</ul>"
        return html
    
    gdpr_detected  = len(results.get("gdpr_indicators", []))
    ccpa_detected  = len(results.get("ccpa_indicators", []))

    # ── GDPR indicator bar width ───────────────────────────────────────────
    gdpr_total  = 6
    ccpa_total  = 3
    gdpr_pct    = int((gdpr_detected / gdpr_total) * 100)
    ccpa_pct    = int((ccpa_detected / ccpa_total) * 100)

    # ── Trackers table ─────────────────────────────────────────────────────
    trackers = results.get("third_party_trackers", [])
    tracker_html = (
        "<table><tr><th>Tracker URL</th></tr>"
        + "".join(f"<tr><td>{t}</td></tr>" for t in trackers)
        + "</table>"
    ) if trackers else "<p>✅ No common third-party trackers detected on this page</p>"

    # ── Build HTML ─────────────────────────────────────────────────────────
    html = f"""
    <html>
    <head>
        <meta charset="UTF-8">
        <title>Privacy & Security Risk Report</title>
        {css}
        <script>
            function downloadPDF() {{
                const opt = {{
                    margin: 0.5,
                    filename: 'privacy_security_risk_report.pdf',
                    image: {{ type: 'jpeg', quality: 0.98 }},
                    html2canvas: {{ scale: 2 }},
                    jsPDF: {{ unit: 'in', format: 'letter', orientation: 'portrait' }}
                }};
                html2pdf().from(document.body).set(opt).save();
            }}
        </script>
        <script src="https://cdnjs.cloudflare.com/ajax/libs/html2pdf.js/0.10.1/html2pdf.bundle.min.js"></script>
    </head>
    <body>
        <h1>Privacy &amp; Security Risk Report</h1>
        <a class="btn-download" href="#" onclick="downloadPDF()">⬇ Download PDF</a>

        <div class="disclaimer">
            ⚠️ <strong>Disclaimer:</strong> This report provides <strong>automated surface-level indicators only</strong>.
            It does <strong>not</strong> constitute a legal GDPR or CCPA compliance audit.
            Results are based on publicly visible page elements and HTTP headers.
            Consult a qualified privacy attorney for a full legal compliance assessment.
        </div>

        <div class="section">
            <h2>Website</h2>
            <p>{results['website']}</p>
        </div>

        <div class="section">
            <h2>Privacy Policy</h2>
            <p>Status: {"✅ Found — <code>" + results['privacy_policy_link'] + "</code>" if results['privacy_policy_found'] else "❌ Not detected on this page"}</p>
        </div>

        <div class="section">
            <h2>Terms &amp; Conditions</h2>
            <p>Status: {"✅ Found — <code>" + results['terms_conditions_link'] + "</code>" if results['terms_conditions_found'] else "❌ Not detected on this page"}</p>
        </div>

        <div class="section">
            <h2>Cookie Banner</h2>
            <p>Status: {"✅ Cookie consent indicators detected in page source" if results['cookie_banner'] else "❌ No cookie consent banner detected"}</p>
        </div>

        <div class="section">
            <h2>Forms Detected</h2>
            <p>Total: {results['forms_found']}</p>
            {"<table><tr><th>Action</th><th>Method</th><th>Inputs</th></tr>"
             + "".join(f"<tr><td>{f['action']}</td><td>{f['method']}</td><td>{', '.join(f['inputs'])}</td></tr>"
                       for f in results['forms_details'])
             + "</table>" if results['forms_found'] > 0 else "<p>No forms detected on this page</p>"}
        </div>

        <div class="section">
            <h2>Third-Party Trackers</h2>
            {tracker_html}
        </div>

        <div class="section">
    <h2>Security Headers</h2>
    <table><tr><th>Header</th><th>Status</th></tr>
    {"".join(
        f"<tr><td>{h}</td><td>{(results['security_headers'].get(h) or results['security_headers'].get(h.lower()) or '❌ Missing')}</td></tr>"
        for h in ["Strict-Transport-Security", "Content-Security-Policy", 
                  "X-Frame-Options", "X-Content-Type-Options", "Referrer-Policy"]
    )}
    </table>
</div>

        <div class="section">
            <h2>GDPR Surface Indicators</h2>
            <p><em>These are surface-level signals only — not a legal compliance determination.</em></p>
            <p><strong>{results.get('gdpr_indicator_summary', '')}</strong></p>
            <div class="indicator-bar-wrap">
                <div class="indicator-bar" style="width:{gdpr_pct}%"></div>
            </div>
            {render_indicators(
                ["Cookie consent banner detected",
                 "Privacy Policy link present",
                 "Form includes a checkbox (possible consent field)",
                 "Content-Security-Policy header present",
                 "Strict-Transport-Security (HSTS) header present",
                 "No common third-party trackers detected"],
                results.get("gdpr_indicators", [])
            )}
        </div>

        <div class="section">
            <h2>CCPA Surface Indicators</h2>
            <p><em>These are surface-level signals only — not a legal compliance determination.</em></p>
            <p><strong>{results.get('ccpa_indicator_summary', '')}</strong></p>
            <div class="indicator-bar-wrap">
                <div class="indicator-bar" style="width:{ccpa_pct}%"></div>
            </div>
            {render_indicators(
                ["'Do Not Sell' language found in Privacy Policy",
                 "Cookie consent mechanism detected",
                 "US/California privacy language detected in policy content"],
                results.get("ccpa_indicators", [])
            )}
        </div>

        <div class="section">
            <h2>Recommendations</h2>
            {"<br>".join(f"<div class='suggestion'>{s}</div>" for s in results['suggestions'])}
        </div>

        <footer style="margin-top:30px; font-size:12px; color:#888;">
            Generated by CompliCheck — Privacy &amp; Security Risk Scanner<br>
            ⚠️ Surface-level automated scan only. Not a substitute for legal advice.
        </footer>
    </body>
    </html>
    """
    return html