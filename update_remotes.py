import os
from dotenv import load_dotenv
import subprocess
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def update_remotes():
    # Load environment variables
    load_dotenv()
    
    # Get GitHub token
    github_token = os.getenv('GITHUB_TOKEN')
    if not github_token:
        logger.error("GitHub token not found in environment variables")
        return
    
    # Get GitHub username
    github_username = "fullstackslife"
    
    # Get list of domains from filesystem
    domains = [d for d in os.listdir('.') if os.path.isdir(d) and '.' in d and not d.startswith('.')]
    
    for domain in domains:
        repo_name = domain.replace('.', '-')
        try:
            # Change to domain directory
            os.chdir(domain)
            
            # Remove existing remote
            subprocess.run(['git', 'remote', 'remove', 'origin'], check=True)
            
            # Add new remote
            remote_url = f"https://{github_token}@github.com/{github_username}/{repo_name}.git"
            subprocess.run(['git', 'remote', 'add', 'origin', remote_url], check=True)
            
            # Push to new remote
            subprocess.run(['git', 'push', '-u', 'origin', 'master'], check=True)
            
            logger.info(f"Updated remote for {domain}")
            
            # Change back to parent directory
            os.chdir('..')
            
        except Exception as e:
            logger.error(f"Failed to update remote for {domain}: {str(e)}")
            os.chdir('..')

if __name__ == "__main__":
    update_remotes() 