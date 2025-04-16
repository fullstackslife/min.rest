import os
import shutil
from pathlib import Path

# List of duplicate directories to remove
duplicates = [
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

def remove_duplicate_dirs():
    current_dir = Path.cwd()
    
    for dir_name in duplicates:
        dir_path = current_dir / dir_name
        if dir_path.exists() and dir_path.is_dir():
            try:
                print(f"Removing duplicate directory: {dir_name}")
                shutil.rmtree(dir_path)
                print(f"Successfully removed {dir_name}")
            except Exception as e:
                print(f"Error removing {dir_name}: {str(e)}")

if __name__ == "__main__":
    remove_duplicate_dirs()
    print("Duplicate removal complete!") 