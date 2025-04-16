import os
from dotenv import load_dotenv
from namecheap_api import NamecheapAPI
import logging
import time

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def split_domain(domain: str) -> tuple[str, str]:
    """Split domain into SLD and TLD parts."""
    parts = domain.split('.')
    if len(parts) < 2:
        raise ValueError(f"Invalid domain format: {domain}")
    return parts[0], parts[1]

def setup_gmail_dns(domain: str):
    """Set up Gmail DNS records for a domain."""
    # Load environment variables
    load_dotenv()
    
    # Initialize Namecheap API
    api = NamecheapAPI(
        api_user=os.getenv('NAMECHEAP_API_USER'),
        api_key=os.getenv('NAMECHEAP_API_KEY'),
        username=os.getenv('NAMECHEAP_USERNAME'),
        client_ip=os.getenv('NAMECHEAP_CLIENT_IP'),
        sandbox=os.getenv('NAMECHEAP_SANDBOX', 'false').lower() == 'true'
    )
    
    # Split domain into SLD and TLD
    sld, tld = split_domain(domain)
    logger.info(f"Setting up Gmail DNS records for {domain}")
    
    # First, get current records
    try:
        current_records = api.get_dns_records(domain)
        logger.info(f"Current records: {current_records}")
    except Exception as e:
        logger.error(f"Failed to get current records: {str(e)}")
        return
    
    # Define all required records
    new_records = [
        # MX Records
        {
            'RecordType': 'MX',
            'HostName': '@',
            'Address': 'aspmx.l.google.com',
            'MXPref': '1',
            'TTL': '3600'
        },
        {
            'RecordType': 'MX',
            'HostName': '@',
            'Address': 'alt1.aspmx.l.google.com',
            'MXPref': '5',
            'TTL': '3600'
        },
        {
            'RecordType': 'MX',
            'HostName': '@',
            'Address': 'alt2.aspmx.l.google.com',
            'MXPref': '5',
            'TTL': '3600'
        },
        {
            'RecordType': 'MX',
            'HostName': '@',
            'Address': 'alt3.aspmx.l.google.com',
            'MXPref': '10',
            'TTL': '3600'
        },
        {
            'RecordType': 'MX',
            'HostName': '@',
            'Address': 'alt4.aspmx.l.google.com',
            'MXPref': '10',
            'TTL': '3600'
        },
        # SPF Record
        {
            'RecordType': 'TXT',
            'HostName': '@',
            'Address': 'v=spf1 include:_spf.google.com ~all',
            'TTL': '3600'
        },
        # DMARC Record
        {
            'RecordType': 'TXT',
            'HostName': '_dmarc',
            'Address': 'v=DMARC1; p=none; rua=mailto:admin@fullstacks.us',
            'TTL': '3600'
        }
    ]
    
    # Prepare parameters for the API call
    params = {
        'SLD': sld,
        'TLD': tld
    }
    
    # Add all records to the parameters
    for i, record in enumerate(new_records, 1):
        for key, value in record.items():
            params[f"{key}{i}"] = value
    
    try:
        # Make the API request to set all hosts at once
        api._make_request('namecheap.domains.dns.setHosts', params)
        logger.info("Successfully set up Gmail DNS records")
        
        # Verify the records were set
        time.sleep(2)  # Wait a bit before verifying
        updated_records = api.get_dns_records(domain)
        logger.info("Updated DNS records:")
        for record in updated_records:
            logger.info(f"- Type: {record.get('type')}, Name: {record.get('name')}, "
                       f"Address: {record.get('address')}, TTL: {record.get('ttl')}")
    
    except Exception as e:
        logger.error(f"Failed to set DNS records: {str(e)}")
        return

if __name__ == "__main__":
    setup_gmail_dns("fullstacks.us") 