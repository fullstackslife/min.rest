import os
import shutil
from pathlib import Path

# List of repositories to set up
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

# Site-specific configurations
SITE_CONFIGS = {
    'TouchedByChanelsCleaning.com': {
        'site_name': 'Touched By Chanel\'s Cleaning',
        'site_description': 'Professional cleaning services for your home or business',
        'site_tagline': 'Making your space shine',
        'contact_email': 'contact@touchedbychanelscleaning.com',
        'contact_phone': '(555) 123-4567'
    },
    'NewAgeWeb.it.com': {
        'site_name': 'New Age Web',
        'site_description': 'Modern web development and digital solutions',
        'site_tagline': 'Building the future of the web',
        'contact_email': 'contact@newageweb.it.com',
        'contact_phone': '(555) 234-5678'
    },
    'FullStacks.live': {
        'site_name': 'Full Stacks Live',
        'site_description': 'Live coding and development resources',
        'site_tagline': 'Code. Create. Connect.',
        'contact_email': 'contact@fullstacks.live',
        'contact_phone': '(555) 345-6789'
    },
    'FullStacks.life': {
        'site_name': 'Full Stacks Life',
        'site_description': 'Resources for full-stack developers',
        'site_tagline': 'Empowering developers worldwide',
        'contact_email': 'contact@fullstacks.life',
        'contact_phone': '(555) 456-7890'
    },
    'ForeverWingsLLC.com': {
        'site_name': 'Forever Wings LLC',
        'site_description': 'Aviation services and consulting',
        'site_tagline': 'Taking your business to new heights',
        'contact_email': 'contact@foreverwingsllc.com',
        'contact_phone': '(555) 567-8901'
    },
    'C-Suite.xyz': {
        'site_name': 'C-Suite XYZ',
        'site_description': 'Executive consulting and leadership development',
        'site_tagline': 'Elevating executive performance',
        'contact_email': 'contact@c-suite.xyz',
        'contact_phone': '(555) 678-9012'
    },
    'BucketGoats.com': {
        'site_name': 'Bucket Goats',
        'site_description': 'Innovative solutions for modern businesses',
        'site_tagline': 'Think outside the bucket',
        'contact_email': 'contact@bucketgoats.com',
        'contact_phone': '(555) 789-0123'
    },
    'BellaAmour.me': {
        'site_name': 'Bella Amour',
        'site_description': 'Beauty and wellness services',
        'site_tagline': 'Your journey to beauty and wellness',
        'contact_email': 'contact@bellaamour.me',
        'contact_phone': '(555) 890-1234'
    }
}

def create_directory_structure(repo_path):
    """Create the necessary directory structure for a site."""
    directories = [
        'assets/css',
        'assets/js',
        'assets/images',
        '.github/workflows'
    ]
    
    for directory in directories:
        os.makedirs(os.path.join(repo_path, directory), exist_ok=True)

def copy_template_files(repo_path, config):
    """Copy and customize template files for a site."""
    template_dir = 'templates/base_site_structure'
    
    # Copy CSS
    shutil.copy(
        os.path.join(template_dir, 'assets/css/style.css'),
        os.path.join(repo_path, 'assets/css/style.css')
    )
    
    # Copy JavaScript
    shutil.copy(
        os.path.join(template_dir, 'assets/js/main.js'),
        os.path.join(repo_path, 'assets/js/main.js')
    )
    
    # Create and customize index.html
    with open(os.path.join(template_dir, 'index.html'), 'r') as f:
        content = f.read()
    
    for key, value in config.items():
        content = content.replace('{{ ' + key + ' }}', value)
    
    with open(os.path.join(repo_path, 'index.html'), 'w') as f:
        f.write(content)
    
    # Create CNAME file
    with open(os.path.join(repo_path, 'CNAME'), 'w') as f:
        f.write(repo_path)

def create_github_workflow(repo_path):
    """Create GitHub Actions workflow for deployment."""
    workflow_content = """name: Deploy to GitHub Pages

on:
  push:
    branches: [ main ]
  workflow_dispatch:

permissions:
  contents: read
  pages: write
  id-token: write

concurrency:
  group: "pages"
  cancel-in-progress: false

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout
        uses: actions/checkout@v4
      
      - name: Setup Pages
        uses: actions/configure-pages@v4
      
      - name: Upload artifact
        uses: actions/upload-pages-artifact@v3
        with:
          path: '.'

  deploy:
    environment:
      name: github-pages
      url: ${{ steps.deployment.outputs.page_url }}
    runs-on: ubuntu-latest
    needs: build
    steps:
      - name: Deploy to GitHub Pages
        id: deployment
        uses: actions/deploy-pages@v4
"""
    
    workflow_path = os.path.join(repo_path, '.github/workflows/deploy.yml')
    os.makedirs(os.path.dirname(workflow_path), exist_ok=True)
    
    with open(workflow_path, 'w') as f:
        f.write(workflow_content)

def main():
    for repo in REPOSITORIES:
        print(f"Setting up {repo}...")
        repo_path = repo
        
        # Create directory structure
        create_directory_structure(repo_path)
        
        # Copy and customize template files
        copy_template_files(repo_path, SITE_CONFIGS[repo])
        
        # Create GitHub workflow
        create_github_workflow(repo_path)
        
        print(f"Completed setup for {repo}")

if __name__ == "__main__":
    main() 