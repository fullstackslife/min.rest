import os
from dotenv import load_dotenv
from domain_manager import DomainManager
import logging
import sys
import json
from pathlib import Path
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('namecheap_debug.log')
    ]
)

# Get logger instances for different components
logger = logging.getLogger(__name__)
namecheap_logger = logging.getLogger('namecheap_api')
domain_logger = logging.getLogger('domain_manager')

def ensure_directory_exists(path: str) -> None:
    """Ensure the directory exists, create it if it doesn't."""
    Path(path).mkdir(parents=True, exist_ok=True)

def ensure_domain_structure(domain: str) -> None:
    """Ensure domain directory structure exists."""
    domain_dir = Path(domain)
    records_dir = domain_dir / "content" / "records"
    ensure_directory_exists(str(records_dir))
    
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

def main():
    # Load environment variables
    load_dotenv()
    
    # Get Namecheap credentials from environment
    namecheap_config = {
        'api_user': os.getenv('NAMECHEAP_API_USER'),
        'api_key': os.getenv('NAMECHEAP_API_KEY'),
        'username': os.getenv('NAMECHEAP_USERNAME'),
        'client_ip': os.getenv('NAMECHEAP_CLIENT_IP'),
        'sandbox': os.getenv('NAMECHEAP_SANDBOX', 'False').lower() == 'true'
    }
    
    # Validate required environment variables
    missing_vars = [k for k, v in namecheap_config.items() if v is None]
    if missing_vars:
        logger.error(f"Missing required environment variables: {', '.join(missing_vars)}")
        return
    
    logger.info("Starting Namecheap API test")
    logger.debug(f"Using Namecheap config: {namecheap_config}")
    
    # Initialize DomainManager with Namecheap config
    try:
        manager = DomainManager(workspace_root=".", namecheap_config=namecheap_config)
        logger.info("Successfully initialized DomainManager")
    except Exception as e:
        logger.error(f"Failed to initialize DomainManager: {str(e)}", exc_info=True)
        return
    
    # Test domain - replace with your actual domain
    test_domain = "fullstacks.life"
    
    try:
        # Ensure domain structure exists
        logger.info(f"Ensuring domain structure exists for {test_domain}...")
        ensure_domain_structure(test_domain)
        
        # Get DNS records from Namecheap
        logger.info(f"Fetching DNS records for {test_domain}...")
        if manager.sync_dns_records(test_domain):
            logger.info("Successfully synced DNS records")
            
            # Get and display the records
            dns_records = manager.get_dns_records(test_domain)
            logger.info(f"DNS Records for {test_domain}:")
            
            # Display records in console
            for record_type, records in dns_records["records"].items():
                if records:
                    logger.info(f"\n{record_type} Records:")
                    for record in records:
                        logger.info(f"  - Name: {record['name']}")
                        logger.info(f"    Value: {record['value']}")
                        logger.info(f"    TTL: {record['ttl']}")
                        logger.info(f"    ID: {record['id']}")
        else:
            logger.error("Failed to sync DNS records")
            
    except Exception as e:
        logger.error(f"Error during DNS record sync: {str(e)}", exc_info=True)

if __name__ == "__main__":
    main() 