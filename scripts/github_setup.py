import os
from pathlib import Path
import logging
import subprocess
import time
import requests
from typing import List, Dict
import json
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# GitHub configuration
GITHUB_USERNAME = "fullstackslife"
GITHUB_TOKEN = os.getenv('GITHUB_TOKEN')

if not GITHUB_TOKEN:
    logger.error("GITHUB_TOKEN environment variable not set")
    exit(1)

def is_valid_domain(domain: str) -> bool:
    """Check if a domain is valid."""
    # Skip hidden directories and files
    if domain.startswith('.'):
        return False
    
    # Skip directories without a dot (not a domain)
    if '.' not in domain:
        return False
    
    # Skip common non-domain directories
    invalid_dirs = {'node_modules', 'venv', 'dist', 'build', 'content', 'assets', 'config'}
    if domain in invalid_dirs:
        return False
    
    # Skip NewAgeWeb.it.com as it needs to keep its existing records
    if domain == 'NewAgeWeb.it.com':
        return False
    
    return True

def git_commands(domain: str) -> bool:
    """Execute git commands for a domain repository."""
    try:
        domain_path = Path(domain)
        
        # Initialize git if not already initialized
        if not (domain_path / '.git').exists():
            subprocess.run(['git', 'init'], cwd=domain_path, check=True)
            logger.info(f"Initialized git repository for {domain}")
        
        # Get current branch name
        try:
            branch = subprocess.check_output(['git', 'rev-parse', '--abbrev-ref', 'HEAD'], 
                                          cwd=domain_path, text=True).strip()
        except:
            branch = 'master'  # Default to master if command fails
        
        # Add all files
        subprocess.run(['git', 'add', '.'], cwd=domain_path, check=True)
        
        # Commit changes (ignore if nothing to commit)
        try:
            subprocess.run(['git', 'commit', '-m', f'Update site content - {datetime.now().isoformat()}'], 
                         cwd=domain_path, check=True)
        except subprocess.CalledProcessError:
            logger.info(f"No changes to commit for {domain}")
        
        # Add remote if not exists
        remote_url = f'https://{GITHUB_USERNAME}:{GITHUB_TOKEN}@github.com/{GITHUB_USERNAME}/{domain}.git'
        try:
            subprocess.run(['git', 'remote', 'get-url', 'origin'], cwd=domain_path, check=True)
        except subprocess.CalledProcessError:
            subprocess.run(['git', 'remote', 'add', 'origin', remote_url], cwd=domain_path, check=True)
            logger.info(f"Added remote for {domain}")
        
        # Push to GitHub using the current branch name
        try:
            subprocess.run(['git', 'push', '-u', 'origin', branch], cwd=domain_path, check=True)
            logger.info(f"Successfully pushed changes for {domain}")
            return True
        except subprocess.CalledProcessError:
            # If push fails, try creating the repository first
            logger.info(f"Creating repository for {domain}")
            headers = {
                'Authorization': f'token {GITHUB_TOKEN}',
                'Accept': 'application/vnd.github.v3+json'
            }
            data = {
                'name': domain,
                'private': False,
                'auto_init': False
            }
            response = requests.post(
                'https://api.github.com/user/repos',
                headers=headers,
                json=data
            )
            if response.status_code == 201:
                # Try pushing again
                subprocess.run(['git', 'push', '-u', 'origin', branch], cwd=domain_path, check=True)
                logger.info(f"Successfully pushed changes for {domain}")
                return True
            else:
                logger.error(f"Failed to create repository for {domain}: {response.text}")
                return False
        
    except subprocess.CalledProcessError as e:
        logger.error(f"Git command failed for {domain}: {str(e)}")
        return False
    except Exception as e:
        logger.error(f"Error processing {domain}: {str(e)}")
        return False

def enable_github_pages(domain: str) -> bool:
    """Enable GitHub Pages for a repository."""
    try:
        headers = {
            'Authorization': f'token {GITHUB_TOKEN}',
            'Accept': 'application/vnd.github.v3+json'
        }
        
        # Get the normalized repository name (GitHub converts to lowercase)
        repo_name = domain.lower()
        
        # Check if Pages is already enabled
        response = requests.get(
            f'https://api.github.com/repos/{GITHUB_USERNAME}/{repo_name}/pages',
            headers=headers
        )
        
        if response.status_code == 200:
            logger.info(f"GitHub Pages is already enabled for {domain}")
            return True
        
        # If not enabled, create the GitHub Pages site
        data = {
            'source': {
                'branch': 'master',  # Use master instead of main
                'path': '/'
            }
        }
        
        # Create the Pages site
        response = requests.post(
            f'https://api.github.com/repos/{GITHUB_USERNAME}/{repo_name}/pages',
            headers=headers,
            json=data
        )
        
        if response.status_code in [201, 204]:
            logger.info(f"Successfully enabled GitHub Pages for {domain}")
            
            # Update repository settings to enforce HTTPS
            update_data = {
                'https_enforced': True
            }
            response = requests.put(
                f'https://api.github.com/repos/{GITHUB_USERNAME}/{repo_name}/pages',
                headers=headers,
                json=update_data
            )
            
            if response.status_code in [200, 204]:
                logger.info(f"Successfully configured HTTPS for {domain}")
            else:
                logger.warning(f"Failed to configure HTTPS for {domain} (will be auto-configured later): {response.text}")
            return True
        else:
            logger.error(f"Failed to enable GitHub Pages for {domain}: {response.text}")
            return False
            
    except Exception as e:
        logger.error(f"Error enabling GitHub Pages for {domain}: {str(e)}")
        return False

def verify_site_access(domain: str) -> bool:
    """Verify if a site is accessible through its custom domain."""
    try:
        # Try both http and https
        for protocol in ['https', 'http']:
            url = f'{protocol}://{domain}'
            try:
                response = requests.get(url, timeout=5, allow_redirects=True)
                if response.status_code == 200:
                    logger.info(f"Successfully accessed {url}")
                    return True
                else:
                    logger.warning(f"Got status code {response.status_code} for {url}")
            except requests.RequestException as e:
                logger.warning(f"Failed to access {url}: {str(e)}")
                continue
        
        logger.warning(f"Could not access {domain} through any protocol")
        logger.info(f"Note: It may take up to 24 hours for DNS changes to fully propagate")
        return False
        
    except Exception as e:
        logger.error(f"Error verifying site access for {domain}: {str(e)}")
        return False

def main():
    if not GITHUB_TOKEN:
        logger.error("GITHUB_TOKEN environment variable not set")
        return
    
    # Get list of domains from filesystem
    all_domains = [d for d in os.listdir('.') if os.path.isdir(d)]
    domains = [domain for domain in all_domains if is_valid_domain(domain)]
    
    if not domains:
        logger.error("No valid domains found")
        return
    
    logger.info(f"Found {len(domains)} valid domains: {', '.join(domains)}")
    
    # Process each domain
    for domain in domains:
        logger.info(f"\nProcessing domain: {domain}")
        
        # Push to GitHub
        if git_commands(domain):
            # Enable GitHub Pages
            if enable_github_pages(domain):
                # Wait a short time for GitHub Pages to start building
                logger.info(f"Waiting for GitHub Pages to start building for {domain}...")
                time.sleep(5)
                
                # Verify site access
                verify_site_access(domain)
            else:
                logger.error(f"Failed to enable GitHub Pages for {domain}")
        else:
            logger.error(f"Failed to push changes for {domain}")
    
    logger.info("\nSetup complete! Note:")
    logger.info("1. It may take up to 24 hours for DNS changes to fully propagate")
    logger.info("2. GitHub Pages will automatically configure HTTPS certificates")
    logger.info("3. You can check the status of your sites at https://github.com/{GITHUB_USERNAME}/<domain>/settings/pages")

if __name__ == "__main__":
    main() 