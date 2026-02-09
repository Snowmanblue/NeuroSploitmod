#!/usr/bin/env python3
import shutil
import sys
import importlib.util
import os
from pathlib import Path

# Colors for output
GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
CYAN = "\033[96m"
RESET = "\033[0m"

def print_status(name, status, message=""):
    if status == "OK":
        print(f"[{GREEN}OK{RESET}] {name:<25} {message}")
    elif status == "MISSING":
        print(f"[{RED}MISSING{RESET}] {name:<25} {message}")
    elif status == "WARNING":
        print(f"[{YELLOW}WARNING{RESET}] {name:<25} {message}")

def check_command(cmd):
    """Check if a command exists in the system PATH or common user bin dirs"""
    # 1. Check PATH
    path = shutil.which(cmd)
    if path:
        return "OK", path

    # 2. Check common user bin dirs
    home = str(Path.home())
    common_paths = [
        os.path.join(home, "go", "bin", cmd),
        os.path.join(home, ".cargo", "bin", cmd),
        os.path.join(home, ".local", "bin", cmd),
        os.path.join(home, "bin", cmd),
        "/usr/local/go/bin/" + cmd
    ]
    for p in common_paths:
        if os.path.exists(p) and os.access(p, os.X_OK):
            return "WARNING", f"Found at {p} (Not in PATH)"
            
    return "MISSING", "Not found in PATH"

def check_python_package(package):
    """Check if a Python package is installed"""
    try:
        spec = importlib.util.find_spec(package)
        if spec is not None:
            return "OK", ""
    except (ImportError, AttributeError, ValueError):
        pass
    return "MISSING", "Run: pip install " + package

def check_env_var(var):
    """Check if an environment variable is set"""
    val = os.getenv(var)
    if val and val.strip():
        if val in ["your-key-here", "your-mistral-api-key"]:
            return "WARNING", "Set to placeholder value"
        return "OK", "Configured"
    return "WARNING", "Not set (some features may fail)"

def main():
    print(f"\n{CYAN}NeuroSploit Tool Verification Script{RESET}")
    print("=" * 50)

    # 1. System Tools
    print(f"\n{CYAN}[+] Checking System Tools{RESET}")
    sys_tools = ["git", "curl", "wget", "jq", "nmap", "go", "cargo"]
    for tool in sys_tools:
        status, msg = check_command(tool)
        print_status(tool, status, msg)

    # 2. Python Dependencies
    print(f"\n{CYAN}[+] Checking Python Libraries{RESET}")
    py_packages = [
        "requests", "dnspython", "urllib3", 
        "anthropic",
    "openai",
    "google.generativeai",
    "mistune",
    "wafw00f", 
    "paramspider"
    ]
    for pkg in py_packages:
        # module name might differ from package name
        module = pkg
        if pkg == "dnspython": module = "dns"
        if pkg == "google.generativeai": module = "google.generativeai"
        
        status, msg = check_python_package(module)
        print_status(pkg, status, msg)

    # 3. Security Tools (Go/Rust/Others)
    print(f"\n{CYAN}[+] Checking Security Tools{RESET}")
    sec_tools = [
        # Network/Port
        "nmap", "rustscan", "naabu", "masscan",
        # Subdomains
        "subfinder", "amass", "assetfinder", "findomain", "puredns",
        # Web
        "httpx", "nuclei", "nikto", "whatweb", "wafw00f",
        "sqlmap", "wpscan", "feroxbuster", "gobuster", "ffuf",
        "dirsearch", "gau", "waybackurls", "katana", "paramspider"
    ]
    
    missing_tools = []
    for tool in sec_tools:
        status, msg = check_command(tool)
        print_status(tool, status, msg)
        if status == "MISSING":
            missing_tools.append(tool)

    # 4. Environment Variables
    print(f"\n{CYAN}[+] Checking Configuration (.env){RESET}")
    
    # Try to load .env manually if python-dotenv not installed
    env_path = Path(".env")
    if env_path.exists():
        print_status(".env file", "OK", "Found")
        # Simple parser
        with open(env_path, "r") as f:
            for line in f:
                if "=" in line and not line.startswith("#"):
                    k, v = line.strip().split("=", 1)
                    os.environ[k] = v
    else:
        print_status(".env file", "MISSING", "Copy .env.example to .env")

    api_keys = [
        "MISTRAL_API_KEY", 
        "OPENAI_API_KEY", 
        "ANTHROPIC_API_KEY", 
        "GOOGLE_API_KEY"
    ]
    for key in api_keys:
        status, msg = check_env_var(key)
        print_status(key, status, msg)

    # Summary
    print("\n" + "=" * 50)
    if missing_tools:
        print(f"{YELLOW}Warning: {len(missing_tools)} tools are missing or not in PATH.{RESET}")
        print("Run usage tests to see if these are critical for your workflow.")
        print("To install missing tools, run: ./install_tools.sh")
        print("If tools show as WARNING (Found at...), run: source ~/.bashrc")
    else:
        print(f"{GREEN}All checked tools are installed!{RESET}")
    print("=" * 50 + "\n")

if __name__ == "__main__":
    main()
