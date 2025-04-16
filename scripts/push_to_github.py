import os
import subprocess
from pathlib import Path

# List of repositories
REPOSITORIES = [
    'TouchedByChanelsCleaning.com',
    'NewAgeWeb.it.com',
    'FullStacks.live',
    'FullStacks.life',
    'ForeverWingsLLC.com',
    'C-Suite.xyz',
    'BucketGoats.com',
    'BellaAmour.me'
]

def run_command(command, cwd=None):
    """Run a command and return its output."""
    try:
        result = subprocess.run(
            command,
            cwd=cwd,
            shell=True,
            check=True,
            capture_output=True,
            text=True
        )
        print(f"Command output: {result.stdout}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error running command: {e}")
        print(f"Error output: {e.stderr}")
        return False

def fix_remote_and_push(repo_path):
    """Fix remote URL and push changes to GitHub repository."""
    print(f"\nUpdating and pushing {repo_path}...")
    
    # Remove existing remote
    run_command("git remote remove origin", repo_path)
    
    # Add correct remote URL
    remote_url = f"https://github.com/fullstackslife/{repo_path}.git"
    if not run_command(f"git remote add origin {remote_url}", repo_path):
        return False
    
    # Push to GitHub - try both master and main branch names
    if not run_command("git push -u origin master", repo_path):
        if not run_command("git push -u origin main", repo_path):
            return False
    
    print(f"Successfully updated and pushed {repo_path}")
    return True

def main():
    for repo in REPOSITORIES:
        repo_path = repo
        if os.path.exists(repo_path):
            fix_remote_and_push(repo_path)
        else:
            print(f"Repository directory {repo_path} does not exist")

if __name__ == "__main__":
    main() 