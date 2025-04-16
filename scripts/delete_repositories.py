import os
from github import Github
from dotenv import load_dotenv
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def delete_repositories():
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
    
    # List of repositories to delete
    repositories = [
        'BellaAmour-me',
        'BucketGoats-com',
        'C-Suite-xyz',
        'ForeverWingsLLC-com',
        'FullStacks-life',
        'FullStacks-live',
        'FullStacks-shop',
        'NewAgeWeb-it-com',
        'TouchedByChanelsCleaning-com'
    ]
    
    for repo_name in repositories:
        try:
            # Get the repository
            repo = user.get_repo(repo_name)
            
            # Delete the repository
            repo.delete()
            logger.info(f"Successfully deleted repository: {repo_name}")
            
        except Exception as e:
            logger.error(f"Failed to delete repository {repo_name}: {str(e)}")

if __name__ == "__main__":
    delete_repositories() 