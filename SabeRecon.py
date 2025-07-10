#!/usr/bin/env python3
import os
import subprocess
from datetime import datetime
from jinja2 import Environment, FileSystemLoader
import random
import string

def detect_wildcard_length(domain):
    fake_path = ''.join(random.choices(string.ascii_lowercase + string.digits, k=16))
    url = f"https://{domain}/{fake_path}"
    try:
        result = subprocess.check_output(f"curl -s -o /dev/null -w '%{{size_download}}' {url}", shell=True, timeout=10)
        return int(result.decode().strip())
    except:
        return None

# --- Branding Banner ---
import pyfiglet
from termcolor import cprint

def print_banner():
    # Big bold text at top
    banner = pyfiglet.figlet_format("SaberShield", font="slant", width=100)
    cprint(banner, "red")
    banner = pyfiglet.figlet_format("Cybersecurity", font ="slant", width=100)
    cprint(banner, "red")

    # Subtitle and version info
    print("                     SaberShield Cybersecurity LLC")
    print("                     \"Sharp Security, Solid Defense\"\n")
    print("                     SabeRecon v0.1\n")

# --- Get User Input ---
def get_inputs():
    raw_url = input("Hello, User! Please enter the URL you would like reconnaissance performed against: ").strip()
    cleaned_url = raw_url.replace("https://", "").replace("http://", "").strip("/")
    output_path = input("Please enter the directory and file you would like the output to be directed to (e.g. documents/recon/output.txt): ").strip()
    return raw_url, cleaned_url, output_path

# --- Create HTML output ---
def generate_html_report(target, output_file, results_dict):
    env = Environment(loader=FileSystemLoader('.'))
    template = env.get_template('template.html')
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    html_content = template.render(
        target=target,
        timestamp=timestamp,
        sections=[{"title": title, "content": content} for title, content in results_dict.items()]
    )

    html_path = output_file.replace(".txt", ".html")
    with open(html_path, 'w') as f:
        f.write(html_content)
    print(f"HTML report saved to {html_path}")

# --- Run Recon Commands ---
def run_recon(display_url, domain_only, output_file):
    results = {}  # Store section outputs for HTML

    wild_len = detect_wildcard_length(domain_only)
    if wild_len:
        gobuster_cmd = f"gobuster dir -u https://{domain_only} -w ./common.txt -b 404 -f --exclude-length {wild_len}"
    else:
        gobuster_cmd = f"gobuster dir -u https://{domain_only} -w ./common.txt -b 404 -f"

    tools = [
        (f"whois {domain_only.replace('www.', '')}", "WHOIS Lookup"),
        (f"nslookup {domain_only}", "NSLookup"),
        (f"dig {domain_only}", "DIG DNS Info"),
        (f"nmap -F {domain_only}", "Nmap Fast Scan"),
        (f"curl -I https://{domain_only}", "HTTP Headers (curl)"),
        (f"whatweb https://{domain_only}", "WhatWeb Fingerprint"),
        (f"subfinder -silent -d {domain_only}", "Subdomain Enumeration (subfinder)"),
        (gobuster_cmd, "Gobuster Directory Scan"),
		(f"wafw00f https://{domain_only}", "WAF Detection (WAFW00F)"),
    ]

    with open(output_file, 'w') as out:
        out.write(f"Reconnaissance Report for {display_url}\nGenerated on {datetime.now()}\n\n")

        def run_cmd(cmd, desc):
            out.write(f"\n\n--- {desc} ---\n")
            try:
                result = subprocess.check_output(cmd, shell=True, stderr=subprocess.STDOUT, timeout=60)
                output = result.decode()
                if desc == "Subdomain Enumeration (subfinder)" and not output.strip():
                    output = "No subdomains found."
            except subprocess.CalledProcessError as e:
                output = f"ERROR during {desc}: {e.output.decode()}"
            except subprocess.TimeoutExpired:
                output = f"{desc} timed out.\n"

            out.write(output)
            results[desc] = output  # Save to results dict

        for cmd, desc in tools:
            run_cmd(cmd, desc)

    generate_html_report(display_url, output_file, results)

# --- Main ---
def main():
    print_banner()
    raw_url, cleaned_url, output_file = get_inputs()
    print(f"\nRunning recon on {raw_url}... output will be saved to {output_file}")
    run_recon(raw_url, cleaned_url, output_file)
    print("\nReconnaissance complete!")

if __name__ == "__main__":
    main()
