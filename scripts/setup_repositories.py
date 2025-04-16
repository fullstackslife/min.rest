import os
from github import Github
from dotenv import load_dotenv
import logging
import subprocess

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def setup_repositories():
    # Load environment variables
    load_dotenv()
    
    # Get GitHub token
    github_token = os.getenv('GITHUB_TOKEN')
    if not github_token:
        logger.error("GitHub token not found in environment variables")
        return
    
    # Initialize GitHub client
    g = Github(github_token)
    user = g.get_user()
    
    # Get list of domains from filesystem
    domains = [d for d in os.listdir('.') if os.path.isdir(d) and '.' in d and not d.startswith('.')]
    
    for domain in domains:
        repo_name = domain.replace('.', '-')
        try:
            # Create repository on GitHub
            repo = user.create_repo(
                repo_name,
                description=f"Website for {domain}",
                private=False,
                has_issues=False,
                has_wiki=False,
                has_downloads=False,
                auto_init=False
            )
            logger.info(f"Created repository {repo_name} at {repo.html_url}")
            
            # Initialize git repository in the domain folder
            os.chdir(domain)
            subprocess.run(['git', 'init'], check=True)
            subprocess.run(['git', 'add', '.'], check=True)
            subprocess.run(['git', 'commit', '-m', 'Initial commit'], check=True)
            
            # Add remote and push
            remote_url = f"https://{github_token}@github.com/{user.login}/{repo_name}.git"
            subprocess.run(['git', 'remote', 'add', 'origin', remote_url], check=True)
            subprocess.run(['git', 'push', '-u', 'origin', 'main'], check=True)
            
            # Enable GitHub Pages
            repo.create_pages_site(
                source={
                    "branch": "main",
                    "path": "/"
                }
            )
            logger.info(f"Enabled GitHub Pages for {repo_name}")
            
            os.chdir('..')
            
        except Exception as e:
            logger.error(f"Failed to set up repository for {domain}: {str(e)}")
            os.chdir('..')

if __name__ == "__main__":
    setup_repositories() 