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

def setup_git_repo(repo_path):
    """Initialize git repository and set up remote."""
    print(f"\nSetting up git for {repo_path}...")
    
    # Initialize git repository
    if not run_command("git init", repo_path):
        return False
    
    # Add all files
    if not run_command("git add .", repo_path):
        return False
    
    # Configure git user (if not already configured)
    if not run_command('git config user.email "your.email@example.com"', repo_path):
        return False
    if not run_command('git config user.name "Your Name"', repo_path):
        return False
    
    # Commit changes
    if not run_command('git commit -m "Initial commit"', repo_path):
        return False
    
    # Add remote (you'll need to replace with your GitHub organization/username)
    remote_url = f"git@github.com:fullstackslife/{repo_path}.git"
    if not run_command(f"git remote add origin {remote_url}", repo_path):
        return False
    
    # Push to GitHub
    if not run_command("git push -u origin main", repo_path):
        return False
    
    print(f"Successfully set up and pushed {repo_path}")
    return True

def main():
    for repo in REPOSITORIES:
        repo_path = repo
        if os.path.exists(repo_path):
            setup_git_repo(repo_path)
        else:
            print(f"Repository directory {repo_path} does not exist")

if __name__ == "__main__":
    main() 