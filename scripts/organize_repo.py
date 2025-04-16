import os
import shutil
import subprocess
from pathlib import Path

def create_directory_if_not_exists(directory):
    if not os.path.exists(directory):
        os.makedirs(directory)

def is_git_repo(path):
    return os.path.exists(os.path.join(path, '.git'))

def run_command(command, cwd=None):
    try:
        subprocess.run(command, cwd=cwd, check=True, shell=True)
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error running command {command}: {e}")
        return False

def safe_remove(path):
    try:
        if os.path.isdir(path):
            shutil.rmtree(path, ignore_errors=True)
        else:
            os.remove(path)
    except Exception as e:
        print(f"Warning: Could not remove {path}: {e}")

def move_domains_to_domains_folder():
    domains_dir = Path('domains')
    create_directory_if_not_exists(domains_dir)
    
    # List of domain folders to move
    domain_folders = [
        'FullStacks.shop',
        'BellaAmour.me',
        'TouchedByChanelsCleaning.com',
        'NewAgeWeb.it.com',
        'FullStacks.live',
        'FullStacks.life',
        'ForeverWingsLLC.com',
        'C-Suite.xyz',
        'BucketGoats.com'
    ]
    
    for domain in domain_folders:
        source_path = Path(domain)
        if source_path.exists():
            target_path = domains_dir / domain
            
            # Remove target if it exists
            if target_path.exists():
                print(f"Removing existing {domain} from domains folder")
                safe_remove(target_path)
            
            print(f"Moving {domain} to domains folder")
            try:
                # Create target directory
                os.makedirs(target_path, exist_ok=True)
                
                # Copy all files except .git
                for item in os.listdir(source_path):
                    s = source_path / item
                    d = target_path / item
                    if item != '.git':
                        if os.path.isdir(s):
                            shutil.copytree(s, d, dirs_exist_ok=True)
                        else:
                            shutil.copy2(s, d)
                
                # Initialize git if needed
                if is_git_repo(source_path):
                    run_command("git init", cwd=target_path)
                
                # Remove source directory
                safe_remove(source_path)
                print(f"Successfully moved {domain}")
            except Exception as e:
                print(f"Error moving {domain}: {e}")

def move_scripts_to_scripts_folder():
    scripts_dir = Path('scripts')
    create_directory_if_not_exists(scripts_dir)
    
    # List of Python scripts to move
    python_scripts = [
        'cleanup_domains.py',
        'move_domains.py',
        'remove_duplicates.py',
        'fix_repos.py',
        'push_to_github.py',
        'setup_content.py',
        'setup_sites.py',
        'delete_repositories.py',
        'update_remotes.py',
        'setup_repositories.py',
        'verify_repos.py',
        'setup_domains.py',
        'github_setup.py',
        'test_namecheap.py',
        'namecheap_api.py',
        'domain_manager.py',
        'dashboard.py',
        'site_generator.py',
        'context_transfer.py',
        'domain_parser.py',
        'engine.py'
    ]
    
    for script in python_scripts:
        if os.path.exists(script):
            target_path = scripts_dir / script
            if os.path.exists(target_path):
                print(f"Removing existing {script} from scripts folder")
                safe_remove(target_path)
            shutil.move(script, target_path)
            print(f"Moved {script} to scripts folder")

def main():
    print("Starting repository organization...")
    move_domains_to_domains_folder()
    move_scripts_to_scripts_folder()
    print("Repository organization complete!")

if __name__ == "__main__":
    main() 