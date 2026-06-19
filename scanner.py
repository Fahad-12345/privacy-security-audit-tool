import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
import time
import os
import json
from webdriver_manager.chrome import ChromeDriverManager

def get_header(results, header_name):
      """Case-insensitive header lookup"""
      headers = results.get("security_headers", {})
      return headers.get(header_name) or headers.get(header_name.lower())


# ------------------------
#  MAIN SCANNER FUNCTION
# ------------------------
def scan_website(url):
    if not url.startswith("http"):
        url = "https://" + url

    suggestions = []

    results = {
        "website": url,
        "privacy_policy_found": False,
        "privacy_policy_link": None,
        "privacy_policy_keywords": [],
        "terms_conditions_found": False,
        "terms_conditions_link": None,
        "terms_keywords": [],
        "forms_found": 0,
        "forms_details": [],
        "cookie_banner": False,
        "cookies": [],
        "third_party_trackers": [],
        "security_headers": {},
        "gdpr_indicators": [],
        "ccpa_indicators": [],
        "suggestions": suggestions
    }

    # Common trackers
    tracker_keywords = [
        "googletagmanager", "google-analytics", "facebook.net",
        "hotjar", "mixpanel", "segment", "doubleclick"
    ]

    # -------------------
    # STEP 1: Static Scan
    # -------------------
    try:
        response = fetch_page(url)
        soup = BeautifulSoup(response.text, "html.parser")

        # Extract links
        links = [(a.text.strip(), a.get("href", "")) for a in soup.find_all("a") if a.get("href")]

        # Privacy Policy check
        for text, link in links:
            if any(k in text.lower() or k in link.lower() for k in ["privacy", "policy", "data policy"]):
                results["privacy_policy_found"] = True
                results["privacy_policy_link"] = link
                results["privacy_policy_keywords"] = analyze_policy_page(url, link)
                break

        # Terms & Conditions check
        for text, link in links:
            if any(k in text.lower() or k in link.lower() for k in ["terms", "conditions", "legal"]):
                results["terms_conditions_found"] = True
                results["terms_conditions_link"] = link
                results["terms_keywords"] = analyze_policy_page(url, link)
                break

        # Forms check
        forms = soup.find_all("form")
        results["forms_found"] = len(forms)
        for form in forms:
            inputs = [inp.get("type", "text") for inp in form.find_all("input")]
            results["forms_details"].append({
                "action": form.get("action") if form.get("action") else "N/A",
                "method": form.get("method").upper() if form.get("method") else "GET",
                "inputs": inputs,
                "has_password": "password" in inputs,
                "has_email": "email" in inputs,
                "has_checkbox": "checkbox" in inputs
            })

        # Tracker detection
        scripts = [s.get("src", "").lower() for s in soup.find_all("script") if s.get("src")]
        trackers = [s for s in scripts if any(t in s for t in tracker_keywords)]
        results["third_party_trackers"] = trackers

        # Security headers
        results["security_headers"] = analyze_security_headers(response.headers)

    except Exception as e:
        results["suggestions"].append(f"Error fetching page: {e}")

    # -------------------
    # STEP 2: Dynamic Scan (Selenium)
    # -------------------
    try:
        options = webdriver.ChromeOptions()
        options.add_argument("--headless=new")
        options.add_argument("--disable-gpu")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.set_capability("goog:loggingPrefs", {"performance": "ALL"})

        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=options)

        driver.get(url)
        time.sleep(3)

        page_source = driver.page_source.lower()

        # Cookie banner detection
        if check_cookie_banner(page_source):
            results["cookie_banner"] = True

        # Cookies
        for cookie in driver.get_cookies():
            results["cookies"].append({
                "name": cookie.get("name"),
                "domain": cookie.get("domain"),
                "secure": cookie.get("secure"),
                "httpOnly": cookie.get("httpOnly"),
                "expiry": cookie.get("expiry")
            })

        # Real browser response headers
        headers = get_security_headers_selenium(driver, url)
        if headers:
            results["security_headers"] = headers

        driver.quit()

    except Exception as e:
        results["suggestions"].append(f"Selenium error: {e}")

    # -------------------
    # STEP 3: Risk Indicator Analysis
    # (No legal compliance claims — surface-level indicators only)
    # -------------------
    results = analyze_risk_indicators(results)

    # -------------------
    # STEP 4: Suggestions
    # -------------------

    if results["privacy_policy_found"]:
        suggestions.append("✅ Privacy Policy link found on the page")
    else:
        suggestions.append("🔴 No Privacy Policy link detected — recommended for user trust")

    if results["terms_conditions_found"]:
        suggestions.append("✅ Terms & Conditions link found on the page")
    else:
        suggestions.append("🔴 No Terms & Conditions link detected")

    if results["cookie_banner"]:
        suggestions.append("✅ Cookie consent banner indicators detected")
    else:
        suggestions.append("🔴 No cookie consent banner detected — consider adding one")

    if results["forms_found"] > 0:
        suggestions.append(f"✅ {results['forms_found']} form(s) detected — review for data collection consent")
    else:
        suggestions.append("ℹ️ No forms detected on this page")

    if results["third_party_trackers"]:
        suggestions.append(f"⚠️ {len(results['third_party_trackers'])} third-party tracker(s) detected — review for privacy impact")
    else:
        suggestions.append("✅ No common third-party trackers detected on this page")

    if get_header(results, "Strict-Transport-Security"):
       suggestions.append("✅ Strict-Transport-Security (HSTS) header present")
    else:
       suggestions.append("🔴 Strict-Transport-Security header missing — add for HTTPS enforcement")

    if get_header(results, "Content-Security-Policy"):
       suggestions.append("✅ Content-Security-Policy header present")
    else:
       suggestions.append("🔴 Content-Security-Policy header missing — helps prevent XSS attacks")

    if get_header(results, "X-Frame-Options"):
       suggestions.append("✅ X-Frame-Options header present — protects against clickjacking")
    else:
       suggestions.append("🔴 X-Frame-Options header missing")

    if get_header(results, "X-Content-Type-Options"):
       suggestions.append("✅ X-Content-Type-Options header present")
    else:
       suggestions.append("🔴 X-Content-Type-Options header missing")

    results["suggestions"] = suggestions
    return results


# ------------------------
#  HELPERS
# ------------------------

def fetch_page(url, retries=3, timeout=20):
    """Fetch webpage with retries and longer timeout"""
    for attempt in range(retries):
        try:
            response = requests.get(
                url,
                timeout=timeout,
                headers={"User-Agent": "Mozilla/5.0"}
            )
            response.raise_for_status()
            return response
        except Exception as e:
            if attempt < retries - 1:
                time.sleep(2)
                continue
            raise e


def analyze_policy_page(base_url, link):
    """Fetch a policy/terms page and check for important keywords"""
    keywords = ["data", "personal", "cookies", "rights", "retention", "third parties", "consent",
                "california", "ccpa", "do not sell", "gdpr"]
    found = []
    try:
        if link.startswith("/"):
            full_link = base_url.rstrip("/") + link
        elif link.startswith("http"):
            full_link = link
        else:
            full_link = base_url.rstrip("/") + "/" + link

        res = requests.get(full_link, timeout=10, headers={"User-Agent": "Mozilla/5.0"})
        text = res.text.lower()
        for k in keywords:
            if k in text:
                found.append(k)
    except:
        pass
    return found


def analyze_security_headers(headers):
    required_headers = [
        "Strict-Transport-Security",
        "Content-Security-Policy",
        "X-Frame-Options",
        "X-Content-Type-Options",
        "Referrer-Policy"
    ]
    result = {}
    for h in required_headers:
        result[h] = headers.get(h) or headers.get(h.lower()) or None
    return result

def get_security_headers_selenium(driver, target_url):
    """Extract real response headers from Chrome performance logs"""
    headers = {}
    try:
        logs = driver.get_log("performance")
        for entry in logs:
            msg = json.loads(entry["message"])["message"]
            if msg["method"] == "Network.responseReceived":
                response_url = msg["params"]["response"]["url"]
                if response_url.startswith(target_url):
                    headers = msg["params"]["response"]["headers"]
                    break
    except Exception as e:
        print(f"[DEBUG] Could not fetch headers via Selenium: {e}")
    return headers


def check_cookie_banner(page_source: str) -> bool:
    """Detect cookie banner keywords in page source"""
    keywords = [
        "cookie-consent", "cookieconsent", "accept cookies",
        "cookie policy", "privacy preferences", "cookie settings",
        "we use cookies", "gdpr", "consent banner"
    ]
    return any(k in page_source for k in keywords)


def analyze_risk_indicators(results):
    """
    Collect surface-level privacy & security risk indicators.
    
    IMPORTANT: This does NOT determine legal GDPR/CCPA compliance.
    These are automated surface checks only — not a legal audit.
    Consult a qualified privacy attorney for legal compliance assessment.
    """

    gdpr_indicators = []
    ccpa_indicators = []

    # ---------------------------
    # GDPR surface indicators
    # ---------------------------
    if results.get("cookie_banner"):
        gdpr_indicators.append("Cookie consent banner detected")

    if results.get("privacy_policy_found"):
        gdpr_indicators.append("Privacy Policy link present")

    if results.get("forms_found", 0) > 0:
        for form in results["forms_details"]:
            if form.get("has_checkbox"):
                gdpr_indicators.append("Form includes a checkbox (possible consent field)")
                break

    if get_header(results, "Content-Security-Policy"):
        gdpr_indicators.append("Content-Security-Policy header present")

    if get_header(results, "Strict-Transport-Security"):
        gdpr_indicators.append("Strict-Transport-Security (HSTS) header present")

    if not results.get("third_party_trackers"):
        gdpr_indicators.append("No common third-party trackers detected")

    # ---------------------------
    # CCPA surface indicators
    # ---------------------------
    privacy_keywords = results.get("privacy_policy_keywords", [])

    if "do not sell" in str(privacy_keywords).lower():
        ccpa_indicators.append("'Do Not Sell' language found in Privacy Policy")

    if results.get("cookie_banner"):
        ccpa_indicators.append("Cookie consent mechanism detected")

    privacy_link = (results.get("privacy_policy_link") or "").lower()
    if any(k in privacy_link for k in ["us", "california", "ccpa"]) or \
       any(k in str(privacy_keywords).lower() for k in ["california", "ccpa", "do not sell"]):
        ccpa_indicators.append("US/California privacy language detected in policy content")

    # ---------------------------
    # Store indicator counts (not compliance verdicts)
    # ---------------------------
    results["gdpr_indicators"] = gdpr_indicators
    results["ccpa_indicators"] = ccpa_indicators

    # Indicator summary strings (honest language)
    gdpr_count = len(gdpr_indicators)
    ccpa_count = len(ccpa_indicators)

    results["gdpr_indicator_summary"] = f"{gdpr_count}/6 GDPR-related indicators detected"
    results["ccpa_indicator_summary"] = f"{ccpa_count}/3 CCPA-related indicators detected"

    return results