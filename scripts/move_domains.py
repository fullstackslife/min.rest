import os
import shutil
from pathlib import Path

def move_domains():
    root_dir = Path.cwd()
    domains_dir = root_dir / "domains"
    
    # List of domains to move from root to domains directory
    domains_to_move = [
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
    
    # Ensure domains directory exists
    domains_dir.mkdir(exist_ok=True)
    
    # Move each domain directory
    for domain in domains_to_move:
        src = root_dir / domain
        dst = domains_dir / domain.lower()  # Convert to lowercase for consistency
        
        if src.exists() and src.is_dir():
            try:
                # If destination exists, remove it first
                if dst.exists():
                    shutil.rmtree(dst)
                
                print(f"Moving {domain} to domains directory...")
                shutil.move(str(src), str(dst))
                print(f"Successfully moved {domain}")
            except Exception as e:
                print(f"Error moving {domain}: {str(e)}")
    
    # Count total domains
    total_domains = len([d for d in domains_dir.iterdir() if d.is_dir()])
    print(f"\nTotal domains in domains directory: {total_domains}")

if __name__ == "__main__":
    move_domains() 