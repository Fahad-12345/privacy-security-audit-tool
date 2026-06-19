import os
from datetime import datetime
from utils import generate_html_report

def save_report(report):
    if not os.path.exists("reports"):
        os.makedirs("reports")

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    html_file = f"reports/privacy_audit_report_{timestamp}.html"
    pdf_file = f"reports/privacy_audit_report_{timestamp}.pdf"

    # Generate HTML content with PDF link embedded
    html_content = generate_html_report(report)

    # Save HTML
    with open(html_file, "w", encoding="utf-8") as f:
        f.write(html_content)

    # Generate PDF
    # HTML(string=html_content).write_pdf(pdf_file)

    print(f"[+] Report saved as HTML: {html_file}")
    # print(f"[+] Report saved as PDF: {pdf_file}")
