import os
import shutil
from pathlib import Path

def cleanup_domains():
    root_dir = Path.cwd()
    domains_dir = root_dir / "domains"
    
    # List of domains to remove from root (since they're already in domains/)
    root_domains = [
        "BucketGoats.com",
        "C-Suite.xyz",
        "ForeverWingsLLC.com",
        "FullStacks.life",
        "FullStacks.live",
        "NewAgeWeb.it.com",
        "TouchedByChanelsCleaning.com",
        "BellaAmour.me",
        "FullStacks.shop"
    ]
    
    # Remove duplicate domains from root
    for domain in root_domains:
        domain_path = root_dir / domain
        if domain_path.exists() and domain_path.is_dir():
            try:
                print(f"Removing duplicate domain from root: {domain}")
                # Use rmtree with ignore_errors to handle permission issues
                shutil.rmtree(domain_path, ignore_errors=True)
                print(f"Successfully removed {domain}")
            except Exception as e:
                print(f"Error removing {domain}: {str(e)}")
    
    # List and count domains in domains directory
    domains = [d for d in domains_dir.iterdir() if d.is_dir()]
    print(f"\nDomains in domains directory ({len(domains)}):")
    for domain in sorted(domains):
        print(f"- {domain.name}")

if __name__ == "__main__":
    cleanup_domains() 