import os
from pathlib import Path
import logging
from typing import List, Dict
import json
from datetime import datetime
from github import Github
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Required files and directories
REQUIRED_FILES = [
    'index.html',
    'about.html',
    'services.html',
    'contact.html',
    'CNAME',
    'README.md',
    '.gitignore',
    'config.template.json'
]

REQUIRED_DIRS = [
    'assets',
    'content',
    'config'
]

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

def verify_domain_structure(domain: str) -> Dict[str, bool]:
    """Verify the structure of a domain repository."""
    results = {
        'files': {},
        'directories': {},
        'overall': True
    }
    
    domain_path = Path(domain)
    
    # Check required files
    for file in REQUIRED_FILES:
        file_path = domain_path / file
        exists = file_path.exists()
        results['files'][file] = exists
        if not exists:
            results['overall'] = False
            logger.warning(f"Missing file: {file_path}")
    
    # Check required directories
    for dir_name in REQUIRED_DIRS:
        dir_path = domain_path / dir_name
        exists = dir_path.exists() and dir_path.is_dir()
        results['directories'][dir_name] = exists
        if not exists:
            results['overall'] = False
            logger.warning(f"Missing directory: {dir_path}")
    
    # Verify CNAME content
    cname_path = domain_path / 'CNAME'
    if cname_path.exists():
        with open(cname_path, 'r') as f:
            content = f.read().strip()
            if content != domain:
                logger.warning(f"CNAME content mismatch in {domain}: expected {domain}, got {content}")
                results['overall'] = False
    
    return results

def update_domain_structure(domain: str) -> None:
    """Update the structure of a domain repository."""
    domain_path = Path(domain)
    
    # Create required directories
    for dir_name in REQUIRED_DIRS:
        dir_path = domain_path / dir_name
        dir_path.mkdir(exist_ok=True)
        logger.info(f"Created directory: {dir_path}")
    
    # Create CNAME file if missing
    cname_path = domain_path / 'CNAME'
    if not cname_path.exists():
        with open(cname_path, 'w') as f:
            f.write(domain)
        logger.info(f"Created CNAME file for {domain}")
    
    # Create README.md if missing
    readme_path = domain_path / 'README.md'
    if not readme_path.exists():
        with open(readme_path, 'w') as f:
            f.write(f"# {domain}\n\nThis is the GitHub Pages repository for {domain}.\n")
        logger.info(f"Created README.md for {domain}")
    
    # Create .gitignore if missing
    gitignore_path = domain_path / '.gitignore'
    if not gitignore_path.exists():
        with open(gitignore_path, 'w') as f:
            f.write("""# Dependencies
node_modules/
venv/

# Build outputs
dist/
build/

# Environment files
.env
.env.local

# IDE files
.idea/
.vscode/

# OS files
.DS_Store
Thumbs.db
""")
        logger.info(f"Created .gitignore for {domain}")
    
    # Create config.template.json if missing
    config_template_path = domain_path / 'config.template.json'
    if not config_template_path.exists():
        template = {
            "site": {
                "title": domain,
                "description": f"Welcome to {domain}",
                "author": "FullStacks.life",
                "email": f"contact@{domain}",
                "phone": "",
                "address": "",
                "social": {
                    "facebook": "",
                    "twitter": "",
                    "instagram": "",
                    "linkedin": ""
                }
            },
            "analytics": {
                "google_analytics_id": "",
                "hubspot_portal_id": "",
                "brevo_conversations_id": ""
            },
            "last_updated": datetime.now().isoformat()
        }
        with open(config_template_path, 'w') as f:
            json.dump(template, f, indent=2)
        logger.info(f"Created config.template.json for {domain}")

def verify_repositories():
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
            repo = user.get_repo(repo_name)
            logger.info(f"Repository {repo_name} exists at {repo.html_url}")
            # Check if GitHub Pages is enabled
            pages = repo.get_pages()
            if pages:
                logger.info(f"GitHub Pages is enabled for {repo_name} at {pages.html_url}")
            else:
                logger.warning(f"GitHub Pages is not enabled for {repo_name}")
        except Exception as e:
            logger.error(f"Repository {repo_name} does not exist or is not accessible: {str(e)}")

def main():
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
        
        # Verify current structure
        results = verify_domain_structure(domain)
        
        if not results['overall']:
            logger.info(f"Updating structure for {domain}")
            update_domain_structure(domain)
            
            # Verify again after updates
            results = verify_domain_structure(domain)
            if results['overall']:
                logger.info(f"Successfully updated structure for {domain}")
            else:
                logger.error(f"Failed to update structure for {domain}")
        else:
            logger.info(f"Domain {domain} structure is valid")

if __name__ == "__main__":
    verify_repositories() 