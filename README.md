# CompliCheck — Privacy & Security Risk Scanner

CompliCheck is an **automated privacy and security risk scanner** that analyzes websites for surface-level privacy and security indicators. It detects privacy policies, cookie banners, security headers, third-party trackers, and forms — and generates downloadable HTML reports.

> ⚠️ **Important:** This tool provides **automated surface-level indicators only**. It does **not** constitute a legal GDPR or CCPA compliance audit. Results are based on publicly visible page elements and HTTP headers. Consult a qualified privacy attorney for a full legal compliance assessment.

---

## What It Actually Does

CompliCheck performs two layers of scanning:

**Static scan** (requests + BeautifulSoup):
- Detects privacy policy and terms & conditions links
- Finds forms and input types
- Detects third-party tracker scripts
- Reads HTTP security headers

**Dynamic scan** (Selenium + Chrome):
- Renders the page fully in a real browser
- Detects cookie consent banners from rendered page source
- Extracts real response headers via Chrome performance logs
- Reads actual cookies set by the website

---

## Features

- ✅ Detect **Privacy Policy** and **Terms & Conditions** links
- ✅ Identify **forms**, input types, and consent checkboxes
- ✅ Detect **Cookie Consent Banner** from rendered page source
- ✅ Analyze **security headers**:
  - Strict-Transport-Security (HSTS)
  - Content-Security-Policy (CSP)
  - X-Frame-Options
  - X-Content-Type-Options
  - Referrer-Policy
- ✅ Detect **third-party trackers** (Google Analytics, Facebook, Hotjar, etc.)
- ✅ Surface-level **GDPR and CCPA indicator checks** (not legal verdicts)
- ✅ Generate **HTML reports** with **PDF download** option
- ✅ Auto-install ChromeDriver via `webdriver-manager`

---

## Screenshots

<img width="1920" height="1017" alt="Screenshot (355)" src="https://github.com/user-attachments/assets/441cdaf6-a7f5-467f-b4b7-52d1d5829909" />

<img width="1920" height="1028" alt="Screenshot (356)" src="https://github.com/user-attachments/assets/3900d252-de77-4263-bc39-33e56e671e81" />

<img width="1920" height="1014" alt="Screenshot (357)" src="https://github.com/user-attachments/assets/5f1cf747-cfbe-471f-819b-7c776ae4ee8e" />

<img width="1920" height="1000" alt="Screenshot (358)" src="https://github.com/user-attachments/assets/5ecab2a8-12af-4bfc-8ea6-9cdebe92c3e4" />

---

## Installation

**1. Clone the repository:**
```bash
git clone https://github.com/Fahad-12345/privacy-security-audit-tool.git
cd PRIVACY_AUDIT_TOOL
```

**2. Create a virtual environment:**
```bash
python -m venv venv
venv\Scripts\activate      # Windows
source venv/bin/activate   # Linux/Mac
```

**3. Install dependencies:**
```bash
pip install -r requirements.txt
```

> ChromeDriver is installed automatically via `webdriver-manager` — no manual setup needed.

---

## Usage

**Run from command line:**
```bash
python main.py
```

Enter any website URL when prompted. The report is saved to the `reports/` folder as an HTML file.

**Or use programmatically:**
```python
from scanner import scan_website
from utils import generate_html_report
from report_generator import save_report

results = scan_website("https://example.com")
save_report(results)
```

Open the generated HTML file in a browser to view the report and download as PDF.

---

## Sample Report Output

Each report includes:
- Privacy policy and terms link status
- Cookie banner detection
- Forms detected with input types
- Third-party trackers found
- Security headers table (present/missing)
- GDPR surface indicators (X/6 detected)
- CCPA surface indicators (X/3 detected)
- Recommendations for improvement

---

## Indicator Logic

### GDPR Surface Indicators (6 checks)
| Indicator | How it's detected |
|---|---|
| Cookie consent banner | Keywords in rendered page source |
| Privacy Policy link present | Link text/href scan |
| Form with consent checkbox | Input type="checkbox" in forms |
| Content-Security-Policy header | HTTP response header |
| Strict-Transport-Security header | HTTP response header |
| No third-party trackers | Script src scan |

### CCPA Surface Indicators (3 checks)
| Indicator | How it's detected |
|---|---|
| "Do Not Sell" language | Privacy policy page content |
| Cookie consent mechanism | Cookie banner detection |
| US/California privacy language | Policy content keywords |

> These are surface-level automated signals only — not legal compliance determinations.

---

## Tech Stack

| Component | Technology |
|---|---|
| Backend scanning | Python, Requests, BeautifulSoup |
| Dynamic rendering | Selenium, ChromeDriver (auto-managed) |
| Report generation | HTML/CSS, html2pdf.js |
| Header extraction | Chrome DevTools performance logs |

---

## Limitations

- Cookie banners that load via JavaScript after a delay may not always be detected
- CCPA "Do Not Sell" detection is keyword-based — legal language varies
- Security headers are checked at the homepage only — subpages may differ
- Results reflect the page state at scan time — websites change frequently

---

## Future Improvements

- Bulk scanning of multiple URLs from a CSV file
- Flask or FastAPI web frontend for browser-based scanning
- Enhanced tracker detection (fingerprinting scripts, pixel trackers)
- Email report delivery
- Scheduled/recurring scans

---

## Author

**Fahad Irfan** — Full-Stack AI Developer

- GitHub: [github.com/Fahad-12345](https://github.com/Fahad-12345)
- Portfolio: [fahad-portfolio-black-xi.vercel.app](https://fahad-portfolio-black-xi.vercel.app)

---

## License

MIT License © Fahad Irfan
