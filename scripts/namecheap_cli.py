import os
import sys
import argparse
from dotenv import load_dotenv
from namecheap_api import NamecheapAPI
import logging
from typing import Dict, List
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def get_namecheap_api() -> NamecheapAPI:
    """Initialize and return Namecheap API client."""
    load_dotenv()
    
    namecheap_config = {
        'api_user': os.getenv('NAMECHEAP_API_USER'),
        'api_key': os.getenv('NAMECHEAP_API_KEY'),
        'username': os.getenv('NAMECHEAP_USERNAME'),
        'client_ip': os.getenv('NAMECHEAP_CLIENT_IP'),
        'sandbox': os.getenv('NAMECHEAP_SANDBOX', 'False').lower() == 'true'
    }
    
    missing_vars = [k for k, v in namecheap_config.items() if v is None]
    if missing_vars:
        logger.error(f"Missing required environment variables: {', '.join(missing_vars)}")
        sys.exit(1)
    
    return NamecheapAPI(
        api_user=namecheap_config['api_user'],
        api_key=namecheap_config['api_key'],
        username=namecheap_config['username'],
        client_ip=namecheap_config['client_ip'],
        sandbox=namecheap_config['sandbox']
    )

def list_domains(api: NamecheapAPI) -> None:
    """List all registered domains."""
    try:
        logger.info("Attempting to fetch domains from Namecheap API...")
        domains = api.get_domains()
        
        if not domains:
            logger.warning("No domains found in Namecheap account")
            logger.info("Checking API configuration...")
            logger.info(f"API User: {api.api_user}")
            logger.info(f"Username: {api.username}")
            logger.info(f"Client IP: {api.client_ip}")
            logger.info(f"Sandbox Mode: {api.sandbox}")
            return
        
        logger.info(f"Found {len(domains)} registered domains:")
        for domain in domains:
            logger.info(f"- {domain['name']} (Expires: {domain['expires']}, Locked: {domain['is_locked']})")
    except Exception as e:
        logger.error(f"Error listing domains: {str(e)}")
        logger.error("Full error details:", exc_info=True)

def get_dns_records(api: NamecheapAPI, domain: str) -> None:
    """Get DNS records for a domain."""
    try:
        records = api.get_dns_records(domain)
        if not records:
            logger.warning(f"No DNS records found for {domain}")
            return
        
        logger.info(f"DNS records for {domain}:")
        for record in records:
            logger.info(f"- Type: {record['type']}, Name: {record['name']}, Address: {record['address']}, TTL: {record['ttl']}")
    except Exception as e:
        logger.error(f"Error getting DNS records: {str(e)}")

def add_dns_record(api: NamecheapAPI, domain: str, record_type: str, name: str, address: str, ttl: int = 1800) -> None:
    """Add a new DNS record."""
    try:
        if api.add_dns_record(domain, record_type, name, address, ttl=ttl):
            logger.info(f"Successfully added {record_type} record for {domain}")
        else:
            logger.error(f"Failed to add {record_type} record for {domain}")
    except Exception as e:
        logger.error(f"Error adding DNS record: {str(e)}")

def update_dns_record(api: NamecheapAPI, domain: str, host_id: str, record_type: str, name: str, address: str, ttl: int = 1800) -> None:
    """Update an existing DNS record."""
    try:
        if api.update_dns_record(domain, host_id, record_type, name, address, ttl=ttl):
            logger.info(f"Successfully updated {record_type} record for {domain}")
        else:
            logger.error(f"Failed to update {record_type} record for {domain}")
    except Exception as e:
        logger.error(f"Error updating DNS record: {str(e)}")

def delete_dns_record(api: NamecheapAPI, domain: str, host_id: str) -> None:
    """Delete a DNS record."""
    try:
        if api.delete_dns_record(domain, host_id):
            logger.info(f"Successfully deleted record {host_id} for {domain}")
        else:
            logger.error(f"Failed to delete record {host_id} for {domain}")
    except Exception as e:
        logger.error(f"Error deleting DNS record: {str(e)}")

def main():
    parser = argparse.ArgumentParser(description='Namecheap API Command Line Interface')
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # List domains command
    subparsers.add_parser('list', help='List all registered domains')
    
    # DNS records commands
    dns_parser = subparsers.add_parser('dns', help='DNS record operations')
    dns_subparsers = dns_parser.add_subparsers(dest='dns_command', help='DNS commands')
    
    # Get DNS records
    get_dns = dns_subparsers.add_parser('get', help='Get DNS records for a domain')
    get_dns.add_argument('domain', help='Domain name')
    
    # Add DNS record
    add_dns = dns_subparsers.add_parser('add', help='Add a DNS record')
    add_dns.add_argument('domain', help='Domain name')
    add_dns.add_argument('type', help='Record type (A, CNAME, MX, TXT, etc.)')
    add_dns.add_argument('name', help='Record name')
    add_dns.add_argument('address', help='Record address')
    add_dns.add_argument('--ttl', type=int, default=1800, help='TTL value (default: 1800)')
    
    # Update DNS record
    update_dns = dns_subparsers.add_parser('update', help='Update a DNS record')
    update_dns.add_argument('domain', help='Domain name')
    update_dns.add_argument('host_id', help='Host ID of the record to update')
    update_dns.add_argument('type', help='Record type (A, CNAME, MX, TXT, etc.)')
    update_dns.add_argument('name', help='Record name')
    update_dns.add_argument('address', help='Record address')
    update_dns.add_argument('--ttl', type=int, default=1800, help='TTL value (default: 1800)')
    
    # Delete DNS record
    delete_dns = dns_subparsers.add_parser('delete', help='Delete a DNS record')
    delete_dns.add_argument('domain', help='Domain name')
    delete_dns.add_argument('host_id', help='Host ID of the record to delete')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    api = get_namecheap_api()
    
    if args.command == 'list':
        list_domains(api)
    elif args.command == 'dns':
        if args.dns_command == 'get':
            get_dns_records(api, args.domain)
        elif args.dns_command == 'add':
            add_dns_record(api, args.domain, args.type, args.name, args.address, args.ttl)
        elif args.dns_command == 'update':
            update_dns_record(api, args.domain, args.host_id, args.type, args.name, args.address, args.ttl)
        elif args.dns_command == 'delete':
            delete_dns_record(api, args.domain, args.host_id)
        else:
            dns_parser.print_help()

if __name__ == "__main__":
    main() 