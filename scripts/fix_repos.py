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

def fix_repository(repo_path):
    """Fix repository structure and deployment configuration."""
    print(f"\nFixing {repo_path}...")
    
    # Create src directory if it doesn't exist
    src_dir = os.path.join(repo_path, 'src')
    if not os.path.exists(src_dir):
        os.makedirs(src_dir)
    
    # Move HTML files to src directory
    html_files = [f for f in os.listdir(repo_path) if f.endswith('.html')]
    for html_file in html_files:
        src = os.path.join(repo_path, html_file)
        dst = os.path.join(src_dir, html_file)
        os.rename(src, dst)
        print(f"Moved {html_file} to src directory")
    
    # Update GitHub Pages workflow
    workflow_file = os.path.join(repo_path, '.github', 'workflows', 'deploy.yml')
    if os.path.exists(workflow_file):
        with open(workflow_file, 'r') as f:
            content = f.read()
        
        # Update the path in the workflow file
        content = content.replace("path: '.'", "path: 'src'")
        
        with open(workflow_file, 'w') as f:
            f.write(content)
        print("Updated GitHub Pages workflow")
    
    # Commit and push changes
    if run_command("git add .", repo_path):
        if run_command('git commit -m "Move HTML files to src directory and update deployment path"', repo_path):
            if run_command("git push origin master", repo_path):
                print(f"Successfully fixed {repo_path}")
                return True
    
    return False

def main():
    for repo in REPOSITORIES:
        repo_path = repo
        if os.path.exists(repo_path):
            fix_repository(repo_path)
        else:
            print(f"Repository directory {repo_path} does not exist")

if __name__ == "__main__":
    main() 