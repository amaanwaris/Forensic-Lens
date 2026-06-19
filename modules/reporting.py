# modules/reporting.py
import os
import datetime

def generate_report(file_path, selected_modules, metadata=None, hashes=None, tamper_result=None, social_result=None):
    """
    Generates a forensic HTML report inside the current case folder.
    """

    metadata = metadata or {}
    hashes = hashes or {}
    tamper_result = tamper_result or {}
    social_result = social_result or {}

    # ----- Console output -----
    print("\n[Report] Generating report for", file_path)
    print("Modules included:", selected_modules)

    print("\n--- Metadata ---")
    if metadata:
        for k, v in metadata.items():
            print(f"{k}: {v}")
    else:
        print("No metadata extracted.")

    print("\n--- Hashes ---")
    if hashes:
        for k, v in hashes.items():
            print(f"{k}: {v}")
    else:
        print("No hashes calculated.")

    if tamper_result:
        print("\n--- Tamper Analysis ---")
        for k, v in tamper_result.items():
            print(f"{k}: {v}")

    if social_result:
        print("\n--- Social Fingerprint ---")
        for k, v in social_result.items():
            print(f"{k}: {v}")

    # ✅ Save inside case folder (/CASE_.../Reports/)
    case_dir = os.getcwd()
    reports_dir = os.path.join(case_dir, "Reports")
    os.makedirs(reports_dir, exist_ok=True)

    base_name = os.path.basename(file_path)
    html_file = os.path.join(reports_dir, f"{base_name}_report.html")

    # ----- HTML Content -----
    html_content = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <title>FORENSIC LENS REPORT {base_name}</title>
        <style>
            body {{ font-family: Arial, sans-serif; background: #f4f4f4; padding: 20px; }}
            h1, h2 {{ color: #333; }}
            table {{ border-collapse: collapse; width: 100%; margin-bottom: 20px; }}
            th, td {{ border: 1px solid #666; padding: 8px; text-align: left; }}
            th {{ background-color: #ddd; }}
            a {{ color: #0066cc; text-decoration: none; }}
        </style>
    </head>
    <body>
        <h1>FORENSIC LENS REPORT </h1>
        <p><strong>File:</strong> {file_path}</p>
        <p><strong>Date:</strong> {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        <p><strong>Modules:</strong> {', '.join(selected_modules)}</p>
    """

    if metadata:
        html_content += "<h2>Metadata</h2><table><tr><th>Field</th><th>Value</th></tr>"
        for k, v in metadata.items():
            if k.lower() == "google maps":
                html_content += f"<tr><td>{k}</td><td><a href='{v}' target='_blank'>{v}</a></td></tr>"
            else:
                html_content += f"<tr><td>{k}</td><td>{v}</td></tr>"
        html_content += "</table>"

    if hashes:
        html_content += "<h2>Hashes</h2><table><tr><th>Algorithm</th><th>Value</th></tr>"
        for k, v in hashes.items():
            html_content += f"<tr><td>{k}</td><td>{v}</td></tr>"
        html_content += "</table>"

    if tamper_result:
        html_content += "<h2>Tamper Analysis</h2><table><tr><th>Check</th><th>Result</th></tr>"
        for k, v in tamper_result.items():
            html_content += f"<tr><td>{k}</td><td>{v}</td></tr>"
        html_content += "</table>"

    if social_result:
        html_content += "<h2>Social Fingerprint</h2><table><tr><th>Check</th><th>Result</th></tr>"
        for k, v in social_result.items():
            html_content += f"<tr><td>{k}</td><td>{v}</td></tr>"
        html_content += "</table>"

    html_content += """
    </body>
    </html>
    """

    # Save HTML report
    try:
        with open(html_file, "w", encoding="utf-8") as f:
            f.write(html_content)
        print(f"\n[Report] HTML report saved to {html_file}")
    except Exception as e:
        print(f"[Report] Failed to save HTML report: {e}")

