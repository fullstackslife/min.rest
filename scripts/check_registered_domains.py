import os
from dotenv import load_dotenv
from namecheap_api import NamecheapAPI
import logging
from datetime import datetime
from typing import Dict, List

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def check_registered_domains() -> List[Dict]:
    """Check all registered domains through Namecheap API."""
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
        return []
    
    try:
        # Initialize Namecheap API
        api = NamecheapAPI(
            api_user=namecheap_config['api_user'],
            api_key=namecheap_config['api_key'],
            username=namecheap_config['username'],
            client_ip=namecheap_config['client_ip'],
            sandbox=namecheap_config['sandbox']
        )
        
        # Get list of domains
        domains = api.get_domains()
        
        if not domains:
            logger.warning("No domains found in Namecheap account")
            return []
        
        logger.info(f"Found {len(domains)} registered domains:")
        for domain in domains:
            logger.info(f"- {domain['name']} (Expires: {domain['expires']}, Locked: {domain['is_locked']})")
        
        return domains
        
    except Exception as e:
        logger.error(f"Error checking registered domains: {str(e)}")
        return []

if __name__ == "__main__":
    check_registered_domains() 