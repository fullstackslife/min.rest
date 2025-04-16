import os
from pathlib import Path
import json
from domain_manager import DomainManager
from namecheap_api import NamecheapAPI
import logging
from typing import Dict, List, Optional
from datetime import datetime
from dotenv import load_dotenv
import requests
from github import Github

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# GitHub Pages IP addresses
GITHUB_PAGES_IPS = [
    "185.199.108.153",
    "185.199.109.153",
    "185.199.110.153",
    "185.199.111.153"
]

# Email forwarding configuration
EMAIL_CONFIG = {
    "MX": [
        {
            "name": "@",
            "address": "mx1.improvmx.com",
            "mx_pref": 10,
            "ttl": 1800
        },
        {
            "name": "@",
            "address": "mx2.improvmx.com",
            "mx_pref": 20,
            "ttl": 1800
        }
    ],
    "TXT": [
        {
            "name": "@",
            "address": "v=spf1 include:spf.improvmx.com ~all",
            "ttl": 1800
        }
    ]
}

def ensure_domain_structure(domain: str) -> None:
    """Ensure domain directory structure exists."""
    domain_dir = Path(domain)
    records_dir = domain_dir / "content" / "records"
    records_dir.mkdir(parents=True, exist_ok=True)
    
    # Create default DNS records file if it doesn't exist
    dns_file = records_dir / "dns.json"
    if not dns_file.exists():
        default_dns = {
            "records": {
                "A": [],
                "CNAME": [],
                "MX": [],
                "TXT": [],
                "NS": []
            },
            "last_updated": datetime.now().isoformat()
        }
        with open(dns_file, 'w') as f:
            json.dump(default_dns, f, indent=2)
        logger.info(f"Created default DNS records file at {dns_file}")

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

def check_github_pages_status(repo_name: str, github_token: str) -> Optional[Dict]:
    """Check if GitHub Pages is already enabled for a repository."""
    try:
        g = Github(github_token)
        repo = g.get_user().get_repo(repo_name)
        pages = repo.get_pages()
        return {
            "enabled": pages is not None,
            "source": pages.source if pages else None,
            "url": pages.html_url if pages else None
        }
    except Exception as e:
        logger.warning(f"Could not check GitHub Pages status for {repo_name}: {str(e)}")
        return None

def check_dns_records(domain: str) -> bool:
    """Check if DNS records are already properly configured."""
    try:
        # Check A records
        for ip in GITHUB_PAGES_IPS:
            response = requests.get(f"http://{domain}", timeout=5)
            if response.status_code == 200:
                return True
    except Exception:
        pass
    return False

def setup_domain(namecheap_api: NamecheapAPI, domain: str, github_username: str, github_token: str) -> bool:
    """Set up a domain with GitHub Pages and email forwarding."""
    try:
        logger.info(f"Setting up domain: {domain}")
        
        # Check if GitHub Pages is already enabled
        repo_name = domain.replace('.', '-')
        pages_status = check_github_pages_status(repo_name, github_token)
        if pages_status and pages_status["enabled"]:
            logger.info(f"GitHub Pages already enabled for {domain} at {pages_status['url']}")
        
        # Check if DNS records are already configured
        if check_dns_records(domain):
            logger.info(f"DNS records already configured for {domain}")
            return True
        
        # Split domain into SLD and TLD
        parts = domain.split('.')
        if len(parts) < 2:
            logger.error(f"Invalid domain format: {domain}")
            return False
        
        # For domains like example.co.uk, we need to handle them differently
        if len(parts) > 2 and parts[-2] in {'co', 'com', 'org', 'net', 'edu', 'gov', 'it'}:
            sld = '.'.join(parts[:-2])
            tld = '.'.join(parts[-2:])
        else:
            sld = parts[0]
            tld = '.'.join(parts[1:])
        
        # First, ensure domain is using Namecheap's default DNS servers
        try:
            logger.info(f"Setting {domain} to use Namecheap's default DNS servers...")
            params = {
                'SLD': sld,
                'TLD': tld
            }
            namecheap_api._make_request('namecheap.domains.dns.setDefault', params)
            logger.info(f"Successfully set {domain} to use Namecheap's default DNS servers")
        except Exception as e:
            logger.error(f"Failed to set default DNS servers for {domain}: {str(e)}")
            return False
        
        # Get current DNS records
        current_records = namecheap_api.get_dns_records(f"{sld}.{tld}")
        logger.info(f"Current DNS records: {current_records}")
        
        # Build list of new records
        new_records = []
        
        # Add GitHub Pages A records
        for ip in GITHUB_PAGES_IPS:
            new_records.append({
                'HostName': '@',
                'RecordType': 'A',
                'Address': ip,
                'TTL': '1800'
            })
        
        # Add GitHub Pages CNAME record
        new_records.append({
            'HostName': 'www',
            'RecordType': 'CNAME',
            'Address': 'fullstackslife.github.io',
            'TTL': '1800'
        })
        
        # Add email forwarding records
        for record in EMAIL_CONFIG["MX"]:
            new_records.append({
                'HostName': record["name"],
                'RecordType': 'MX',
                'Address': record["address"],
                'MXPref': str(record["mx_pref"]),
                'TTL': str(record["ttl"])
            })
        
        for record in EMAIL_CONFIG["TXT"]:
            new_records.append({
                'HostName': record["name"],
                'RecordType': 'TXT',
                'Address': record["address"],
                'TTL': str(record["ttl"])
            })
        
        # Update DNS records
        try:
            params = {
                'SLD': sld,
                'TLD': tld,
                'HostName1': '@',
                'RecordType1': 'A',
                'Address1': '185.199.108.153',
                'TTL1': '1800',
                'HostName2': '@',
                'RecordType2': 'A',
                'Address2': '185.199.109.153',
                'TTL2': '1800',
                'HostName3': '@',
                'RecordType3': 'A',
                'Address3': '185.199.110.153',
                'TTL3': '1800',
                'HostName4': '@',
                'RecordType4': 'A',
                'Address4': '185.199.111.153',
                'TTL4': '1800',
                'HostName5': 'www',
                'RecordType5': 'CNAME',
                'Address5': 'fullstackslife.github.io',
                'TTL5': '1800'
            }
            
            # Make the request
            namecheap_api._make_request('namecheap.domains.dns.setHosts', params)
            logger.info(f"Successfully updated DNS records for {domain}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to update DNS records: {str(e)}")
            return False
        
    except Exception as e:
        logger.error(f"Error setting up domain {domain}: {str(e)}")
        return False

def main():
    # Load environment variables
    load_dotenv()
    
    # Initialize Namecheap API
    namecheap_api = NamecheapAPI(
        api_user=os.getenv('NAMECHEAP_API_USER'),
        api_key=os.getenv('NAMECHEAP_API_KEY'),
        username=os.getenv('NAMECHEAP_USERNAME'),
        client_ip=os.getenv('NAMECHEAP_CLIENT_IP'),
        sandbox=os.getenv('NAMECHEAP_SANDBOX', 'false').lower() == 'true'
    )
    
    # Get GitHub token
    github_token = os.getenv('GITHUB_TOKEN')
    if not github_token:
        logger.error("GitHub token not found in environment variables")
        return
    
    # Get list of domains from filesystem
    all_domains = [d for d in os.listdir('.') if os.path.isdir(d)]
    domains = [domain for domain in all_domains if is_valid_domain(domain)]
    
    if not domains:
        logger.error("No valid domains found")
        return
    
    logger.info(f"Found {len(domains)} valid domains: {', '.join(domains)}")
    
    # Fixed GitHub username for all domains
    github_username = "fullstackslife"
    logger.info(f"Using GitHub username: {github_username}")
    
    # Set up each domain
    for domain in domains:
        if setup_domain(namecheap_api, domain, github_username, github_token):
            logger.info(f"Successfully set up DNS records for {domain}")
        else:
            logger.error(f"Failed to set up DNS records for {domain}")

if __name__ == "__main__":
    main() 