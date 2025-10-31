# main.py

from scanner import scan_website
from report_generator import save_report

def main():
    # Ask user for website URL
    url = input("Enter the website URL to scan: ").strip()

    # Step 1: Run scanner
    results = scan_website(url)

    # Step 2: Save report
    save_report(results)

    print("[+] Privacy audit completed successfully!")

if __name__ == "__main__":
    main()
